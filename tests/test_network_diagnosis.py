"""Test to diagnose network connectivity from browser"""
import pytest
import time
from config import TestConfig


def test_browser_can_reach_backend(browser):
    """Test if browser can make requests to backend"""

    # Try to fetch backend health endpoint using JavaScript fetch
    result = browser.execute_script("""
        return fetch('http://backend:5000/health')
            .then(response => response.json())
            .then(data => ({success: true, data: data}))
            .catch(error => ({success: false, error: error.toString()}));
    """)

    # Wait for the Promise to resolve
    time.sleep(2)

    # Try again with async execution
    result = browser.execute_async_script("""
        var callback = arguments[arguments.length - 1];

        fetch('http://backend:5000/health')
            .then(response => response.json())
            .then(data => callback({success: true, data: data}))
            .catch(error => callback({success: false, error: error.toString()}));
    """)

    print(f"\n[DIAGNOSIS] Fetch result: {result}")

    # Also check what API_URL the frontend is using
    api_url = browser.execute_script("return window.__API_URL__;")
    print(f"[DIAGNOSIS] window.__API_URL__ = {api_url}")

    # Check the actual hostname
    hostname = browser.execute_script("return window.location.hostname;")
    print(f"[DIAGNOSIS] window.location.hostname = {hostname}")

    # Check if fetch fails, log the error
    if not result.get('success'):
        print(f"[DIAGNOSIS] ERROR: {result.get('error')}")
        pytest.fail(f"Browser cannot reach backend: {result.get('error')}")
    else:
        print(f"[DIAGNOSIS] SUCCESS: {result.get('data')}")
