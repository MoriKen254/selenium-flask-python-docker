"""Check what scripts are actually loaded on the page"""
import pytest


def test_check_loaded_scripts(browser):
    """Check all scripts loaded on the page"""
    import time
    time.sleep(2)

    scripts = browser.execute_script("""
        const scripts = Array.from(document.querySelectorAll('script'));
        return scripts.map(s => ({
            src: s.src || 'inline',
            content: s.src ? null : s.textContent.substring(0, 100)
        }));
    """)

    print("\n=== Scripts Loaded ===")
    for i, script in enumerate(scripts):
        print(f"{i+1}. {script}")

    # Check if interceptor was loaded
    has_interceptor = any('interceptor' in str(s.get('src', '')) for s in scripts)
    print(f"\nHas interceptor script: {has_interceptor}")

    # Check if mocking is enabled
    mocking_enabled = browser.execute_script("return window.__API_MOCKING_ENABLED__ === true;")
    print(f"__API_MOCKING_ENABLED__: {mocking_enabled}")

    # Check if __ENABLE_API_MOCKING__ was set
    enable_mocking = browser.execute_script("return window.__ENABLE_API_MOCKING__;")
    print(f"__ENABLE_API_MOCKING__: {enable_mocking}")
