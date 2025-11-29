# controllers/actions/flow_auto/actions_auto/base_flow_auto_action.py

import time
import random
import pyautogui
import psutil 

class BaseFlowAutoAction:
    """
    Base class cho tất cả Auto Flow Actions
    Chứa các helper methods chung
    """
    
    def __init__(self, profile_id, log_prefix="[AUTO ACTION]"):
        """
        Initialize base action
        
        Args:
            profile_id: GoLogin profile ID
            log_prefix: Prefix for log messages
        """
        self.profile_id = profile_id
        self.log_prefix = log_prefix
        self.parameters = {}
    # ========== ABSTRACT METHOD (TEMPLATE PATTERN) ==========

    def execute(self):
        """
        Template method: Execute action with automatic tab cleanup before action.
    
        Subclasses should override _execute_internal() instead of execute().
    
        Flow:
        1. Clean up extra tabs (keep tab 1 only) - automatic
        2. Execute action (subclass implementation via _execute_internal)
    
        Returns:
            bool: Success status from _execute_internal()
        """
        # Auto cleanup before action (keep first tab)
        # self.log("========== PRE-ACTION CLEANUP ==========")
        # cleanup_success = self._close_extra_tabs_keep_first()
        # if not cleanup_success:
        #     self.log("Tab cleanup failed, proceeding with action anyway", "WARNING")
        # self.log("========== STARTING ACTION ==========")
    
        # Execute subclass implementation
        try:
            result = self._execute_internal()
            self.log(f"========== ACTION {'SUCCESS' if result else 'FAILED'} ==========")
            return result
        except Exception as e:
            self.log(f"========== ACTION ERROR: {e} ==========", "ERROR")
            import traceback
            traceback.print_exc()
            return False

    def _execute_internal(self):
        """
        Internal execute method to be overridden by subclasses.
    
        Subclasses implement action logic here instead of execute().
    
        Returns:
            bool: Success status
    
        Raises:
            NotImplementedError: If subclass doesn't override
        """
        raise NotImplementedError("Subclasses must override _execute_internal()")


    # ========== TYPING METHODS ==========
    
    def _type_human_like(self, text):
        """
        Type text with human-like delays
        
        Args:
            text: Text to type
        """
        for char in text:
            pyautogui.write(char)
            
            # 70% fast typing, 30% slow typing (more human-like)
            if random.random() < 0.7:
                time.sleep(random.uniform(0.05, 0.15))
            else:
                time.sleep(random.uniform(0.15, 0.25))
    
    def _type_with_mistakes(self, text, mistake_rate=0.05):
        """
        Type text with occasional mistakes and corrections (more realistic)
        
        Args:
            text: Text to type
            mistake_rate: Probability of making a mistake (0-1)
        """
        for i, char in enumerate(text):
            # Random chance to make a typo
            if random.random() < mistake_rate and i > 0:
                # Type wrong character
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                pyautogui.write(wrong_char)
                time.sleep(random.uniform(0.05, 0.1))
                
                # Realize mistake, backspace
                pyautogui.press('backspace')
                time.sleep(random.uniform(0.1, 0.2))
            
            # Type correct character
            pyautogui.write(char)
            
            # Human-like delay
            if random.random() < 0.7:
                time.sleep(random.uniform(0.05, 0.15))
            else:
                time.sleep(random.uniform(0.15, 0.25))
    
    # ========== CURSOR CHECKING ==========
    
    def _is_hand_cursor(self):
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
            self.log(f"Error checking cursor: {e}", "WARNING")
            return False
    
    # ========== RANDOM DELAYS ==========
    
    def _random_delay(self, min_seconds=0.5, max_seconds=2.0):
        """
        Random delay to simulate human behavior
        
        Args:
            min_seconds: Minimum delay
            max_seconds: Maximum delay
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def _random_short_pause(self):
        """Random short pause (0.1-0.3s)"""
        time.sleep(random.uniform(0.1, 0.3))
    
    def _random_thinking_pause(self):
        """Random thinking pause (0.5-1.5s)"""
        time.sleep(random.uniform(0.5, 1.5))
        
    # ========== KEYWORD GENERATION (REUSABLE) ==========

    def _generate_keyword(self, keywords):
        """
        Generate keyword with variation (giống Non-Auto version)
        Reusable cho YouTube Search, Google Search, etc.
    
        Args:
            keywords: Dict containing keywords_youtube/keywords_google and suffix_prefix
        
        Returns:
            str: Final keyword with suffix/prefix or None
        """
        try:
            # Get keywords list (support both youtube and google)
            keywords_list = keywords.get('keywords_youtube', []) or keywords.get('keywords_google', [])
        
            if not keywords_list:
                self.log("No keywords in params", "WARNING")
                return None
        
            # Random chọn 1 keyword
            keyword = random.choice(keywords_list)
            self.log(f"Selected base keyword: '{keyword}'")
        
            # Get suffix_prefix string
            suffix_prefix_string = keywords.get('suffix_prefix', '')
        
            if not suffix_prefix_string:
                # No variation, return original keyword
                return keyword
        
            # Parse suffix_prefix thành list
            from helpers.keyword_variation_helper import KeywordVariationHelper
            suffix_prefix_list = KeywordVariationHelper.parse_suffix_prefix_list(suffix_prefix_string)
        
            # Generate keyword variation
            final_keyword = KeywordVariationHelper.generate_keyword_variation(
                keyword, suffix_prefix_list
            )
        
            self.log(f"Generated keyword variation: '{final_keyword}'")
            return final_keyword
        
        except Exception as e:
            self.log(f"Error generating keyword: {e}", "ERROR")
            import traceback
            traceback.print_exc()
        
            # Fallback: return first keyword if available
            keywords_list = keywords.get('keywords_youtube', []) or keywords.get('keywords_google', [])
            if keywords_list:
                return keywords_list[0]
            return None

    # ========== IMAGE DETECTION (REUSABLE) ==========

    def _find_image_on_screen(self, image_path, region=None, accuracy=0.7, click_offset_x=0, click_offset_y=0):
        """
        Find image on screen using template matching
        Reusable cho search icon, channel logo, button detection, etc.
    
        Args:
            image_path: Path to template image
            region: Search region (x, y, width, height) or None for full screen
            accuracy: Match accuracy (0.0 - 1.0) - will be converted to 0-100 for ImageSearcher
            click_offset_x: X offset from found image center (for clickable area)
            click_offset_y: Y offset from found image center (for clickable area)
    
        Returns:
            dict: {
                'found': bool,
                'center': (x, y),  # Center of found image
                'click_position': (x, y)  # Position with offset applied
            } or None if not found
        """
        try:
            from models.image_search import ImageSearcher
        
            # Convert accuracy from 0-1 to 0-100 (ImageSearcher expects percentage)
            accuracy_percent = accuracy * 100
        
            # Create searcher with image_path, region, and accuracy
            searcher = ImageSearcher(
                image_path=image_path,
                region=region,
                accuracy=accuracy_percent
            )
        
            # Search returns: (success: bool, result: tuple or None)
            success, result = searcher.search()
        
            if success and result:
                center_x, center_y, confidence = result
                click_x = center_x + click_offset_x
                click_y = center_y + click_offset_y
            
                self.log(f"✓ Found image at ({center_x}, {center_y}), confidence: {confidence:.2f}, click position: ({click_x}, {click_y})")
            
                return {
                    'found': True,
                    'center': (center_x, center_y),
                    'click_position': (click_x, click_y),
                    'confidence': confidence
                }
            else:
                self.log(f"Image not found: {image_path}")
                return None
            
        except Exception as e:
            self.log(f"Image detection error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return None


    def _find_multiple_images(self, image_path, region=None, accuracy=0.7):
        """
        Find all occurrences of image on screen
        Useful for finding multiple channel logos, buttons, etc.
    
        Args:
            image_path: Path to template image
            region: Search region (x, y, width, height) or None for full screen
            accuracy: Match accuracy (0.0 - 1.0)
        
        Returns:
            list: List of dicts with 'center' and 'click_position', or empty list
        """
        try:
            import pyautogui
        
            # Find all matches
            matches = list(pyautogui.locateAllOnScreen(image_path, confidence=accuracy, region=region))
        
            if not matches:
                self.log(f"No matches found for: {image_path}", "WARNING")
                return []
        
            results = []
            for match in matches:
                center_x = match.left + (match.width // 2)
                center_y = match.top + (match.height // 2)
            
                results.append({
                    'center': (center_x, center_y),
                    'click_position': (center_x, center_y),
                    'bbox': (match.left, match.top, match.width, match.height)
                })
        
            self.log(f"✓ Found {len(results)} matches")
            return results
        
        except Exception as e:
            self.log(f"Multiple image detection error: {e}", "ERROR")
            return []

    # ========== TAB MANAGEMENT (ORBITA BROWSER) ==========

    def _is_orbita_window(self):
        """
        Check if current foreground window is GoLogin profile browser (Orbita/Chromium).
    
        Detection logic:
        - NOT by window title (title is page content, e.g., "YouTube - Video")
        - By process: Check if process is chrome.exe/orbita.exe with GoLogin profile_id in command line
    
        Returns:
            bool: True if GoLogin profile browser, False otherwise
        """
        try:
            import win32gui
            import win32process
            import psutil
        
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
        
            # Get process ID from window
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
        
            # Get process info
            try:
                process = psutil.Process(pid)
                process_name = process.name().lower()
                cmdline = ' '.join(process.cmdline()).lower()
            
                # Check if process is Chrome/Chromium (GoLogin Orbita is Chromium-based)
                is_chrome_based = any(name in process_name for name in ['chrome', 'orbita'])
            
                # Check if command line contains profile_id (GoLogin unique pattern: --user-data-dir=.../profile_id/)
                has_profile_id = self.profile_id.lower() in cmdline if self.profile_id else False
            
                # GoLogin profile browser = Chrome-based process + has profile_id in cmdline
                is_gologin_browser = is_chrome_based and has_profile_id
            
                if is_gologin_browser:
                    self.log(f"✓ GoLogin profile browser detected (PID={pid}, title='{window_title[:60]}...')")
                else:
                    self.log(f"Not GoLogin browser: PID={pid}, process={process_name}, has_profile_id={has_profile_id}", "DEBUG")
            
                return is_gologin_browser
        
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                self.log(f"Cannot access process {pid}: {e}", "WARNING")
                return False
    
        except Exception as e:
            self.log(f"Error checking GoLogin browser: {e}", "WARNING")
            return False


    def _close_extra_tabs_keep_first(self):
        """
        Close all tabs except the first tab in current GoLogin browser window.
    
        Uses PyAutoGUI + win32gui to close tabs within SAME window only.
    
        Logic:
        1. Get current window handle (profile browser)
        2. Switch to tab 1 (Ctrl+1)
        3. Loop: Ctrl+2 to jump to tab 2 (if exists), check if still same window
        4. If same window → close tab (Ctrl+W), repeat
        5. If window changed → break (switched to different profile/app)
    
        Returns:
            bool: True if successfully closed extra tabs or only 1 tab exists, False if error
        """
        try:
            # Step 1: Check if GoLogin browser
            if not self._is_orbita_window():
                self.log("Not on GoLogin browser, skipping tab cleanup", "WARNING")
                return False
        
            self.log("Starting extra tabs cleanup (keep first tab only)")
        
            import win32gui
            import time
        
            # Step 2: Get current window handle (IMPORTANT: lock to this window)
            initial_hwnd = win32gui.GetForegroundWindow()
            initial_title = win32gui.GetWindowText(initial_hwnd)
            self.log(f"Target window (hwnd={initial_hwnd}): '{initial_title[:80]}...'")
        
            # Step 3: Switch to tab 1 (first tab)
            pyautogui.hotkey('ctrl', '1')
            time.sleep(0.8)
        
            # Verify still in same window
            current_hwnd = win32gui.GetForegroundWindow()
            if current_hwnd != initial_hwnd:
                self.log("Window changed after Ctrl+1, aborting", "WARNING")
                return False
        
            tab1_title = win32gui.GetWindowText(current_hwnd)
            self.log(f"Tab 1 title: '{tab1_title[:80]}...'")
        
            # Step 4: Try to switch to tab 2 (check if multiple tabs exist)
            pyautogui.hotkey('ctrl', '2')
            time.sleep(0.8)
        
            current_hwnd = win32gui.GetForegroundWindow()
        
            # FIX: If window changed → switched to different window → abort
            if current_hwnd != initial_hwnd:
                self.log("Window changed after Ctrl+2 (different profile/app), aborting", "WARNING")
                # Switch back to original window
                win32gui.SetForegroundWindow(initial_hwnd)
                return False
        
            current_title = win32gui.GetWindowText(current_hwnd)
        
            # If title same as tab 1 → only 1 tab exists (Ctrl+2 didn't switch)
            if current_title == tab1_title:
                self.log("Only 1 tab detected (Ctrl+2 had no effect), nothing to close")
                return True
        
            self.log(f"Multiple tabs detected - tab 2 title: '{current_title[:80]}...'")
        
            # Step 5: Close extra tabs (always try Ctrl+2, close if exists)
            max_tabs_to_close = 20  # Safety limit
            tabs_closed = 0
        
            for attempt in range(max_tabs_to_close):
                # Try switch to tab 2 (after closing, next tab becomes tab 2)
                pyautogui.hotkey('ctrl', '2')
                time.sleep(0.6)
            
                current_hwnd = win32gui.GetForegroundWindow()
            
                # FIX: If window changed → break (reached end or switched to other window)
                if current_hwnd != initial_hwnd:
                    self.log(f"Window changed (switched to different window), stopping at {tabs_closed} tabs closed")
                    # Switch back
                    win32gui.SetForegroundWindow(initial_hwnd)
                    break
            
                current_title = win32gui.GetWindowText(current_hwnd)
            
                # If current title == tab1_title → cycled back to tab 1 → no more tabs
                if current_title == tab1_title:
                    self.log(f"✓ All extra tabs closed - back to tab 1 (closed {tabs_closed} tabs)")
                    break
            
                # Close current tab (tab 2+) with Ctrl+W
                self.log(f"Closing tab (attempt {attempt + 1}): '{current_title[:60]}...'")
                pyautogui.hotkey('ctrl', 'w')
                time.sleep(0.6)
                tabs_closed += 1
            
                # After close, verify still in same window
                current_hwnd = win32gui.GetForegroundWindow()
                if current_hwnd != initial_hwnd:
                    self.log(f"Window changed after close, stopped at {tabs_closed} tabs closed")
                    win32gui.SetForegroundWindow(initial_hwnd)
                    break
        
            if tabs_closed == 0:
                self.log("No tabs closed - only 1 tab exists")
            else:
                self.log(f"✓ Successfully closed {tabs_closed} extra tabs")
        
            # Final: Ensure on tab 1
            pyautogui.hotkey('ctrl', '1')
            time.sleep(0.3)
        
            return True
    
        except Exception as e:
            self.log(f"Error closing extra tabs: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False


    def _get_current_url(self):
        """
        Get current URL from browser address bar
    
        Method:
        1. Focus address bar (Ctrl+L) - auto selects all
        2. Copy to clipboard (Ctrl+C)
        3. Press ESC to exit address bar focus
        4. Read from clipboard
    
        Returns:
            str: Current URL, or empty string if failed
        """
        try:
            # Focus address bar (auto-selects all text)
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.2)  # Reduced wait time
        
            # Copy to clipboard (no need for Ctrl+A)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.2)  # Reduced wait time
        
            # ESC to exit address bar focus (prevent paste issues)
            pyautogui.press('esc')
            time.sleep(0.1)
        
            # Read from clipboard
            import pyperclip
            url = pyperclip.paste()
        
            self.log(f"Current URL: {url}")
            return url.strip()
    
        except Exception as e:
            self.log(f"Failed to get current URL: {e}", "ERROR")
            return ""
        
    
    def check_page_fully_loaded(self):
        """
        Check if page is fully loaded by detecting reload icon
        
        Logic:
        - Find reload icon in reload browser area
        - If reload icon FOUND → page fully loaded → return True
        - If NOT found after max_wait_seconds → still loading/timeout → return False
        - Check every check_interval seconds
        
        All params are hardcoded from self.params (set by subclass)
        
        Returns:
            bool: True if page fully loaded (reload icon found), False if timeout/still loading
        """
        reload_icon_path = self.parameters.get("reload_browser_icon_path", "").strip()        
        if not reload_icon_path:
            try:
           
                area_x = int(self.parameters.get("reload_browser_area_x", "0"))
                area_y = int(self.parameters.get("reload_browser_area_y", "0"))
                area_width = int(self.parameters.get("reload_browser_area_width", "200"))
                area_height = int(self.parameters.get("reload_browser_area_height", "100"))
            
                # Hardcoded timing
                max_wait_seconds = 10.0
                check_interval = 1.0
            
                if not reload_icon_path:
                    self.log("No reload icon path specified", "WARNING")
                    return False
            
                # Check if icon file exists
                import os
                if not os.path.exists(reload_icon_path):
                    self.log(f"Reload icon file not found: {reload_icon_path}", "ERROR")
                    return False
            
                # Define search region
                search_region = None
                if area_width > 0 and area_height > 0:
                    search_region = (area_x, area_y, area_width, area_height)
                    self.log(f"Reload check region: {search_region}")
                else:
                    self.log("Invalid reload check region", "ERROR")
                    return False
            
                # Loop: Check for reload icon until found or timeout
                elapsed_time = 0.0
                check_count = 0
            
                while elapsed_time < max_wait_seconds:
                    check_count += 1
                    self.log(f"[CHECK {check_count}] Looking for reload icon... (elapsed: {elapsed_time:.1f}s)")
                
                    # Find reload icon
                    result = self._find_image_on_screen(
                        image_path=reload_icon_path,
                        region=search_region,
                        accuracy=0.8,
                        click_offset_x=0,
                        click_offset_y=0
                    )
                
                    if result and result['found']:
                        # Reload icon FOUND → page fully loaded
                        reload_x, reload_y = result['center']
                        self.log(f"✓ Page FULLY LOADED - reload icon found at ({reload_x}, {reload_y})")
                        return True
                    else:
                        # NOT found yet → still loading, wait and retry
                        self.log(f"⟳ Page still loading - reload icon not found yet")
                        time.sleep(check_interval)
                        elapsed_time += check_interval
            
                # Timeout - reload icon never appeared
                self.log(f"✗ Timeout after {max_wait_seconds}s - reload icon NOT found", "WARNING")
                return False
            
            except Exception as e:
                self.log(f"Error checking page load: {e}", "ERROR")
                import traceback
                traceback.print_exc()
                return False

        return False

    # ========== LOGGING ==========
    
    def log(self, message, level="INFO"):
        """
        Log message with prefix
        
        Args:
            message: Log message
            level: Log level (INFO, WARNING, ERROR, DEBUG)
        """
        print(f"{self.log_prefix} [{level}] {message}")
    
   