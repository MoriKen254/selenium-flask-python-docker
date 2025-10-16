"""Check if there's any persisted state affecting fetch"""
import pytest


def test_check_storage_and_globals(browser):
    """Check storage and global state"""
    import time
    time.sleep(2)

    result = browser.execute_script("""
        return {
            sessionStorage: {
                __MOCK_TODOS__: sessionStorage.getItem('__MOCK_TODOS__'),
                __MOCK_NEXT_ID__: sessionStorage.getItem('__MOCK_NEXT_ID__'),
                length: sessionStorage.length,
                keys: Object.keys(sessionStorage)
            },
            localStorage: {
                length: localStorage.length,
                keys: Object.keys(localStorage)
            },
            globals: {
                __API_MOCKING_ENABLED__: window.__API_MOCKING_ENABLED__,
                __ENABLE_API_MOCKING__: window.__ENABLE_API_MOCKING__,
                __TEST_API__: typeof window.__TEST_API__,
                __MOCK_TODOS__: typeof window.__MOCK_TODOS__
            },
            fetchType: typeof window.fetch,
            xhrType: typeof window.XMLHttpRequest,
            fetchToString: window.fetch.toString().substring(0, 200)
        };
    """)

    print(f"\nStorage and globals: {result}")
