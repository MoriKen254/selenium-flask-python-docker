"""Debug test to check why todo creation is failing"""
import pytest
from pages import TodoPage


def test_debug_create_todo_error(browser):
    """Debug what error occurs when creating a todo"""
    page = TodoPage(browser)
    page.wait_for_page_load()

    import time
    time.sleep(2)

    # Check initial state
    api_url = browser.execute_script("return window.__API_URL__;")
    print(f"\nAPI_URL: {api_url}")

    # Check if React has mounted
    has_react = browser.execute_script("return typeof window.React !== 'undefined';")
    print(f"Has React: {has_react}")

    has_root = browser.execute_script("return document.getElementById('root') !== null;")
    print(f"Has root element: {has_root}")

    root_content = browser.execute_script("return document.getElementById('root').innerHTML.length;")
    print(f"Root content length: {root_content}")

    # Check if axios is available
    has_axios = browser.execute_script("return typeof window.axios !== 'undefined';")
    print(f"Has axios: {has_axios}")

    # Check page title
    page_title = browser.execute_script("return document.querySelector('h1') ? document.querySelector('h1').textContent : null;")
    print(f"Page title: {page_title}")

    # Try manual axios POST to see what error we get
    manual_result = browser.execute_script("""
        return (async () => {
            try {
                const response = await window.axios.post(window.__API_URL__ + '/api/todos', {
                    title: 'Manual test',
                    description: ''
                });
                return {success: true, status: response.status, data: response.data};
            } catch (error) {
                return {
                    success: false,
                    message: error.message,
                    code: error.code,
                    response: error.response ? {
                        status: error.response.status,
                        data: error.response.data
                    } : null
                };
            }
        })();
    """)
    print(f"Manual axios POST result: {manual_result}")

    # Try to create a todo using the form
    page.enter_title("Test Todo")
    page.click_add_button()

    # Wait a bit for the request to complete
    time.sleep(2)

    # Check for error message
    error_msg = browser.execute_script("""
        var errorEl = document.querySelector('.error-message');
        return errorEl ? errorEl.textContent : null;
    """)
    print(f"Error message: {error_msg}")

    # Check console errors (if captured)
    console_errors = browser.execute_script("""
        if (window.__CAPTURED_CONSOLE_LOGS__) {
            return window.__CAPTURED_CONSOLE_LOGS__.filter(log => log.level === 'error');
        }
        return [];
    """)
    print(f"Console errors: {console_errors}")

    # Check if todo was created
    todos = page.get_all_todos()
    print(f"Todos after create attempt: {len(todos)}")
    for todo in todos:
        print(f"  - {todo['title']}")
