"""Check if API_URL is available when React mounts"""
import pytest


def test_api_url_timing(browser):
    """Check API_URL at different stages of page load"""
    import time

    # Check immediately after page load
    time.sleep(0.5)
    api_url_early = browser.execute_script("return window.__API_URL__;")
    print(f"\nAPI_URL after 0.5s: {api_url_early}")

    time.sleep(1)
    api_url_mid = browser.execute_script("return window.__API_URL__;")
    print(f"API_URL after 1.5s: {api_url_mid}")

    time.sleep(2)
    api_url_late = browser.execute_script("return window.__API_URL__;")
    print(f"API_URL after 3.5s: {api_url_late}")

    # Check if config.js was loaded successfully
    config_script = browser.execute_script("""
        const scripts = Array.from(document.querySelectorAll('script'));
        const configScript = scripts.find(s => s.src && s.src.includes('config.js'));
        return {
            found: !!configScript,
            src: configScript ? configScript.src : null,
            loaded: configScript ? !configScript.onerror : null
        };
    """)
    print(f"Config script status: {config_script}")

    # Try to manually load and execute config.js
    config_test = browser.execute_script("""
        return fetch('/config.js')
            .then(r => r.text())
            .then(text => ({success: true, length: text.length, content: text.substring(0, 200)}))
            .catch(err => ({success: false, error: err.message}));
    """)
    print(f"Manual config.js load: {config_test}")
