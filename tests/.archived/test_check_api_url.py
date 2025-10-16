"""Quick test to check what API URL the frontend is using"""
import pytest


def test_check_api_url(browser):
    """Check what API URL the frontend has configured"""
    import time
    time.sleep(2)  # Wait for page to load

    api_url = browser.execute_script("return window.__API_URL__;")
    print(f"\n__API_URL__: {api_url}")

    hostname = browser.execute_script("return window.location.hostname;")
    print(f"hostname: {hostname}")

    # Check if mock interceptor is active (should be false in integration mode)
    is_mocking = browser.execute_script("return window.__API_MOCKING_ENABLED__ === true;")
    print(f"__API_MOCKING_ENABLED__: {is_mocking}")

    has_test_api = browser.execute_script("return typeof window.__TEST_API__ !== 'undefined';")
    print(f"Has __TEST_API__: {has_test_api}")

    # Try to manually call the backend with GET
    result = browser.execute_script("""
        return fetch(window.__API_URL__ + '/api/todos')
            .then(r => ({status: r.status, ok: r.ok}))
            .catch(err => ({error: err.message}));
    """)
    print(f"Backend GET result: {result}")

    # Try to manually call the backend with POST
    post_result = browser.execute_script("""
        return fetch(window.__API_URL__ + '/api/todos', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({title: 'Test Todo', description: ''})
        })
            .then(r => ({status: r.status, ok: r.ok}))
            .catch(err => ({error: err.message}));
    """)
    print(f"Backend POST result: {post_result}")
