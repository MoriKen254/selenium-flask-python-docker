"""Test to diagnose todo creation issues"""
import pytest
import time
from pages.todo_page import TodoPage


def test_diagnose_create_todo_issue(browser):
    """Diagnose why create todo is failing in integration tests"""
    page = TodoPage(browser)

    # Check initial state
    api_url = browser.execute_script("return window.__API_URL__;")
    print(f"\n[DIAGNOSIS] API_URL: {api_url}")

    # Check if backend is reachable from browser
    backend_health = browser.execute_async_script("""
        var callback = arguments[arguments.length - 1];
        fetch(arguments[0] + '/health')
            .then(response => response.json())
            .then(data => callback({success: true, data: data}))
            .catch(error => callback({success: false, error: error.toString()}));
    """, api_url)
    print(f"[DIAGNOSIS] Backend health check: {backend_health}")

    # Try to create a todo via JavaScript and capture detailed error
    result = browser.execute_async_script("""
        var callback = arguments[arguments.length - 1];
        var apiUrl = arguments[0];
        var todoData = {title: 'Diagnostic Test', description: 'Testing todo creation'};

        fetch(apiUrl + '/api/todos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(todoData)
        })
        .then(response => {
            console.log('[DIAGNOSIS] Response status:', response.status);
            console.log('[DIAGNOSIS] Response headers:', Array.from(response.headers.entries()));
            return response.json().then(data => ({
                success: response.ok,
                status: response.status,
                data: data
            }));
        })
        .catch(error => {
            console.error('[DIAGNOSIS] Fetch error:', error);
            return {
                success: false,
                error: error.toString(),
                message: error.message
            };
        })
        .then(result => callback(result));
    """, api_url)

    print(f"\n[DIAGNOSIS] Create todo result: {result}")

    if result.get('success'):
        print(f"[DIAGNOSIS] SUCCESS - Todo created: {result.get('data')}")
    else:
        print(f"[DIAGNOSIS] FAILURE - Error: {result.get('error')}")
        print(f"[DIAGNOSIS] Status: {result.get('status')}")
        print(f"[DIAGNOSIS] Message: {result.get('message')}")

    # Now try using the page object's create method
    print("\n[DIAGNOSIS] Now trying with page.create_todo()...")
    page.create_todo("Test via Page Object", "Testing")

    # Wait a bit
    time.sleep(2)

    # Check if error message appeared
    try:
        error_elem = browser.find_element("css selector", ".error-message")
        error_text = error_elem.text
        print(f"[DIAGNOSIS] Error message displayed: {error_text}")
    except:
        print("[DIAGNOSIS] No error message displayed")

    # Check if todo appeared
    todos = page.get_all_todos()
    print(f"[DIAGNOSIS] Todos on page: {len(todos)}")
    for todo in todos:
        print(f"  - {todo}")

    # Get console logs if possible
    try:
        logs = browser.get_log('browser')
        print("\n[DIAGNOSIS] Browser console logs:")
        for log in logs:
            print(f"  [{log['level']}] {log['message']}")
    except:
        print("[DIAGNOSIS] Cannot retrieve browser logs (Firefox doesn't support this)")

    # Check React error state
    react_error = browser.execute_script("return document.querySelector('.error-message')?.textContent;")
    print(f"\n[DIAGNOSIS] React error state: {react_error}")

    # If failed, don't assert - just report
    if not result.get('success'):
        pytest.fail(f"Todo creation failed: {result}")
