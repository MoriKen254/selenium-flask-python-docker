"""Check if axios is properly loaded in the React app"""
import pytest


def test_check_axios_module_loaded(browser):
    """Check if axios module is available in the bundle"""
    import time
    time.sleep(3)

    # Try to access axios in different ways
    result = browser.execute_script("""
        return {
            // Check if axios is on window (it shouldn't be for modules)
            windowAxios: typeof window.axios,

            // Check if we can access it from the React DevTools
            // (won't work but good to check)
            hasReactDevTools: typeof window.__REACT_DEVTOOLS_GLOBAL_HOOK__ !== 'undefined',

            // Check the bundle size (axios should make it larger)
            bundleScripts: Array.from(document.querySelectorAll('script')).map(s => ({
                src: s.src,
                loaded: s.src ? true : false
            })).filter(s => s.src.includes('bundle'))
        };
    """)

    print(f"\nAxios check result: {result}")

    # Now try to trigger an axios call and capture the exact error
    error_details = browser.execute_script("""
        return new Promise((resolve) => {
            // Import axios dynamically won't work, but we can try to trigger the app's axios
            // by manually calling the app's methods if they're exposed

            // Wait a bit then resolve
            setTimeout(() => {
                resolve({
                    message: 'Cannot directly access axios in module context'
                });
            }, 100);
        });
    """)

    print(f"Error details: {error_details}")

    # Let me try a different approach - check if the app has any global error handlers
    has_error_handler = browser.execute_script("""
        return {
            hasWindowError: typeof window.onerror !== 'undefined',
            hasUnhandledRejection: typeof window.onunhandledrejection !== 'undefined'
        };
    """)
    print(f"Error handlers: {has_error_handler}")
