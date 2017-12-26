import argparse
import asyncio
import logging
import pprint
import time

from cleansweep import get_sweeps_by_token
from cleansweep.constants import logger

def main():
    """Runs the sweeper once and prints the output, optionally logging more"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', help='Turn on debug logging', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    while True:
        sweeps_by_token = asyncio.get_event_loop().run_until_complete(get_sweeps_by_token())

        # Print from most profitable to least
        token_sweeps = []
        for token, sweeps in sweeps_by_token.items():
            max_sweep = max(sweeps, key=lambda s: s.revenue)
            token_sweeps.append((token, max_sweep.revenue, max_sweep))

        pprint.pprint(sorted(
            token_sweeps,
            # Revenue descending
            key=lambda s: -s[1],
        ))
        time.sleep(10)
