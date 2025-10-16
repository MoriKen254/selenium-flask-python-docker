"""Check React app state"""
import pytest
import time
from pages.todo_page import TodoPage


def test_check_react_state(browser):
    """Check what React actually has in state"""
    page = TodoPage(browser)
    page.wait_for_page_load()

    # Wait a bit longer
    time.sleep(3)

    # Check what the page shows
    print("\n=== Checking page state ===")

    # Check for empty state message
    try:
        empty_msg = browser.find_element('css selector', '.empty-state')
        print(f"Empty state message found: {empty_msg.text}")
    except:
        print("No empty state message")

    # Check for loading message
    try:
        loading_msg = browser.find_element('css selector', '.loading')
        print(f"Loading message found: {loading_msg.text}")
    except:
        print("No loading message")

    # Check for error message
    try:
        error_msg = browser.find_element('css selector', '.error-message')
        print(f"Error message found: {error_msg.text}")
    except:
        print("No error message")

    # Check todo items
    try:
        items = browser.find_elements('css selector', '.todo-item')
        print(f"Todo items found: {len(items)}")
        for item in items:
            print(f"  - {item.text[:100]}")
    except Exception as e:
        print(f"Error finding todo items: {e}")

    # Try to get React state directly
    react_state = browser.execute_script("""
        // Try to find React root and get state
        const root = document.querySelector('#root');
        if (root && root._reactRootContainer) {
            return 'React root found';
        }
        return 'No React root';
    """)
    print(f"React state check: {react_state}")

    # Manually refresh to trigger a new fetch
    print("\n=== Manually triggering page refresh ===")
    browser.refresh()
    time.sleep(3)

    # Check again
    todos_after = page.get_all_todos()
    print(f"Todos after refresh: {len(todos_after)}")

    assert True  # Just for debugging
