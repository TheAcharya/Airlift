# Airlift Tests

This directory contains tests for Airlift, including comprehensive local tests and integration tests that interact with Airtable and Dropbox services.

## Setup

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Configure environment (for integration tests):**
   - Copy `.env.example` to `.env`
   - Fill in your real Airtable and Dropbox credentials

3. **Verify assets:**
   - Ensure `tests/assets/` contains the JSON and image files
   - JSON should reference the image files correctly

## Running Tests

### Comprehensive Tests (No API Tokens Required):
```bash
# Run comprehensive tests locally
pytest tests/test_comprehensive.py -v

# Or use the build script
./scripts/local-test-build.sh --comprehensive-test
```

### Upload Tests (Requires API Tokens):
```bash
pytest tests/test_upload.py -v -s
```

### Delete Database Entries Tests (Requires API Tokens):
```bash
pytest tests/test_delete_database_entries.py -v -s
```

### Empty Dropbox Folder Tests (Requires Dropbox Tokens):
```bash
pytest tests/test_empty_dropbox_folder.py -v -s
```

### All Tests:
```bash
pytest tests/ -v -s --disable-warnings
```

## Test Structure

```
tests/
├── __init__.py                      # Test suite module
├── input_command.py                 # Args configuration and environment variables
├── test_comprehensive.py            # Comprehensive tests (no API tokens required)
├── test_upload.py                   # Upload tests (requires API tokens)
├── test_delete_database_entries.py  # Delete database entries test (requires API tokens)
├── test_empty_dropbox_folder.py     # Empty Dropbox folder test (requires Dropbox tokens)
├── README.md                        # This file
└── assets/                          # Test data files
    ├── airtable-upload-test.json
    ├── *.gif                        # Image attachments
    └── *-Palette.jpg                # Palette attachments
```

### File Descriptions

- **`input_command.py`**: Contains `AirliftArgs` dataclass and `ARGS_DICT` configuration loaded from environment variables
- **`test_comprehensive.py`**: Comprehensive test suite that validates all CLI arguments, data processing, and mocked functionality without requiring API tokens
- **`test_upload.py`**: Main upload test with fixtures that tests the complete upload workflow (requires API tokens)
- **`test_delete_database_entries.py`**: Tests the `--delete-all-database-entries` functionality (requires API tokens)
- **`test_empty_dropbox_folder.py`**: Tests the `--empty-dropbox-folder` functionality (requires Dropbox tokens)

## Important Notes

⚠️ **Integration tests make real API calls!**

- **Dropbox**: Will upload/delete files in your Dropbox account
- **Airtable**: Will add/delete records in your specified table
- **Costs**: May incur API usage charges
- **Data**: Will create/delete real data in your services

## Environment Variables

Required in `.env` for integration tests:
```bash
CI_AIRTABLE_TOKEN=your_token
CI_AIRTABLE_BASE=your_base_id  
CI_AIRTABLE_TABLE=your_table_id
CI_DROPBOX_APP_KEY=your_dropbox_app_key
CI_DROPBOX_REFRESH_TOKEN=your_refresh_token
```

## Assets

The `tests/assets/` directory should contain:
- `airtable-upload-test.json` - Test data file (JSON format)
- `*.gif` files - Test images referenced in JSON (Image Filename)
- `*-Palette.jpg` files - Test palette images referenced in JSON (Palette Filename)

## Cleanup

After running upload tests, you may want to clean up:
- Delete uploaded files from Dropbox
- Remove test records from Airtable

**Quick Cleanup:**
```bash
# Delete all entries from the test Airtable table
pytest tests/test_delete_database_entries.py -v -s

# Empty the Dropbox folder
pytest tests/test_empty_dropbox_folder.py -v -s
```
