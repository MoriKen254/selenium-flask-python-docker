"""Page Object Model for Todo List Application.

This module provides a Page Object Model implementation for the Todo List application.
It encapsulates all UI interactions and works seamlessly in both unit (mocked APIs) and
integration (real backend) testing modes.

The page object provides methods for:
    - Creating, reading, updating, and deleting todos
    - Verifying UI state and error messages
    - Waiting for dynamic content changes
    - Handling browser alerts and confirmations
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import List, Dict, Optional


class TodoPage:
    """Page Object for the Todo List main page.

    This class encapsulates all interactions with the todo list UI using the Page Object
    Model pattern. It provides high-level methods for test scenarios and handles element
    location, waiting, and error recovery automatically.

    Attributes:
        driver: Selenium WebDriver instance for browser control.
        wait: WebDriverWait instance with 10-second default timeout.
        TITLE_INPUT: Locator for todo title input field.
        DESCRIPTION_TEXTAREA: Locator for todo description textarea.
        ADD_BUTTON: Locator for add todo submit button.
        TODO_ITEMS: Locator for all todo item containers.
        TODO_TITLE: Locator for todo title text.
        TODO_DESCRIPTION: Locator for todo description text.
        TODO_CHECKBOX: Locator for completion checkbox.
        EDIT_BUTTON: Locator for edit button.
        DELETE_BUTTON: Locator for delete button.
        SAVE_BUTTON: Locator for save button in edit mode.
        CANCEL_BUTTON: Locator for cancel button in edit mode.
        ERROR_MESSAGE: Locator for error message display.
        LOADING_INDICATOR: Locator for loading indicator.
        EMPTY_STATE: Locator for empty state message.
        STATS: Locator for statistics display.
        COMPLETED_TODO: Locator for completed todo items.

    Example:
        >>> from selenium import webdriver
        >>> driver = webdriver.Firefox()
        >>> page = TodoPage(driver)
        >>> page.create_todo("Buy groceries", "Milk and eggs")
        >>> page.wait_for_todo_to_appear("Buy groceries")
        >>> todos = page.get_all_todos()
        >>> assert len(todos) == 1
    """

    # Locators
    TITLE_INPUT = (By.CSS_SELECTOR, "input[placeholder='Todo title...']")
    DESCRIPTION_TEXTAREA = (By.CSS_SELECTOR, "textarea[placeholder='Description (optional)...']")
    ADD_BUTTON = (By.CSS_SELECTOR, "button[type='submit'].btn-primary")
    TODO_ITEMS = (By.CSS_SELECTOR, ".todo-item")
    TODO_TITLE = (By.CSS_SELECTOR, ".todo-title")
    TODO_DESCRIPTION = (By.CSS_SELECTOR, ".todo-description")
    TODO_CHECKBOX = (By.CSS_SELECTOR, ".checkbox")
    EDIT_BUTTON = (By.CSS_SELECTOR, ".btn-edit")
    DELETE_BUTTON = (By.CSS_SELECTOR, ".btn-delete")
    SAVE_BUTTON = (By.CSS_SELECTOR, ".btn-success")
    CANCEL_BUTTON = (By.CSS_SELECTOR, ".btn-secondary")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".error-message")
    LOADING_INDICATOR = (By.CSS_SELECTOR, ".loading")
    EMPTY_STATE = (By.CSS_SELECTOR, ".empty-state")
    STATS = (By.CSS_SELECTOR, ".stats")
    COMPLETED_TODO = (By.CSS_SELECTOR, ".todo-item.completed")

    def __init__(self, driver):
        """Initialize the TodoPage with a WebDriver instance.

        Args:
            driver: Selenium WebDriver instance (Firefox, Chrome, etc.)
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # Navigation
    def wait_for_page_load(self, timeout=10):
        """Wait for the page to be fully loaded"""
        self.wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    # Input Actions
    def enter_title(self, title: str):
        """Enter todo title"""
        element = self.wait.until(EC.presence_of_element_located(self.TITLE_INPUT))
        element.clear()
        element.send_keys(title)

    def enter_description(self, description: str):
        """Enter todo description"""
        element = self.wait.until(EC.presence_of_element_located(self.DESCRIPTION_TEXTAREA))
        element.clear()
        element.send_keys(description)

    def click_add_button(self):
        """Click the Add Todo button"""
        button = self.wait.until(EC.element_to_be_clickable(self.ADD_BUTTON))
        button.click()

    def create_todo(self, title: str, description: str = ""):
        """
        Complete workflow to create a new todo
        Works in both unit and integration modes
        """
        self.enter_title(title)
        if description:
            self.enter_description(description)
        self.click_add_button()

        # Wait for todo to appear in list
        import time
        time.sleep(0.5)  # Allow for animation/rendering

    # Reading/Verification
    def get_all_todos(self) -> List[Dict]:
        """
        Get all todos displayed on the page
        Returns list of dicts with todo information
        """
        todos = []
        try:
            todo_elements = self.driver.find_elements(*self.TODO_ITEMS)

            for element in todo_elements:
                try:
                    title_el = element.find_element(*self.TODO_TITLE)
                    title = title_el.text

                    description = ""
                    try:
                        desc_el = element.find_element(*self.TODO_DESCRIPTION)
                        description = desc_el.text
                    except NoSuchElementException:
                        pass

                    is_completed = 'completed' in element.get_attribute('class')

                    todos.append({
                        'title': title,
                        'description': description,
                        'completed': is_completed,
                        'element': element
                    })
                except Exception as e:
                    print(f"Error parsing todo element: {e}")
                    continue

        except NoSuchElementException:
            pass

        return todos

    def get_todo_count(self) -> int:
        """Get the total number of todos"""
        return len(self.get_all_todos())

    def get_completed_count(self) -> int:
        """Get number of completed todos"""
        return len(self.driver.find_elements(*self.COMPLETED_TODO))

    def find_todo_by_title(self, title: str) -> Optional[Dict]:
        """Find a specific todo by its title"""
        todos = self.get_all_todos()
        for todo in todos:
            if todo['title'] == title:
                return todo
        return None

    def is_empty_state_displayed(self) -> bool:
        """Check if empty state message is shown"""
        try:
            self.driver.find_element(*self.EMPTY_STATE)
            return True
        except NoSuchElementException:
            return False

    # Update Actions
    def toggle_todo_completion(self, todo_title: str):
        """Toggle the completed status of a todo"""
        todo = self.find_todo_by_title(todo_title)
        if todo:
            checkbox = todo['element'].find_element(*self.TODO_CHECKBOX)
            checkbox.click()
            import time
            time.sleep(0.5)  # Wait for state update

    def edit_todo(self, old_title: str, new_title: str = None, new_description: str = None):
        """
        Edit a todo's title and/or description
        """
        todo = self.find_todo_by_title(old_title)
        if not todo:
            raise ValueError(f"Todo with title '{old_title}' not found")

        # Click edit button
        edit_btn = todo['element'].find_element(*self.EDIT_BUTTON)
        edit_btn.click()

        import time
        time.sleep(0.3)  # Wait for edit mode to activate

        # Update fields if provided
        if new_title is not None:
            title_input = todo['element'].find_element(By.CSS_SELECTOR, "input.input-field")
            title_input.clear()
            title_input.send_keys(new_title)

        if new_description is not None:
            desc_textarea = todo['element'].find_element(By.CSS_SELECTOR, "textarea.textarea-field")
            desc_textarea.clear()
            desc_textarea.send_keys(new_description)

        # Click save
        save_btn = todo['element'].find_element(*self.SAVE_BUTTON)
        save_btn.click()
        time.sleep(0.5)  # Wait for save to complete

    def delete_todo(self, todo_title: str):
        """Delete a todo (handles confirmation dialog)"""
        import time
        from selenium.common.exceptions import StaleElementReferenceException

        # Retry logic for stale elements
        max_retries = 3
        for attempt in range(max_retries):
            try:
                todo = self.find_todo_by_title(todo_title)
                if not todo:
                    raise ValueError(f"Todo with title '{todo_title}' not found")

                # Click delete button
                delete_btn = todo['element'].find_element(*self.DELETE_BUTTON)
                delete_btn.click()

                # Handle browser confirmation dialog
                time.sleep(0.3)  # Wait for alert to appear
                try:
                    alert = self.driver.switch_to.alert
                    alert.accept()
                    time.sleep(1)  # Wait longer for deletion to complete
                except:
                    # If no alert (or already handled), continue
                    pass

                # Successfully clicked and handled dialog, break retry loop
                break

            except StaleElementReferenceException:
                if attempt == max_retries - 1:
                    raise
                print(f"[DELETE] Stale element, retrying... (attempt {attempt + 1})")
                time.sleep(0.5)
                continue

    # Error Handling
    def is_error_displayed(self) -> bool:
        """Check if an error message is displayed"""
        try:
            self.driver.find_element(*self.ERROR_MESSAGE)
            return True
        except NoSuchElementException:
            return False

    def get_error_message(self) -> str:
        """Get the error message text"""
        try:
            error_el = self.driver.find_element(*self.ERROR_MESSAGE)
            return error_el.text
        except NoSuchElementException:
            return ""

    # Stats
    def get_stats(self) -> Dict[str, int]:
        """Get todo statistics (total, completed, pending)"""
        try:
            stats_el = self.driver.find_element(*self.STATS)
            stats_text = stats_el.text

            # Parse stats text (format: "Total: X Completed: Y Pending: Z")
            import re
            total_match = re.search(r'Total:\s*(\d+)', stats_text)
            completed_match = re.search(r'Completed:\s*(\d+)', stats_text)
            pending_match = re.search(r'Pending:\s*(\d+)', stats_text)

            return {
                'total': int(total_match.group(1)) if total_match else 0,
                'completed': int(completed_match.group(1)) if completed_match else 0,
                'pending': int(pending_match.group(1)) if pending_match else 0
            }
        except (NoSuchElementException, AttributeError):
            return {'total': 0, 'completed': 0, 'pending': 0}

    # Wait Helpers
    def wait_for_todo_count(self, expected_count: int, timeout: int = 5):
        """Wait until the todo count matches expected value"""
        WebDriverWait(self.driver, timeout).until(
            lambda d: self.get_todo_count() == expected_count,
            message=f"Expected {expected_count} todos, but condition not met"
        )

    def wait_for_todo_to_appear(self, title: str, timeout: int = 5):
        """Wait for a specific todo to appear"""
        WebDriverWait(self.driver, timeout).until(
            lambda d: self.find_todo_by_title(title) is not None,
            message=f"Todo with title '{title}' did not appear"
        )

    def wait_for_todo_to_disappear(self, title: str, timeout: int = 5):
        """Wait for a specific todo to be removed"""
        WebDriverWait(self.driver, timeout).until(
            lambda d: self.find_todo_by_title(title) is None,
            message=f"Todo with title '{title}' did not disappear"
        )
