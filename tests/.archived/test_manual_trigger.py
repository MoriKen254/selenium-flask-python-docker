"""Test manually triggering API calls"""
import pytest
import time
from config import is_unit_mode

pytestmark = pytest.mark.skipif(not is_unit_mode(), reason="Only runs in unit mode")


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

    # Verify the manual calls returned mock data
    assert result.get('status') == 200, "XHR call should succeed with status 200"
    assert 'Mock Todo' in result.get('responseText', ''), "XHR response should contain mock data"

    assert fetch_result.get('success') is True, "Fetch call should succeed"
    assert 'Mock Todo' in fetch_result.get('text', ''), "Fetch response should contain mock data"

    print("\n✓ All manual API calls returned mocked data successfully!")
