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
                time.sleep(0.5)
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
        time.sleep(0.5)
        
        # Check if maximized
        placement = win32gui.GetWindowPlacement(target_hwnd)
        is_maximized = (placement[1] == win32con.SW_SHOWMAXIMIZED)
        time.sleep(0.5)
        if not is_maximized:
            print(f"[APP HELPER] Not maximized, maximizing...")
            win32gui.ShowWindow(target_hwnd, win32con.SW_MAXIMIZE)
            time.sleep(0.5)
        else:
            print(f"[APP HELPER] Already maximized")
        
        print(f"[APP HELPER] ✓ Window ready: '{target_title}'")
        time.sleep(0.5)
        return True
    
    except Exception as e:
        print(f"[APP HELPER] Error bringing window to front: {e}")
        import traceback
        traceback.print_exc()
        return False


def perform_random_movements_with_click_detection(max_attempts=5, type_action=None):
    """
    Move mouse randomly in center 3/4 of screen and click if cursor becomes hand
    
    Area constraints:
    - Horizontal: Center 3/4 (12.5% margin on each side)
    - Vertical: 300px from top, 100px from bottom
    
    Args:
        max_attempts (int): Number of random movement attempts (default: 5)
        type_action: None/Google => Google will find link 30% left screen
    
    Returns:
        tuple: (clicked: bool, click_position: tuple or None)
            - clicked: True if clicked a clickable element, False otherwise
            - click_position: (x, y) tuple if clicked, None otherwise
    
    Example:
        >>> from helpers.app_helpers import perform_random_movements_with_click_detection
        >>> 
        >>> def my_log(msg):
        ...     print(f"[LOG] {msg}")
        >>> 
        >>> clicked, position = perform_random_movements_with_click_detection(
        ...     max_attempts=5,
        ...     log_callback=my_log
        ... )
        >>> 
        >>> if clicked:
        ...     print(f"Clicked at {position}")
    """
    import pyautogui
    import random
    import time
    from controllers.actions.mouse_move_action import MouseMoveAction
    
    try:
        # Get screen size
        screen_width, screen_height = pyautogui.size()
        
        # ========== DEFINE MOVEMENT AREA ==========
        # Horizontal: Center 3/4 (12.5% margin left/right)
        if type_action == "google":
            min_x = 200 
            max_x = int(screen_width * 0.3)   # 30% from left
        else:
            min_x = int(screen_width * 0.125)   # 12.5% from left
            max_x = int(screen_width * 0.875)   # 12.5% from right (87.5% from left)
        # Vertical: 300px from top, 100px from bottom
        min_y = 300
        max_y = screen_height - 200
     
       
        # ========== RETRY ATTEMPTS ==========
        for attempt in range(1, max_attempts + 1):
            # Random position within defined area
            random_x = random.randint(min_x, max_x)
            random_y = random.randint(min_y, max_y)
          
            safe_x = screen_width - 18  # 10px từ mép phải
            safe_y = random.randint(100, screen_height - 100)  # Random từ 100px đến (height-100)px
            # Move mouse (no click yet)
            MouseMoveAction.move_and_click_static(
                random_x, random_y,
                click_type=None,  # Just move, don't click
                fast=False
            )           
            
            # ========== CHECK IF CURSOR IS HAND ==========
            if is_hand_cursor():             
                time.sleep(random.uniform(0.5, 2))
                # Click using pyautogui (cursor is already at position)
                pyautogui.click()
                
                # Wait for potential page navigation
                click_wait = random.uniform(2, 3)
                time.sleep(click_wait)
                
                return True, (random_x, random_y)  # Successfully clicked
          
            
            # Wait 1-2s before next attempt (if not last attempt)
            MouseMoveAction.move_and_click_static(safe_x, safe_y, "single_click", fast=False)
            time.sleep(0.3)
            scroll_amount = random.randint(-400, -200)  # Scroll down                    
            pyautogui.scroll(scroll_amount)
            if attempt < max_attempts:
                retry_wait = random.uniform(1, 2)
                time.sleep(retry_wait)
        
        # No clickable element found after max_attempts
        return False, None
    
    except Exception as e:     
        import traceback
        traceback.print_exc()
        return False, None


def is_hand_cursor():
    """
    Check if cursor is hand pointer (clickable element)
        
    Returns:
        bool: True if hand cursor
    """
    try:
        import win32gui
        time.sleep(0.5)
            
        cursor_info = win32gui.GetCursorInfo()
        hand_cursor_handles = [32649, 65567, 65563, 65561, 60171, 60169, 32513]
            
        return cursor_info[1] in hand_cursor_handles
    except Exception as e:       
        return False
