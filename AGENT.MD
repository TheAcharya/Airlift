# Airlift - AI Agent Documentation

## Project Overview

Airlift is a Python-based command-line tool for uploading and merging CSV or JSON data files with attachments to Airtable databases. The project provides an automated solution for data migration and synchronization with Airtable, including support for file attachments via Dropbox integration.

## Architecture Overview

### Core Components

The project follows a modular architecture with clear separation of concerns:

1. **CLI Interface** (`cli.py`, `cli_args.py`) - Command-line argument parsing and main execution flow
2. **Data Processing** (`csv_data.py`, `json_data.py`) - File format handling and data validation
3. **Airtable Integration** (`airtable_client.py`, `airtable_upload.py`) - API communication and data upload
4. **Dropbox Integration** (`dropbox_client.py`) - File storage and sharing for attachments
5. **Utilities** (`utils.py`, `utils_exceptions.py`) - Helper functions and custom exceptions
6. **Error Handling** (`airtable_error_handling.py`) - Centralized error management

### Data Flow

1. User provides CSV/JSON file and Airtable credentials via CLI
2. System validates file format and parses data into standardized format
3. Airtable schema validation and column mapping
4. Optional Dropbox upload for attachment files
5. Concurrent data upload to Airtable with progress tracking
6. Error handling and logging throughout the process

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

## Development Guidelines

### Code Structure

#### Module Organization
- Each major functionality is separated into its own module
- Clear import hierarchy with minimal circular dependencies
- Consistent naming conventions across modules

#### Error Handling
- Custom exception classes for different error types
- Centralized error handling in CLI layer
- Graceful degradation for non-critical errors
- Comprehensive logging for debugging

#### Configuration Management
- Command-line argument parsing with argparse
- JSON-based configuration for Dropbox tokens
- Environment-agnostic file path handling

### Coding Standards

#### Python Conventions
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Implement proper docstrings for public functions
- Use logging instead of print statements

#### Error Handling Patterns
- Use custom exceptions for domain-specific errors
- Implement proper exception chaining
- Provide meaningful error messages to users
- Log detailed error information for debugging

#### Testing Considerations
- Unit tests for individual modules
- Integration tests for end-to-end workflows
- Mock external API calls to avoid network dependencies
- Test error conditions and edge cases

### Dependencies

#### Core Dependencies
- `pyairtable` 3.1.1 - Airtable API client with latest 3.x APIs
- `requests` - HTTP client for API calls
- `dropbox` 12.0.2 - Dropbox API client with latest APIs and explicit OAuth2 scopes
- `tqdm` - Progress bar implementation
- `icecream` - Debug logging utility

#### Development Dependencies
- `poetry` 2.1.3 - Dependency management and packaging
- Python 3.9+ compatibility (matches GitHub Actions workflow)
- `setuptools` 80.9.0 - Package installation utilities

### Build and Distribution

#### Packaging
- Poetry-based dependency management
- PyInstaller for binary distribution
- Cross-platform build support (Linux, macOS, Windows)
- Homebrew integration for macOS

#### Release Process
- Semantic versioning (MAJOR.MINOR.PATCH)
- Automated GitHub releases
- Binary distribution for all platforms
- Changelog maintenance

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
└── scripts/
    ├── local-test-build.sh  # Build script
    └── README.md            # Detailed usage documentation
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

## API Integration Patterns

### Airtable API
- RESTful API communication using pyairtable 3.x
- Bearer token authentication
- JSON payload formatting
- Rate limiting consideration
- Error response handling
- Automatic field creation with pyairtable 3.x APIs

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
- Configurable worker thread count
- Progress tracking for large datasets
- Memory-efficient data processing

### Error Recovery
- Graceful handling of network failures
- Retry logic for transient errors
- Partial upload recovery
- Comprehensive error logging

## Maintenance and Support

### Logging Strategy
- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- File-based logging with configurable paths
- Structured log messages for parsing
- Version information in logs

### Monitoring and Debugging
- Progress bar for user feedback
- Verbose mode for detailed output
- Error categorization and reporting
- Performance timing utilities

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

This documentation should be kept in sync with the cursorrule file to ensure consistent development practices and code quality standards across the project. 