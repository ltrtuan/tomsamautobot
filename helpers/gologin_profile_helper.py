# helpers/gologin_profile_helper.py

from models.global_variables import GlobalVariables
from models.gologin_api import get_gologin_api
import random
import threading
import time
_chromedriver_lock = threading.Lock()
_window_focus_lock = threading.Lock()
class GoLoginProfileHelper:
    """Helper class for common GoLogin profile operations"""
     # ========== THÊM CLASS VARIABLES ĐỂ CACHE ==========
    _keywords_cache = {}   # Cache: {file_path: [keywords]}
    _websites_cache = {}   # Cache: {file_path: [websites]}
    # ==================================================
    @staticmethod
    def get_profile_list(params, api_token, log_prefix="[GOLOGIN]"):
        """
        Get profile list from either range or manual input
    
        Args:
            params: Dict containing profile parameters
            api_token: GoLogin API token
            log_prefix: Prefix for log messages
        
        Returns:
            tuple: (success, profile_list or error_message)
        """
        try:
            # ========== GET PROFILE IDs: RANGE OR MANUAL ==========
            profile_count = params.get("profile_count", "30").strip()
            profile_start_index = params.get("profile_start_index", "0").strip()
        
            if profile_count and profile_start_index:
                try:
                    count = int(profile_count)
                    start_index = int(profile_start_index)
                except ValueError:
                    return False, f"Invalid range: count='{profile_count}', start='{profile_start_index}'"
            
                if count <= 0:
                    return False, f"Profile count must be > 0 (got {count})"
            
                if start_index < 0:
                    return False, f"Start index must be >= 0 (got {start_index})"
            
                print(f"{log_prefix} Range: {count} profiles starting from index {start_index}")
            
                # Fetch all profiles from API
                gologin_api = get_gologin_api(api_token)
                success, profiles_data = gologin_api.get_all_profiles(count=count, start_index=start_index)
            
                if not success:
                    return False, f"Failed to fetch profiles: {profiles_data}"
            
                # Extract profile IDs
                all_profile_ids = [profile.get("id") for profile in profiles_data if profile.get("id")]
            
                if not all_profile_ids:
                    return False, "No profiles found in account"
            
                print(f"{log_prefix} ✓ Fetched {len(all_profile_ids)} profiles from API (starting from index {start_index})")
            
                # API đã trả về đúng range, không cần slice lại
                profile_list = all_profile_ids
            
                if not profile_list:
                    return False, f"No profiles found"
            
                print(f"{log_prefix} ✓ Using {len(profile_list)} profiles")
                return True, profile_list
            
            else:
                # Original logic: Get profile IDs from params
                profile_ids = params.get("profile_ids", "").strip()
                if not profile_ids:
                    return False, "Profile IDs are required"
            
                # Parse profile IDs
                profile_list = GoLoginProfileHelper.parse_profile_ids(profile_ids, log_prefix)
            
                if not profile_list:
                    return False, "No valid profile IDs found"
            
                return True, profile_list
            
        except Exception as e:
            return False, f"Error getting profile list: {e}"

    
    @staticmethod
    def parse_profile_ids(profile_ids_text, log_prefix="[GOLOGIN]"):
        """Parse profile IDs from text, support variables"""
        profile_list = []
        parts = profile_ids_text.split(";")
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Check if variable format
            if part.startswith("<") and part.endswith(">"):
                var_name = part[1:-1]
                var_value = GlobalVariables().get(var_name, "")
                if var_value:
                    profile_list.append(var_value)
                else:
                    print(f"{log_prefix} Warning: Variable '{var_name}' is empty")
            else:
                profile_list.append(part)
        
        return profile_list
    
    @staticmethod
    def select_profile(profile_list, how_to_get):
        """Select profile based on method"""
        if how_to_get == "Sequential by loop":
            loop_index = GlobalVariables().get("loop_index", "0")
            try:
                index = int(loop_index) % len(profile_list)
                return profile_list[index]
            except:
                return profile_list[0]
        else:
            # Random
            return random.choice(profile_list)
    
    @staticmethod
    def load_keywords(params, log_prefix="[GOLOGIN]"):
        """
        Load keywords from file with caching
    
        Args:
            params: Dict containing keywords_file or keywords_variable
            log_prefix: Prefix for log messages
        
        Returns:
            list: List of keywords
        """
        try:
            # Get keywords file - priority: variable > direct path
            keywords_file = None
            keywords_var = params.get("keywords_variable", "").strip()
            if keywords_var:
                keywords_file = GlobalVariables().get(keywords_var, "")
        
            if not keywords_file:
                keywords_file = params.get("keywords_file", "").strip()
        
            if not keywords_file:
                return []
        
            import os
            if not os.path.exists(keywords_file):
                print(f"{log_prefix} Keywords file not found: {keywords_file}")
                return []
        
            # ========== CHECK CACHE FIRST ==========
            if keywords_file in GoLoginProfileHelper._keywords_cache:
                cached = GoLoginProfileHelper._keywords_cache[keywords_file]
                print(f"{log_prefix} ✓ Using cached {len(cached)} keywords")
                return cached
            # ======================================
        
            # Load from file (first time only)
            print(f"{log_prefix} Loading keywords from file (first time)...")
            with open(keywords_file, 'r', encoding='utf-8') as f:
                keywords = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
            if not keywords:
                print(f"{log_prefix} ✗ No valid keywords found in file")
                return []
        
            # ========== SAVE TO CACHE ==========
            GoLoginProfileHelper._keywords_cache[keywords_file] = keywords
            print(f"{log_prefix} ✓ Loaded and cached {len(keywords)} keywords")
            # ==================================
        
            return keywords
        except Exception as e:
            print(f"{log_prefix} Error loading keywords: {e}")
            return []
        

    @staticmethod
    def load_websites(params, log_prefix="[GOLOGIN]"):
        """
        Load websites from file with caching
        
        Args:
            params: Dict containing websites_file or websites_variable
            log_prefix: Prefix for log messages
            
        Returns:
            list: List of website URLs
        """
        try:
            import os
            
            # Get websites file - priority: variable > direct path
            websites_file = None
            websites_var = params.get("websites_variable", "").strip()
            if websites_var:
                from models.global_variables import GlobalVariables
                websites_file = GlobalVariables().get(websites_var, "")
            
            if not websites_file:
                websites_file = params.get("websites_file", "").strip()
            
            if not websites_file or not os.path.exists(websites_file):
                print(f"{log_prefix} ✗ Websites file not found: {websites_file}")
                return []
            
            # ========== CHECK CACHE FIRST ==========
            if websites_file in GoLoginProfileHelper._websites_cache:
                cached = GoLoginProfileHelper._websites_cache[websites_file]
                print(f"{log_prefix} ✓ Using cached {len(cached)} websites")
                return cached
            # ======================================
            
            # Load from file (first time only)
            print(f"{log_prefix} Loading websites from file (first time)...")
            websites = []
            with open(websites_file, 'r', encoding='utf-8') as f:
                for line in f:
                    url = line.strip()
                    if url and not url.startswith('#'):
                        # Fix URL: add https:// if missing protocol
                        if not url.startswith(('http://', 'https://')):
                            url = 'https://' + url
                        websites.append(url)
            
            if not websites:
                print(f"{log_prefix} ✗ No valid URLs found in file")
                return []
            
            # ========== SAVE TO CACHE ==========
            GoLoginProfileHelper._websites_cache[websites_file] = websites
            print(f"{log_prefix} ✓ Loaded and cached {len(websites)} websites")
            # ==================================
            
            return websites
        except Exception as e:
            print(f"{log_prefix} Error loading websites: {e}")
            return []
        

    @staticmethod
    def cleanup_browser_tabs(driver, log_prefix="[GOLOGIN]"):
        """Close all tabs except first one"""
        try:
            all_handles = driver.window_handles
            if len(all_handles) > 1:
                print(f"{log_prefix} Found {len(all_handles)} tabs, closing old tabs...")
                
                # Keep first tab, close others
                first_handle = all_handles[0]
                for handle in all_handles[1:]:
                    try:
                        driver.switch_to.window(handle)
                        driver.close()
                    except:
                        pass
                
                # Switch back to first tab
                driver.switch_to.window(first_handle)
                print(f"{log_prefix} ✓ Cleaned up tabs, using main tab")
            else:
                print(f"{log_prefix} ✓ Only 1 tab, no cleanup needed")
            return True
        except Exception as e:
            print(f"{log_prefix} ⚠ Tab cleanup error: {e}")
            return False
    
    @staticmethod
    def get_chrome_version_from_debugger(debugger_address, log_prefix="[GOLOGIN]"):
        """Get Chrome version from debugger address"""
        try:
            import requests
            host, port = debugger_address.split(":")
            response = requests.get(f"http://{host}:{port}/json/version", timeout=5)
            if response.status_code == 200:
                data = response.json()
                browser_version = data.get("Browser", "")
                if "/" in browser_version:
                    version = browser_version.split("/")[1]
                    major_version = version.split(".")[0]
                    print(f"{log_prefix} Detected Chrome version: {version}")
                    return major_version
        except Exception as e:
            print(f"{log_prefix} Failed to detect Chrome version: {e}")
        return None
    
    @staticmethod
    def connect_selenium(debugger_address, log_prefix="[GOLOGIN]"):
        """Connect Selenium to GoLogin Orbita browser with thread-safe ChromeDriver management"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            import time
        
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", debugger_address)
        
            # Detect Chrome version
            chrome_version = GoLoginProfileHelper.get_chrome_version_from_debugger(
                debugger_address, log_prefix
            )        
            
            
            try:
                if chrome_version:
                    print(f"{log_prefix} Installing ChromeDriver for Chrome {chrome_version}...")
                    chromedriver_path = ChromeDriverManager(driver_version=chrome_version).install()
                else:
                    print(f"{log_prefix} Installing ChromeDriver with auto-detection...")
                    chromedriver_path = ChromeDriverManager().install()
                
                print(f"{log_prefix} ChromeDriver path: {chromedriver_path}")
                
                # Small delay to ensure file is fully written
                time.sleep(0.5)
                
                # Create service
                service = Service(chromedriver_path)
                service.log_output = None
                
            except Exception as install_err:
                print(f"{log_prefix} ✗ ChromeDriver install error: {install_err}")
                raise
        
            # ========== LOCK RELEASED - NOW CREATE WEBDRIVER ==========
            print(f"{log_prefix} Creating WebDriver instance...")
        
            # Retry logic for "file being used" error
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    print(f"{log_prefix} ✓ Selenium connected to Orbita")
                    return driver
            
                except Exception as create_err:
                    error_msg = str(create_err)
                    if "being used by another process" in error_msg or "wrong permissions" in error_msg:
                        if attempt < max_retries - 1:
                            wait_time = 2 + (attempt * 2)
                            print(f"{log_prefix} ⚠ ChromeDriver in use, retrying in {wait_time}s... (attempt {attempt+1}/{max_retries})")
                            time.sleep(wait_time)
                            continue
                        else:
                            print(f"{log_prefix} ✗ ChromeDriver still in use after {max_retries} attempts")
                            raise
                    else:
                        # Other error, raise immediately
                        raise
        
            return None
    
        except Exception as e:
            print(f"{log_prefix} Selenium connection error: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def close_browser_physically(profile_id, driver=None, log_prefix="[GOLOGIN]"):
        """
        Close browser by physically clicking X button - THREAD SAFE
        This ensures browser closes properly before SDK cleanup
        
        Process:
        1. Get browser window position and size
        2. Calculate X button position (top-right corner)
        3. Move mouse to X button
        4. Click X button
        5. Wait for browser to close
        
        Args:
            profile_id: Profile ID
            driver: Optional Selenium WebDriver (to get window position)
            log_prefix: Prefix for log messages
            
        Returns:
            bool: True if successful
        """
        # ========== ACQUIRE WINDOW FOCUS LOCK ==========
        with _window_focus_lock:
            print(f"{log_prefix} [{profile_id}] Closing browser physically...")
            
            try:
                import platform
                if platform.system() != "Windows":
                    print(f"{log_prefix} [{profile_id}] ℹ Physical close not implemented for this OS")
                    return False
                
                import psutil
                import win32gui
                import win32process
                import win32con
                from controllers.actions.mouse_move_action import MouseMoveAction
                import time
                
                # Find browser window for this profile
                hwnd = None
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        cmdline = proc.info.get('cmdline', [])
                        if not cmdline:
                            continue
                        
                        cmdline_str = ' '.join(cmdline).lower()
                        
                        # Check if this is the main browser process for this profile
                        if profile_id.lower() in cmdline_str and '--type=renderer' not in cmdline_str:
                            pid = proc.info['pid']
                            
                            # Find window handle for this process
                            def enum_callback(window_hwnd, pid_list):
                                if win32gui.IsWindowVisible(window_hwnd):
                                    _, found_pid = win32process.GetWindowThreadProcessId(window_hwnd)
                                    if found_pid == pid:
                                        pid_list.append(window_hwnd)
                                return True
                            
                            windows = []
                            win32gui.EnumWindows(enum_callback, windows)
                            
                            if windows:
                                hwnd = windows[0]
                                break
                                
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if not hwnd:
                    print(f"{log_prefix} [{profile_id}] ⚠ Could not find browser window")
                    return False
                
                # Get window position and size
                try:
                    rect = win32gui.GetWindowRect(hwnd)
                    x, y, right, bottom = rect
                    width = right - x
                    height = bottom - y
                    
                    print(f"{log_prefix} [{profile_id}] Window: ({x}, {y}), Size: {width}x{height}")
                    
                    # Calculate X button position (top-right corner)
                    # Windows 11: X button is ~15px from right, ~15px from top
                    # Size: ~47x32 pixels
                    close_button_x = right - 15 - 23  # 23px = half of button width
                    close_button_y = y + 15 + 16      # 16px = half of button height
                    
                    print(f"{log_prefix} [{profile_id}] Calculated X button position: ({close_button_x}, {close_button_y})")
                    
                    # Ensure window is maximized and in front
                    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(0.5)
                    
                    # Move mouse to X button and click
                    print(f"{log_prefix} [{profile_id}] Moving mouse to X button...")
                    MouseMoveAction.move_and_click_static(
                        close_button_x,
                        close_button_y,
                        click_type="single_click",
                        fast=True  # Fast move for cleanup
                    )
                    
                    print(f"{log_prefix} [{profile_id}] ✓ Clicked X button")
                    
                    # Wait for browser to close
                    print(f"{log_prefix} [{profile_id}] Waiting 5s for browser to close...")
                    time.sleep(5)
                    
                    # Verify browser is closed
                    try:
                        if win32gui.IsWindow(hwnd):
                            print(f"{log_prefix} [{profile_id}] ⚠ Window still exists, forcing close...")
                            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                            time.sleep(2)
                    except:
                        pass  # Window already closed
                    
                    print(f"{log_prefix} [{profile_id}] ✓ Browser closed physically")
                    return True
                    
                except Exception as e:
                    print(f"{log_prefix} [{profile_id}] ⚠ Click X button error: {e}")
                    return False
                
            except ImportError as ie:
                print(f"{log_prefix} [{profile_id}] ⚠ Missing dependencies: {ie}")
                return False
            except Exception as e:
                print(f"{log_prefix} [{profile_id}] ⚠ Physical close error: {e}")
                import traceback
                traceback.print_exc()
                return False
        # ========== LOCK RELEASED ==========


    # @staticmethod
    # def bring_profile_to_front(profile_id, driver=None, log_prefix="[GOLOGIN]"):
    #     """
    #     Bring GoLogin profile window to front AND maximize it - THREAD SAFE
    #     Support 2 modes:
    #     - With driver: Use Selenium to maximize (faster, more reliable)
    #     - Without driver: Use win32gui to bring to front + maximize (for multi-threading)
    
    #     Args:
    #         profile_id: Profile ID
    #         driver: Optional Selenium WebDriver instance (for maximize)
    #         log_prefix: Prefix for log messages
    
    #     Returns:
    #         bool: True if successful
    #     """
    
    #     # ========== ACQUIRE WINDOW FOCUS LOCK TO PREVENT CONFLICTS ==========
    #     with _window_focus_lock:
    #         print(f"{log_prefix} [{profile_id}] Acquiring window focus lock...")
        
    #         try:
    #             # MODE 1: If driver provided, use Selenium maximize (RECOMMENDED)
    #             if driver:
    #                 try:
    #                     driver.maximize_window()
    #                     print(f"{log_prefix} [{profile_id}] ✓ Browser maximized via Selenium")
                    
    #                     # Optional: Verify window size
    #                     import time
    #                     time.sleep(0.5)
                    
    #                     window_size = driver.get_window_size()
    #                     print(f"{log_prefix} [{profile_id}] Window size: {window_size['width']}x{window_size['height']}")
                    
    #                     # Delay before releasing lock (let window settle)
    #                     time.sleep(1)
    #                     return True
                    
    #                 except Exception as e:
    #                     print(f"{log_prefix} [{profile_id}] ⚠ Selenium maximize failed: {e}")
    #                     # Continue to MODE 2 as fallback
            
    #             # MODE 2: Use win32gui to bring to front + maximize (for multi-threading or fallback)
    #             import psutil
    #             import platform
            
    #             if platform.system() != "Windows":
    #                 print(f"{log_prefix} [{profile_id}] ℹ Window control not implemented for this OS")
    #                 return False
            
    #             # Find GoLogin Chrome process for this profile
    #             for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    #                 try:
    #                     cmdline = proc.info.get('cmdline', [])
    #                     if not cmdline:
    #                         continue
                    
    #                     cmdline_str = ' '.join(cmdline).lower()
                    
    #                     # Check if this is the main browser process for this profile
    #                     if profile_id.lower() in cmdline_str and '--type=renderer' not in cmdline_str:
    #                         pid = proc.info['pid']
                        
    #                         try:
    #                             import win32gui
    #                             import win32con
    #                             import win32process
                            
    #                             def enum_windows_callback(hwnd, pid_list):
    #                                 if win32gui.IsWindowVisible(hwnd):
    #                                     _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
    #                                     if found_pid == pid:
    #                                         pid_list.append(hwnd)
    #                                 return True
                            
    #                             windows = []
    #                             win32gui.EnumWindows(enum_windows_callback, windows)
                            
    #                             if windows:
    #                                 hwnd = windows[0]
                                
    #                                 # Step 1: Restore window (in case minimized)
    #                                 win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                                
    #                                 # Step 2: Maximize window
    #                                 win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                                
    #                                 # Step 3: Bring to foreground
    #                                 win32gui.SetForegroundWindow(hwnd)
                                
    #                                 print(f"{log_prefix} [{profile_id}] ✓ Brought to front and maximized via win32gui")
                                
    #                                 # Delay before releasing lock
    #                                 time.sleep(1)
    #                                 return True
                        
    #                         except ImportError:
    #                             print(f"{log_prefix} [{profile_id}] ⚠ win32gui not available")
    #                             return False
                
    #                 except (psutil.NoSuchProcess, psutil.AccessDenied):
    #                     continue
            
    #             print(f"{log_prefix} [{profile_id}] ⚠ Could not find browser window")
    #             return False
            
    #         except Exception as e:
    #             print(f"{log_prefix} [{profile_id}] ⚠ Error: {e}")
    #             return False
    #     # ===================================================================

    @staticmethod
    def bring_profile_to_front(profile_id, driver=None, log_prefix="[GOLOGIN]"):
        """
        Bring GoLogin profile window to front AND maximize it - THREAD SAFE
    
        Support 2 modes:
        - With driver: Use Selenium to maximize (faster, more reliable)
        - Without driver: Use win32gui to FORCE bring to front + maximize (for multi-threading)
    
        Args:
            profile_id: Profile ID
            driver: Optional Selenium WebDriver instance (for maximize)
            log_prefix: Prefix for log messages
        
        Returns:
            bool: True if successful
        """
        # ========== ACQUIRE WINDOW FOCUS LOCK TO PREVENT CONFLICTS ==========
        with _window_focus_lock:
            print(f"{log_prefix} [{profile_id}] Acquiring window focus lock...")
        
            try:
                # MODE 1: If driver provided, use Selenium maximize (RECOMMENDED)
                if driver:
                    try:
                        driver.maximize_window()
                        print(f"{log_prefix} [{profile_id}] ✓ Browser maximized via Selenium")
                    
                        # Optional: Verify window size
                        import time
                        time.sleep(0.5)
                        window_size = driver.get_window_size()
                        print(f"{log_prefix} [{profile_id}] Window size: {window_size['width']}x{window_size['height']}")
                    
                        # Try to FORCE bring to front using win32gui (fallback to ensure focus)
                        # This is needed when multiple Chrome windows are open
                        try:
                            import psutil
                            import platform
                        
                            if platform.system() == "Windows":
                                # Find the Chrome window for this profile
                                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                                    try:
                                        cmdline = proc.info.get('cmdline', [])
                                        if not cmdline:
                                            continue
                                    
                                        cmdline_str = ' '.join(cmdline).lower()
                                    
                                        # Check if this is the main browser process for this profile
                                        if profile_id.lower() in cmdline_str and '--type=renderer' not in cmdline_str:
                                            pid = proc.info['pid']
                                        
                                            import win32gui
                                            import win32con
                                            import win32process
                                        
                                            def enum_windows_callback(hwnd, pid_list):
                                                if win32gui.IsWindowVisible(hwnd):
                                                    _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                                                    if found_pid == pid:
                                                        pid_list.append(hwnd)
                                                return True
                                        
                                            windows = []
                                            win32gui.EnumWindows(enum_windows_callback, windows)
                                        
                                            if windows:
                                                hwnd = windows[0]
                                            
                                                # ===== CHECK IF ALREADY IN FOREGROUND FIRST =====
                                                foreground_hwnd = win32gui.GetForegroundWindow()
                                            
                                                if foreground_hwnd == hwnd:
                                                    print(f"{log_prefix} [{profile_id}] ✓ Window already in foreground, skip bring to front")
                                                    time.sleep(0.5)
                                                    return True
                                                # =================================================
                                            
                                                # FORCE bring to front with AttachThreadInput trick
                                                try:
                                                    # Get thread IDs
                                                    foreground_thread = win32process.GetWindowThreadProcessId(foreground_hwnd)[0]
                                                    target_thread = win32process.GetWindowThreadProcessId(hwnd)[0]
                                                
                                                    # Attach threads to allow SetForegroundWindow
                                                    if foreground_thread != target_thread:
                                                        win32process.AttachThreadInput(foreground_thread, target_thread, True)
                                                
                                                    # Restore if minimized
                                                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                                                
                                                    # Maximize
                                                    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                                                
                                                    # Set foreground (now it works because threads are attached)
                                                    win32gui.SetForegroundWindow(hwnd)
                                                
                                                    # Detach threads
                                                    if foreground_thread != target_thread:
                                                        win32process.AttachThreadInput(foreground_thread, target_thread, False)
                                                
                                                    print(f"{log_prefix} [{profile_id}] ✓ FORCED window to foreground")
                                                
                                                except Exception as force_err:
                                                    print(f"{log_prefix} [{profile_id}] ⚠ Force foreground error: {force_err}")
                                            
                                                break
                                            
                                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                                        continue
                        except Exception as force_err:
                            print(f"{log_prefix} [{profile_id}] ℹ Could not force foreground (fallback OK): {force_err}")
                    
                        # Delay before releasing lock (let window settle)
                        time.sleep(1)
                        return True
                    
                    except Exception as e:
                        print(f"{log_prefix} [{profile_id}] ⚠ Selenium maximize failed: {e}")
                        # Continue to MODE 2 as fallback
            
                # MODE 2: Use win32gui to FORCE bring to front + maximize (for multi-threading or fallback)
                import psutil
                import platform
            
                if platform.system() != "Windows":
                    print(f"{log_prefix} [{profile_id}] ℹ Window control not implemented for this OS")
                    return False
            
                # Find GoLogin Chrome process for this profile
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        cmdline = proc.info.get('cmdline', [])
                        if not cmdline:
                            continue
                    
                        cmdline_str = ' '.join(cmdline).lower()
                    
                        # Check if this is the main browser process for this profile
                        if profile_id.lower() in cmdline_str and '--type=renderer' not in cmdline_str:
                            pid = proc.info['pid']
                        
                            try:
                                import win32gui
                                import win32con
                                import win32process
                            
                                def enum_windows_callback(hwnd, pid_list):
                                    if win32gui.IsWindowVisible(hwnd):
                                        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                                        if found_pid == pid:
                                            pid_list.append(hwnd)
                                    return True
                            
                                windows = []
                                win32gui.EnumWindows(enum_windows_callback, windows)
                            
                                if windows:
                                    hwnd = windows[0]
                                
                                    # ===== CHECK IF ALREADY IN FOREGROUND FIRST =====
                                    foreground_hwnd = win32gui.GetForegroundWindow()
                                
                                    if foreground_hwnd == hwnd:
                                        # Already in foreground, just make sure it's maximized
                                        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                                        print(f"{log_prefix} [{profile_id}] ✓ Already in foreground, ensured maximized")
                                        import time
                                        time.sleep(0.5)
                                        return True
                                    # =================================================
                                
                                    # FORCE bring to front with AttachThreadInput trick
                                    try:
                                        # Get thread IDs
                                        foreground_thread = win32process.GetWindowThreadProcessId(foreground_hwnd)[0]
                                        target_thread = win32process.GetWindowThreadProcessId(hwnd)[0]
                                    
                                        # Attach threads to allow SetForegroundWindow
                                        if foreground_thread != target_thread:
                                            win32process.AttachThreadInput(foreground_thread, target_thread, True)
                                    
                                        # Restore if minimized
                                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                                    
                                        # Maximize
                                        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                                    
                                        # Set foreground (now it works because threads are attached)
                                        win32gui.SetForegroundWindow(hwnd)
                                    
                                        # Detach threads
                                        if foreground_thread != target_thread:
                                            win32process.AttachThreadInput(foreground_thread, target_thread, False)
                                    
                                        print(f"{log_prefix} [{profile_id}] ✓ FORCED to front and maximized via win32gui")
                                    
                                    except Exception as force_err:
                                        print(f"{log_prefix} [{profile_id}] ⚠ Force foreground error: {force_err}")
                                        # Fallback to old method
                                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                                        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                                        win32gui.SetForegroundWindow(hwnd)
                                        print(f"{log_prefix} [{profile_id}] ✓ Used fallback method")
                                
                                    # Delay before releasing lock
                                    import time
                                    time.sleep(1)
                                    return True
                                
                            except ImportError:
                                print(f"{log_prefix} [{profile_id}] ⚠ win32gui not available")
                                return False
                            
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            
                print(f"{log_prefix} [{profile_id}] ⚠ Could not find browser window")
                return False
            
            except Exception as e:
                print(f"{log_prefix} [{profile_id}] ⚠ Error: {e}")
                return False



   
    @staticmethod
    def check_and_fix_crashed_tabs(driver, debugger_address, log_prefix="[GOLOGIN]", use_window_lock=True):
        """
        Check for crashed tabs and fix using raw HTTP to Chrome DevTools
        Strategy: Always create new tab first, then close crashed ones
    
        Args:
            driver: Selenium WebDriver instance
            debugger_address: Chrome debugger address (e.g., "127.0.0.1:9222")
            log_prefix: Prefix for log messages
            use_window_lock: If True, use _window_focus_lock when activating (for Start action with physical interaction)
                            If False, no lock (for Collect action with 100% Selenium)
    
        Returns:
            bool: True if successful (no crash or fixed), False if cannot fix
        """
        try:
            from selenium.common.exceptions import WebDriverException
            import time
            import requests
        
            print(f"{log_prefix} Checking for crashed tabs...")
        
            crashed = False
            crashed_handle = None
        
            # Try to detect if current tab is crashed
            try:
                # Try to execute simple script
                driver.execute_script("return 1;")
                print(f"{log_prefix} ✓ No crashed tabs detected")
                return True
            except WebDriverException as e:
                error_msg = str(e).lower()
                if "tab crashed" in error_msg or "target closed" in error_msg:
                    print(f"{log_prefix} ⚠ Selenium reported: Tab crashed")
                    crashed = True
                    # Try to get current window handle (may fail)
                    try:
                        crashed_handle = driver.current_window_handle
                    except:
                        pass
                else:
                    print(f"{log_prefix} ℹ No crash detected (other error ignored)")
                    return True
            except Exception as e:
                print(f"{log_prefix} ℹ Crash check error: {e}")
                return True  # Continue anyway
        
            if not crashed:
                return True
        
            # TAB IS CRASHED - USE RAW HTTP TO CREATE NEW TAB
            print(f"{log_prefix} ✗ Tab crashed, creating new tab via DevTools HTTP API...")
        
            try:
                base_url = f"http://{debugger_address}"
            
                # Step 1: Get all targets BEFORE (for comparison)
                print(f"{log_prefix} Querying existing targets...")
                try:
                    response_before = requests.get(f"{base_url}/json", timeout=5)
                    targets_before = response_before.json() if response_before.status_code == 200 else []
                    target_ids_before = set([t.get("id") for t in targets_before if t.get("type") == "page"])
                    print(f"{log_prefix} Found {len(target_ids_before)} existing page target(s)")
                except Exception as e:
                    print(f"{log_prefix} ⚠ Could not query targets: {e}")
                    target_ids_before = set()
            
                # Step 2: Create new page via HTTP PUT (ALWAYS CREATE NEW)
                print(f"{log_prefix} Creating new tab via HTTP PUT...")
                new_page_response = requests.put(f"{base_url}/json/new?about:blank", timeout=5)
                if new_page_response.status_code not in [200, 201]:
                    print(f"{log_prefix} ✗ Failed to create new page: {new_page_response.status_code}")
                    print(f"{log_prefix} Response: {new_page_response.text}")
                    return False
            
                new_page = new_page_response.json()
                new_page_id = new_page.get("id")
                print(f"{log_prefix} ✓ Created new page with ID: {new_page_id[:12]}...")
                time.sleep(1.5)
            
                # Step 3: Get all targets AFTER
                try:
                    response_after = requests.get(f"{base_url}/json", timeout=5)
                    targets_after = response_after.json() if response_after.status_code == 200 else []
                    target_ids_after = set([t.get("id") for t in targets_after if t.get("type") == "page"])
                    print(f"{log_prefix} Found {len(target_ids_after)} page target(s) after creation")
                
                    # Verify new tab was created
                    if new_page_id not in target_ids_after:
                        print(f"{log_prefix} ⚠ New tab ID not found in target list (may have different ID)")
                except Exception as e:
                    print(f"{log_prefix} ⚠ Could not verify new tab: {e}")
            
                # Step 4: Activate the new page - CONDITIONAL LOCK based on use_window_lock parameter
                if use_window_lock:
                    # Start action: Use lock to prevent window focus conflicts with physical mouse
                    with _window_focus_lock:
                        try:
                            activate_url = f"{base_url}/json/activate/{new_page_id}"
                            activate_response = requests.get(activate_url, timeout=3)
                            if activate_response.status_code == 200:
                                print(f"{log_prefix} ✓ Activated new page (with lock)")
                            else:
                                print(f"{log_prefix} ⚠ Activate returned: {activate_response.status_code}")
                        except Exception as activate_err:
                            print(f"{log_prefix} ⚠ Could not activate: {activate_err}")
        
                        time.sleep(0.5)  # Let window settle inside lock
                else:
                    # Collect action: No lock needed (100% Selenium, no physical interaction)
                    try:
                        activate_url = f"{base_url}/json/activate/{new_page_id}"
                        activate_response = requests.get(activate_url, timeout=3)
                        if activate_response.status_code == 200:
                            print(f"{log_prefix} ✓ Activated new page (no lock)")
                        else:
                            print(f"{log_prefix} ⚠ Activate returned: {activate_response.status_code}")
                    except Exception as activate_err:
                        print(f"{log_prefix} ⚠ Could not activate: {activate_err}")
    
                    time.sleep(0.5)  # Let window settle
                # ← KẾT THÚC LOCK
            
                # Step 5: Get fresh window handles
                handles = driver.window_handles
                print(f"{log_prefix} Found {len(handles)} Selenium handle(s)")
            
                if len(handles) == 0:
                    print(f"{log_prefix} ✗ No handles available")
                    return False
            
                # Step 6: Try each handle until we find one that works
                working_handle = None
                for i, handle in enumerate(handles):
                    try:
                        driver.switch_to.window(handle)
                        # Test if this handle works
                        driver.execute_script("return 1;")
                        working_handle = handle
                        print(f"{log_prefix} ✓ Found working handle at index {i}")
                        break
                    except WebDriverException:
                        print(f"{log_prefix} ℹ Handle {i} is crashed, trying next...")
                        continue
            
                if working_handle:
                    # Navigate to about:blank to ensure clean state
                    try:
                        driver.get("about:blank")
                        print(f"{log_prefix} ✓ Successfully switched to working tab")
                    except Exception as nav_err:
                        print(f"{log_prefix} ⚠ Navigate error: {nav_err}")
                
                    # Step 7: Close crashed handles
                    print(f"{log_prefix} Closing crashed tab(s)...")
                    closed_count = 0
                    for handle in handles:
                        if handle != working_handle:
                            try:
                                driver.switch_to.window(handle)
                                driver.close()
                                closed_count += 1
                                print(f"{log_prefix} ✓ Closed crashed tab")
                            except Exception:
                                pass
                
                    # Switch back to working handle
                    remaining = driver.window_handles
                    if remaining:
                        driver.switch_to.window(remaining[0])
                        print(f"{log_prefix} ✓ Fixed crashed tab(s) - created 1 new, closed {closed_count} crashed")
                        return True
                    else:
                        print(f"{log_prefix} ✗ All handles are crashed")
                        return False
                else:
                    print(f"{log_prefix} ✗ All handles are crashed")
                    return False
                
            except requests.exceptions.RequestException as http_err:
                print(f"{log_prefix} ✗ HTTP request failed: {http_err}")
                return False
            except Exception as fix_err:
                print(f"{log_prefix} ✗ Fix failed: {fix_err}")
                import traceback
                traceback.print_exc()
                return False
            
        except Exception as e:
            print(f"{log_prefix} ✗ Crash check error: {e}")
            import traceback
            traceback.print_exc()
            return True  # Continue anyway
