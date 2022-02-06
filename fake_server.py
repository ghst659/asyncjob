#!/usr/bin/env python3

import argparse
import asyncio
import collections.abc
import datetime
import logging
import sys

async def main(argv: collections.abc.Sequence[str]) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("--name", metavar="NAME",
                        dest="name", default="NONAME",
                        help="Name of this workload.")
    parser.add_argument("--setup", metavar="ITERATIONS", type=int,
                        dest="setup", default=5,
                        help="Number of iterations spent in setup")
    parser.add_argument("--period", metavar="SECONDS", type=int,
                        dest="period", default=1,
                        help="Interval between beeps.")
    parser.add_argument("--limit", metavar="ITERATIONS", type=int,
                        dest="limit", default=10,
                        help="Maximum number of iterations.")
    parser.add_argument("--verbose",
                        dest='verbose', action="store_true",
                        help="run verbosely")
    args = parser.parse_args(args=argv[1:])
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    await setup(args.name, args.period, args.setup)
    await work_loop(args.name, args.period, args.limit)
    return 0

async def setup(name: str, period: int, duration: int):
    """Fake setup task."""
    logging.info("%s: setup init", name)
    for i in range(duration):
        if i > 0:
            await asyncio.sleep(period)
        logging.info("%s: setup %d", name, i)
    logging.info("%s: setup done", name)

async def work_loop(name: str, period: int, limit: int):
    """Fake working loop."""
    logging.info("%s: work start", name)
    for i in range(limit):
        if i > 0:
           await asyncio.sleep(period)
        ahora = datetime.datetime.now()
        logging.info("%s: work %d: %s", name, i, ahora.isoformat())
    logging.info("%s: work stop", name)

if __name__ == "__main__":
    asyncio.run(main(sys.argv))
