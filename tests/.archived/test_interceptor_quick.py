"""Quick test to verify API interceptor works"""
import pytest
from pages.todo_page import TodoPage
from config import is_unit_mode

pytestmark = pytest.mark.skipif(not is_unit_mode(), reason="Only runs in unit mode")


def test_interceptor_loads_mock_data(browser):
    """Verify that mock data loads successfully in unit mode"""
    page = TodoPage(browser)
    page.wait_for_page_load()

    # In unit mode, we should see mock todos
    todos = page.get_all_todos()
    print(f"Found {len(todos)} todos")
    for todo in todos:
        print(f"  - {todo['title']}: {todo['completed']}")

    # Should have 2 default mock todos
    assert len(todos) >= 2, f"Expected at least 2 mock todos, found {len(todos)}"


def test_can_create_todo(browser):
    """Verify we can create a todo in unit mode"""
    page = TodoPage(browser)
    page.wait_for_page_load()

    initial_count = page.get_todo_count()
    print(f"Initial todo count: {initial_count}")

    # Create a todo
    page.create_todo("Test Todo", "Test Description")
    page.wait_for_todo_to_appear("Test Todo")

    # Verify it was created
    todo = page.find_todo_by_title("Test Todo")
    assert todo is not None, "Todo was not created"
    assert todo['title'] == "Test Todo"
    assert todo['description'] == "Test Description"
    assert todo['completed'] is False

    # Verify count increased
    new_count = page.get_todo_count()
    assert new_count == initial_count + 1, f"Expected {initial_count + 1} todos, found {new_count}"
