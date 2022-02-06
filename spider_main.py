#!/usr/bin/env python3

import aiohttp  # https://docs.aiohttp.org/en/stable/
import argparse
import asyncio
import bs4  # https://pypi.org/project/beautifulsoup4/
import collections.abc
import datetime
import logging
import re
import subprocess
import sys

async def main(argv: collections.abc.Sequence[str]) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("--concurrency", metavar="N", type=int,
                        dest="concurrency", default=10,
                        help="Number of concurrent I/O requests.")
    parser.add_argument("--pattern", metavar="PATTERN",
                        dest="pattern", default=lambda p: re.compile(x),
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
    async with aiohttp.ClientSession() as session:
        for site in (canonurl(s) for s in args.sites):
            soup = await fetch(session, site)
            print(site, "#" * 20, soup.title.string)
            if args.links:
                for link in soup.find_all("a"):
                    print(" ", link.get("href"))
            if args.text:
                print(soup.get_text())
    return 0

async def fetch(session: aiohttp.ClientSession, url: str) -> bs4.BeautifulSoup:
    """Returns the prettified webpage contents at URL."""
    async with session.get(url) as response:
        html = await response.text()
        return bs4.BeautifulSoup(html, "html.parser")

def canonurl(u: str) -> str:
    """Returns a canonical url."""
    if u.startswith(r"http://") or u.startswith(r"https://"):
        return u
    return f"http://{u}"

if __name__ == "__main__":
    asyncio.run(main(sys.argv))
