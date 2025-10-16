"""Debug test to check if interceptor is working"""
import pytest
import time
from config import is_unit_mode

pytestmark = pytest.mark.skipif(not is_unit_mode(), reason="Only runs in unit mode")


def test_check_interceptor_loaded(browser):
    """Check if the API interceptor is loaded and active"""
    time.sleep(2)  # Wait for page to fully load

    # Check if interceptor is loaded
    is_enabled = browser.execute_script("return window.__API_MOCKING_ENABLED__ === true;")
    print(f"API Mocking Enabled: {is_enabled}")

    # Check if TEST_API is available
    has_test_api = browser.execute_script("return typeof window.__TEST_API__ !== 'undefined';")
    print(f"Has TEST API: {has_test_api}")

    # Get mock data
    if has_test_api:
        mock_data = browser.execute_script("return window.__TEST_API__.getMockData();")
        print(f"Mock data: {mock_data}")

    # Try to manually trigger a fetch
    print("\n=== Testing Manual Fetch ===")
    result = browser.execute_script("""
        return fetch('/api/todos')
            .then(r => r.json())
            .then(data => ({success: true, data: data}))
            .catch(err => ({success: false, error: err.message}));
    """)
    print(f"Fetch result: {result}")

    assert is_enabled, "API interceptor not loaded"
    assert has_test_api, "TEST API not available"
