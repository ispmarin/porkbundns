#!/usr/bin/env python3
import sys
import argparse
import logging

from dns import manage_records

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Update DNS records on Porkbun")
    parser.add_argument(
        "-f",
        "--hostfile",
        type=str,
        dest="host_file",
        help="File with host DNS definitions, CSV format",
    )
    parser.add_argument(
        "-d",
        "--definitions",
        type=str,
        dest="def_file",
        default=".env/base.json",
        help="File with Porkbun credentials, JSON format",
    )
    args = parser.parse_args(args=None if sys.argv[1:] else ["--help"])

    logger.info("Starting DNS update using Porkbun API")
    manage_records.bulk_update(args.host_file, args.def_file)
    logger.info("Done updating records")
