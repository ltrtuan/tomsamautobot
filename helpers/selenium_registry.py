# helpers/selenium_registry.py

"""
Global Selenium driver registry
All actions should use these functions to register/unregister Selenium drivers
"""

# Import global registry from main
import sys
if 'main' in sys.modules:
    from main import _active_selenium_drivers
else:
    # Fallback nếu chạy standalone
    _active_selenium_drivers = []

def register_selenium_driver(driver):
    """
    Register a Selenium driver for automatic cleanup
    
    Args:
        driver: Selenium WebDriver instance
    
    Usage:
        driver = webdriver.Chrome(...)
        register_selenium_driver(driver)
    """
    if driver and driver not in _active_selenium_drivers:
        _active_selenium_drivers.append(driver)
        print(f"[SELENIUM REGISTRY] ✓ Driver registered (Total: {len(_active_selenium_drivers)})")

def unregister_selenium_driver(driver):
    """
    Unregister a Selenium driver (when manually cleaned up)
    
    Args:
        driver: Selenium WebDriver instance
    
    Usage:
        driver.quit()
        unregister_selenium_driver(driver)
    """
    if driver in _active_selenium_drivers:
        _active_selenium_drivers.remove(driver)
        print(f"[SELENIUM REGISTRY] ✓ Driver unregistered (Remaining: {len(_active_selenium_drivers)})")

def get_active_driver_count():
    """Get count of active drivers"""
    return len(_active_selenium_drivers)
