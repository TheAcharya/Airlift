"""
Integration tests for the Airlift upload workflow (Airtable + Dropbox).

These tests intentionally call live Airtable and Dropbox APIs:

- CI runs them via airtable_image_upload_test.yml with GitHub Secrets
  (CI_AIRTABLE_*, CI_DROPBOX_*). Use a dedicated sandbox base/table and folders.
- Locally, tests skip when required CI_* variables are unset.
- CLI argument and parsing behavior without APIs is in test_comprehensive.py.

See tests/README.md for setup and safety notes.
"""

import contextlib
import json
import os
import pathlib
import tempfile
import time
import warnings
from typing import Generator, Optional, Tuple

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
    
    # Cleanup (ignore OSError if file already removed)
    with contextlib.suppress(OSError):
        os.unlink(temp_path)


@pytest.fixture(scope="function")
def load_clients(dropbox_token_file) -> Generator[Tuple[AirliftArgs, new_client, Optional[dropbox_client]], None, None]:
    """
    Load Airlift clients.
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


def test_upload_rows(load_clients) -> None:
    """
    End-to-end test: upload fixture data and verify record count on live Airtable.

    Uses real API clients; table.all() reads confirm rows were created (sandbox only).
    """
    args, airtable_client, dbx = load_clients
    
    print(f"Airlift version {__version__}")
    print(f"Payload file: {args.csv_file}")
    print(f"Attachment columns map: {args.attachment_columns_map}")
    
    suffix = pathlib.Path(args.csv_file).suffix
    
    # Converting data into airtable supported format
    if "csv" in suffix:
        data = csv_read(args.csv_file, args.fail_on_duplicate_csv_columns)
    elif "json" in suffix:
        data = json_read(args.csv_file, args.fail_on_duplicate_csv_columns)
    else:
        raise CriticalError("File type not supported!")
    
    print("Validation done!")
    
    if not data:
        raise CriticalError("File is empty!")
    
    # Validating data and creating an uploadable data
    data = airtable_client.create_uploadable_data(data=data, args=args)
    
    # Live API: record count before upload (CI sandbox table only).
    before_records = airtable_client.table.all()
    before_count = len(before_records)

    # Uploading the data
    upload_instance = Upload(client=airtable_client, new_data=data, dbx=dbx, args=args)
    upload_instance.upload_data()

    # Verify records were uploaded by checking table count increase.
    # Airtable can be briefly eventually consistent; retry a few times.
    expected_min_after = before_count + len(data)
    after_count = before_count
    for _ in range(5):
        after_count = len(airtable_client.table.all())
        if after_count >= expected_min_after:
            break
        time.sleep(1)
    assert after_count >= expected_min_after, (
        f"Expected at least {expected_min_after} records after upload, "
        f"found {after_count}."
    )

    # Verify upload instance was initialized with expected data and upload completed
    assert hasattr(upload_instance, "new_data")
    assert len(upload_instance.new_data) == len(data)
