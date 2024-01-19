import logging
import os
import signal
import sys
import pathlib
from pathlib import Path
from typing import Any, Optional

from airlift.version import __version__
from airlift.utils_exceptions import CriticalError,AirtableError 
from airlift.cli_args import parse_args
from airlift.csv_data import csv_read
from airlift.airtable_upload import Upload
from airlift.json_data import json_read
from airlift.airtable_client import new_client
from airlift.dropbox_client import dropbox_client,change_refresh_access_token
from icecream import ic

logger = logging.getLogger(__name__)

def abort(*_: Any) -> None:  # pragma: no cover
    print("\nAbort")  # noqa: WPS421
    os._exit(1)

def cli(*argv: str) -> None:
    ic.disable()
    args = parse_args(argv)
    setup_logging(is_verbose=args.verbose,log_file=args.log)
    logger.info(f"Airlift version {__version__}")

    workers = args.workers if args.workers else 5

    if not args.dropbox_refresh_token: #if dropbox-refresh-token flag is not present, continue normal procedure

        #creating drop box client
        if args.dropbox_token:
            dbx = dropbox_client(args.dropbox_token,args.md)
        else:
            dbx = None

        #creating airtable client
        airtable_client = new_client(token=args.token,base=args.base,table=args.table)

        logger.info(f"Validating {args.csv_file.name} and Airtable Schema")

        suffix = pathlib.Path(args.csv_file.name).suffix

        #converting data into airtable supported format
        if "csv" in suffix:
            data = csv_read(args.csv_file,args.fail_on_duplicate_csv_columns)
        elif "json" in suffix:
            data = json_read(args.csv_file,args.fail_on_duplicate_csv_columns)
        else:
            raise CriticalError("File type not supported!")

        logger.info("Validation done!")

        if not data:
            raise CriticalError("File is empty!")

        #checking for missing columns
        if args.rename_key_column:
            ignore_column_check = [args.rename_key_column[0]]
        else:
            ignore_column_check = None

        data = airtable_client.missing_fields_check(data,disable_bypass=args.disable_bypass_column_creation,ignore_columns=ignore_column_check)
        
        #uploading the data
        upload_instance = Upload(client=airtable_client, new_data=data,dbx=dbx,args=args)
        upload_instance.upload_data()
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
    except (AirtableError,CriticalError) as e:
        logger.critical(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)

