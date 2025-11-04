# helpers/app_helpers.py

import win32gui
import win32con
import time


def check_and_focus_window_by_title(window_title_filter):
    """
    Check if window with title exists, maximize if needed, bring to front
    
    Args:
        window_title_filter (str): Text to search in window title (case-insensitive)
    
    Returns:
        bool: True if window found and focused, False otherwise
    
    Logic:
        1. Get current foreground window
        2. If current window title contains filter:
           - If already maximized → skip (do nothing)
           - If not maximized → maximize it
        3. If current window doesn't match:
           - Find window by title
           - Bring to front
           - Maximize if not maximized
    """
    if not window_title_filter:
        print("[APP HELPER] No window title filter provided")
        return False
    
    window_title_filter_lower = window_title_filter.lower()
    
    # ========== STEP 1: CHECK CURRENT FOREGROUND WINDOW ==========
    try:
        current_hwnd = win32gui.GetForegroundWindow()
        current_title = win32gui.GetWindowText(current_hwnd)
        
        # Check if current window matches filter
        if window_title_filter_lower in current_title.lower():
            print(f"[APP HELPER] Current window matches: '{current_title}'")
            
            # Check if maximized
            placement = win32gui.GetWindowPlacement(current_hwnd)
            is_maximized = (placement[1] == win32con.SW_SHOWMAXIMIZED)
            
            if is_maximized:
                print(f"[APP HELPER] Already maximized, skipping")
                return True
            else:
                print(f"[APP HELPER] Not maximized, maximizing...")
                win32gui.ShowWindow(current_hwnd, win32con.SW_MAXIMIZE)
                time.sleep(0.2)
                print(f"[APP HELPER] ✓ Maximized")
                return True
    
    except Exception as e:
        print(f"[APP HELPER] Error checking current window: {e}")
    
    # ========== STEP 2: FIND WINDOW BY TITLE ==========
    print(f"[APP HELPER] Current window doesn't match, searching for: '{window_title_filter}'")
    
    target_hwnd = None
    
    def enum_windows_callback(hwnd, results):
        # KEEP ORIGINAL: Only check visible (simple)
        if not win32gui.IsWindowVisible(hwnd):
            return True
        
        try:
            window_title = win32gui.GetWindowText(hwnd)
            if window_title_filter_lower in window_title.lower():
                # KEEP ORIGINAL: 2-element tuple
                results.append((hwnd, window_title))
                print(f"[APP HELPER] Found matching window: '{window_title}'")
        except:
            pass
        
        return True
    
    # Search all windows
    found_windows = []
    win32gui.EnumWindows(enum_windows_callback, found_windows)
    
    # ========== NEW: If not found, search again including hidden windows ==========
    if not found_windows:
        print(f"[APP HELPER] No visible window found, searching hidden/tray windows...")
        
        def enum_all_windows_callback(hwnd, results):
            # Check all windows (including hidden/tray)
            if not win32gui.IsWindowEnabled(hwnd):
                return True
            
            try:
                window_title = win32gui.GetWindowText(hwnd)
                if window_title_filter_lower in window_title.lower():
                    results.append((hwnd, window_title))
                    is_visible = win32gui.IsWindowVisible(hwnd)
                    visibility = "visible" if is_visible else "hidden/tray"
                    print(f"[APP HELPER] Found matching window: '{window_title}' ({visibility})")
            except:
                pass
            
            return True
        
        win32gui.EnumWindows(enum_all_windows_callback, found_windows)
    
    if not found_windows:
        print(f"[APP HELPER] ✗ No window found with title: '{window_title_filter}'")
        return False
    
    # Use first matching window (KEEP ORIGINAL: 2-element tuple)
    target_hwnd, target_title = found_windows[0]
    
    if len(found_windows) > 1:
        print(f"[APP HELPER] Found {len(found_windows)} windows, using first: '{target_title}'")
    
    # ========== STEP 3: BRING TO FRONT AND MAXIMIZE ==========
    try:
        # Check if window is visible
        is_visible = win32gui.IsWindowVisible(target_hwnd)
        is_minimized = win32gui.IsIconic(target_hwnd)
        
        # Restore if minimized OR not visible (tray)
        if is_minimized or not is_visible:
            if not is_visible:
                print(f"[APP HELPER] Restoring from System Tray...")
            else:
                print(f"[APP HELPER] Restoring from minimized...")
            
            win32gui.ShowWindow(target_hwnd, win32con.SW_RESTORE)
            time.sleep(0.5)  # Wait for restore to complete
        
        # Bring to foreground
        print(f"[APP HELPER] Bringing to front...")
        win32gui.SetForegroundWindow(target_hwnd)
        time.sleep(0.2)
        
        # Check if maximized
        placement = win32gui.GetWindowPlacement(target_hwnd)
        is_maximized = (placement[1] == win32con.SW_SHOWMAXIMIZED)
        
        if not is_maximized:
            print(f"[APP HELPER] Not maximized, maximizing...")
            win32gui.ShowWindow(target_hwnd, win32con.SW_MAXIMIZE)
            time.sleep(0.2)
        else:
            print(f"[APP HELPER] Already maximized")
        
        print(f"[APP HELPER] ✓ Window ready: '{target_title}'")
        return True
    
    except Exception as e:
        print(f"[APP HELPER] Error bringing window to front: {e}")
        import traceback
        traceback.print_exc()
        return False
