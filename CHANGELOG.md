# Changelog

### 1.3.2

**🎉 Released:**
- 25th February 2026

**🔨 Improvements:**
- Replaced bare `except:` with specific exceptions (`KeyError`, `Exception`) in dropbox_client and cli so KeyboardInterrupt and SystemExit are not caught
- Replaced empty `except OSError: pass` with `contextlib.suppress(OSError)` in test fixture cleanup (test_upload, test_delete_database_entries, test_empty_dropbox_folder)
- Removed unused imports and unused local variables across the codebase (CodeQL clean-up)

---

### 1.3.1

**🎉 Released:**
- 8th February 2026

**🔨 Improvements:**
- Added comprehensive test coverage for upload worker stop signal and CLI exception handler with 78 total test methods

**🐞 Bug Fix:**
- Fixed upload worker stop signal — add `stop_event` so workers exit when one raises CriticalError
- Fixed CLI exception handler referencing `args` before it may be set (e.g. when parse_args fails)

---

### 1.3.0

**🎉 Released:**
- 1st December 2025

**🔨 Improvements:**
- Added `--delete-all-database-entries` to delete all entries from the specified Airtable table
- Added `--empty-dropbox-folder` to empty the contents of the Dropbox folder
- Updated `pyairtable` to version 3.3.0
- Added comprehensive test suite (`test_comprehensive.py`) for local testing
- Added `--comprehensive-test` option to `local-test-build.sh` (#23)
- Added new GitHub Actions workflow for unit tests (`unit_tests.yml`)
- Added new GitHub Actions workflow for delete database entries test (`airtable_delete_database_entries_test.yml`)
- Improved CLI argument validation with user-friendly error messages

---

### 1.2.0

**🎉 Released:**
- 21st July 2025

**🔨 Improvements:**
- Upgraded from Python 3.8 to Python 3.9
- Updated to the latest `pyairtable` library
- Updated to the latest Dropbox API (#42)
- Updated to latest security patches across all dependencies (#41)
- Improved code maintainability and modern Python practices
- Improved build reproducibility across environments
- Enhanced ephemeral build `local-test-build.sh` reliability
- Added Airtable Upload Test

---

### 1.1.4

**🎉 Released:**
- 11th November 2024

**🔨 Improvements:**
- Updated dependencies packages

---

### 1.1.3

**🎉 Released:**
- 20th May 2024

**🔨 Improvements:**
- Improved log output for `--rename-key-column`
- Improved upload speed

---

### 1.1.2

**🎉 Released:**
- 10th May 2024

**🔨 Improvements:**
- Updated dependencies packages

---

### 1.1.1

**🎉 Released:**
- 28th April 2024

**🔨 Improvements:**
- Added support to log skipped images (#38)

---

### 1.1.0

**🎉 Released:**
- 27th April 2024

**🔨 Improvements:**
- Added support to auto-skip image upload when associated row has missing images (#37)

---

### 1.0.9

**🎉 Released:**
- 26th April 2024

**🔨 Improvements:**
- Added support for multiple attachemnt columns mapping

**🐞 Bug Fix:**
- Improved handling of multiple attachemnt columns (#36)

---

### 1.0.8

**🎉 Released:**
- 2nd March 2024

**🐞 Bug Fix:**
- Improved error handling of Airtable wrong token (#35)

---

### 1.0.7

**🎉 Released:**
- 16th February 2024

**🔨 Improvements:**
- Improved logic for `--dropbox-refresh-token` augmentation (#34)
- Improved log output with `--verbose` augmentation

**🐞 Bug Fix:**
- Fixed Dropbox refresh token creation (#31)
- Improved error handling of property mismatch (#33)

---

### 1.0.6

**🎉 Released:**
- 22nd January 2024

**🔨 Improvements:**
- Added new macOS pkg release with notarization ticket stapled
- Improved error message without arguments

---

### 1.0.5

**🎉 Released:**
- 15th January 2024

**🔨 Improvements:**
- Added codesign and notarization to macOS binary

---

### 1.0.4

**🎉 Released:**
- 18th December 2023

**🔨 Improvements:**
- Added `.json` support for [MarkersExtractor](https://github.com/TheAcharya/MarkersExtractor) (#28)
- Improved progress bar behaviour (#30)
- Improved warning log output
- Improved internal codebase

---

### 1.0.3

**🎉 Released:**
- 13th December 2023

**🔨 Improvements:**
- Added `--rename-key-column` : rename the key column in the file to a different key column in Airtable (#27)

---

### 1.0.2

**🎉 Released:**
- 11th December 2023

**🔨 Improvements:**
- Added Airlift version number in Log File (#26)

**🐞 Bug Fix:**
- Fixed `metavar` argument parser (#24)
- Fixed `tqdm` breaking due to multiprocess (#13)

---

### 1.0.1

**🎉 Released:**
- 22nd November 2023

**🔨 Improvements:**
- Added `--columns-copy` : Copys value of one column to multiple other columns (#25)
- Improved error handling logic when attachments are not found

---

### 1.0.0
**🎉 Released:**
- 18th November 2023

This is the first public release of **Airlift**!
