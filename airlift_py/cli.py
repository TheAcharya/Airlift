import logging
import os
import signal
import sys
from pathlib import Path
from typing import Any, Optional
import pathlib

from airlift_py.utils_exceptions import CriticalError,AirtableError 
from airlift_py.cli_args import parse_args
from airlift_py.csv_data import csv_read
from airlift_py.airtable_upload import upload_data
from airlift_py.json_data import json_read
from airlift_py.airtable_client import new_client
from airlift_py.dropbox_client import dropbox_client,change_refresh_access_token

logger = logging.getLogger(__name__)

def abort(*_: Any) -> None:  # pragma: no cover
    print("\nAbort")  # noqa: WPS421
    os._exit(1)

def cli(*argv: str) -> None:
    args = parse_args(argv)
    setup_logging(is_verbose=args.verbose,log_file=args.log)

    workers = args.workers if args.workers else 5

    if not args.dropbox_refresh_token:

        if args.dropbox_token:
            dbx = dropbox_client(args.dropbox_token,args.md)
        else:
            dbx = None

        airtable_client = new_client(token=args.token,base=args.base,table=args.table)

        logger.info(f"Validating {args.csv_file.name} and Airtable Schema")

        suffix = pathlib.Path(args.csv_file.name).suffix

        if "csv" in suffix:
            data = csv_read(args.csv_file,args.fail_on_duplicate_csv_columns)
        elif "json" in suffix:
            data = json_read(args.csv_file,args.fail_on_duplicate_csv_columns)
        else:
            raise CriticalError("File type not supported!")
        #print(data)

        logger.info("Validation done!")

        if not data:
            raise CriticalError("File is empty!")

        data = airtable_client.missing_fields_check(data,disable_bypass=args.disable_bypass_column_creation)

        dirname = os.path.dirname(args.csv_file)
        upload_data(client=airtable_client, new_data=data, workers = workers,dirname=dirname,dbx=dbx,attachment_columns=args.attachment_columns,attachment_columns_map=args.attachment_columns_map)
    else:
        change_refresh_access_token(args.dropbox_token)


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

