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
from airlift.dropbox_client import dropbox_client, change_refresh_access_token, empty_dropbox_folder
from icecream import ic

logger = logging.getLogger(__name__)

def abort(*_: Any) -> None:  # pragma: no cover
    print("\nAbort")  # noqa: WPS421
    os._exit(1)

def _validate_required_args(args) -> None:
    """Validate required arguments based on the operation mode."""
    missing_args = []
    
    # Dropbox refresh token mode only needs dropbox-token
    if args.dropbox_refresh_token:
        if not args.dropbox_token:
            missing_args.append("--dropbox-token")
        if missing_args:
            _print_missing_args_error(missing_args)
        return
    
    # Empty Dropbox folder mode only needs dropbox-token
    if args.empty_dropbox_folder:
        if not args.dropbox_token:
            missing_args.append("--dropbox-token")
        if missing_args:
            _print_missing_args_error(missing_args)
        return
    
    # All other modes require token, base, and table
    if not args.token:
        missing_args.append("--token")
    if not args.base:
        missing_args.append("--base")
    if not args.table:
        missing_args.append("--table")
    
    # Delete all database entries mode doesn't need a file
    if args.delete_all_database_entries:
        if missing_args:
            _print_missing_args_error(missing_args)
        return
    
    # Normal upload mode requires a file
    if not args.csv_file:
        missing_args.append("FILE")
    
    if missing_args:
        _print_missing_args_error(missing_args)


def _print_missing_args_error(missing_args: list) -> None:
    """Print error message for missing arguments and exit."""
    import sys
    print("usage: airlift [-h] --token TOKEN --base BASE --table TABLE [OPTION]... FILE")
    print()
    print(f"airlift: error: the following arguments are required: {', '.join(missing_args)}")
    sys.exit(2)


def cli(*argv: str) -> None:
    args = None
    try:
        ic.disable()
        args = parse_args(argv)
        
        # Validate required arguments before proceeding
        _validate_required_args(args)
        
        setup_logging(is_verbose=args.verbose,log_file=args.log)
        logger.info(f"Airlift version {__version__}")

        workers = args.workers if args.workers else 5

        # Handle delete all database entries operation
        if args.delete_all_database_entries:
            logger.warning("WARNING: This will delete ALL entries from the specified Airtable table!")
            logger.info(f"Target: Base={args.base}, Table={args.table}")
            
            # Create Airtable client and delete all records
            airtable_client = new_client(token=args.token, base=args.base, table=args.table)
            deleted_count = airtable_client.delete_all_records()
            logger.info(f"Operation complete. Deleted {deleted_count} records.")

        # Handle empty Dropbox folder operation
        elif args.empty_dropbox_folder:
            folder_name = "Marker Data" if args.md else "Airlift"
            logger.warning(f"WARNING: This will delete ALL contents from the Dropbox folder '/{folder_name}'!")
            logger.info(f"The folder itself will NOT be deleted.")
            
            # Empty the Dropbox folder contents
            deleted_count = empty_dropbox_folder(args.dropbox_token, args.md)
            logger.info(f"Operation complete. Deleted {deleted_count} items from '/{folder_name}'.")

        elif not args.dropbox_refresh_token: #if dropbox-refresh-token flag is not present, continue normal procedure

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

            #validating data and creating an uploadable data
            data = airtable_client.create_uploadable_data(data=data,args=args)
        
            #uploading the data
            upload_instance = Upload(client=airtable_client, new_data=data,dbx=dbx,args=args)
            upload_instance.upload_data()
        else:
            get_token = True
            while get_token:
                os.system('cls' if os.name=='nt' else 'clear')
                try:
                    change_refresh_access_token(args.dropbox_token)
                    get_token = False
                except:
                    print("Error during retreival of token! Do you want to try again? (y/n)")
                    user_choice = input("(y/n)->")

                    if user_choice.lower() == 'y':
                        get_token = True
                    elif user_choice.lower() == 'n':
                        get_token = False
                    else:
                        print(f"{user_choice} is an invalid choice please choose y or n.")
                        get_token = False

        logger.info("Done!")

    except Exception as e:
        if getattr(args, "verbose", False):
            logger.error("Error", exc_info=e)
        else:
            logger.error(e)

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

