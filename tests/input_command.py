"""
Input command configuration for Airlift tests.
Contains the arguments dictionary loaded from environment variables.
"""

import os
from dataclasses import dataclass
from pathlib import PosixPath
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class AirliftArgs:
    """Args structure for Airlift tool."""
    payload_file: str
    token: str
    base: str
    table: str
    dropbox_token: str
    attachment_columns: Optional[List]
    workers: int
    verbose: bool
    md: bool
    disable_bypass_column_creation: bool
    fail_on_duplicate_csv_columns: bool
    rename_key_column: Optional[List]
    attachment_columns_map: Optional[List]
    columns_copy: Optional[List]
    log: Optional[str]


ARGS_DICT = {
    "payload_file": PosixPath("tests/assets/airtable-upload-test.json"),
    "token": os.getenv("CI_AIRTABLE_TOKEN"),
    "base": os.getenv("CI_AIRTABLE_BASE"),
    "table": os.getenv("CI_AIRTABLE_TABLE"),
    "dropbox_token": None,  # Will be set by fixture
    "attachment_columns": None,
    "workers": 5,
    "verbose": True,
    "md": True,
    "disable_bypass_column_creation": True,
    "fail_on_duplicate_csv_columns": False,
    "rename_key_column": None,
    "attachment_columns_map": [
        ["Image Filename", "Attachments"],
        ["Palette Filename", "Palette Attachments"]
    ],
    "columns_copy": None,
    "log": None,
}

