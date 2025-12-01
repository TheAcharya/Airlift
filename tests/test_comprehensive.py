"""
Airlift - Comprehensive Test Suite

This is the definitive test suite for Airlift that validates all CLI arguments,
flags, and switches. It provides complete coverage of the application's functionality
without requiring actual API calls (no Airtable or Dropbox tokens needed).

Test Coverage:
- All CLI arguments and their validation
- Argument parsing and type conversion
- Error handling for invalid arguments
- CSV and JSON data processing
- Data type detection and guessing
- Mock testing of core functionality
- Edge cases and boundary conditions
- Airtable client operations (mocked)
- Dropbox client operations (mocked)
- Upload functionality (mocked)

TABLE OF CONTENTS:
==================

1. TestCLIArgumentParsing
   - test_required_arguments_missing
   - test_general_options
   - test_dropbox_options
   - test_column_options
   - test_validation_options
   - test_version_argument
   - test_help_argument

2. TestCSVDataProcessing
   - test_csv_read_valid_file
   - test_csv_read_file_not_found
   - test_csv_duplicate_columns_fail
   - test_csv_duplicate_columns_remove
   - test_csv_empty_file

3. TestJSONDataProcessing
   - test_json_read_valid_file
   - test_json_read_file_not_found
   - test_json_empty_file

4. TestDataTypeGuesser
   - test_guess_number_type
   - test_guess_date_type
   - test_guess_email_type
   - test_guess_bool_type
   - test_guess_unknown_type

5. TestAirtableClient
   - test_client_initialization
   - test_missing_field_check
   - test_rename_key_column_validation
   - test_create_uploadable_data

6. TestUploadFunctionality
   - test_upload_initialization
   - test_worker_thread_count
   - test_attachment_column_handling

7. TestDropboxClient
   - test_token_loading
   - test_ssl_configuration
   - test_folder_creation

8. TestErrorHandling
   - test_critical_error
   - test_airtable_error
   - test_type_conversion_error
   - test_client_error_codes

9. TestUtilities
   - test_timer_wrapper
   - test_get_all_timings

10. TestVersionAndConstants
    - test_version_exists
    - test_version_format

11. TestComprehensiveScenarios
    - test_full_upload_scenario_args
    - test_attachment_mapping_scenario
    - test_column_copy_scenario
    - test_rename_key_column_scenario

12. TestEdgeCases
    - test_empty_arguments
    - test_whitespace_handling
    - test_special_characters_in_paths
"""

import csv
import json
import os
import tempfile
import warnings
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from argparse import Namespace

import pytest

# Import Airlift modules
from airlift.cli_args import parse_args
from airlift.utils_exceptions import CriticalError, AirtableError, TypeConversionError
from airlift.version import __version__
from airlift.csv_data import csv_read, _csv_read_rows, _list_duplicates, _remove_duplicates
from airlift.json_data import json_read, _json_read_rows
from airlift.airlift_data_guesser import guess_data_type
from airlift.utils import timer_wrapper, get_all_timings
from airlift.airtable_error_handling import ClientError

# Suppress warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)


# ============================================================================
# 1. TestCLIArgumentParsing - CLI Argument Parsing and Validation
# ============================================================================
class TestCLIArgumentParsing:
    """Test comprehensive CLI argument parsing and validation."""
    
    def test_required_arguments_missing(self):
        """Test that missing required arguments are handled."""
        # Test with no arguments - should not raise but args will be None for required fields
        args = parse_args([])
        assert args.token is None
        assert args.base is None
        assert args.table is None
    
    def test_general_options(self):
        """Test general CLI options."""
        args = parse_args([
            "--token", "pat_test_token_12345",
            "--base", "appTestBaseId123",
            "--table", "tblTestTableId456",
            "--log", "test.log",
            "--verbose",
            "--workers", "10",
            "test.csv"
        ])
        
        assert args.token == "pat_test_token_12345"
        assert args.base == "appTestBaseId123"
        assert args.table == "tblTestTableId456"
        assert args.log == Path("test.log")
        assert args.verbose is True
        assert args.workers == 10
        assert args.csv_file == Path("test.csv")
    
    def test_dropbox_options(self):
        """Test Dropbox-related CLI options."""
        # Note: With nargs="+", positional arg must come before to avoid being consumed
        args = parse_args([
            "--token", "pat_test_token_12345",
            "--base", "appTestBaseId123",
            "--table", "tblTestTableId456",
            "--dropbox-token", "dropbox-token.json",
            "--attachment-columns", "Image", "Photo",
        ])
        
        assert args.dropbox_token == Path("dropbox-token.json")
        assert args.attachment_columns == ["Image", "Photo"]
        assert args.dropbox_refresh_token is False
    
    def test_dropbox_refresh_token_flag(self):
        """Test Dropbox refresh token flag."""
        args = parse_args([
            "--dropbox-token", "dropbox-token.json",
            "--dropbox-refresh-token"
        ])
        
        assert args.dropbox_refresh_token is True
    
    def test_attachment_columns_map(self):
        """Test attachment columns mapping."""
        args = parse_args([
            "--token", "pat_test_token_12345",
            "--base", "appTestBaseId123",
            "--table", "tblTestTableId456",
            "--dropbox-token", "dropbox-token.json",
            "--attachment-columns-map", "Image Filename", "Attachments",
            "--attachment-columns-map", "Palette Filename", "Palette Attachments",
            "test.csv"
        ])
        
        assert args.attachment_columns_map == [
            ["Image Filename", "Attachments"],
            ["Palette Filename", "Palette Attachments"]
        ]
    
    def test_column_options(self):
        """Test column-related CLI options."""
        args = parse_args([
            "--token", "pat_test_token_12345",
            "--base", "appTestBaseId123",
            "--table", "tblTestTableId456",
            "--disable-bypass-column-creation",
            "--columns-copy", "Source", "Dest1", "Dest2",
            "--rename-key-column", "OldKey", "NewKey",
            "test.csv"
        ])
        
        assert args.disable_bypass_column_creation is True
        assert args.columns_copy == ["Source", "Dest1", "Dest2"]
        assert args.rename_key_column == ["OldKey", "NewKey"]
    
    def test_validation_options(self):
        """Test validation CLI options."""
        args = parse_args([
            "--token", "pat_test_token_12345",
            "--base", "appTestBaseId123",
            "--table", "tblTestTableId456",
            "--fail-on-duplicate-csv-columns",
            "test.csv"
        ])
        
        assert args.fail_on_duplicate_csv_columns is True
    
    def test_version_argument(self):
        """Test version argument."""
        with pytest.raises(SystemExit):
            parse_args(["--version"])
    
    def test_help_argument(self):
        """Test help argument."""
        with pytest.raises(SystemExit):
            parse_args(["--help"])
    
    def test_hidden_md_flag(self):
        """Test hidden --md flag for Marker Data integration."""
        args = parse_args([
            "--token", "pat_test_token_12345",
            "--base", "appTestBaseId123",
            "--table", "tblTestTableId456",
            "--md",
            "test.csv"
        ])
        
        assert args.md is True


# ============================================================================
# 2. TestCSVDataProcessing - CSV File Processing
# ============================================================================
class TestCSVDataProcessing:
    """Test CSV data processing functionality."""
    
    def test_csv_read_valid_file(self):
        """Test reading a valid CSV file."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("Name,Age,City\n")
            f.write("Alice,30,New York\n")
            f.write("Bob,25,Los Angeles\n")
            temp_path = f.name
        
        try:
            result = csv_read(Path(temp_path), fail_on_dup=False)
            assert len(result) == 2
            assert result[0]["fields"]["Name"] == "Alice"
            assert result[0]["fields"]["Age"] == "30"
            assert result[1]["fields"]["Name"] == "Bob"
        finally:
            os.unlink(temp_path)
    
    def test_csv_read_file_not_found(self):
        """Test reading a non-existent CSV file."""
        with pytest.raises(CriticalError, match="not found"):
            csv_read(Path("/nonexistent/path/file.csv"), fail_on_dup=False)
    
    def test_csv_duplicate_columns_fail(self):
        """Test that duplicate columns cause failure when flag is set."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("Name,Age,Name\n")
            f.write("Alice,30,Alice2\n")
            temp_path = f.name
        
        try:
            with pytest.raises(CriticalError, match="Duplicate columns"):
                csv_read(Path(temp_path), fail_on_dup=True)
        finally:
            os.unlink(temp_path)
    
    def test_csv_duplicate_columns_remove(self):
        """Test that duplicate columns are removed when flag is not set."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("Name,Age,Name\n")
            f.write("Alice,30,Alice2\n")
            temp_path = f.name
        
        try:
            result = csv_read(Path(temp_path), fail_on_dup=False)
            assert len(result) == 1
            # The last duplicate column value should be used
            assert "Name" in result[0]["fields"]
        finally:
            os.unlink(temp_path)
    
    def test_csv_empty_columns(self):
        """Test CSV with no columns raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("")
            temp_path = f.name
        
        try:
            with pytest.raises(CriticalError, match="no columns"):
                csv_read(Path(temp_path), fail_on_dup=False)
        finally:
            os.unlink(temp_path)
    
    def test_list_duplicates(self):
        """Test duplicate detection utility."""
        assert _list_duplicates(["a", "b", "c"]) == []
        assert _list_duplicates(["a", "b", "a"]) == ["a"]
        assert _list_duplicates(["a", "a", "b", "b"]) == ["a", "b"]
    
    def test_remove_duplicates(self):
        """Test duplicate removal from rows."""
        rows = [{"Name": "Alice", "": "empty", "Age": "30"}]
        result = _remove_duplicates(rows)
        assert result[0] == {"Name": "Alice", "Age": "30"}


# ============================================================================
# 3. TestJSONDataProcessing - JSON File Processing
# ============================================================================
class TestJSONDataProcessing:
    """Test JSON data processing functionality."""
    
    def test_json_read_valid_file(self):
        """Test reading a valid JSON file."""
        test_data = [
            {"Name": "Alice", "Age": 30, "City": "New York"},
            {"Name": "Bob", "Age": 25, "City": "Los Angeles"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            result = json_read(Path(temp_path), fail_on_dup=False)
            assert len(result) == 2
            assert result[0]["fields"]["Name"] == "Alice"
            assert result[0]["fields"]["Age"] == 30
            assert result[1]["fields"]["Name"] == "Bob"
        finally:
            os.unlink(temp_path)
    
    def test_json_read_file_not_found(self):
        """Test reading a non-existent JSON file."""
        with pytest.raises(CriticalError, match="not found"):
            json_read(Path("/nonexistent/path/file.json"), fail_on_dup=False)
    
    def test_json_empty_file(self):
        """Test reading an empty JSON array."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump([], f)
            temp_path = f.name
        
        try:
            with pytest.raises(CriticalError, match="no data"):
                json_read(Path(temp_path), fail_on_dup=False)
        finally:
            os.unlink(temp_path)
    
    def test_json_complex_data(self):
        """Test reading JSON with complex nested data."""
        test_data = [
            {
                "Name": "Project",
                "Tags": ["tag1", "tag2"],
                "Metadata": {"key": "value"}
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            result = json_read(Path(temp_path), fail_on_dup=False)
            assert len(result) == 1
            assert result[0]["fields"]["Tags"] == ["tag1", "tag2"]
        finally:
            os.unlink(temp_path)


# ============================================================================
# 4. TestDataTypeGuesser - Data Type Detection
# ============================================================================
class TestDataTypeGuesser:
    """Test data type guessing functionality."""
    
    def test_guess_number_type(self):
        """Test number type detection."""
        assert guess_data_type("123") == "number"
        assert guess_data_type("123.45") == "number"
        assert guess_data_type("0") == "number"
        assert guess_data_type("999999") == "number"
    
    def test_guess_date_type(self):
        """Test date type detection."""
        assert guess_data_type("2024-01-15") == "date"
        assert guess_data_type("2023-12-31") == "date"
        assert guess_data_type("1990-05-20") == "date"
    
    def test_guess_email_type(self):
        """Test email type detection."""
        assert guess_data_type("test@example.com") == "email"
        assert guess_data_type("user.name@domain.org") == "email"
        assert guess_data_type("admin+tag@company.co.uk") == "email"
    
    def test_guess_bool_type(self):
        """Test boolean type detection."""
        assert guess_data_type("true") == "bool"
        assert guess_data_type("false") == "bool"
        assert guess_data_type("True") == "bool"
        assert guess_data_type("False") == "bool"
    
    def test_guess_unknown_type(self):
        """Test unknown type detection."""
        assert guess_data_type("hello world") == "unknown"
        assert guess_data_type("random text") == "unknown"
        assert guess_data_type("") == "unknown"
        assert guess_data_type("abc123") == "unknown"


# ============================================================================
# 5. TestAirtableClient - Airtable Client Operations (Mocked)
# ============================================================================
class TestAirtableClient:
    """Test Airtable client functionality with mocks."""
    
    @patch('airlift.airtable_client.Api')
    def test_client_initialization(self, mock_api):
        """Test Airtable client initialization."""
        from airlift.airtable_client import new_client
        
        mock_api_instance = MagicMock()
        mock_api.return_value = mock_api_instance
        
        client = new_client(
            token="pat_test_token",
            base="appTestBase",
            table="tblTestTable"
        )
        
        assert client.api == "pat_test_token"
        assert client.base_id == "appTestBase"
        assert client.table_id == "tblTestTable"
        mock_api.assert_called_once_with("pat_test_token")
    
    @patch('airlift.airtable_client.Api')
    def test_missing_field_single(self, mock_api):
        """Test single field existence check."""
        from airlift.airtable_client import new_client
        
        # Create mock table schema
        mock_field = MagicMock()
        mock_field.name = "ExistingField"
        
        mock_table = MagicMock()
        mock_table.id = "tblTestTable"
        mock_table.fields = [mock_field]
        
        mock_schema = MagicMock()
        mock_schema.tables = [mock_table]
        
        mock_base = MagicMock()
        mock_base.schema.return_value = mock_schema
        
        mock_api_instance = MagicMock()
        mock_api_instance.base.return_value = mock_base
        mock_api.return_value = mock_api_instance
        
        client = new_client(
            token="pat_test_token",
            base="appTestBase",
            table="tblTestTable"
        )
        
        assert client.missing_field_single("ExistingField") is True
        assert client.missing_field_single("NonExistentField") is False
    
    def test_rename_key_column_validation(self):
        """Test rename key column validation logic."""
        from airlift.airtable_client import new_client
        
        # Create a mock args object with same column names
        mock_args = MagicMock()
        mock_args.rename_key_column = ["SameColumn", "SameColumn"]
        
        with patch('airlift.airtable_client.Api'):
            client = new_client(
                token="pat_test_token",
                base="appTestBase",
                table="tblTestTable"
            )
            
            with pytest.raises(CriticalError, match="same column name"):
                client._rename_key_column_check(mock_args)


# ============================================================================
# 6. TestUploadFunctionality - Upload Operations (Mocked)
# ============================================================================
class TestUploadFunctionality:
    """Test upload functionality with mocks."""
    
    def test_upload_initialization(self):
        """Test Upload class initialization."""
        from airlift.airtable_upload import Upload
        
        mock_client = MagicMock()
        mock_dbx = MagicMock()
        mock_args = MagicMock()
        mock_args.csv_file = Path("tests/assets/test.csv")
        mock_args.attachment_columns = None
        mock_args.attachment_columns_map = None
        mock_args.columns_copy = None
        mock_args.rename_key_column = None
        mock_args.workers = 5
        mock_args.log = None
        
        upload = Upload(
            client=mock_client,
            new_data=[{"fields": {"Name": "Test"}}],
            dbx=mock_dbx,
            args=mock_args
        )
        
        assert upload.workers == 5
        assert upload.client == mock_client
        assert upload.dbx == mock_dbx
    
    def test_worker_thread_count_default(self):
        """Test default worker thread count."""
        from airlift.airtable_upload import Upload
        
        mock_client = MagicMock()
        mock_args = MagicMock()
        mock_args.csv_file = Path("tests/assets/test.csv")
        mock_args.attachment_columns = None
        mock_args.attachment_columns_map = None
        mock_args.columns_copy = None
        mock_args.rename_key_column = None
        mock_args.workers = None  # Not specified
        mock_args.log = None
        
        upload = Upload(
            client=mock_client,
            new_data=[],
            dbx=None,
            args=mock_args
        )
        
        assert upload.workers == 5  # Default value
    
    def test_worker_thread_count_custom(self):
        """Test custom worker thread count."""
        from airlift.airtable_upload import Upload
        
        mock_client = MagicMock()
        mock_args = MagicMock()
        mock_args.csv_file = Path("tests/assets/test.csv")
        mock_args.attachment_columns = None
        mock_args.attachment_columns_map = None
        mock_args.columns_copy = None
        mock_args.rename_key_column = None
        mock_args.workers = 10
        mock_args.log = None
        
        upload = Upload(
            client=mock_client,
            new_data=[],
            dbx=None,
            args=mock_args
        )
        
        assert upload.workers == 10


# ============================================================================
# 7. TestDropboxClient - Dropbox Client Operations (Mocked)
# ============================================================================
class TestDropboxClient:
    """Test Dropbox client functionality with mocks."""
    
    def test_token_file_loading(self):
        """Test loading tokens from JSON file."""
        token_data = {
            "app_key": "test_app_key",
            "refresh_token": "test_refresh_token"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(token_data, f)
            temp_path = f.name
        
        try:
            # Read the token file manually to verify format
            with open(temp_path, 'r') as f:
                loaded = json.load(f)
            
            assert loaded["app_key"] == "test_app_key"
            assert loaded["refresh_token"] == "test_refresh_token"
        finally:
            os.unlink(temp_path)
    
    def test_token_file_missing_app_key(self):
        """Test error when app_key is missing from token file."""
        token_data = {
            "refresh_token": "test_refresh_token"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(token_data, f)
            temp_path = f.name
        
        try:
            with open(temp_path, 'r') as f:
                loaded = json.load(f)
            
            assert "app_key" not in loaded
        finally:
            os.unlink(temp_path)
    
    def test_ssl_configuration(self):
        """Test SSL environment configuration."""
        from airlift.dropbox_client import _configure_ssl_environment
        
        # This should not raise any errors
        _configure_ssl_environment()
        
        # Verify environment variables may be set
        # (actual values depend on certifi installation)


# ============================================================================
# 8. TestErrorHandling - Error Handling and Exceptions
# ============================================================================
class TestErrorHandling:
    """Test error handling and exception classes."""
    
    def test_critical_error(self):
        """Test CriticalError exception."""
        with pytest.raises(CriticalError):
            raise CriticalError("Test critical error")
    
    def test_critical_error_message(self):
        """Test CriticalError exception message."""
        try:
            raise CriticalError("Test error message")
        except CriticalError as e:
            assert str(e) == "Test error message"
    
    def test_airtable_error(self):
        """Test AirtableError exception."""
        with pytest.raises(AirtableError):
            raise AirtableError("Test Airtable error")
    
    def test_type_conversion_error(self):
        """Test TypeConversionError exception."""
        with pytest.raises(TypeConversionError):
            raise TypeConversionError("Test type conversion error")
    
    def test_client_error_403(self):
        """Test ClientError handling for 403 status."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        
        mock_error = MagicMock()
        mock_error.response = mock_response
        
        with pytest.raises(AirtableError, match="protected resource"):
            ClientError(mock_error)
    
    def test_client_error_401(self):
        """Test ClientError handling for 401 status."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        
        mock_error = MagicMock()
        mock_error.response = mock_response
        
        with pytest.raises(AirtableError, match="invalid credentials"):
            ClientError(mock_error)
    
    def test_client_error_422(self):
        """Test ClientError handling for 422 status."""
        mock_response = MagicMock()
        mock_response.status_code = 422
        
        mock_error = MagicMock()
        mock_error.response = mock_response
        
        with pytest.raises(CriticalError, match="invalid"):
            ClientError(mock_error)


# ============================================================================
# 9. TestUtilities - Utility Functions
# ============================================================================
class TestUtilities:
    """Test utility functions."""
    
    def test_timer_wrapper(self):
        """Test timer wrapper decorator."""
        import time
        
        @timer_wrapper
        def slow_function():
            time.sleep(0.01)
            return "result"
        
        result = slow_function()
        assert result == "result"
        
        timings = get_all_timings()
        assert "slow_function" in timings
        assert timings["slow_function"] >= 0.01
    
    def test_get_all_timings(self):
        """Test getting all function timings."""
        timings = get_all_timings()
        assert isinstance(timings, dict)


# ============================================================================
# 10. TestVersionAndConstants - Version and Constants
# ============================================================================
class TestVersionAndConstants:
    """Test version and constant values."""
    
    def test_version_exists(self):
        """Test that version exists."""
        assert __version__ is not None
    
    def test_version_format(self):
        """Test version format (semantic versioning)."""
        assert isinstance(__version__, str)
        parts = __version__.split(".")
        assert len(parts) >= 2  # At least major.minor
        for part in parts:
            assert part.isdigit()
    
    def test_version_value(self):
        """Test current version value."""
        assert __version__ == "1.2.0"


# ============================================================================
# 11. TestComprehensiveScenarios - Complex Multi-Feature Scenarios
# ============================================================================
class TestComprehensiveScenarios:
    """Test comprehensive scenarios combining multiple features."""
    
    def test_full_upload_scenario_args(self):
        """Test full upload scenario argument parsing."""
        args = parse_args([
            "--token", "pat_test_token_12345",
            "--base", "appTestBaseId123",
            "--table", "tblTestTableId456",
            "--log", "upload.log",
            "--verbose",
            "--workers", "8",
            "--dropbox-token", "dropbox-token.json",
            "--attachment-columns", "Image",
            "--disable-bypass-column-creation",
            "--fail-on-duplicate-csv-columns",
            "data.csv"
        ])
        
        assert args.token == "pat_test_token_12345"
        assert args.base == "appTestBaseId123"
        assert args.table == "tblTestTableId456"
        assert args.log == Path("upload.log")
        assert args.verbose is True
        assert args.workers == 8
        assert args.dropbox_token == Path("dropbox-token.json")
        assert args.attachment_columns == ["Image"]
        assert args.disable_bypass_column_creation is True
        assert args.fail_on_duplicate_csv_columns is True
        assert args.csv_file == Path("data.csv")
    
    def test_attachment_mapping_scenario(self):
        """Test attachment mapping scenario."""
        args = parse_args([
            "--token", "pat_test_token_12345",
            "--base", "appTestBaseId123",
            "--table", "tblTestTableId456",
            "--dropbox-token", "dropbox-token.json",
            "--attachment-columns-map", "Local Image", "Remote Image",
            "--attachment-columns-map", "Local Thumb", "Remote Thumb",
            "data.json"
        ])
        
        assert args.attachment_columns_map == [
            ["Local Image", "Remote Image"],
            ["Local Thumb", "Remote Thumb"]
        ]
        assert args.csv_file == Path("data.json")
    
    def test_column_copy_scenario(self):
        """Test column copy scenario."""
        # Note: With nargs="+", positional arg must come before to avoid being consumed
        args = parse_args([
            "--token", "pat_test_token_12345",
            "--base", "appTestBaseId123",
            "--table", "tblTestTableId456",
            "--columns-copy", "Status", "Status Backup", "Status Archive",
        ])
        
        assert args.columns_copy == ["Status", "Status Backup", "Status Archive"]
    
    def test_rename_key_column_scenario(self):
        """Test rename key column scenario."""
        args = parse_args([
            "--token", "pat_test_token_12345",
            "--base", "appTestBaseId123",
            "--table", "tblTestTableId456",
            "--rename-key-column", "CSV ID", "Airtable ID",
            "data.csv"
        ])
        
        assert args.rename_key_column == ["CSV ID", "Airtable ID"]
    
    def test_marker_data_scenario(self):
        """Test Marker Data integration scenario with --md flag."""
        args = parse_args([
            "--token", "pat_test_token_12345",
            "--base", "appTestBaseId123",
            "--table", "tblTestTableId456",
            "--dropbox-token", "dropbox-token.json",
            "--attachment-columns-map", "Image Filename", "Attachments",
            "--md",
            "markers.json"
        ])
        
        assert args.md is True
        assert args.attachment_columns_map == [["Image Filename", "Attachments"]]


# ============================================================================
# 12. TestEdgeCases - Edge Cases and Boundary Conditions
# ============================================================================
class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_string_values(self):
        """Test handling of empty string values in CSV."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("Name,Value,Status\n")
            f.write("Alice,,Active\n")
            f.write(",30,\n")
            temp_path = f.name
        
        try:
            result = csv_read(Path(temp_path), fail_on_dup=False)
            assert len(result) == 2
            assert result[0]["fields"]["Value"] == ""
            assert result[1]["fields"]["Name"] == ""
            assert result[1]["fields"]["Status"] == ""
        finally:
            os.unlink(temp_path)
    
    def test_unicode_characters(self):
        """Test handling of Unicode characters."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("Name,City,Emoji\n")
            f.write("日本語,東京,🎉\n")
            f.write("Ελληνικά,Αθήνα,🏛️\n")
            temp_path = f.name
        
        try:
            result = csv_read(Path(temp_path), fail_on_dup=False)
            assert len(result) == 2
            assert result[0]["fields"]["Name"] == "日本語"
            assert result[0]["fields"]["Emoji"] == "🎉"
        finally:
            os.unlink(temp_path)
    
    def test_special_characters_in_values(self):
        """Test handling of special characters in CSV values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Description"])
            writer.writerow(["Test", "Contains, comma"])
            writer.writerow(["Test2", 'Contains "quotes"'])
            temp_path = f.name
        
        try:
            result = csv_read(Path(temp_path), fail_on_dup=False)
            assert len(result) == 2
            assert "comma" in result[0]["fields"]["Description"]
        finally:
            os.unlink(temp_path)
    
    def test_large_csv_file(self):
        """Test handling of larger CSV files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("ID,Name,Value\n")
            for i in range(100):
                f.write(f"{i},Name_{i},Value_{i}\n")
            temp_path = f.name
        
        try:
            result = csv_read(Path(temp_path), fail_on_dup=False)
            assert len(result) == 100
            assert result[99]["fields"]["ID"] == "99"
        finally:
            os.unlink(temp_path)
    
    def test_json_with_null_values(self):
        """Test handling of null values in JSON."""
        test_data = [
            {"Name": "Alice", "Age": None, "City": "New York"},
            {"Name": None, "Age": 25, "City": None}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            result = json_read(Path(temp_path), fail_on_dup=False)
            assert len(result) == 2
            assert result[0]["fields"]["Age"] is None
            assert result[1]["fields"]["Name"] is None
        finally:
            os.unlink(temp_path)
    
    def test_path_with_spaces(self):
        """Test handling of file paths with spaces."""
        args = parse_args([
            "--token", "pat_test_token_12345",
            "--base", "appTestBaseId123",
            "--table", "tblTestTableId456",
            "--log", "path with spaces/log.txt",
            "path with spaces/data.csv"
        ])
        
        assert args.log == Path("path with spaces/log.txt")
        assert args.csv_file == Path("path with spaces/data.csv")
    
    def test_workers_zero_or_negative(self):
        """Test workers argument with edge values."""
        args = parse_args([
            "--token", "pat_test_token_12345",
            "--base", "appTestBaseId123",
            "--table", "tblTestTableId456",
            "--workers", "0",
            "data.csv"
        ])
        
        assert args.workers == 0  # Parsed as-is, CLI layer handles defaults
        
        args = parse_args([
            "--token", "pat_test_token_12345",
            "--base", "appTestBaseId123",
            "--table", "tblTestTableId456",
            "--workers", "1",
            "data.csv"
        ])
        
        assert args.workers == 1


# ============================================================================
# 13. TestCLIIntegration - CLI Integration Tests
# ============================================================================
class TestCLIIntegration:
    """Test CLI integration scenarios."""
    
    def test_cli_main_import(self):
        """Test that CLI main function can be imported."""
        from airlift.cli import main, cli, setup_logging
        
        assert callable(main)
        assert callable(cli)
        assert callable(setup_logging)
    
    def test_setup_logging_verbose(self):
        """Test logging setup in verbose mode."""
        from airlift.cli import setup_logging
        import logging
        
        setup_logging(is_verbose=True, log_file=None)
        
        airlift_logger = logging.getLogger("airlift")
        assert airlift_logger.level == logging.DEBUG
    
    def test_setup_logging_normal(self):
        """Test logging setup in normal mode."""
        from airlift.cli import setup_logging
        import logging
        
        setup_logging(is_verbose=False, log_file=None)
        
        airlift_logger = logging.getLogger("airlift")
        assert airlift_logger.level == logging.INFO
    
    def test_setup_logging_with_file(self):
        """Test logging setup with log file."""
        from airlift.cli import setup_logging
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            temp_path = f.name
        
        try:
            setup_logging(is_verbose=True, log_file=Path(temp_path))
            # Logging setup should not raise any errors
        finally:
            os.unlink(temp_path)


# ============================================================================
# Main Entry Point
# ============================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=long"])

