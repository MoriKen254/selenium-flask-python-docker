"""Debug test to check console logs"""
import pytest
import time
from config import is_unit_mode

pytestmark = pytest.mark.skipif(not is_unit_mode(), reason="Only runs in unit mode")


def test_check_console_logs(browser):
    """Check browser console for mock messages using JavaScript capture"""
    time.sleep(3)  # Wait for everything to load

    # Get captured console logs from JavaScript (Firefox-compatible)
    logs = browser.execute_script("""
        // Return any captured console logs if available
        if (window.__CAPTURED_CONSOLE_LOGS__) {
            return window.__CAPTURED_CONSOLE_LOGS__;
        }
        return [];
    """)

    print("\n=== CAPTURED CONSOLE LOGS ===")
    if logs:
        for log in logs:
            print(f"[{log.get('level', 'LOG')}] {log.get('message', '')}")
    else:
        print("No console logs captured (console capture not enabled)")

    # Check if API mocking is enabled
    is_enabled = browser.execute_script("return window.__API_MOCKING_ENABLED__;")
    print(f"\n__API_MOCKING_ENABLED__: {is_enabled}")
    assert is_enabled, "API mocking should be enabled"

    # Check mock data
    mock_data = browser.execute_script("return window.__TEST_API__ ? window.__TEST_API__.getMockData() : null;")
    print(f"Mock Data: {mock_data}")
    assert mock_data is not None, "Mock data should be available"
    assert len(mock_data) >= 2, "Should have at least 2 mock todos"

    # Check if fetch was overridden
    fetch_str = browser.execute_script("return window.fetch.toString().substring(0, 100);")
    print(f"Fetch function: {fetch_str}")

    # Check XHR
    xhr_type = browser.execute_script("return typeof window.XMLHttpRequest;")
    print(f"XMLHttpRequest type: {xhr_type}")

    print("\n✓ All console checks passed!")
