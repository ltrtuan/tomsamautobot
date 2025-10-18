﻿# helpers/gologin_profile_helper.py

from models.global_variables import GlobalVariables
from models.gologin_api import get_gologin_api
import random

class GoLoginProfileHelper:
    """Helper class for common GoLogin profile operations"""
    
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
        """Load keywords from file for YouTube/Google search"""
        try:
            # Get keywords file path
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
            
            # Read keywords
            with open(keywords_file, 'r', encoding='utf-8') as f:
                keywords = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if keywords:
                print(f"{log_prefix} Loaded {len(keywords)} keywords from file")
            return keywords
        except Exception as e:
            print(f"{log_prefix} Error loading keywords: {e}")
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
        """Connect Selenium to GoLogin Orbita browser"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", debugger_address)
            
            # Detect Chrome version
            chrome_version = GoLoginProfileHelper.get_chrome_version_from_debugger(
                debugger_address, log_prefix
            )
            
            if chrome_version:
                print(f"{log_prefix} Installing ChromeDriver for Chrome {chrome_version}...")
                service = Service(ChromeDriverManager(driver_version=chrome_version).install())
            else:
                print(f"{log_prefix} Installing ChromeDriver with auto-detection...")
                service = Service(ChromeDriverManager().install())
            
            # Disable ChromeDriver logs
            service.log_output = None
            
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print(f"{log_prefix} ✓ Selenium connected to Orbita")
            return driver
        except Exception as e:
            print(f"{log_prefix} Selenium connection error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def bring_profile_to_front(profile_id, driver=None, log_prefix="[GOLOGIN]"):
        """
        Bring GoLogin profile window to front AND maximize it
        Support 2 modes:
        - With driver: Use Selenium to maximize (faster, more reliable)
        - Without driver: Use win32gui to bring to front + maximize (for multi-threading)
    
        Args:
            profile_id: Profile ID
            driver: Optional Selenium WebDriver instance (for maximize)
            log_prefix: Prefix for log messages
        
        Returns:
            bool: True if successful
        """
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
                
                    return True
                except Exception as e:
                    print(f"{log_prefix} [{profile_id}] ⚠ Selenium maximize failed: {e}")
                    # Continue to MODE 2 as fallback
        
            # MODE 2: Use win32gui to bring to front + maximize (for multi-threading or fallback)
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
                            
                                # Step 1: Restore window (in case minimized)
                                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                            
                                # Step 2: Maximize window
                                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                            
                                # Step 3: Bring to foreground
                                win32gui.SetForegroundWindow(hwnd)
                            
                                print(f"{log_prefix} [{profile_id}] ✓ Brought to front and maximized via win32gui")
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
    def check_and_fix_crashed_tabs(driver, debugger_address, log_prefix="[GOLOGIN]"):
        """
        Check for crashed tabs and fix using raw HTTP to Chrome DevTools
        Strategy: Always create new tab first, then close crashed ones
    
        Args:
            driver: Selenium WebDriver instance
            debugger_address: Chrome debugger address (e.g., "127.0.0.1:9222")
            log_prefix: Prefix for log messages
        
        Returns:
            bool: True if successful (no crash or fixed), False if cannot fix
        """
        try:
            from selenium.common.exceptions import WebDriverException
            import time
            import requests
        
            print(f"{log_prefix} Checking for crashed tabs...")
        
            # Try to detect if current tab is crashed
            crashed = False
            crashed_handle = None
        
            try:
                # Try to execute simple script
                driver.execute_script("return 1")
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
                    print(f"{log_prefix} ✓ No crash detected (other error ignored)")
                    return True
        
            if not crashed:
                return True
        
            # ========== TAB IS CRASHED - USE RAW HTTP TO CREATE NEW TAB ==========
            print(f"{log_prefix} ✗ Tab crashed, creating new tab via DevTools HTTP API...")
        
            try:
                # Parse debugger address
                if ":" in debugger_address:
                    host, port = debugger_address.split(":")
                else:
                    host = "127.0.0.1"
                    port = debugger_address
            
                base_url = f"http://{host}:{port}"
            
                # Step 1: Get all targets BEFORE (for comparison)
                print(f"{log_prefix} Querying existing targets...")
                try:
                    response_before = requests.get(f"{base_url}/json", timeout=5)
                    targets_before = response_before.json() if response_before.status_code == 200 else []
                    target_ids_before = set(t.get('id') for t in targets_before if t.get('type') == 'page')
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
                new_page_id = new_page.get('id')
                print(f"{log_prefix} ✓ Created new page with ID: {new_page_id[:12]}...")
            
                time.sleep(1.5)
            
                # Step 3: Get all targets AFTER
                try:
                    response_after = requests.get(f"{base_url}/json", timeout=5)
                    targets_after = response_after.json() if response_after.status_code == 200 else []
                    target_ids_after = set(t.get('id') for t in targets_after if t.get('type') == 'page')
                    print(f"{log_prefix} Found {len(target_ids_after)} page target(s) after creation")
                
                    # Verify new tab was created
                    if new_page_id not in target_ids_after:
                        print(f"{log_prefix} ⚠ New tab ID not found in target list (may have different ID)")
                except Exception as e:
                    print(f"{log_prefix} ⚠ Could not verify new tab: {e}")
            
                # Step 4: Activate the new page
                try:
                    activate_url = f"{base_url}/json/activate/{new_page_id}"
                    activate_response = requests.get(activate_url, timeout=3)
                    if activate_response.status_code == 200:
                        print(f"{log_prefix} ✓ Activated new page")
                    else:
                        print(f"{log_prefix} ⚠ Activate returned {activate_response.status_code}")
                except Exception as activate_err:
                    print(f"{log_prefix} ⚠ Could not activate: {activate_err}")
            
                time.sleep(1)
            
                # Step 5: Try to switch Selenium to new tab
                print(f"{log_prefix} Switching Selenium to new tab...")
                try:
                    # Get fresh window handles
                    handles = driver.window_handles
                    print(f"{log_prefix} Found {len(handles)} Selenium handle(s)")
                
                    if len(handles) == 0:
                        print(f"{log_prefix} ✗ No handles available")
                        return False
                
                    # Try each handle until we find one that works
                    working_handle = None
                    for i, handle in enumerate(handles):
                        try:
                            driver.switch_to.window(handle)
                            # Test if this handle works
                            driver.execute_script("return 1")
                            working_handle = handle
                            print(f"{log_prefix} ✓ Found working handle at index {i}")
                            break
                        except WebDriverException:
                            print(f"{log_prefix} Handle {i} is crashed, trying next...")
                            continue
                
                    if working_handle:
                        # Navigate to about:blank to ensure clean state
                        try:
                            driver.get("about:blank")
                            print(f"{log_prefix} ✓ Successfully switched to working tab")
                        except Exception as nav_err:
                            print(f"{log_prefix} ⚠ Navigate error: {nav_err}")
                    
                        # Step 6: Close crashed handles
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
                                    # May already be closed or unreachable
                                    pass
                    
                        # Switch back to working handle
                        try:
                            driver.switch_to.window(working_handle)
                        except:
                            # Use remaining handles
                            remaining = driver.window_handles
                            if remaining:
                                driver.switch_to.window(remaining[0])
                    
                        print(f"{log_prefix} ✓ Fixed crashed tab(s) - created 1 new, closed {closed_count} crashed")
                        return True
                    else:
                        print(f"{log_prefix} ✗ All handles are crashed")
                        return False
            
                except Exception as selenium_err:
                    print(f"{log_prefix} ✗ Selenium operations failed: {selenium_err}")
                    # New tab was created via HTTP, but Selenium can't access it
                    # This might require reconnecting Selenium
                    print(f"{log_prefix} ℹ New tab exists in browser, but Selenium session may need reconnect")
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
            print(f"{log_prefix} ⚠ Crash check error: {e}")
            import traceback
            traceback.print_exc()
            return True  # Continue anyway




    @staticmethod
    def kill_zombie_chrome_processes(profile_id, log_prefix="[GOLOGIN]"):
        """
        Kill ONLY GoLogin Orbita browser processes for this specific profile
        Does NOT kill GoLogin.exe main application
    
        Args:
            profile_id: Profile ID to clean up
            log_prefix: Prefix for log messages
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import psutil
            import os
            print(f"{log_prefix} [{profile_id}] Checking for zombie Orbita processes...")
        
            killed_count = 0
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    proc_name = proc.info['name'].lower()
                    proc_exe = proc.info.get('exe', '')
                    cmdline = proc.info.get('cmdline', [])
                
                    # ========== CRITICAL: ONLY MATCH CHROME.EXE, NOT GOLOGIN.EXE ==========
                    # Skip if this is GoLogin main app
                    if proc_name in ['gologin.exe', 'gologin']:
                        continue
                
                    # Only target chrome.exe processes
                    if proc_name not in ['chrome.exe', 'chrome']:
                        continue
                
                    # Check if this chrome.exe is from GoLogin/Orbita directory
                    is_gologin_orbita = False
                    if proc_exe:
                        proc_exe_lower = proc_exe.lower()
                    
                        # Check for GoLogin Orbita browser paths
                        if '.gologin' in proc_exe_lower and 'orbita' in proc_exe_lower:
                            is_gologin_orbita = True
                        elif 'appdata\\local\\gologin\\browser' in proc_exe_lower:
                            is_gologin_orbita = True
                        elif 'appdata/local/gologin/browser' in proc_exe_lower:
                            is_gologin_orbita = True
                        elif '\\gologin\\browser\\orbita' in proc_exe_lower:
                            is_gologin_orbita = True
                        elif '/gologin/browser/orbita' in proc_exe_lower:
                            is_gologin_orbita = True
                
                    if not is_gologin_orbita:
                        continue
                
                    # Check if this browser belongs to the specific profile
                    belongs_to_profile = False
                    if cmdline:
                        cmdline_str = ' '.join(cmdline).lower()
                    
                        # Profile ID must be in user-data-dir or profile-directory
                        if profile_id.lower() in cmdline_str:
                            # Must have user-data-dir or profile-directory to confirm it's a profile browser
                            if '--user-data-dir' in cmdline_str or '--profile-directory' in cmdline_str:
                                belongs_to_profile = True
                
                    # Kill ONLY if:
                    # 1. It's chrome.exe (not GoLogin.exe)
                    # 2. It's from GoLogin Orbita directory
                    # 3. It belongs to this specific profile
                    if is_gologin_orbita and belongs_to_profile:
                        print(f"{log_prefix} [{profile_id}] Killing zombie Orbita PID {proc.info['pid']} ({proc_name})")
                        proc.kill()
                        killed_count += 1
            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        
            if killed_count > 0:
                print(f"{log_prefix} [{profile_id}] ✓ Killed {killed_count} zombie Orbita process(es)")
                import time
                time.sleep(2)
            else:
                print(f"{log_prefix} [{profile_id}] ✓ No zombie Orbita processes found")
        
            return True
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ⚠ Zombie check error: {e}")
            return False

