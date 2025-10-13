"""
Todo CRUD Test Suite
These tests work in BOTH unit and integration modes without code duplication

Run in UNIT mode (stubbed APIs):
    TEST_MODE=unit pytest tests/test_todo_crud.py

Run in INTEGRATION mode (real backend):
    TEST_MODE=integration pytest tests/test_todo_crud.py
"""
import pytest
from pages import TodoPage
from config import is_unit_mode, is_integration_mode


class TestTodoCreation:
    """Tests for creating new todos"""

    def test_create_todo_with_title_only(self, browser):
        """
        Test creating a todo with just a title
        Works in both unit and integration modes
        """
        page = TodoPage(browser)
        page.wait_for_page_load()

        # Create a new todo
        page.create_todo("Buy groceries")

        # Verify todo appears in the list
        page.wait_for_todo_to_appear("Buy groceries")
        todo = page.find_todo_by_title("Buy groceries")

        assert todo is not None, "Todo should be created"
        assert todo['title'] == "Buy groceries"
        assert todo['completed'] is False

    def test_create_todo_with_title_and_description(self, browser):
        """Test creating a todo with title and description"""
        page = TodoPage(browser)
        page.wait_for_page_load()

        # Create todo with description
        page.create_todo("Finish project", "Complete the testing implementation")

        # Verify
        page.wait_for_todo_to_appear("Finish project")
        todo = page.find_todo_by_title("Finish project")

        assert todo is not None
        assert todo['title'] == "Finish project"
        assert todo['description'] == "Complete the testing implementation"
        assert todo['completed'] is False

    def test_create_multiple_todos(self, browser):
        """Test creating multiple todos in sequence"""
        page = TodoPage(browser)
        page.wait_for_page_load()

        # Create multiple todos
        todos_to_create = [
            ("Task 1", "First task"),
            ("Task 2", "Second task"),
            ("Task 3", "Third task")
        ]

        for title, desc in todos_to_create:
            page.create_todo(title, desc)

        # Verify all todos exist
        page.wait_for_todo_count(len(todos_to_create))

        for title, _ in todos_to_create:
            todo = page.find_todo_by_title(title)
            assert todo is not None, f"Todo '{title}' should exist"

    def test_todo_count_updates_after_creation(self, browser):
        """Test that stats update correctly after creating todos"""
        page = TodoPage(browser)
        page.wait_for_page_load()

        # Create a todo
        page.create_todo("Test todo")
        page.wait_for_todo_to_appear("Test todo")

        # Verify stats
        stats = page.get_stats()
        assert stats['total'] >= 1, "Total count should include new todo"
        assert stats['pending'] >= 1, "Pending count should include new todo"


class TestTodoReading:
    """Tests for reading/viewing todos"""

    def test_empty_state_when_no_todos(self, browser, mock_api):
        """
        Test empty state display
        Note: Uses mock_api fixture to ensure clean state in unit mode
        """
        if is_unit_mode():
            mock_api.set_todos([])  # Clear all todos in unit mode

        page = TodoPage(browser)
        page.wait_for_page_load()

        # In integration mode, we might need to delete existing todos
        if is_integration_mode():
            todos = page.get_all_todos()
            for todo in todos:
                page.delete_todo(todo['title'])

        # Verify empty state
        assert page.is_empty_state_displayed(), "Empty state should be shown"
        assert page.get_todo_count() == 0

    def test_display_existing_todos(self, browser):
        """Test that existing todos are displayed"""
        page = TodoPage(browser)
        page.wait_for_page_load()

        # Get all todos
        todos = page.get_all_todos()

        # In unit mode, we should have mock data
        # In integration mode, depends on database state
        if is_unit_mode():
            assert len(todos) >= 2, "Mock data should include default todos"

    def test_stats_display_correctly(self, browser):
        """Test that statistics are calculated and displayed correctly"""
        page = TodoPage(browser)
        page.wait_for_page_load()

        # Create some todos
        page.create_todo("Todo 1")
        page.wait_for_todo_to_appear("Todo 1")

        page.create_todo("Todo 2")
        page.wait_for_todo_to_appear("Todo 2")

        # Mark one as completed
        page.toggle_todo_completion("Todo 1")

        # Verify stats
        stats = page.get_stats()
        assert stats['total'] >= 2
        assert stats['completed'] >= 1
        assert stats['pending'] >= 1


class TestTodoUpdate:
    """Tests for updating todos"""

    def test_toggle_todo_completion(self, browser):
        """Test marking a todo as complete/incomplete"""
        page = TodoPage(browser)
        page.wait_for_page_load()

        # Create a todo
        page.create_todo("Task to complete")
        page.wait_for_todo_to_appear("Task to complete")

        # Verify initially not completed
        todo = page.find_todo_by_title("Task to complete")
        assert todo['completed'] is False

        # Toggle completion
        page.toggle_todo_completion("Task to complete")

        # Verify now completed
        import time
        time.sleep(0.5)
        todo = page.find_todo_by_title("Task to complete")
        assert todo['completed'] is True

        # Toggle back
        page.toggle_todo_completion("Task to complete")
        time.sleep(0.5)
        todo = page.find_todo_by_title("Task to complete")
        assert todo['completed'] is False

    def test_edit_todo_title(self, browser):
        """Test editing a todo's title"""
        page = TodoPage(browser)
        page.wait_for_page_load()

        # Create a todo
        original_title = "Original title"
        page.create_todo(original_title)
        page.wait_for_todo_to_appear(original_title)

        # Edit the title
        new_title = "Updated title"
        page.edit_todo(original_title, new_title=new_title)

        # Verify changes
        page.wait_for_todo_to_appear(new_title)
        assert page.find_todo_by_title(new_title) is not None
        assert page.find_todo_by_title(original_title) is None

    def test_edit_todo_description(self, browser):
        """Test editing a todo's description"""
        page = TodoPage(browser)
        page.wait_for_page_load()

        # Create a todo
        page.create_todo("Task", "Original description")
        page.wait_for_todo_to_appear("Task")

        # Edit description
        page.edit_todo("Task", new_description="Updated description")

        # Verify
        import time
        time.sleep(0.5)
        todo = page.find_todo_by_title("Task")
        assert todo['description'] == "Updated description"


class TestTodoDelete:
    """Tests for deleting todos"""

    def test_delete_single_todo(self, browser):
        """Test deleting a single todo"""
        page = TodoPage(browser)
        page.wait_for_page_load()

        # Create a todo
        page.create_todo("Todo to delete")
        page.wait_for_todo_to_appear("Todo to delete")

        # Delete it
        page.delete_todo("Todo to delete")

        # Verify it's gone
        page.wait_for_todo_to_disappear("Todo to delete")
        assert page.find_todo_by_title("Todo to delete") is None

    def test_delete_multiple_todos(self, browser):
        """Test deleting multiple todos"""
        page = TodoPage(browser)
        page.wait_for_page_load()

        # Create multiple todos
        todos = ["Delete 1", "Delete 2", "Delete 3"]
        for title in todos:
            page.create_todo(title)
            page.wait_for_todo_to_appear(title)

        # Delete all
        for title in todos:
            page.delete_todo(title)
            page.wait_for_todo_to_disappear(title)

        # Verify all gone
        for title in todos:
            assert page.find_todo_by_title(title) is None


class TestTodoWorkflows:
    """End-to-end workflow tests"""

    def test_complete_todo_workflow(self, browser):
        """Test a complete create-edit-complete-delete workflow"""
        page = TodoPage(browser)
        page.wait_for_page_load()

        # Step 1: Create
        page.create_todo("Workflow test", "Test the complete workflow")
        page.wait_for_todo_to_appear("Workflow test")

        # Step 2: Edit
        page.edit_todo("Workflow test", new_title="Workflow test - edited")
        page.wait_for_todo_to_appear("Workflow test - edited")

        # Step 3: Mark as complete
        page.toggle_todo_completion("Workflow test - edited")
        import time
        time.sleep(0.5)
        todo = page.find_todo_by_title("Workflow test - edited")
        assert todo['completed'] is True

        # Step 4: Delete
        page.delete_todo("Workflow test - edited")
        page.wait_for_todo_to_disappear("Workflow test - edited")

    def test_multiple_users_scenario(self, browser):
        """
        Test scenario simulating multiple users adding todos
        (simulated by sequential adds in test)
        """
        page = TodoPage(browser)
        page.wait_for_page_load()

        initial_count = page.get_todo_count()

        # "User 1" adds todos
        page.create_todo("User 1 - Task A")
        page.create_todo("User 1 - Task B")

        # "User 2" adds todos
        page.create_todo("User 2 - Task A")
        page.create_todo("User 2 - Task B")

        # Verify all added
        expected_count = initial_count + 4
        page.wait_for_todo_count(expected_count)
        assert page.get_todo_count() == expected_count


@pytest.mark.skipif(is_unit_mode(), reason="Integration-only test")
class TestIntegrationSpecific:
    """
    Tests that only run in integration mode
    These test backend-specific behavior
    """

    def test_data_persists_after_page_refresh(self, browser):
        """Test that todos persist after refreshing the page"""
        page = TodoPage(browser)
        page.wait_for_page_load()

        # Create a todo
        page.create_todo("Persistence test")
        page.wait_for_todo_to_appear("Persistence test")

        # Refresh page
        browser.refresh()
        page.wait_for_page_load()

        # Verify todo still exists
        assert page.find_todo_by_title("Persistence test") is not None


@pytest.mark.skipif(is_integration_mode(), reason="Unit-only test")
class TestUnitSpecific:
    """
    Tests that only run in unit mode
    These test mock-specific functionality
    """

    def test_mock_data_manipulation(self, browser, mock_api):
        """Test manipulating mock data programmatically"""
        page = TodoPage(browser)

        # Set specific mock data
        custom_todos = [
            {
                "id": 999,
                "title": "Custom mock todo",
                "description": "Set via mock API",
                "completed": False
            }
        ]
        mock_api.set_todos(custom_todos)

        # Reload to see new data
        browser.refresh()
        page.wait_for_page_load()

        # Verify custom todo appears
        todo = page.find_todo_by_title("Custom mock todo")
        assert todo is not None
        assert todo['description'] == "Set via mock API"
