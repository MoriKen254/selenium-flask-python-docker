"""Comprehensive diagnostic test for integration mode"""
import pytest
from pages import TodoPage


def test_integration_page_load_diagnosis(browser):
    """Diagnose what happens when page loads in integration mode"""
    import time

    print("\n=== INTEGRATION MODE DIAGNOSIS ===")

    # Wait for initial page load
    time.sleep(3)

    # 1. Check basic page elements
    print("\n1. Basic Page Elements:")
    page_title = browser.execute_script("return document.title;")
    print(f"   Page title: {page_title}")

    has_root = browser.execute_script("return document.getElementById('root') !== null;")
    print(f"   Has root element: {has_root}")

    root_html_length = browser.execute_script("return document.getElementById('root').innerHTML.length;")
    print(f"   Root HTML length: {root_html_length}")

    # 2. Check if config.js loaded
    print("\n2. Configuration:")
    api_url = browser.execute_script("return window.__API_URL__;")
    print(f"   window.__API_URL__: {api_url}")

    # 3. Check if React loaded
    print("\n3. React Status:")
    has_react_root = browser.execute_script("""
        const root = document.getElementById('root');
        return root && root.children.length > 0;
    """)
    print(f"   React rendered (has children): {has_react_root}")

    # Check for React app elements
    has_h1 = browser.execute_script("return document.querySelector('h1') !== null;")
    print(f"   Has h1 element: {has_h1}")

    has_form = browser.execute_script("return document.querySelector('form') !== null;")
    print(f"   Has form element: {has_form}")

    has_input = browser.execute_script("return document.querySelector('input[placeholder*=\"title\"]') !== null;")
    print(f"   Has title input: {has_input}")

    # 4. Check for JavaScript errors
    print("\n4. JavaScript Status:")
    js_errors = browser.execute_script("""
        return window.__JS_ERRORS__ || [];
    """)
    print(f"   JavaScript errors: {js_errors}")

    # 5. Check network/axios status
    print("\n5. Network Status:")
    online = browser.execute_script("return navigator.onLine;")
    print(f"   Browser online: {online}")

    # 6. Try to manually trigger a GET request
    print("\n6. Manual Network Test:")
    get_result = browser.execute_script("""
        return fetch(window.__API_URL__ + '/api/todos')
            .then(r => ({status: r.status, ok: r.ok}))
            .catch(err => ({error: err.message}));
    """)
    print(f"   Manual GET /api/todos: {get_result}")

    # 7. Check if there's an error message displayed
    print("\n7. Error Messages:")
    error_msg = browser.execute_script("""
        const errorEl = document.querySelector('.error-message');
        return errorEl ? errorEl.textContent : null;
    """)
    print(f"   Error message on page: {error_msg}")

    # 8. Check loading state
    print("\n8. Loading State:")
    loading_msg = browser.execute_script("""
        const loadingEl = document.querySelector('.loading');
        return loadingEl ? loadingEl.textContent : null;
    """)
    print(f"   Loading message: {loading_msg}")

    # 9. Count todos displayed
    print("\n9. Todos Displayed:")
    todo_count = browser.execute_script("""
        const todos = document.querySelectorAll('.todo-item');
        return todos.length;
    """)
    print(f"   Number of todos: {todo_count}")

    # 10. Try to get React component state (if exposed)
    print("\n10. Try Manual Todo Creation:")

    # Enter title
    try:
        page = TodoPage(browser)
        page.enter_title("Diagnostic Test Todo")
        print("   ✓ Successfully entered title")

        # Click add button
        page.click_add_button()
        print("   ✓ Successfully clicked add button")

        # Wait and check for error
        time.sleep(3)

        error_after = browser.execute_script("""
            const errorEl = document.querySelector('.error-message');
            return errorEl ? errorEl.textContent : null;
        """)
        print(f"   Error after submit: {error_after}")

        todo_count_after = browser.execute_script("""
            const todos = document.querySelectorAll('.todo-item');
            return todos.length;
        """)
        print(f"   Todos after submit: {todo_count_after}")

    except Exception as e:
        print(f"   ✗ Error during manual creation: {e}")

    print("\n=== END DIAGNOSIS ===\n")
