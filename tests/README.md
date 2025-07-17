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
   - Ensure `tests/assets/` contains the CSV and image files
   - CSV should reference the image files correctly

## Running Tests

### All tests:
```bash
pytest tests/
```

### Specific test classes:
```bash
# Test CSV processing only
pytest tests/test_upload.py::TestCSVProcessing -v

# Test Dropbox integration
pytest tests/test_upload.py::TestDropboxIntegration -v

# Test Airtable integration  
pytest tests/test_upload.py::TestAirtableIntegration -v

# Test actual uploads (careful - this uploads real data!)
pytest tests/test_upload.py::TestDataUpload -v
```

### With output:
```bash
pytest tests/ -v -s
```

## Test Structure

- **TestCSVProcessing**: Tests CSV file parsing and validation
- **TestDropboxIntegration**: Tests real Dropbox file uploads
- **TestAirtableIntegration**: Tests Airtable connection and client
- **TestDataUpload**: Tests actual data upload to Airtable (with/without attachments)
- **TestErrorHandling**: Tests error scenarios with invalid data
- **TestAssetFiles**: Validates test assets are present and correct

## Important Notes

⚠️ **These tests make real API calls!**

- **Dropbox**: Will upload test images to your Dropbox account
- **Airtable**: Will add records to your specified table
- **Costs**: May incur API usage charges
- **Data**: Will create real data in your services

## Environment Variables

Required in `.env`:
```bash
AIRTABLE_TOKEN=your_token
AIRTABLE_BASE=your_base_id  
AIRTABLE_TABLE=your_table_id
DROPBOX_APP_KEY=your_dropbox_app_key
DROPBOX_REFRESH_TOKEN=your_refresh_token
```

## Assets

The `tests/assets/` directory should contain:
- `big_cats.csv` - Test data file
- `*.jpg` files - Test images referenced in CSV

## Cleanup

After running tests, you may want to:
- Delete uploaded files from Dropbox
- Remove test records from Airtable
- Check API usage in both services