#!/usr/bin/env python3

import argparse
import asyncio
import collections.abc
import datetime
import logging
import re
import subprocess
import sys

async def main(argv: collections.abc.Sequence[str]) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("--replicas", metavar="REPLICAS", type=int,
                        dest="replicas", default=2,
                        help="Number of job replicas")
    parser.add_argument("--pattern", metavar="PATTERN",
                        dest="pattern", default="",
                        help="Pattern to watch out for.")
    parser.add_argument("--verbose",
                        dest='verbose', action="store_true",
                        help="run verbosely")
    parser.add_argument("command", nargs="*",
                        help="command-line to execute.")
    args = parser.parse_args(args=argv[1:])
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    branches = []
    for r in range(args.replicas):
        tag = f"BRANCH-{r}"
        branches.append(
            asyncio.create_task(branch(tag, args.command, args.pattern)))
    await asyncio.gather(*branches)
    return 0

async def branch(tag: str, base: list[str], pattern: str):
    command = base + ["--name", tag]
    job = await start(command, pattern)
    logging.info(f"RETURN TO {tag}")
    async for raw_line in job.stdout:
        line = raw_line.decode("utf-8")
        logging.info("remainder: %s", line.rstrip())

async def start(cmd: list[str], pattern: str) -> asyncio.subprocess.Process:
    """Starts command and returns the process after seeing the pattern."""
    watcher = re.compile(pattern)
    job = await asyncio.create_subprocess_exec(cmd[0], *cmd[1:],
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.STDOUT)
    async for raw_line in job.stdout:
        line = raw_line.decode("utf-8")
        logging.info("output: %s", line.rstrip())
        if watcher.search(line):
            logging.info("FOUND: %s", pattern)
            break;
    return job
    
    
if __name__ == "__main__":
    asyncio.run(main(sys.argv))
