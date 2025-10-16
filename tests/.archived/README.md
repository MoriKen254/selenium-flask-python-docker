# Archived Test Files

This directory contains debug and diagnostic test files that were used during development and troubleshooting. These tests are not part of the regular test suite but are kept for reference.

## Contents

### Debug Tests
Files used to debug specific issues during development:
- `test_debug_*.py` - Various debugging tests
- `test_check_*.py` - Configuration and setup verification tests

### Diagnostic Tests
Tests used to diagnose integration issues:
- `test_integration_diagnosis.py` - Integration mode diagnostics
- `test_interceptor_quick.py` - Quick interceptor testing
- `test_manual_trigger.py` - Manual test triggering

### Configuration Tests
Tests to verify API and configuration setup:
- `test_api_url_at_runtime.py` - Runtime API URL verification
- `test_verify_api_url.py` - API URL validation
- `test_check_axios_*.py` - Axios library verification

### Old Scripts
- `rebuild_run_tests.bat` - Old rebuild script (replaced by scripts/run_all_tests.bat)

## Usage

These files are archived and not run as part of the regular test suite. If you need to use them for debugging:

```bash
# From tests directory
cd .archived
pytest test_debug_console.py -v
```

## Note

The main test suite is in `tests/test_todo_crud.py`. Use the scripts in `tests/scripts/` to run the official test suite.
