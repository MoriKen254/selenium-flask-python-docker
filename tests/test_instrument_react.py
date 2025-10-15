"""Test that instruments React to see what's happening during form submission"""
import pytest
import time
from selenium.webdriver.common.by import By


def test_instrument_react_form_submission(browser):
    """Instrument React's handleCreateTodo to see what's happening"""

    # Wait for React to load
    time.sleep(2)

    # Instrument console.log to capture all logs
    browser.execute_script("""
        window.__CAPTURED_LOGS__ = [];
        const originalLog = console.log;
        const originalError = console.error;
        const originalWarn = console.warn;

        console.log = function(...args) {
            window.__CAPTURED_LOGS__.push({level: 'log', message: args.join(' ')});
            originalLog.apply(console, args);
        };
        console.error = function(...args) {
            window.__CAPTURED_LOGS__.push({level: 'error', message: args.join(' ')});
            originalError.apply(console, args);
        };
        console.warn = function(...args) {
            window.__CAPTURED_LOGS__.push({level: 'warn', message: args.join(' ')});
            originalWarn.apply(console, args);
        };

        console.log('[INSTRUMENTATION] Console capture installed');
    """)

    # Try to hook into React's fetch calls
    browser.execute_script("""
        const originalFetch = window.fetch;
        let fetchCallCount = 0;

        window.fetch = function(...args) {
            fetchCallCount++;
            console.log(`[FETCH ${fetchCallCount}] Called with URL: ${args[0]}`);
            if (args[1]) {
                console.log(`[FETCH ${fetchCallCount}] Method: ${args[1].method || 'GET'}`);
                console.log(`[FETCH ${fetchCallCount}] Headers: ${JSON.stringify(args[1].headers || {})}`);
                console.log(`[FETCH ${fetchCallCount}] Body: ${args[1].body || 'none'}`);
            }

            return originalFetch.apply(this, args)
                .then(response => {
                    console.log(`[FETCH ${fetchCallCount}] Response status: ${response.status} ${response.statusText}`);
                    console.log(`[FETCH ${fetchCallCount}] Response ok: ${response.ok}`);
                    return response;
                })
                .catch(error => {
                    console.error(`[FETCH ${fetchCallCount}] Error: ${error.toString()}`);
                    console.error(`[FETCH ${fetchCallCount}] Error name: ${error.name}`);
                    console.error(`[FETCH ${fetchCallCount}] Error message: ${error.message}`);
                    throw error;
                });
        };

        console.log('[INSTRUMENTATION] Fetch wrapper installed');
    """)

    print("\n[TEST] Instrumentation complete")

    # Now fill the form and submit
    print("[TEST] Filling form...")
    title_input = browser.find_element(By.CSS_SELECTOR, "input[placeholder='Todo title...']")
    title_input.clear()
    title_input.send_keys("Instrumented Test")

    print("[TEST] Clicking submit...")
    submit_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()

    # Wait for operation to complete
    time.sleep(3)

    # Get all captured logs
    logs = browser.execute_script("return window.__CAPTURED_LOGS__;")
    print(f"\n[CAPTURED LOGS] Total: {len(logs)}")
    for log in logs:
        print(f"  [{log['level'].upper()}] {log['message']}")

    # Check result
    todos = browser.find_elements(By.CSS_SELECTOR, ".todo-item")
    print(f"\n[TEST] Final todo count: {len(todos)}")

    try:
        error = browser.find_element(By.CSS_SELECTOR, ".error-message")
        print(f"[TEST] Error displayed: {error.text}")
    except:
        print("[TEST] No error displayed")

    # Assert we captured some fetch activity
    fetch_logs = [log for log in logs if 'FETCH' in log['message']]
    print(f"\n[TEST] Fetch-related logs: {len(fetch_logs)}")

    if len(todos) == 0:
        pytest.fail(f"Todo creation failed. See captured logs above.")
