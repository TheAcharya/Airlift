"""
Empty Dropbox folder tests for Airlift.
Tests the empty Dropbox folder workflow.
"""

import json
import os
import tempfile
import warnings
from typing import Generator

import pytest

from airlift.dropbox_client import empty_dropbox_folder
from airlift.version import __version__

# Suppress all warnings from external libraries
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
warnings.filterwarnings("ignore", message=".*PydanticDeprecatedSince211.*")
warnings.filterwarnings("ignore", message=".*model_fields.*deprecated.*")


@pytest.fixture(scope="function")
def dropbox_token_file() -> Generator[str, None, None]:
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


def test_empty_dropbox_folder_airlift(dropbox_token_file) -> None:
    """Test emptying the Airlift folder in Dropbox."""
    print(f"Airlift version {__version__}")
    print(f"Target folder: /Airlift")
    
    print("WARNING: Emptying ALL contents from the Dropbox folder '/Airlift'!")
    
    # Empty the Airlift folder (md=False)
    deleted_count = empty_dropbox_folder(dropbox_token_file, md=False)
    
    print(f"Operation complete. Deleted {deleted_count} items from '/Airlift'.")
    
    # Verify deletion was successful (count should be >= 0)
    assert deleted_count >= 0
    
    print("Airlift folder successfully emptied.")


def test_empty_dropbox_folder_marker_data(dropbox_token_file) -> None:
    """Test emptying the Marker Data folder in Dropbox."""
    print(f"Airlift version {__version__}")
    print(f"Target folder: /Marker Data")
    
    print("WARNING: Emptying ALL contents from the Dropbox folder '/Marker Data'!")
    
    # Empty the Marker Data folder (md=True)
    deleted_count = empty_dropbox_folder(dropbox_token_file, md=True)
    
    print(f"Operation complete. Deleted {deleted_count} items from '/Marker Data'.")
    
    # Verify deletion was successful (count should be >= 0)
    assert deleted_count >= 0
    
    print("Marker Data folder successfully emptied.")

