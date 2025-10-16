"""Test if XMLHttpRequest works in integration mode"""
import pytest


def test_xhr_functionality(browser):
    """Test if XHR can make requests"""
    import time
    time.sleep(2)

    result = browser.execute_script("""
        return new Promise((resolve) => {
            const xhr = new XMLHttpRequest();
            xhr.open('GET', window.__API_URL__ + '/api/todos');

            xhr.onload = function() {
                resolve({
                    success: true,
                    status: xhr.status,
                    responseLength: xhr.responseText.length,
                    response: xhr.responseText.substring(0, 100)
                });
            };

            xhr.onerror = function() {
                resolve({
                    success: false,
                    error: 'XHR onerror triggered',
                    status: xhr.status,
                    statusText: xhr.statusText,
                    readyState: xhr.readyState
                });
            };

            xhr.ontimeout = function() {
                resolve({
                    success: false,
                    error: 'XHR timeout'
                });
            };

            try {
                xhr.send();
            } catch (e) {
                resolve({
                    success: false,
                    error: 'Exception during send: ' + e.message
                });
            }
        });
    """)

    print(f"\nXHR test result: {result}")

    assert result.get('success') == True, f"XHR should work: {result}"
