"""
Delete database entries tests for Airlift.
Tests the delete all database entries workflow for Airtable.
"""

import contextlib
import json
import os
import tempfile
import warnings
from typing import Generator, Optional, Tuple

import pytest

from airlift.airtable_client import new_client
from airlift.dropbox_client import dropbox_client
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
def load_client_and_data(dropbox_token_file) -> Generator[Tuple[AirliftArgs, new_client, Optional[dropbox_client]], None, None]:
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


def test_delete_database_entries(load_client_and_data) -> None:
    """Test deleting all entries from Airtable database."""
    args, airtable_client, dbx = load_client_and_data
    
    print(f"Airlift version {__version__}")
    print(f"Target Base: {args.base}")
    print(f"Target Table: {args.table}")
    
    print("WARNING: Deleting ALL entries from the specified Airtable table!")
    
    # Delete all records from the table
    deleted_count = airtable_client.delete_all_records()
    
    print(f"Operation complete. Deleted {deleted_count} records.")
    
    # Verify deletion was successful (count should be >= 0)
    assert deleted_count >= 0
    
    # Verify table is now empty
    remaining_records = airtable_client.table.all()
    assert len(remaining_records) == 0, f"Expected 0 records, but found {len(remaining_records)}"
    
    print("All entries successfully deleted from the database.")

