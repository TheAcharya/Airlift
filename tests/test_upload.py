import pytest
import warnings
from dataclasses import dataclass
import pathlib
from pathlib import Path
from airlift.version import __version__
from airlift.utils_exceptions import CriticalError,AirtableError 
from airlift.cli_args import parse_args
from airlift.csv_data import csv_read
from airlift.airtable_upload import Upload
from airlift.json_data import json_read
from airlift.airtable_client import new_client
from airlift.dropbox_client import dropbox_client,change_refresh_access_token
from icecream import ic

# Suppress all warnings from external libraries
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

# Suppress deprecation warnings from external libraries
warnings.filterwarnings("ignore", category=DeprecationWarning, module="dropbox")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pyairtable")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")
warnings.filterwarnings("ignore", message=".*PydanticDeprecatedSince211.*")
warnings.filterwarnings("ignore", message=".*model_fields.*deprecated.*")
warnings.filterwarnings("ignore", message=".*Accessing the 'model_fields' attribute.*")

@dataclass
class AirliftArgs:
    """Simple args structure for your Airlift tool."""
    csv_file: str
    token: str
    base: str
    table: str
    dropbox_token: str
    attachment_columns: list
    workers: int
    verbose: bool
    md: bool
    disable_bypass_column_creation: bool
    fail_on_duplicate_csv_columns: bool
    rename_key_column: bool
    attachment_columns_map: bool
    columns_copy: bool
    log: bool


class TestAirlift:

    @pytest.fixture(autouse=True)
    def setup_args(
        self,
        test_config, 
        dropbox_token_file, 
        test_csv_file, 
        clean_log_file
    ):

        self.args = AirliftArgs(
                csv_file="tests/assets/big_cats.csv",
                token=test_config["airtable_token"],
                base=test_config["airtable_base"],
                table=test_config["airtable_table"],
                dropbox_token=dropbox_token_file,
                disable_bypass_column_creation=True,
                attachment_columns="Image Filename",
                workers=5,
                verbose=True,
                md=True,
                fail_on_duplicate_csv_columns=False,
                rename_key_column=False,
                attachment_columns_map=False,
                columns_copy=False,
                log=False,
            )
    
    def test_setup_verification(self):
        """Verify everything is created properly."""
        # Check args exist
        assert self.args.csv_file is not None
        assert self.args.token is not None
        assert self.args.dropbox_token is not None
        
        # Check files exist
        assert Path(self.args.csv_file).exists()
        assert Path(self.args.dropbox_token).exists()
        
        print(f"CSV file: {self.args.csv_file}")
        print(f"Dropbox token file: {self.args.dropbox_token}")
        print(f"Workers: {self.args.workers}")

    def test_upload_functionality(self):
    
        args = self.args
        print(f"Airlift version {__version__}")

        workers = args.workers if args.workers else 5

        #creating drop box client
        if args.dropbox_token:
            dbx = dropbox_client(args.dropbox_token,args.md)
        else:
            dbx = None

        #creating airtable client
        airtable_client = new_client(token=args.token,base=args.base,table=args.table)

        print(f"Validating {args.csv_file} and Airtable Schema")

        suffix = pathlib.Path(args.csv_file).suffix

        #converting data into airtable supported format
        if "csv" in suffix:
            data = csv_read(args.csv_file,args.fail_on_duplicate_csv_columns)
        elif "json" in suffix:
            data = json_read(args.csv_file,args.fail_on_duplicate_csv_columns)
        else:
            raise CriticalError("File type not supported!")

        print("Validation done!")

        if not data:
            raise CriticalError("File is empty!")

        #validating data and creating an uploadable data
        data = airtable_client.create_uploadable_data(data=data,args=args)
    
        #uploading the data
        upload_instance = Upload(client=airtable_client, new_data=data,dbx=dbx,args=args)
        upload_instance.upload_data()

        assert 1 == 1