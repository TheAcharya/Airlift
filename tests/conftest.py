"""
Pytest configuration and fixtures for Airlift tests.
"""

import json
import os
import tempfile
import warnings
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Suppress all warnings at the earliest possible point
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
warnings.filterwarnings("ignore", message=".*PydanticDeprecatedSince211.*")
warnings.filterwarnings("ignore", message=".*model_fields.*deprecated.*")

# Load environment variables from .env file
load_dotenv()

@pytest.fixture(scope="session", autouse=True)
def suppress_warnings():
    """Suppress all warnings for the entire test session."""
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
    warnings.filterwarnings("ignore", message=".*PydanticDeprecatedSince211.*")
    warnings.filterwarnings("ignore", message=".*model_fields.*deprecated.*")
    yield

@pytest.fixture(scope="session")
def test_config():
    """
    Test configuration loaded from environment variables.
    """
    config = {
        "airtable_token": os.getenv("AIRTABLE_TOKEN"),
        "airtable_base": os.getenv("AIRTABLE_BASE"),
        "airtable_table": os.getenv("AIRTABLE_TABLE"),
        "dropbox_app_key": os.getenv("DROPBOX_APP_KEY"),
        "dropbox_refresh_token": os.getenv("DROPBOX_REFRESH_TOKEN"),
    }
    
    # Validate required environment variables
    required_vars = ["airtable_token", "airtable_base", "airtable_table", "dropbox_app_key", "dropbox_refresh_token"]
    missing_vars = [var for var in required_vars if not config[var]]
    
    if missing_vars:
        pytest.skip(f"Missing required environment variables: {', '.join(missing_vars.upper())}")
    
    return config

@pytest.fixture(scope="function")
def dropbox_token_file(test_config):
    """
    Create a temporary dropbox token JSON file from environment variables.
    """
    dropbox_data = {
        "app_key": test_config["dropbox_app_key"],
        "refresh_token": test_config["dropbox_refresh_token"]
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

@pytest.fixture(scope="session")
def assets_dir():
    """
    Path to test assets directory.
    """
    return Path(__file__).parent / "assets"

@pytest.fixture(scope="session")
def test_csv_file(assets_dir):
    """
    Path to test CSV file.
    """
    csv_path = assets_dir / "big_cats.csv"
    if not csv_path.exists():
        pytest.skip(f"Test CSV file not found: {csv_path}")
    return str(csv_path)

@pytest.fixture(scope="session")
def test_image_files(assets_dir):
    """
    List of test image files.
    """
    image_extensions = [".jpg", ".jpeg", ".png", ".gif"]
    image_files = []
    
    for file_path in assets_dir.iterdir():
        if file_path.suffix.lower() in image_extensions:
            image_files.append(str(file_path))
    
    if not image_files:
        pytest.skip("No test image files found in assets directory")
    
    return image_files

@pytest.fixture(scope="function")
def clean_log_file():
    """
    Ensure test log file is cleaned up after each test.
    """
    log_file = "test_log.txt"
    yield log_file
    
    # Cleanup
    if os.path.exists(log_file):
        os.remove(log_file)