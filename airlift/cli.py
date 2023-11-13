import logging
import os
import signal
import sys
from pathlib import Path
from typing import Any, Optional
import pathlib

from airlift.utils_exceptions import CriticalError,AirtableError 
from airlift.cli_args import parse_args
from airlift.csv_data import csv_read
from airlift.airtable_upload import upload_data
from airlift.json_data import json_read
from airlift.airtable_client import new_client

logger = logging.getLogger(__name__)

def abort(*_: Any) -> None:  # pragma: no cover
    print("\nAbort")  # noqa: WPS421
    os._exit(1)

def cli(*argv: str) -> None:
    args = parse_args(argv)
    setup_logging(is_verbose=args.verbose,log_file=args.log)

    workers = args.workers if args.workers else 5

    airtable_client = new_client(token=args.token,base=args.base,table=args.table)

    logger.info(f"validating {args.csv_file.name} and Airtable Schema")

    suffix = pathlib.Path(args.csv_file.name).suffix

    if "csv" in suffix:
        data = csv_read(args.csv_file,args.fail_on_duplicate_csv_columns,args.attachment_columns,args.dropbox_token)
    elif "json" in suffix:
        data = json_read(args.csv_file,args.fail_on_duplicate_csv_columns)
    else:
        raise CriticalError("File type not supported!")
    #print(data)

    logger.info("Validation done!")

    if not data:
        raise CriticalError("file is empty")

    data = airtable_client.missing_fields_check(data,disable_bypass=args.disable_bypass_column_creation)

    upload_data(client=airtable_client, new_data=data, workers = workers)

    logger.info("Done!")

def setup_logging(is_verbose: bool=False, log_file: Optional[Path]=None) -> None:
    logging.basicConfig(format="%(levelname)s: %(message)s")

    logging.getLogger("airlift").setLevel(
        logging.DEBUG if is_verbose else logging.INFO
    )

    if log_file:
        file_handler = logging.FileHandler(log_file)
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

