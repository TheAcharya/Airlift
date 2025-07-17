# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Airlift is a Python command-line tool for uploading CSV/JSON data with attachments to Airtable databases. It uses Dropbox as a temporary storage provider for attachments since Airtable's API doesn't support direct file uploads. The project is built with Poetry for dependency management and uses PyInstaller for cross-platform binary distribution.

## Development Commands

### Building and Testing
```bash
# Build the project using the ephemeral build system (recommended)
./scripts/local-test-build.sh

# Test the built binary
./test-build/airlift --help

# Clean build environment
./scripts/local-test-build.sh --clean

# Build with dependency updates
./scripts/local-test-build.sh --update-deps

# Install dependencies for development
poetry install

# Run the application in development
poetry run airlift --help
```

### Dependency Management
```bash
# Update poetry.lock file
poetry lock

# Update specific packages
./scripts/local-test-build.sh --update requests dropbox

# Show outdated packages
./scripts/local-test-build.sh --show-outdated

# Install new dependency
poetry add <package-name>

# Install development dependency
poetry add --group dev <package-name>
```

### Development Environment
- **Python Version**: 3.9+ (matches GitHub Actions BUILD_PYTHON_VERSION: 3.9)
- **Poetry Version**: 2.1.3 (matches GitHub Actions BUILD_POETRY_VERSION: 2.1.3)
- **Build System**: Use `./scripts/local-test-build.sh` for all builds to ensure consistency with CI/CD

## Code Architecture

### Core Module Structure
- `cli.py` + `cli_args.py`: Command-line interface and argument parsing
- `airtable_client.py` + `airtable_upload.py`: Airtable API integration using pyairtable 3.x
- `dropbox_client.py`: Dropbox API integration for file storage using SDK 12.x
- `csv_data.py` + `json_data.py`: Data file parsing and validation
- `utils.py` + `utils_exceptions.py`: Utility functions and custom exceptions
- `airtable_error_handling.py`: Centralized error management
- `airlift_data_guesser.py`: Data type inference and column mapping

### Data Flow Architecture
1. **Input Processing**: CSV/JSON files are parsed and validated
2. **Schema Validation**: Airtable table schema is fetched and columns are mapped
3. **Attachment Handling**: Files are uploaded to Dropbox and sharing URLs generated
4. **Concurrent Upload**: Data is uploaded to Airtable using ThreadPoolExecutor
5. **Progress Tracking**: Real-time progress bars and comprehensive logging

### Key Design Patterns
- **Modular Architecture**: Clear separation between data processing, API clients, and CLI
- **Error Handling**: Custom exception hierarchy with proper error propagation
- **Concurrent Processing**: ThreadPoolExecutor for parallel uploads with configurable workers
- **API Integration**: RESTful clients for Airtable and Dropbox with proper authentication

## Important Development Guidelines

### Build System Requirements
- **ALWAYS** use `./scripts/local-test-build.sh` for building instead of manual Poetry/PyInstaller commands
- The build script creates an ephemeral environment in `.build/` that matches GitHub Actions exactly
- PyInstaller is installed separately during build (not in pyproject.toml)
- Build outputs go to `test-build/` directory and should be tested with `./test-build/airlift --help`

### API Integration Patterns
- **Airtable**: Uses pyairtable 3.x with Bearer token authentication and automatic field creation
- **Dropbox**: Uses SDK 12.x with OAuth2 flow and explicit scopes for enhanced security
- Both APIs require proper error handling, rate limiting, and refresh token management

### Code Quality Standards
- Follow PEP 8 style guidelines with 88-character line limit (Black formatter)
- Use type hints for all function parameters and return values
- Implement comprehensive docstrings for public functions
- Use logging instead of print statements
- Handle errors with custom exceptions from `utils_exceptions.py`

### Testing and Validation
- Always test builds using the ephemeral build system
- Validate API integrations with proper mock testing
- Test with different file formats and sizes
- Verify cross-platform compatibility

### Security Considerations
- Never hardcode credentials - use JSON token files
- Implement OAuth2 flows with explicit scopes
- Sanitize all user inputs and file paths
- Use secure file upload mechanisms

## Dependencies and Versions

### Core Dependencies (from pyproject.toml)
- `pyairtable ^3.1.1`: Airtable API client with latest 3.x APIs
- `dropbox ^12.0.2`: Dropbox API client with latest SDK and OAuth2 scopes
- `requests ^2.32.4`: HTTP client for API calls
- `tqdm ^4.66.4`: Progress bar implementation
- `pydantic ^2.11.7`: Data validation and serialization

### Build Environment (matches GitHub Actions)
- Python 3.9+ (BUILD_PYTHON_VERSION: 3.9)
- Poetry 2.1.3 (BUILD_POETRY_VERSION: 2.1.3)
- Setuptools 80.9.0 (setuptools==80.9.0)
- PyInstaller (latest, installed separately during build)

## Common Development Tasks

### Adding New Data Format Support
1. Create new parser module following `csv_data.py` pattern
2. Add format detection to `airlift_data_guesser.py`
3. Update CLI arguments in `cli_args.py`
4. Test with sample files and various edge cases

### Extending API Integration
1. Follow existing patterns in `airtable_client.py` and `dropbox_client.py`
2. Implement proper error handling using custom exceptions
3. Add logging with appropriate levels
4. Test authentication flows and rate limiting

### Error Handling Enhancement
1. Add new exception types to `utils_exceptions.py`
2. Update `airtable_error_handling.py` for centralized handling
3. Ensure proper error propagation and user-friendly messages
4. Test error scenarios and recovery mechanisms

## File Organization Notes

### Git-ignored Directories
- `.build/`: Ephemeral build environment (completely temporary)
- `test-build/`: Build output and PyInstaller artifacts
- `Demo/`, `docker/`, `dropbox_token.json`, `log.txt`: Development files

### Important Configuration Files
- `pyproject.toml`: Poetry configuration and dependencies
- `airlift.spec`: PyInstaller specification file
- `.cursorrules`: Development guidelines and coding standards
- `AGENT.MD`: Comprehensive project documentation