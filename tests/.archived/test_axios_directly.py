"""Test axios directly by triggering React's axios"""
import pytest
from pages import TodoPage


def test_trigger_react_fetch_todos(browser):
    """Try to trigger React's fetchTodos method"""
    import time

    page = TodoPage(browser)
    page.wait_for_page_load()
    time.sleep(3)

    # Check if there's an initial error
    initial_error = browser.execute_script("""
        const errorEl = document.querySelector('.error-message');
        return errorEl ? errorEl.textContent : null;
    """)
    print(f"\nInitial error on page: {initial_error}")

    # Check how many todos are displayed
    todo_count = browser.execute_script("""
        return document.querySelectorAll('.todo-item').length;
    """)
    print(f"Initial todo count: {todo_count}")

    # Try to manually trigger a refresh by clicking a button or similar
    # Since the page shows an error, React's useEffect must have tried and failed

    # Let's check the exact axios error by hooking into console.error before the app loads
    # Actually, the app is already loaded. Let's try to access React's internal state

    # Try to force a re-fetch by manipulating the page
    browser.refresh()
    page.wait_for_page_load()
    time.sleep(3)

    after_refresh_error = browser.execute_script("""
        const errorEl = document.querySelector('.error-message');
        return errorEl ? errorEl.textContent : null;
    """)
    print(f"Error after refresh: {after_refresh_error}")

    todo_count_after = browser.execute_script("""
        return document.querySelectorAll('.todo-item').length;
    """)
    print(f"Todo count after refresh: {todo_count_after}")
