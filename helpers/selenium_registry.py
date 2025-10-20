# helpers/selenium_registry.py

"""
Global Selenium driver registry with profile tracking
All actions should use these functions to register/unregister Selenium drivers
"""

import threading

# Global registry: {profile_id: driver} or {thread_id: driver}
_active_selenium_drivers = {}
_registry_lock = threading.Lock()


def register_selenium_driver(driver, profile_id=None):
    """
    Register a Selenium driver for automatic cleanup
    
    Args:
        driver: Selenium WebDriver instance
        profile_id: Optional profile ID for tracking (recommended for multi-profile)
    
    Usage:
        # With profile_id (recommended for GoLogin profiles)
        register_selenium_driver(driver, "profile_123")
        
        # Without profile_id (legacy support)
        register_selenium_driver(driver)
    """
    if not driver:
        return
    
    with _registry_lock:
        thread_id = threading.current_thread().ident
        
        # Create key: prefer profile_id, fallback to thread_id
        if profile_id:
            key = f"profile_{profile_id}"
        else:
            key = f"thread_{thread_id}"
        
        _active_selenium_drivers[key] = driver
        
        print(f"[SELENIUM REGISTRY] ✓ Driver registered: {key} (Total: {len(_active_selenium_drivers)})")


def unregister_selenium_driver(profile_id=None):
    """
    Unregister a Selenium driver (when manually cleaned up)
    
    Args:
        profile_id: Optional profile ID (should match register call)
    
    Usage:
        # With profile_id
        unregister_selenium_driver("profile_123")
        
        # Without profile_id (uses current thread)
        unregister_selenium_driver()
    """
    with _registry_lock:
        thread_id = threading.current_thread().ident
        
        # Create key: prefer profile_id, fallback to thread_id
        if profile_id:
            key = f"profile_{profile_id}"
        else:
            key = f"thread_{thread_id}"
        
        if key in _active_selenium_drivers:
            del _active_selenium_drivers[key]
            print(f"[SELENIUM REGISTRY] ✓ Driver unregistered: {key} (Remaining: {len(_active_selenium_drivers)})")
        else:
            print(f"[SELENIUM REGISTRY] ⚠ Driver not found: {key}")


def get_active_driver_count():
    """Get count of active drivers"""
    with _registry_lock:
        return len(_active_selenium_drivers)


def get_driver_by_profile(profile_id):
    """
    Get driver by profile ID
    
    Args:
        profile_id: Profile ID
        
    Returns:
        WebDriver instance or None
    """
    with _registry_lock:
        key = f"profile_{profile_id}"
        return _active_selenium_drivers.get(key)


def cleanup_all_drivers():
    """
    Cleanup all registered drivers
    Used for emergency cleanup on application shutdown
    """
    with _registry_lock:
        print(f"[SELENIUM REGISTRY] Cleaning up {len(_active_selenium_drivers)} drivers...")
        
        for key, driver in list(_active_selenium_drivers.items()):
            try:
                driver.quit()
                print(f"[SELENIUM REGISTRY] ✓ Cleaned up: {key}")
            except Exception as e:
                print(f"[SELENIUM REGISTRY] ⚠ Cleanup error for {key}: {e}")
        
        _active_selenium_drivers.clear()
        print("[SELENIUM REGISTRY] ✓ All drivers cleaned up")


def list_active_drivers():
    """
    List all active drivers (for debugging)
    
    Returns:
        dict: {key: driver}
    """
    with _registry_lock:
        return dict(_active_selenium_drivers)
