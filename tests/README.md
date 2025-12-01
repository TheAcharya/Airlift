# Airlift Tests

This directory contains real API tests for Airlift that actually interact with Airtable and Dropbox services.

## Setup

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Configure environment:**
   - Copy `.env.example` to `.env`
   - Fill in your real Airtable and Dropbox credentials

3. **Verify assets:**
   - Ensure `tests/assets/` contains the JSON and image files
   - JSON should reference the image files correctly

## Running Tests

### All tests:
```bash
pytest tests/test_upload.py -v -s
```

### With output:
```bash
pytest tests/test_upload.py -v -s --disable-warnings
```

## Test Structure

```
tests/
├── __init__.py          # Test suite module
├── input_command.py     # Args configuration and environment variables
├── test_upload.py       # Upload tests with fixtures
├── README.md            # This file
└── assets/              # Test data files
    ├── airtable-upload-test.json
    ├── *.gif            # Image attachments
    └── *-Palette.jpg    # Palette attachments
```

### File Descriptions

- **`input_command.py`**: Contains `AirliftArgs` dataclass and `ARGS_DICT` configuration loaded from environment variables
- **`test_upload.py`**: Main upload test with fixtures that tests the complete workflow

## Important Notes

⚠️ **These tests make real API calls!**

- **Dropbox**: Will upload test images to your Dropbox account
- **Airtable**: Will add records to your specified table
- **Costs**: May incur API usage charges
- **Data**: Will create real data in your services

## Environment Variables

Required in `.env`:
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

After running tests, you may want to:
- Delete uploaded files from Dropbox
- Remove test records from Airtable
- Check API usage in both services
