"""Test to capture the actual network error during todo creation"""
import pytest
import time
from pages.todo_page import TodoPage


def test_capture_create_todo_network_error(browser):
    """Capture detailed network error when creating a todo via UI"""
    page = TodoPage(browser)

    # Inject network request capture
    browser.execute_script("""
        window.__NETWORK_REQUESTS__ = [];
        window.__NETWORK_ERRORS__ = [];

        // Intercept fetch
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            console.log('[CAPTURE] Fetch called with:', args);
            window.__NETWORK_REQUESTS__.push({
                type: 'fetch',
                url: args[0],
                options: args[1],
                timestamp: new Date().toISOString()
            });

            return originalFetch.apply(this, args)
                .then(response => {
                    console.log('[CAPTURE] Fetch response:', response.status, response.ok);
                    window.__NETWORK_REQUESTS__[window.__NETWORK_REQUESTS__.length - 1].response = {
                        status: response.status,
                        ok: response.ok,
                        statusText: response.statusText
                    };
                    return response;
                })
                .catch(error => {
                    console.error('[CAPTURE] Fetch error:', error);
                    window.__NETWORK_ERRORS__.push({
                        type: 'fetch',
                        error: error.toString(),
                        message: error.message,
                        timestamp: new Date().toISOString()
                    });
                    throw error;
                });
        };
    """)

    print("\n[TEST] Network capture injected")

    # Now create a todo via UI
    print("[TEST] Creating todo via UI...")
    page.enter_title("Test Todo")
    page.enter_description("Testing network capture")

    # Capture the state before click
    print("[TEST] Clicking submit button...")
    page.click_add_button()

    # Wait for request to complete
    time.sleep(3)

    # Check captured requests
    requests = browser.execute_script("return window.__NETWORK_REQUESTS__;")
    errors = browser.execute_script("return window.__NETWORK_ERRORS__;")

    print(f"\n[CAPTURE] Total requests: {len(requests)}")
    for i, req in enumerate(requests):
        print(f"\n  Request {i+1}:")
        print(f"    Type: {req.get('type')}")
        print(f"    URL: {req.get('url')}")
        print(f"    Options: {req.get('options')}")
        if 'response' in req:
            print(f"    Response: {req['response']}")

    print(f"\n[CAPTURE] Total errors: {len(errors)}")
    for i, err in enumerate(errors):
        print(f"\n  Error {i+1}:")
        print(f"    Type: {err.get('type')}")
        print(f"    Error: {err.get('error')}")
        print(f"    Message: {err.get('message')}")

    # Check if todo was created
    todos = page.get_all_todos()
    print(f"\n[TEST] Todos on page: {len(todos)}")

    # Check for error message
    if page.is_error_displayed():
        print(f"[TEST] Error displayed: {page.get_error_message()}")

    # If no todos and we have errors, fail with details
    if len(todos) == 0 and len(errors) > 0:
        pytest.fail(f"Todo creation failed with errors: {errors}")
