"""Debug test to check console logs"""
import pytest
import time


def test_check_console_logs(browser):
    """Check browser console for mock messages"""
    time.sleep(3)  # Wait for everything to load

    # Get browser console logs
    logs = browser.get_log('browser')
    print("\n=== BROWSER CONSOLE LOGS ===")
    for log in logs:
        print(f"[{log['level']}] {log['message']}")

    # Check if API mocking is enabled
    is_enabled = browser.execute_script("return window.__API_MOCKING_ENABLED__;")
    print(f"\n__API_MOCKING_ENABLED__: {is_enabled}")

    # Check mock data
    mock_data = browser.execute_script("return window.__TEST_API__ ? window.__TEST_API__.getMockData() : null;")
    print(f"Mock Data: {mock_data}")

    # Check if fetch was overridden
    fetch_str = browser.execute_script("return window.fetch.toString().substring(0, 100);")
    print(f"Fetch function: {fetch_str}")

    # Check XHR
    xhr_type = browser.execute_script("return typeof window.XMLHttpRequest;")
    print(f"XMLHttpRequest type: {xhr_type}")

    assert True  # Always pass, just for debugging
