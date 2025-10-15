"""
Pytest configuration and shared fixtures
Handles Selenium WebDriver setup with mode-aware API mocking
"""
import pytest
import os
import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from pathlib import Path

from config import TestConfig, is_unit_mode


@pytest.fixture(scope='session', autouse=True)
def print_test_config():
    """Print test configuration at the start of test session"""
    TestConfig.print_config()


@pytest.fixture(scope='function', autouse=True)
def clean_database():
    """
    Clean database before each test in integration mode
    This ensures each test starts with a clean slate
    """
    if TestConfig.is_integration_mode():
        try:
            conn = psycopg2.connect(
                host=TestConfig.DB_HOST,
                port=TestConfig.DB_PORT,
                dbname=TestConfig.DB_NAME,
                user=TestConfig.DB_USER,
                password=TestConfig.DB_PASSWORD
            )
            cursor = conn.cursor()
            cursor.execute("TRUNCATE TABLE todos RESTART IDENTITY CASCADE;")
            conn.commit()
            cursor.close()
            conn.close()
            print("[TEST] Database cleaned before test")
        except Exception as e:
            print(f"[TEST] Warning: Could not clean database: {e}")

    yield


@pytest.fixture(scope='function')
def driver(request):
    """
    Selenium WebDriver fixture with automatic API mocking for unit tests
    Automatically injects API interceptor when TEST_MODE=unit
    """
    # Setup WebDriver based on browser configuration
    if TestConfig.BROWSER == 'chrome':
        options = ChromeOptions()
        if TestConfig.HEADLESS:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        # Reduce resource usage to prevent hangs
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-sync')

        # Get chromedriver path and ensure we use the actual binary, not THIRD_PARTY_NOTICES
        driver_path = ChromeDriverManager().install()

        # Fix for webdriver-manager returning wrong file from chrome-for-testing structure
        if 'THIRD_PARTY_NOTICES' in driver_path or not driver_path.endswith('chromedriver'):
            import glob
            from pathlib import Path
            driver_dir = Path(driver_path).parent
            # Look for the actual chromedriver binary in the directory
            potential_drivers = list(driver_dir.glob('**/chromedriver')) + list(driver_dir.glob('**/chromedriver.exe'))
            if potential_drivers:
                driver_path = str(potential_drivers[0])

        # Ensure the binary has execute permissions
        import stat
        current_permissions = os.stat(driver_path).st_mode
        os.chmod(driver_path, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        service = ChromeService(driver_path)
        web_driver = webdriver.Chrome(service=service, options=options)

    elif TestConfig.BROWSER == 'firefox':
        options = FirefoxOptions()
        if TestConfig.HEADLESS:
            options.add_argument('--headless')
        options.add_argument('--width=1920')
        options.add_argument('--height=1080')

        # Use pre-installed geckodriver if available, otherwise use webdriver-manager
        geckodriver_path = '/usr/local/bin/geckodriver'
        if os.path.exists(geckodriver_path):
            service = FirefoxService(geckodriver_path)
        else:
            service = FirefoxService(GeckoDriverManager().install())
        web_driver = webdriver.Firefox(service=service, options=options)

    else:
        raise ValueError(f"Unsupported browser: {TestConfig.BROWSER}")

    # Configure timeouts
    web_driver.implicitly_wait(TestConfig.IMPLICIT_WAIT)
    web_driver.set_page_load_timeout(TestConfig.PAGE_LOAD_TIMEOUT)

    # Store test info for screenshot naming
    web_driver.test_name = request.node.name

    yield web_driver

    # Teardown: Take screenshot on failure if configured
    if request.node.rep_call.failed if hasattr(request.node, 'rep_call') else False:
        if TestConfig.SCREENSHOT_ON_FAILURE:
            take_screenshot(web_driver, request.node.name)

    web_driver.quit()


@pytest.fixture(scope='function')
def browser(driver):
    """
    Enhanced browser fixture that automatically handles API mocking
    This is the main fixture tests should use
    """
    if is_unit_mode():
        print("[TEST] Running in UNIT mode - API interceptor will load from index.html")

        # Navigate to frontend with ?mock=true parameter
        # This triggers the interceptor to load BEFORE React initializes
        mock_url = f"{TestConfig.FRONTEND_URL}?mock=true"
        driver.get(mock_url)

        # Wait for page and interceptor to load
        import time
        time.sleep(1)

        # Verify interceptor loaded
        is_loaded = driver.execute_script("return window.__API_MOCKING_ENABLED__ === true;")
        if is_loaded:
            print("[TEST] API interceptor loaded successfully")
        else:
            print("[TEST] WARNING: API interceptor did not load!")

        # Wait for React to mount and fetch data (will be intercepted)
        time.sleep(0.5)

    else:
        print("[TEST] Running in INTEGRATION mode - using real backend")
        driver.get(TestConfig.FRONTEND_URL)

        # Wait for React to mount and make initial fetch
        import time
        time.sleep(2)

    return driver


def inject_api_interceptor(driver):
    """
    Inject the API interceptor JavaScript into the page
    Only called when TEST_MODE=unit
    """
    interceptor_path = Path(__file__).parent / 'mocks' / 'api_interceptor.js'

    with open(interceptor_path, 'r') as f:
        interceptor_js = f.read()

    # Set mock delay from config
    driver.execute_script(f"window.__MOCK_DELAY__ = {TestConfig.MOCK_DELAY_MS};")

    # Inject the interceptor
    driver.execute_script(interceptor_js)

    # Verify injection
    is_enabled = driver.execute_script("return window.__API_MOCKING_ENABLED__ === true;")
    assert is_enabled, "API interceptor failed to initialize"


@pytest.fixture(scope='function')
def mock_api(browser):
    """
    Fixture providing access to mock API controls (only in unit mode)
    Allows tests to manipulate mock data programmatically
    """
    if not is_unit_mode():
        pytest.skip("mock_api fixture only available in unit mode")

    class MockAPI:
        def __init__(self, driver):
            self.driver = driver

        def reset_data(self):
            """Reset mock data to default state"""
            self.driver.execute_script("window.__TEST_API__.resetMockData();")

        def set_todos(self, todos):
            """Set specific mock todo data"""
            import json
            todos_json = json.dumps(todos)
            self.driver.execute_script(f"window.__TEST_API__.setMockData({todos_json});")

        def get_todos(self):
            """Get current mock todo data"""
            return self.driver.execute_script("return window.__TEST_API__.getMockData();")

        def add_todo(self, todo):
            """Add a todo to mock data"""
            import json
            todo_json = json.dumps(todo)
            return self.driver.execute_script(f"return window.__TEST_API__.addMockTodo({todo_json});")

    return MockAPI(browser)


def take_screenshot(driver, test_name):
    """Take a screenshot and save it with the test name"""
    screenshots_dir = Path(TestConfig.SCREENSHOTS_DIR)
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    # Clean test name for filename
    safe_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in test_name)
    screenshot_path = screenshots_dir / f"{safe_name}.png"

    try:
        driver.save_screenshot(str(screenshot_path))
        print(f"\n[SCREENSHOT] Saved to: {screenshot_path}")
    except Exception as e:
        print(f"\n[SCREENSHOT] Failed to save screenshot: {e}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to store test result in the item for access in fixtures
    Used for conditional screenshot capture
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(scope='function')
def wait_for_page_load(browser):
    """Helper fixture to wait for page to be fully loaded"""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    def _wait(timeout=10):
        WebDriverWait(browser, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    return _wait
