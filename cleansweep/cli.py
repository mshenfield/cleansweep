import argparse
import asyncio
import logging
import pprint
import time

from cleansweep import listen
from cleansweep.constants import logger

def main():
    """Runs the sweeper once and prints the output, optionally logging more"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', help='Turn on debug logging', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    asyncio.get_event_loop().run_until_complete(listen())
