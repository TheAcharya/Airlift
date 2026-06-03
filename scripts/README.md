# Local Test Build Script

## Overview

The `local-test-build.sh` script provides a completely ephemeral build environment for Airlift. It creates a self-contained build system that doesn't install anything on your system, making it perfect for development, testing, and CI/CD workflows.

## Key Features

- Fully Ephemeral: Everything is contained in project directories
- No System Installation: Downloads standalone CPython into `.build/python/` (python-build-standalone)
- GitHub Actions compatible: Poetry, setuptools, and plugin-export pins match CI/CD (macOS uses standalone Python bootstrap)
- Cross-Platform: Works on macOS
- Clean Output: Professional logging without emojis
- Flexible Updates: Multiple dependency management options

## Prerequisites

### System Requirements
- macOS (Apple Silicon or Intel)
- Host tools only: `curl` and `tar` (to download/extract Python into `.build/`)
- No system Python, Homebrew Python, or Poetry install required

## Quick Start

### Basic Build
```bash
# From the project root directory
./scripts/local-test-build.sh
```

This will:
1. Download standalone CPython 3.14.5 into `.build/python/` (pinned python-build-standalone release)
2. Install pip 26.1.2 in `.build/python/`
3. Install setuptools 82.0.1 in `.build/python/`
4. Install Poetry 2.4.1 in `.build/python/`
5. Install project dependencies via Poetry
6. Install PyInstaller for building
7. Build the application
8. Output the binary to `test-build/airlift`

### Run the Built Application
```bash
./test-build/airlift --help
```

## Command Line Options

### Build Options
```bash
# Normal build
./scripts/local-test-build.sh

# Build and run tests
./scripts/local-test-build.sh --test

# Clean .build/, test-build/, .pytest_cache/ and exit
./scripts/local-test-build.sh --clean
```

### Dependency Management
```bash
# Update poetry.lock file before building
./scripts/local-test-build.sh --update-lock

# Update all dependencies to latest versions
./scripts/local-test-build.sh --update-deps

# Update specific packages
./scripts/local-test-build.sh --update requests pytest

# Only update lock file (no build)
./scripts/local-test-build.sh --lock-only --update requests

# Show outdated packages
./scripts/local-test-build.sh --show-outdated
```

### Help
```bash
# Show detailed help
./scripts/local-test-build.sh --help
```

## Directory Structure

After running the script, your project will have:

```
Airlift/
├── .build/                    # Ephemeral build environment (gitignored)
│   ├── python/               # Standalone CPython + pip + Poetry
│   ├── downloads/            # Cached Python tarball
│   ├── venv/                 # Poetry project virtual environment
│   ├── cache/                # Poetry cache
│   ├── pip-cache/            # pip download cache
│   ├── poetry-config/        # Poetry configuration
│   └── poetry-home/          # Poetry application data
├── test-build/               # Build output (gitignored)
│   ├── airlift              # Final executable binary
│   └── build/               # PyInstaller build artifacts
├── scripts/
│   └── local-test-build.sh  # This script
└── ... (other project files)
```

## Detailed Usage Examples

### Development Workflow

1. First Time Setup
   ```bash
   # Clone the repository
   git clone https://github.com/TheAcharya/Airlift.git
   cd Airlift
   
   # Build the application
   ./scripts/local-test-build.sh
   ```

2. Regular Development
   ```bash
   # Make changes to your code
   # ...
   
   # Rebuild
   ./scripts/local-test-build.sh
   
   # Test the changes
   ./test-build/airlift --help
   ```

3. Update Dependencies
   ```bash
   # Update specific package
   ./scripts/local-test-build.sh --update requests
   
   # Update all dependencies
   ./scripts/local-test-build.sh --update-deps
   ```

4. Clean and Rebuild
   ```bash
   # Clean everything
   ./scripts/local-test-build.sh --clean
   
   # Fresh build
   ./scripts/local-test-build.sh
   ```

### CI/CD Integration

The script is designed to work seamlessly with GitHub Actions and uses identical versions:

```yaml
# Example GitHub Actions step
- name: Build Airlift
  run: |
    chmod +x scripts/local-test-build.sh
    ./scripts/local-test-build.sh
```

**Version alignment with GitHub Actions** (Poetry, setuptools, plugin-export pins):
- Python: **3.14** in workflows (`BUILD_PYTHON_VERSION`); local script uses standalone **3.14.5** on macOS
- pip: **26.1.2** (local bootstrap only)
- Poetry: **2.4.1** (`BUILD_POETRY_VERSION`)
- Setuptools: **82.0.1** (`BUILD_SETUPTOOLS_VERSION`)
- poetry-plugin-export: **1.10.0** (`BUILD_POETRY_PLUGIN_EXPORT_VERSION`)
- PyInstaller: latest (installed in Poetry venv at build time; matches CI workflow)

## Environment Details

### Build Environment
- Standalone Python: `.build/python/` (python-build-standalone 3.14.5, not system Python)
- Project venv: `.build/venv/` (Poetry-managed dependencies)
- pip: 26.1.2 (pinned bootstrap in `.build/python/`)
- Setuptools: 82.0.1 (installed before Poetry)
- Poetry: 2.4.1 (installed via pip in `.build/python/`)
- Dependencies: Managed by Poetry in `.build/venv/`

### Build Output
- Binary: `test-build/airlift`
- Size: ~20MB typical on macOS (Python 3.14 one-file bundle; varies by platform)
- Architecture: Native to your system
- Dependencies: Self-contained (no external dependencies)

### PyInstaller Configuration
- Spec File: Uses `airlift.spec` from project root
- Output Directory: `test-build/`
- Build Artifacts: `test-build/build/`
- Installation: Installed separately (not in `pyproject.toml`)

## Troubleshooting

### Common Issues

1. "Missing required host tools"
   ```bash
   # curl and tar must be available (standard on macOS)
   which curl tar
   ```

2. "Failed to download standalone Python"
   ```bash
   # Retry after network check, or clean and rebuild
   ./scripts/local-test-build.sh --clean
   ./scripts/local-test-build.sh
   ```

3. "Missing required tools"
   ```bash
   # Install curl if missing
   brew install curl
   # xar and cpio are usually pre-installed on macOS
   ```

4. Build fails with PyInstaller errors
   ```bash
   # Clean and rebuild
   ./scripts/local-test-build.sh --clean
   ./scripts/local-test-build.sh
   ```

5. Permission denied
   ```bash
   # Make script executable
   chmod +x scripts/local-test-build.sh
   ```

6. SSL Warning during build
   ```
   urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, 
   currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'
   ```
   This warning is normal on macOS when building locally due to different SSL library versions 
   between the build environment and system. It doesn't affect the functionality of the built binary 
   and can be safely ignored.

### Debug Mode

If you encounter issues, you can inspect the build environment:

```bash
# Check what's in the build directory
ls -la .build/

# Check the virtual environment
.build/python/bin/python --version

# Check setuptools installation
.build/python/bin/pip show setuptools

# Check Poetry installation
.build/python/bin/poetry --version

# Check PyInstaller installation
.build/python/bin/poetry run pyinstaller --version
```

## Cleanup

### Manual Cleanup
```bash
# Remove build directories
rm -rf .build/ test-build/ .pytest_cache/

# Or use the script
./scripts/local-test-build.sh --clean
```

### What Gets Cleaned
- `.build/` - Complete ephemeral environment
- `test-build/` - Build output and artifacts
- `dist/` - Legacy build output (if exists)
- `build/` - Legacy build artifacts (if exists)

## Best Practices

### For Developers
1. Always run from project root: The script expects `pyproject.toml` in the current directory
2. Use clean builds: Run `--clean` when switching branches or after dependency changes
3. Test the binary: Always verify `./test-build/airlift --help` works after building
4. Keep dependencies updated: Use `--show-outdated` to check for updates
5. Version consistency: Local builds use identical versions to production CI/CD

### For CI/CD
1. Use exact versions: The script uses identical versions to GitHub Actions workflow
2. Clean before build: Always run `--clean` in CI to ensure fresh builds
3. Cache dependencies: Consider caching `.build/` in CI for faster builds
4. Test the output: Verify the built binary works in your deployment environment
5. Version consistency: Local builds match production builds exactly

## Script Configuration

### Script configuration variables
Pinned at the top of `scripts/local-test-build.sh` (Poetry/setuptools align with GitHub Actions):
```bash
BUILD_DIR=".build"
TEST_BUILD_DIR="test-build"
PYTHON_STANDALONE_VERSION="3.14.5"   # macOS standalone CPython (python-build-standalone)
PYTHON_STANDALONE_RELEASE_TAG="20260510"
PIP_VERSION="26.1.2"
POETRY_VERSION="2.4.1"               # matches BUILD_POETRY_VERSION in workflows
SETUPTOOLS_VERSION="82.0.1"          # matches BUILD_SETUPTOOLS_VERSION in workflows
POETRY_PLUGIN_EXPORT_VERSION="1.10.0"
```

### Customization
To modify the script behavior, edit the configuration section at the top of `local-test-build.sh`.

## Support

### Getting Help
```bash
# Show script help
./scripts/local-test-build.sh --help

# Check script version and configuration
head -20 scripts/local-test-build.sh
```

### Reporting Issues
If you encounter issues with the build script:
1. Run `./scripts/local-test-build.sh --clean`
2. Try a fresh build
3. Check the prerequisites
4. Review the troubleshooting section above

## Security Notes

- The script only downloads and installs packages from trusted sources (PyPI, Poetry)
- All dependencies are installed in isolated virtual environments
- No system-wide installations or modifications are made
- The build environment is completely ephemeral and can be safely deleted
- Version pinning ensures reproducible builds across environments

## Version Alignment

This build script aligns dependency tooling with the GitHub Actions workflows:

- **Python**: workflows use **3.14**; the local script downloads standalone **3.14.5** on macOS
- **pip**: **26.1.2** (local bootstrap)
- **Poetry**: **2.4.1**
- **Setuptools**: **82.0.1**
- **poetry-plugin-export**: **1.10.0**
- **PyInstaller**: latest (installed in the Poetry venv during build)

Local macOS builds use the same Poetry/setuptools pins as CI; the Python bootstrap differs (standalone tarball vs `actions/setup-python` on Linux/macOS/Windows runners).

---

Note: This script is designed to be completely self-contained and safe to run. It will not modify your system Python installation or install any packages globally. 