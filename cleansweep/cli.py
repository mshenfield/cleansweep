import argparse
import asyncio
import logging
import pprint
import time

from cleansweep import run_client
from cleansweep.constants import logger

def main():
    """Runs the sweeper once and prints the output, optionally logging more"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', help='Turn on debug logging', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        socket_io_logger = logging.getLogger('socketIO-client')
        socket_io_logger.setLevel(logging.DEBUG)
        socket_io_logger.addHandler(logging.StreamHandler())

    run_client()
