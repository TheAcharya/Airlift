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

# Dev CLI (after --comprehensive-test or full build; uses .build/venv/)
.build/venv/bin/airlift --help

# Prefer the binary for release parity
./test-build/airlift --help
```

### Dependency Management
```bash
# Regenerate poetry.lock (after pyproject.toml changes)
./scripts/local-test-build.sh --lock-only

# Update one package at a time (recommended; updates lock file)
./scripts/local-test-build.sh --lock-only --update requests
./scripts/local-test-build.sh --comprehensive-test

# Update lock then full build
./scripts/local-test-build.sh --update requests

# Update all deps within ^ ranges (use sparingly)
./scripts/local-test-build.sh --update-deps

# Show outdated packages (uses .build/ Poetry)
./scripts/local-test-build.sh --show-outdated
```

Prefer `./scripts/local-test-build.sh` over bare `poetry lock` so resolution uses the
ephemeral Python 3.14.5 environment in `.build/`.

## Architecture Overview

### Core Components

The project follows a modular architecture with clear separation of concerns:

| Module | Description |
|--------|-------------|
| `cli.py` + `cli_args.py` | Command-line interface and argument parsing |
| `airtable_client.py` + `airtable_upload.py` | Airtable API integration using pyairtable 3.x |
| `dropbox_client.py` | Dropbox API integration for file storage using SDK 12.x |
| `csv_data.py` + `json_data.py` | Data file parsing and validation |
| `utils_exceptions.py` | Shared custom exception hierarchy |

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
- **ALWAYS** use `./scripts/local-test-build.sh` for building and dependency lock updates
- The build script is **fully self-contained** under `.build/` (no system Python/Poetry install)
- Downloads **CPython 3.14.5** via [python-build-standalone](https://github.com/astral-sh/python-build-standalone/releases)
- PyInstaller is installed separately during build (not in pyproject.toml)
- Build outputs go to `test-build/`; verify with `./test-build/airlift --help`

### Development Environment (local, via `local-test-build.sh`)
- **Python**: 3.14.5 standalone (`PYTHON_STANDALONE_VERSION` in build script)
- **Python constraint** (`pyproject.toml`): `>=3.10,<3.15`
- **Poetry**: 2.4.1 (bootstrap in `.build/python/`)
- **Setuptools** (bootstrap): 82.0.1
- **poetry-plugin-export**: 1.10.0

### CI vs local (important)
- **Local** builds use standalone **Python 3.14.5** via `local-test-build.sh`
- **GitHub Actions** (`build.yml`, `release_github.yml`): **Python 3.14**, Poetry **2.4.1**, setuptools **82.0.1**
- All Poetry-based workflows use the same toolchain pins as `build.yml`
- **Commit `poetry.lock`** (or stop gitignoring it) so CI resolution matches local locks

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

# Or via ephemeral venv (after build script has installed deps)
.build/venv/bin/pytest tests/test_comprehensive.py -v

# Integration tests (requires API tokens; same venv)
.build/venv/bin/pytest tests/test_upload.py -v -s
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
- **No system-level Python, Poetry, pip, or project deps** (only host `curl` + `tar`)
- Standalone CPython from python-build-standalone (macOS arm64/x86_64)
- Professional logging without emojis
- Flexible dependency management (`--lock-only`, `--update`, `--update-deps`)

#### Build Process
1. Downloads/extracts standalone **CPython 3.14.5** into `.build/python/`
2. Installs **pip 26.1.2**, **setuptools 82.0.1**, and **Poetry 2.4.1** into `.build/python/`
3. Configures Poetry paths under `.build/` (`venv/`, `cache/`, `poetry-config/`, etc.)
4. Installs **poetry-plugin-export 1.10.0**
5. Runs `poetry install` into `.build/venv/`
6. Installs PyInstaller in the Poetry venv (not in `pyproject.toml`)
7. Builds with PyInstaller → `test-build/airlift`

#### Directory Structure
```
Airlift/
├── .build/                    # Ephemeral build environment (gitignored)
│   ├── python/               # Standalone CPython + pip + Poetry
│   ├── downloads/            # Cached Python tarball
│   ├── venv/                 # Poetry project virtualenv
│   ├── cache/                # Poetry cache
│   ├── pip-cache/            # pip cache
│   ├── poetry-config/        # Poetry configuration
│   └── poetry-home/          # Poetry application data
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

# Clean (.build/, test-build/, .pytest_cache/)
./scripts/local-test-build.sh --clean

# Lock file only
./scripts/local-test-build.sh --lock-only

# Update one dependency + lock
./scripts/local-test-build.sh --lock-only --update urllib3

# Comprehensive tests (installs deps if needed)
./scripts/local-test-build.sh --comprehensive-test

# Show outdated packages
./scripts/local-test-build.sh --show-outdated
```

#### CI/CD Integration
| Context | Python | Poetry | setuptools | poetry-plugin-export |
|---------|--------|--------|------------|----------------------|
| Local (`local-test-build.sh`) | 3.14.5 standalone | 2.4.1 | 82.0.1 | 1.10.0 |
| `build.yml` / `release_github.yml` | 3.14 (setup-python) | 2.4.1 | 82.0.1 | 1.10.0 |
| `unit_tests.yml`, integration test workflows | 3.14 | 2.4.1 | 82.0.1 | 1.10.0 |

## Dependencies and Versions

### Core Dependencies (from `pyproject.toml`)
| Package | Constraint | Notes |
|---------|------------|-------|
| `python` | `>=3.10,<3.15` | Local builds use **3.14.5** |
| `pyairtable` | ^3.3.0 | Resolved to 3.4.x locally |
| `dropbox` | ^12.0.2 | Caps `stone` to &lt;3.3.3 |
| `requests` | ^2.32.4 | |
| `tqdm` | ^4.66.4 | |
| `pydantic` | ^2.13.0 | **Required for Python 3.14** (2.11.x core fails to build) |
| `icecream` | ^2.1.3 | |
| `pytest` | ^9.0.0 | In main deps for PyInstaller bundle |

Use `poetry.lock` for exact resolved versions. Regenerate via
`./scripts/local-test-build.sh --lock-only` after `pyproject.toml` edits.

### Dependency update constraints (do not force)
| Package | Why |
|---------|-----|
| `pydantic-core` | Pinned by `pydantic` (e.g. 2.13.4 → `==2.46.4`); do not bump core alone |
| `stone` | Dropbox requires `stone >=2,<3.3.3`; cannot use latest 3.3.9 |

### Local build toolchain (`local-test-build.sh`)
- Python **3.14.5** (python-build-standalone tag `20260510`)
- pip **26.1.2**
- Setuptools **82.0.1** (bootstrap only)
- Poetry **2.4.1**
- PyInstaller **latest** (installed in Poetry venv at build time)

## Python 3.14 Migration Workflow

When changing Python or toolchain versions:

1. Update `python` in `pyproject.toml` if needed
2. Update pins in `scripts/local-test-build.sh` (`PYTHON_STANDALONE_*`, `POETRY_VERSION`, etc.)
3. `./scripts/local-test-build.sh --clean`
4. `./scripts/local-test-build.sh --lock-only`
5. `./scripts/local-test-build.sh --comprehensive-test`
6. `./scripts/local-test-build.sh` and test `./test-build/airlift`
7. Update GitHub Actions workflows **last** (after local is green)

If `poetry install` fails on 3.14, bump **pydantic** to `^2.13.0` or newer before other packages.

## Common Development Tasks

### Adding New Data Format Support
1. Create new parser module following `csv_data.py` pattern
2. Add format detection routing in `cli.py`
3. Update CLI arguments in `cli_args.py`
4. Test with sample files and various edge cases

### Extending API Integration
1. Follow existing patterns in `airtable_client.py` and `dropbox_client.py`
2. Implement proper error handling using custom exceptions
3. Add logging with appropriate levels
4. Test authentication flows and rate limiting

### Error Handling Enhancement
1. Add new exception types to `utils_exceptions.py`
2. Ensure proper error propagation and user-friendly messages
3. Test error scenarios and recovery mechanisms

### Adding New Features Checklist

When adding new CLI features:
1. Add argument definition in `cli_args.py` schema
2. Handle the argument in `cli.py`
3. Add validation in `_validate_required_args()` if required
4. Implement the feature in appropriate module
5. Add tests in `test_comprehensive.py`
6. Update `AGENT.MD` and `.cursorrules` (keep in sync)
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
- Keep workflow env pins in sync with `scripts/local-test-build.sh` when toolchain changes

## Maintenance and Support

### Monitoring and Debugging
- Progress bar for user feedback
- Verbose mode for detailed output
- Error categorization and reporting

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
