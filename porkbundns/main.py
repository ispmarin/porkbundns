#!/usr/bin/env python3
import argparse
import logging
import sys

from dns.recordhandler import RecordHandler

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

    porkbunhandler = RecordHandler(args.def_file)
    logger.info("Starting DNS update using Porkbun API")
    porkbunhandler.change_records(args.host_file, "create")
    logger.info("Done updating records")
