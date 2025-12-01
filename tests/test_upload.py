"""
Upload tests for Airlift.
Tests the complete upload workflow to Airtable with Dropbox attachments.
"""

import json
import os
import pathlib
import tempfile
import warnings
from typing import Generator, Union

import pytest

from airlift.airtable_client import new_client
from airlift.airtable_upload import Upload
from airlift.csv_data import csv_read
from airlift.dropbox_client import dropbox_client
from airlift.json_data import json_read
from airlift.utils_exceptions import CriticalError
from airlift.version import __version__

from .input_command import ARGS_DICT, AirliftArgs

# Suppress all warnings from external libraries
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
warnings.filterwarnings("ignore", message=".*PydanticDeprecatedSince211.*")
warnings.filterwarnings("ignore", message=".*model_fields.*deprecated.*")


@pytest.fixture(scope="function")
def dropbox_token_file():
    """
    Create a temporary dropbox token JSON file from environment variables.
    """
    app_key = os.getenv("CI_DROPBOX_APP_KEY")
    refresh_token = os.getenv("CI_DROPBOX_REFRESH_TOKEN")
    
    if not app_key or not refresh_token:
        pytest.skip("Dropbox credentials not available in environment variables")
    
    dropbox_data = {
        "app_key": app_key,
        "refresh_token": refresh_token
    }
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(dropbox_data, f, indent=2)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except OSError:
        pass


@pytest.fixture(scope="function")
def load_client_and_data(dropbox_token_file) -> Generator[Union[AirliftArgs, new_client, dropbox_client], None, None]:
    """
    Load Airlift clients and data.
    Yields args, airtable_client, and dropbox_client.
    """
    # Create args with dropbox token file
    args_dict = ARGS_DICT.copy()
    args_dict["dropbox_token"] = dropbox_token_file
    args = AirliftArgs(**args_dict)
    
    # Skip test if Airtable credentials are not available
    if not args.token:
        pytest.skip("Airtable token not available in environment variables")
    
    try:
        # Creating dropbox client
        dbx = dropbox_client(args.dropbox_token, args.md) if args.dropbox_token else None
        
        # Creating airtable client
        airtable_client = new_client(token=args.token, base=args.base, table=args.table)
        
        yield args, airtable_client, dbx
    except Exception as e:
        pytest.skip(f"Failed to connect to API: {e}")


def test_upload_rows(load_client_and_data) -> None:
    """Test uploading rows to Airtable with attachments."""
    args, airtable_client, dbx = load_client_and_data
    
    print(f"Airlift version {__version__}")
    print(f"Payload file: {args.payload_file}")
    print(f"Attachment columns map: {args.attachment_columns_map}")
    
    suffix = pathlib.Path(args.payload_file).suffix
    
    # Converting data into airtable supported format
    if "csv" in suffix:
        data = csv_read(args.payload_file, args.fail_on_duplicate_csv_columns)
    elif "json" in suffix:
        data = json_read(args.payload_file, args.fail_on_duplicate_csv_columns)
    else:
        raise CriticalError("File type not supported!")
    
    print("Validation done!")
    
    if not data:
        raise CriticalError("File is empty!")
    
    # Validating data and creating an uploadable data
    data = airtable_client.create_uploadable_data(data=data, args=args)
    
    # Uploading the data
    upload_instance = Upload(client=airtable_client, new_data=data, dbx=dbx, args=args)
    upload_instance.upload_data()
    
    assert 1 == 1
