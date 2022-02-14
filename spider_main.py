#!/usr/bin/env python3

import aiohttp  # https://docs.aiohttp.org/en/stable/
import argparse
import asyncio
import bs4  # https://pypi.org/project/beautifulsoup4/
import collections
import collections.abc
import dataclasses
import datetime
import logging
import os
import re
import subprocess
import sys
import urllib.parse

@dataclasses.dataclass
class WorkItem:
    level: int
    url: str

async def main(argv: collections.abc.Sequence[str]) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("--concurrency", metavar="N", type=int,
                        dest="concurrency", default=10,
                        help="Number of concurrent I/O requests.")
    parser.add_argument("--depth", metavar="DEPTH", type=int, default=5,
                        dest="depth",
                        help="Maximum depth of recursion.")
    parser.add_argument("--pattern", metavar="PATTERN", default=None,
                        dest="pattern", type=lambda p: re.compile(x),
                        help="Pattern to watch out for.")
    parser.add_argument("--links", action="store_true", dest="links",
                        help="print links in document.")
    parser.add_argument("--text", action="store_true", dest="text",
                        help="print text in document.")
    parser.add_argument("--verbose",
                        dest='verbose', action="store_true",
                        help="run verbosely")
    parser.add_argument("sites", nargs="*",
                        help="root websites to visit.")
    args = parser.parse_args(args=argv[1:])
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    result = collections.defaultdict(set)
    patience = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=patience) as session:
        work_queue = asyncio.Queue()
        for site in args.sites:
            await work_queue.put((0, site.casefold()))
        pool = []
        for i in range(args.concurrency):
            pool.append(asyncio.create_task(fetch_loop(i, session,
                                                       work_queue, result)))
        await work_queue.join()
        for w in pool:
            w.cancel()
        await asyncio.gather(*pool)
    for site, links in result.items():
        print(site)
        for link in sorted(links):
            print("   ", link)
    return 0

async def fetch_loop(id: int, session: aiohttp.ClientSession,
                     queue: asyncio.Queue, result: dict[str, set]):
    """Repeatedly fetch and process urls."""
    while not asyncio.current_task().cancelled():
        try:
            item = await queue.get()
        except asyncio.CancelledError:
            logging.info("worker %d cancelled during queue get", id)
            return
        else:
            try:
                level, url = item
                if url in result or not url or not url.startswith("http"):
                    continue
                soup = await fetch(session, url)
                for a in soup.find_all("a"):
                    raw_link = a.get("href")
                    link_type = a.get("type")
                    child = urllib.parse.urljoin(url, raw_link).casefold()
                    if not child.endswith(".html"):
                        logging.info("ignore non-html: %s", child)
                        continue
                    # logging.info("%s %s -> %s", url, raw_link, child)
                    result[url].add(child)
                    if level < 4:
                        await queue.put((level + 1, child))
            except asyncio.CancelledError:
                logging.info("worker %d cancelled: working on %s", id, url)
                return
            finally:
                queue.task_done()

async def fetch(session: aiohttp.ClientSession,
                url: str) -> bs4.BeautifulSoup:
    """Returns the prettified webpage contents at URL."""
    logging.info("fetch: %s", url)
    async with session.get(url) as response:
        html = await response.text()
        return bs4.BeautifulSoup(html, "html.parser")

if __name__ == "__main__":
    sys.exit(asyncio.run(main(sys.argv)))
