# Airlift - AI Agent Documentation

This file provides comprehensive guidance for AI agents (Claude, Cursor, etc.) when working with code in this repository.

## Project Overview

Airlift is a Python-based command-line tool for uploading and merging CSV or JSON data files with attachments to Airtable databases. It uses Dropbox as a temporary storage provider for attachments since Airtable's API doesn't support direct file uploads. The project is built with Poetry for dependency management and uses PyInstaller for cross-platform binary distribution.

## Quick Reference Commands

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

# Run comprehensive tests (no API tokens required)
./scripts/local-test-build.sh --comprehensive-test

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

## Architecture Overview

### Core Components

The project follows a modular architecture with clear separation of concerns:

| Module | Description |
|--------|-------------|
| `cli.py` + `cli_args.py` | Command-line interface and argument parsing |
| `airtable_client.py` + `airtable_upload.py` | Airtable API integration using pyairtable 3.x |
| `dropbox_client.py` | Dropbox API integration for file storage using SDK 12.x |
| `csv_data.py` + `json_data.py` | Data file parsing and validation |
| `utils.py` + `utils_exceptions.py` | Utility functions and custom exceptions |
| `airtable_error_handling.py` | Centralized error management |
| `airlift_data_guesser.py` | Data type inference and column mapping |

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

## Key Features

### Data Format Support
- CSV files with UTF-8 encoding
- JSON files with array of objects structure
- Automatic column validation and mapping
- Support for duplicate column handling

### Airtable Integration
- Personal access token authentication
- Base and table ID validation
- Automatic column creation (configurable)
- Support for single/multiple select fields
- Column renaming and copying capabilities
- Delete all database entries functionality

### Dropbox Operations
- Empty folder contents without deleting the folder itself
- Works with both `/Airlift` and `/Marker Data` folders (via `--md` flag)
- Progress bar for deletion operations

### Attachment Handling
- Dropbox integration for file storage
- Multiple attachment column support
- Column mapping for attachment fields
- Automatic file path resolution

### Performance Features
- Multi-threaded upload processing
- Configurable worker thread count
- Progress bar with real-time updates
- Comprehensive logging system

## Code Organization

### Module Structure
- Keep each module focused on a single responsibility
- Use clear, descriptive module names that reflect their purpose
- Maintain consistent import patterns across modules
- Avoid circular dependencies between modules

### File Naming Conventions
- Use snake_case for all Python files and functions
- Use descriptive names that clearly indicate functionality
- Follow the existing naming pattern: `airlift_*.py` for core modules

## Important Development Guidelines

### Build System Requirements
- **ALWAYS** use `./scripts/local-test-build.sh` for building instead of manual Poetry/PyInstaller commands
- The build script creates an ephemeral environment in `.build/` that matches GitHub Actions exactly
- PyInstaller is installed separately during build (not in pyproject.toml)
- Build outputs go to `test-build/` directory and should be tested with `./test-build/airlift --help`

### Development Environment
- **Python Version**: 3.9+ (matches GitHub Actions BUILD_PYTHON_VERSION: 3.9)
- **Poetry Version**: 2.1.3 (matches GitHub Actions BUILD_POETRY_VERSION: 2.1.3)
- **Build System**: Use `./scripts/local-test-build.sh` for all builds to ensure consistency with CI/CD

### Code Quality Standards
- Follow PEP 8 style guidelines with 88-character line limit (Black formatter)
- Use type hints for all function parameters and return values
- Implement comprehensive docstrings for public functions
- Use logging instead of print statements
- Handle errors with custom exceptions from `utils_exceptions.py`

### API Integration Patterns
- **Airtable**: Uses pyairtable 3.x with Bearer token authentication and automatic field creation
- **Dropbox**: Uses SDK 12.x with OAuth2 flow and explicit scopes for enhanced security
- Both APIs require proper error handling, rate limiting, and refresh token management

### CLI Arguments Structure
```python
schema: ArgSchema = {
    "POSITIONAL": { ... },
    "general_options": { ... },
    "dropbox options": { ... },
    "column_options": { ... },
    "custom application options": { ... },
    "validation_options": { ... },
    "database_options": { ... },  # --delete-all-database-entries, --empty-dropbox-folder
}
```

### Testing and Validation
- Always test builds using the ephemeral build system
- Run comprehensive tests with `--comprehensive-test` flag (no API tokens required)
- Validate API integrations with proper mock testing
- Test with different file formats and sizes
- Verify cross-platform compatibility

### Test Structure
```
tests/
├── __init__.py                      # Test suite module
├── input_command.py                 # Args configuration and environment variables
├── test_upload.py                   # Upload tests (requires API tokens)
├── test_delete_database_entries.py  # Delete tests (requires API tokens)
├── test_empty_dropbox_folder.py     # Dropbox folder tests (requires Dropbox tokens)
├── test_comprehensive.py            # Comprehensive tests (no API tokens required)
├── README.md                        # Test documentation
└── assets/                          # Test data files
```

### Running Tests
```bash
# Comprehensive tests (no API tokens required)
./scripts/local-test-build.sh --comprehensive-test

# Or directly with pytest
pytest tests/test_comprehensive.py -v

# Integration tests (requires API tokens)
pytest tests/test_upload.py -v -s
pytest tests/test_delete_database_entries.py -v -s
pytest tests/test_empty_dropbox_folder.py -v -s
```

### Security Considerations
- Never hardcode credentials - use JSON token files
- Implement OAuth2 flows with explicit scopes
- Sanitize all user inputs and file paths
- Use secure file upload mechanisms

## Ephemeral Build System

### Local Test Build Script

The project includes a comprehensive ephemeral build system (`scripts/local-test-build.sh`) that provides:

#### Key Features
- Fully ephemeral build environment in `.build/` directory
- No system-level installations or modifications
- Uses system Python with virtual environments
- GitHub Actions compatible approach
- Cross-platform support
- Professional logging without emojis
- Flexible dependency management options

#### Build Process
1. Creates virtual environment using system Python 3.9+
2. Installs setuptools 80.9.0 (matches GitHub Actions)
3. Installs Poetry 2.1.3 in the virtual environment
4. Installs project dependencies via Poetry
5. Installs PyInstaller separately (not in pyproject.toml)
6. Builds application using PyInstaller
7. Outputs binary to `test-build/` directory

#### Directory Structure
```
Airlift/
├── .build/                    # Ephemeral build environment (gitignored)
│   ├── python/               # Virtual environment
│   ├── venv/                 # Poetry virtual environment
│   └── cache/                # Poetry cache
├── test-build/               # Build output (gitignored)
│   ├── airlift              # Final executable binary
│   └── build/               # PyInstaller build artifacts
├── scripts/
│   ├── local-test-build.sh  # Build script
│   └── README.md            # Detailed usage documentation
└── tests/
    ├── test_comprehensive.py        # Comprehensive tests (no API tokens)
    ├── test_upload.py               # Upload tests (requires API tokens)
    ├── test_delete_database_entries.py  # Delete tests (requires API tokens)
    └── test_empty_dropbox_folder.py     # Dropbox folder tests (requires Dropbox tokens)
```

#### Usage Examples
```bash
# Basic build
./scripts/local-test-build.sh

# Build with dependency updates
./scripts/local-test-build.sh --update-deps

# Update specific packages
./scripts/local-test-build.sh --update requests pytest

# Clean build environment
./scripts/local-test-build.sh --clean

# Show outdated packages
./scripts/local-test-build.sh --show-outdated

# Run comprehensive tests
./scripts/local-test-build.sh --comprehensive-test
```

#### CI/CD Integration
The build script is designed to work seamlessly with GitHub Actions and uses identical versions:
- Python 3.9+ (matches BUILD_PYTHON_VERSION: 3.9)
- Poetry 2.1.3 (matches BUILD_POETRY_VERSION: 2.1.3)
- Setuptools 80.9.0 (matches setuptools==80.9.0)
- PyInstaller latest version (matches CI workflow)
- poetry-plugin-export for requirements.txt generation
- No PyInstaller in pyproject.toml (installed separately)
- Same approach as CI/CD pipeline
- Completely ephemeral and safe
- Consistent with production build process

## Dependencies and Versions

### Core Dependencies (from pyproject.toml)
| Package | Version | Description |
|---------|---------|-------------|
| `pyairtable` | ^3.3.0 | Airtable API client with latest 3.x APIs |
| `dropbox` | ^12.0.2 | Dropbox API client with OAuth2 scopes |
| `requests` | ^2.32.4 | HTTP client for API calls |
| `tqdm` | ^4.66.4 | Progress bar implementation |
| `pydantic` | ^2.11.7 | Data validation and serialization |
| `icecream` | ^2.1.3 | Debug logging utility |

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

### Adding New Features Checklist

When adding new CLI features:
1. Add argument definition in `cli_args.py` schema
2. Handle the argument in `cli.py`
3. Add validation in `_validate_required_args()` if required
4. Implement the feature in appropriate module
5. Add tests in `test_comprehensive.py`
6. Update `AGENT.MD` documentation
7. Update `README.md` if user-facing
8. Run comprehensive tests: `./scripts/local-test-build.sh --comprehensive-test`
9. Build and test binary: `./scripts/local-test-build.sh`

## File Organization Notes

### Git-ignored Directories
- `.build/`: Ephemeral build environment (completely temporary)
- `test-build/`: Build output and PyInstaller artifacts
- `Demo/`, `docker/`, `dropbox_token.json`, `log.txt`: Development files

### Important Configuration Files
| File | Description |
|------|-------------|
| `pyproject.toml` | Poetry configuration and dependencies |
| `airlift.spec` | PyInstaller specification file |
| `.cursorrules` | Development guidelines and coding standards |
| `AGENT.MD` | This comprehensive project documentation |

## API Integration Patterns

### Airtable API
- RESTful API communication using pyairtable 3.x
- Bearer token authentication
- JSON payload formatting
- Rate limiting consideration
- Error response handling
- Automatic field creation with pyairtable 3.x APIs
- Batch delete operations (10 records per request)

### Dropbox API
- OAuth2 authentication flow with explicit scopes
- Refresh token management
- File upload and sharing
- URL generation for attachments
- Folder structure management
- Latest Dropbox SDK 12.x with enhanced security features

## Security Considerations

### Authentication
- Secure token storage in JSON files
- OAuth2 flow for Dropbox integration with explicit scopes
- Personal access token for Airtable
- No hardcoded credentials

### Data Handling
- UTF-8 encoding for international character support
- File path validation and sanitization
- Error message sanitization
- Secure file upload handling

## Performance Optimization

### Upload Efficiency
- Concurrent processing with ThreadPoolExecutor
- Configurable worker thread count (default: 5)
- Progress tracking for large datasets
- Memory-efficient data processing

### Error Recovery
- Graceful handling of network failures
- Retry logic for transient errors
- Partial upload recovery
- Comprehensive error logging

## Error Handling Patterns

### Exception Hierarchy
- Use `CriticalError` for fatal application errors
- Use `AirtableError` for Airtable-specific issues
- Use `TypeConversionError` for data type issues
- Implement proper exception chaining

### Logging Strategy
- Use structured logging with appropriate levels
- Include context information in log messages
- Implement file-based logging for debugging
- Use consistent log message formatting

## Code Review Guidelines

### Review Checklist
- Verify proper error handling implementation
- Check for security vulnerabilities
- Ensure proper logging and debugging support
- Validate performance implications
- Confirm documentation updates
- Verify build script compatibility
- Add tests for new features

### Quality Standards
- Maintain high test coverage for new features
- Ensure backward compatibility when possible
- Follow established naming conventions
- Implement proper type hints throughout
- Test builds using the ephemeral build system
- Ensure version consistency between local and CI environments

## Maintenance and Support

### Monitoring and Debugging
- Progress bar for user feedback
- Verbose mode for detailed output
- Error categorization and reporting
- Performance timing utilities

## GitHub Actions Workflows

| Workflow | Trigger | Description |
|----------|---------|-------------|
| `unit_tests.yml` | Push/PR to master/dev | Comprehensive tests (no API tokens) |
| `airtable_image_upload_test.yml` | Weekly/Manual | Upload integration test |
| `airtable_delete_database_entries_test.yml` | Weekly/Manual | Delete entries + Empty Dropbox folder tests |
| `build.yml` | Push/PR | Build verification |
| `release_github.yml` | Release | Binary distribution |

## Future Development

### Planned Features
- Additional file format support
- Enhanced error recovery mechanisms
- Performance optimizations
- Extended Airtable field type support
- Continued Dropbox SDK updates for improved API compatibility

### Architecture Evolution
- Plugin system for custom data processors
- Configuration file support
- Web interface for non-technical users
- API server mode for integration
- Modernized integration patterns with latest SDK features

## Integration Guidelines

### External Systems
- Airtable webhook integration
- CI/CD pipeline integration
- Monitoring and alerting systems
- Backup and recovery procedures

### User Experience
- Clear command-line help and documentation
- Intuitive error messages
- Progress indication for long operations
- Comprehensive usage examples

---

This documentation should be kept in sync with the `.cursorrules` file to ensure consistent development practices and code quality standards across the project.
