"""
Test Configuration Management System
Handles switching between UNIT (stubbed) and INTEGRATION (real backend) test modes
"""
import os
from enum import Enum
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


class TestMode(Enum):
    """Test execution modes"""
    UNIT = "unit"           # Stubbed API calls, no backend required
    INTEGRATION = "integration"  # Real API calls, full system required


class TestConfig:
    """
    Central configuration for test execution
    Supports environment variable overrides and programmatic configuration
    """

    # Test Mode Configuration
    MODE = TestMode(os.getenv('TEST_MODE', 'unit'))

    # Frontend URLs
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

    # Backend API URLs
    # In UNIT mode, this is ignored; in INTEGRATION mode, this is used
    BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')

    # Selenium Configuration
    BROWSER = os.getenv('BROWSER', 'chrome').lower()
    HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
    IMPLICIT_WAIT = int(os.getenv('IMPLICIT_WAIT', '10'))
    PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))

    # Test Execution Configuration
    SCREENSHOT_ON_FAILURE = os.getenv('SCREENSHOT_ON_FAILURE', 'true').lower() == 'true'
    SCREENSHOTS_DIR = os.getenv('SCREENSHOTS_DIR', './test_screenshots')
    TEST_DATA_DIR = os.getenv('TEST_DATA_DIR', './tests/data')

    # Mock/Stub Configuration
    MOCK_DELAY_MS = int(os.getenv('MOCK_DELAY_MS', '100'))  # Simulate network latency
    ENABLE_REQUEST_LOGGING = os.getenv('ENABLE_REQUEST_LOGGING', 'true').lower() == 'true'

    @classmethod
    def is_unit_mode(cls) -> bool:
        """Check if running in unit test mode (stubbed APIs)"""
        return cls.MODE == TestMode.UNIT

    @classmethod
    def is_integration_mode(cls) -> bool:
        """Check if running in integration test mode (real APIs)"""
        return cls.MODE == TestMode.INTEGRATION

    @classmethod
    def get_api_url(cls, endpoint: str) -> str:
        """
        Get the appropriate API URL based on test mode
        In UNIT mode, this returns a placeholder (APIs are intercepted)
        In INTEGRATION mode, this returns the real backend URL
        """
        if cls.is_integration_mode():
            return f"{cls.BACKEND_URL}{endpoint}"
        else:
            # In unit mode, we return the endpoint pattern
            # The actual interception happens in the browser
            return endpoint

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary for logging/debugging"""
        return {
            'mode': cls.MODE.value,
            'frontend_url': cls.FRONTEND_URL,
            'backend_url': cls.BACKEND_URL if cls.is_integration_mode() else 'STUBBED',
            'browser': cls.BROWSER,
            'headless': cls.HEADLESS,
        }

    @classmethod
    def set_mode(cls, mode: str):
        """Programmatically set test mode (useful for test fixtures)"""
        cls.MODE = TestMode(mode.lower())

    @classmethod
    def print_config(cls):
        """Print current configuration for debugging"""
        print("=" * 50)
        print("TEST CONFIGURATION")
        print("=" * 50)
        for key, value in cls.to_dict().items():
            print(f"{key.upper()}: {value}")
        print("=" * 50)


# Convenience functions
def is_unit_mode() -> bool:
    """Global helper to check if in unit test mode"""
    return TestConfig.is_unit_mode()


def is_integration_mode() -> bool:
    """Global helper to check if in integration test mode"""
    return TestConfig.is_integration_mode()
