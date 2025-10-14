"""Test manually triggering API calls"""
import pytest
import time


def test_manual_api_call(browser):
    """Manually trigger an API call from the browser"""
    time.sleep(2)

    # Manually trigger the API call using execute_script
    result = browser.execute_script("""
        // Create a promise to make the API call
        return new Promise((resolve) => {
            const xhr = new XMLHttpRequest();
            xhr.open('GET', 'http://localhost:5000/api/todos');
            xhr.onload = function() {
                resolve({
                    status: xhr.status,
                    response: xhr.response,
                    responseText: xhr.responseText
                });
            };
            xhr.onerror = function() {
                resolve({error: 'XHR failed'});
            };
            xhr.send();
        });
    """)

    print(f"\nManual XHR result: {result}")

    # Also try with fetch
    fetch_result = browser.execute_script("""
        return fetch('/api/todos')
            .then(r => r.text())
            .then(text => ({success: true, text: text}))
            .catch(err => ({success: false, error: err.message}));
    """)

    print(f"Manual fetch result: {fetch_result}")

    # Check console logs again
    logs = browser.get_log('browser')
    print("\n=== Console logs after manual calls ===")
    for log in logs:
        print(f"[{log['level']}] {log['message']}")

    assert True  # Just for debugging
