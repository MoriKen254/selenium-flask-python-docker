"""Check what axios error is occurring"""
import pytest
from pages import TodoPage


def test_check_axios_post_error(browser):
    """Try to capture the actual axios error"""
    page = TodoPage(browser)
    page.wait_for_page_load()

    import time
    time.sleep(2)

    # Check what URL axios would use
    api_url = browser.execute_script("return window.__API_URL__;")
    print(f"\n__API_URL__: {api_url}")

    # Inject error capture code
    browser.execute_script("""
        window.__AXIOS_ERRORS__ = [];
        window.__AXIOS_REQUESTS__ = [];

        // Intercept console.error to capture axios errors
        const originalError = console.error;
        console.error = function(...args) {
            const errorStr = args.map(a => {
                if (a && typeof a === 'object') {
                    return JSON.stringify(a, Object.getOwnPropertyNames(a));
                }
                return String(a);
            }).join(' ');
            window.__AXIOS_ERRORS__.push(errorStr);
            originalError.apply(console, args);
        };

        // Also capture console.log for axios request attempts
        const originalLog = console.log;
        console.log = function(...args) {
            const logStr = args.map(a => String(a)).join(' ');
            if (logStr.includes('axios') || logStr.includes('POST') || logStr.includes('api')) {
                window.__AXIOS_REQUESTS__.push(logStr);
            }
            originalLog.apply(console, args);
        };
    """)

    # Try to create a todo
    page.enter_title("Test Todo")
    page.click_add_button()

    # Wait for the request to complete/fail
    time.sleep(3)

    # Get captured errors
    errors = browser.execute_script("return window.__AXIOS_ERRORS__;")
    print(f"\nCaptured axios errors: {errors}")

    # Check network state
    online = browser.execute_script("return navigator.onLine;")
    print(f"Browser online: {online}")

    # Check if there's a more detailed error in the DOM
    error_text = browser.execute_script("""
        var errorEl = document.querySelector('.error-message');
        return errorEl ? errorEl.textContent : null;
    """)
    print(f"Error message: {error_text}")
