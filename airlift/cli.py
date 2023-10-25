import logging
import os
import signal
import sys
from pathlib import Path
from typing import Any, Optional

from airlift.utils_exceptions import CriticalError,AirtableError 
from airlift.cli_args import parse_args
from airlift.csv_data import csv_read
from airlift.airtable_upload import upload_data
from airlift.airtable_client import new_client

logger = logging.getLogger(__name__)

def abort(*_: Any) -> None:  # pragma: no cover
    print("\nAbort")  # noqa: WPS421
    os._exit(1)

def cli(*argv: str) -> None:
    args = parse_args(argv)
    setup_logging()
    logger.info("validating CSV file and Airtable Schema")

    data = csv_read(args.csv_file)
    airtable_client = new_client(token=args.token,base=args.base,table=args.table)

    logger.info("Uploading {} ...".format(args.csv_file.name))

    upload_data(client=airtable_client, new_data=data)

    logger.info("Done!")

def setup_logging() -> None:
    logging.basicConfig(format="%(levelname)s: %(message)s")

    logging.getLogger("airlift").setLevel(
        logging.DEBUG
    )

    file_handler = logging.FileHandler("airlift.log")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)-8.8s] %(message)s")
    )
    logging.getLogger("airlift").addHandler(file_handler)

    logging.getLogger("airtable").setLevel(logging.WARNING)

def main() -> None:

    signal.signal(signal.SIGINT, abort)
    try:
        cli(*sys.argv[1:])
    except(CriticalError,AirtableError) as e:
        logger.critical(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)

