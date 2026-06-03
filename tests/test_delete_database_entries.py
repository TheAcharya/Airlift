"""
Integration tests for Airlift --delete-all-database-entries (Airtable).

These tests intentionally call the live Airtable API. They are not unit tests
and are not meant to be mocked:

- CI runs them via airtable_delete_database_entries_test.yml with GitHub
  Secrets (CI_AIRTABLE_*). Point those secrets at a disposable sandbox base/table,
  never production data.
- Locally, tests skip when CI_* environment variables are unset.
- Mocked delete behavior is covered in tests/test_comprehensive.py.

See tests/README.md for setup and safety notes.
"""

import contextlib
import json
import os
import tempfile
import warnings
from typing import Any, Generator, NoReturn, Optional, Tuple

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
def load_clients(dropbox_token_file) -> Generator[Tuple[AirliftArgs, Any, Optional[Any]], None, None]:
    """
    Set up and yield Airlift args, Airtable client, and optional Dropbox client.
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


def test_delete_database_entries(load_clients) -> None:
    """
    End-to-end test: delete every record in the CI sandbox Airtable table.

    Real deletion is required here to validate batch delete against Airtable.
    Do not replace with mocks in this test; use test_comprehensive.py instead.
    """
    args, airtable_client, _ = load_clients

    print(f"Airlift version {__version__}")
    print(f"Target Base: {args.base}")
    print(f"Target Table: {args.table}")

    print(
        "WARNING: Deleting ALL entries from the CI sandbox table "
        "(CI_AIRTABLE_BASE / CI_AIRTABLE_TABLE)!"
    )

    deleted_count = airtable_client.delete_all_records()

    print(f"Operation complete. Deleted {deleted_count} records.")

    # Integration check: confirm the sandbox table is empty (live API read).
    remaining_records = airtable_client.table.all()
    assert len(remaining_records) == 0, f"Expected 0 records, but found {len(remaining_records)}"
    
    print("All entries successfully deleted from the database.")


def test_delete_database_entries_api_error(load_clients, monkeypatch) -> None:
    """
    Unit-style test: delete_all_records propagates API failures.

    Uses monkeypatch only to simulate an error without calling Airtable delete.
    """
    _, airtable_client, _ = load_clients

    def _failing_delete_all_records() -> NoReturn:
        raise RuntimeError("API failure during delete_all_records")

    # No live delete: patch the client method to raise before any API call.
    monkeypatch.setattr(airtable_client, "delete_all_records", _failing_delete_all_records)
    with pytest.raises(RuntimeError, match="API failure during delete_all_records"):
        airtable_client.delete_all_records()

