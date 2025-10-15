"""Test to check if React state is being updated when Selenium types"""
import pytest
import time
from selenium.webdriver.common.by import By


def test_check_react_state_on_input(browser):
    """Check if React state updates when Selenium types into controlled inputs"""

    # Find the title input
    title_input = browser.find_element(By.CSS_SELECTOR, "input[placeholder='Todo title...']")

    print("\n[TEST] Initial state:")
    # Check initial React state
    react_state = browser.execute_script("""
        // Try to access React's internal state via the input element
        const input = document.querySelector("input[placeholder='Todo title...']");
        return {
            domValue: input.value,
            placeholder: input.placeholder
        };
    """)
    print(f"  DOM value: '{react_state['domValue']}'")

    # Type using Selenium
    print("\n[TEST] Typing 'Test Todo' using Selenium...")
    title_input.clear()
    title_input.send_keys("Test Todo")

    # Check state after typing
    time.sleep(0.5)
    state_after = browser.execute_script("""
        const input = document.querySelector("input[placeholder='Todo title...']");
        return {
            domValue: input.value
        };
    """)
    print(f"  DOM value after typing: '{state_after['domValue']}'")

    # Now try to trigger the onChange event manually
    print("\n[TEST] Manually triggering input and change events...")
    browser.execute_script("""
        const input = document.querySelector("input[placeholder='Todo title...']");

        // Create and dispatch input event (React listens to this)
        const inputEvent = new Event('input', { bubbles: true });
        input.dispatchEvent(inputEvent);

        // Also dispatch change event
        const changeEvent = new Event('change', { bubbles: true });
        input.dispatchEvent(changeEvent);
    """)

    time.sleep(0.5)

    # Check if form can be submitted
    print("\n[TEST] Attempting to submit form...")
    submit_result = browser.execute_script("""
        const form = document.querySelector('form');
        const button = form.querySelector('button[type="submit"]');

        // Check if button is disabled
        const isDisabled = button.disabled;

        // Try to trigger form submission programmatically
        const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
        form.dispatchEvent(submitEvent);

        return {
            buttonDisabled: isDisabled,
            buttonText: button.textContent,
            formExists: !!form
        };
    """)
    print(f"  Button disabled: {submit_result['buttonDisabled']}")
    print(f"  Button text: {submit_result['buttonText']}")
    print(f"  Form exists: {submit_result['formExists']}")

    # Wait and check if todo was created
    time.sleep(2)

    # Check for any network requests
    todos = browser.find_elements(By.CSS_SELECTOR, ".todo-item")
    print(f"\n[TEST] Todos on page: {len(todos)}")

    # Check for error
    try:
        error = browser.find_element(By.CSS_SELECTOR, ".error-message")
        print(f"[TEST] Error displayed: {error.text}")
    except:
        print("[TEST] No error displayed")

    print("\n[TEST] Now trying with proper React event simulation...")
    # Clear and try with React-compatible events
    browser.execute_script("""
        const input = document.querySelector("input[placeholder='Todo title...']");
        input.value = 'React Event Test';

        // Trigger React's synthetic event
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        nativeInputValueSetter.call(input, 'React Event Test');

        const inputEvent = new Event('input', { bubbles: true});
        input.dispatchEvent(inputEvent);
    """)

    time.sleep(0.5)

    # Now click submit
    submit_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()

    time.sleep(2)

    # Check result
    todos = browser.find_elements(By.CSS_SELECTOR, ".todo-item")
    print(f"[TEST] Todos after React event: {len(todos)}")

    try:
        error = browser.find_element(By.CSS_SELECTOR, ".error-message")
        print(f"[TEST] Error: {error.text}")
    except:
        print("[TEST] No error - success!")
