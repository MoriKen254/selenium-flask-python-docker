"""Verify API URL is correctly set in React app"""
import pytest
from pages import TodoPage


def test_verify_api_url_variable(browser):
    """Check if the React app has the correct API_URL"""
    page = TodoPage(browser)
    page.wait_for_page_load()

    import time
    time.sleep(2)

    # Check React internal state/variables
    result = browser.execute_script("""
        // Try to access the React app's internal state
        // Get the root element
        const root = document.getElementById('root');
        if (!root) {
            return {error: 'Root element not found'};
        }

        // Check if __API_URL__ is set
        return {
            __API_URL__: window.__API_URL__,
            hasRoot: !!root,
            rootHTML: root.innerHTML.substring(0, 200),
            location: window.location.href
        };
    """)

    print(f"\nResult: {result}")

    assert result.get('__API_URL__') is not None, "API_URL should be set"
    assert result.get('__API_URL__') == 'http://backend:5000', f"API_URL should be http://backend:5000, got {result.get('__API_URL__')}"
