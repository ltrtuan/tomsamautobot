# controllers/actions/gologin_selenium_start_action.py

from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from models.gologin_api import get_gologin_api
import random
import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from helpers.selenium_registry import register_selenium_driver, unregister_selenium_driver

class GoLoginSeleniumStartAction(BaseAction):
    """Handler for GoLogin Selenium Start Profile action - Fast cookies import"""
    
    def prepare_play(self):
        """Execute GoLogin Selenium Start Profile"""
        try:
            # Get API token from variable name
            api_key_variable = self.params.get("api_key_variable", "").strip()
            if not api_key_variable:
                print("[GOLOGIN START] Error: API key variable name is required")
                self.set_variable(False)
                return
            
            # Get API token value from GlobalVariables
            api_token = GlobalVariables().get(api_key_variable, "")
            if not api_token:
                print(f"[GOLOGIN START] Error: Variable '{api_key_variable}' is empty or not set")
                self.set_variable(False)
                return
            
            print(f"[GOLOGIN START] Using API token from variable: {api_key_variable}")
            
            # Get profile IDs
            profile_ids = self.params.get("profile_ids", "").strip()
            if not profile_ids:
                print("[GOLOGIN START] Error: Profile IDs are required")
                self.set_variable(False)
                return
            
            # Parse profile IDs
            profile_list = self._parse_profile_ids(profile_ids)
            if not profile_list:
                print("[GOLOGIN START] Error: No valid profile IDs found")
                self.set_variable(False)
                return
            
            print(f"[GOLOGIN START] Total profiles to start: {len(profile_list)}")
            
            # ========== CHECK AND UPDATE PROXY IF PROVIDED ==========
            # Get proxy variable names
            proxy_mode_var = self.params.get("proxy_mode_variable", "").strip()
            proxy_host_var = self.params.get("proxy_host_variable", "").strip()
            proxy_port_var = self.params.get("proxy_port_variable", "").strip()
            proxy_username_var = self.params.get("proxy_username_variable", "").strip()
            proxy_password_var = self.params.get("proxy_password_variable", "").strip()
            
            # Check if all 5 variable names are provided
            if proxy_mode_var and proxy_host_var and proxy_port_var and proxy_username_var and proxy_password_var:
                print("[GOLOGIN START] ========== PROXY UPDATE ==========")
                print("[GOLOGIN START] Proxy configuration detected, retrieving values from variables...")
                
                # Get actual values from GlobalVariables
                proxy_mode = GlobalVariables().get(proxy_mode_var, "")
                proxy_host = GlobalVariables().get(proxy_host_var, "")
                proxy_port = GlobalVariables().get(proxy_port_var, "")
                proxy_username = GlobalVariables().get(proxy_username_var, "")
                proxy_password = GlobalVariables().get(proxy_password_var, "")
                
                # Check if all values are non-empty
                if proxy_mode and proxy_host and proxy_port and proxy_username and proxy_password:
                    proxy_config = {
                        "mode": proxy_mode,
                        "host": proxy_host,
                        "port": proxy_port,
                        "username": proxy_username,
                        "password": proxy_password
                    }
                    
                    print(f"[GOLOGIN START] Retrieved proxy values:")
                    print(f"[GOLOGIN START]   Mode: {proxy_mode} (from {proxy_mode_var})")
                    print(f"[GOLOGIN START]   Host: {proxy_host} (from {proxy_host_var})")
                    print(f"[GOLOGIN START]   Port: {proxy_port} (from {proxy_port_var})")
                    print(f"[GOLOGIN START]   Username: {proxy_username} (from {proxy_username_var})")
                    
                    # Get GoLogin API instance
                    gologin_api = get_gologin_api(api_token)
                    
                    # Call GoLoginAPI method to update proxy
                    proxy_success, proxy_message = gologin_api.update_proxy_for_profiles(profile_list, proxy_config)
                    
                    if proxy_success:
                        print(f"[GOLOGIN START] ✓ {proxy_message}")
                    else:
                        print(f"[GOLOGIN START] ⚠ Warning: {proxy_message}")
                        print("[GOLOGIN START] Continuing without proxy update...")
                else:
                    print("[GOLOGIN START] ⚠ Warning: Some proxy variables are empty, skipping proxy update")
                print("[GOLOGIN START] ===================================")
            else:
                print("[GOLOGIN START] No proxy configuration provided (variable names missing), skipping proxy update")
            
            # SEQUENTIAL MODE - Select 1 profile and start
            print("[GOLOGIN START] ========== SEQUENTIAL MODE ==========")
            how_to_get = self.params.get("how_to_get", "Random")
            profile_id = self._select_profile(profile_list, how_to_get)
            print(f"[GOLOGIN START] Selected profile ID: {profile_id}")
            
            # Start single profile
            success = self._start_single_profile(profile_id, api_token)
            self.set_variable(success)
            
        except Exception as e:
            print(f"[GOLOGIN START] Error: {e}")
            import traceback
            traceback.print_exc()
            self.set_variable(False)
    
    def _start_single_profile(self, profile_id, api_token):
        """Start a single profile and import cookies"""
        driver = None
        try:
            print(f"\n[GOLOGIN START] [{profile_id}] Starting profile...")
            
            # Get options
            refresh_fingerprint = self.params.get("refresh_fingerprint", False)
         
            
            # Get GoLogin API instance
            gologin = get_gologin_api(api_token)
            
            # Refresh fingerprint if requested
            if refresh_fingerprint:
                print(f"[GOLOGIN START] [{profile_id}] Refreshing fingerprint...")
                success = gologin.refresh_fingerprint(profile_id)
                if success:
                    print(f"[GOLOGIN START] [{profile_id}] ✓ Fingerprint refreshed")
                else:
                    print(f"[GOLOGIN START] [{profile_id}] ⚠ Failed to refresh fingerprint")          
            
            # Start profile
            print(f"[GOLOGIN START] [{profile_id}] Starting profile...")
            
            # NO extra_params needed for fast start
            extra_params = [
                 "--enable-logging",  # Enable logging
                "--v=1",  # Verbose level
                "--disk-cache-size=0",  # Disable cache to force writes
                "--media-cache-size=0",
                "--enable-features=NetworkService",
                "--disable-features=CookiesWithoutSameSiteMustBeSecure"
            ]
            
            success, debugger_address = gologin.start_profile(profile_id, extra_params=extra_params)
            if not success:
                print(f"[GOLOGIN START] [{profile_id}] ✗ Failed to start profile: {debugger_address}")
                return False
            
            print(f"[GOLOGIN START] [{profile_id}] ✓ Profile started: {debugger_address}")
            
            # Connect Selenium
            driver = self._start_selenium_profile(debugger_address)
            if not driver:
                print(f"[GOLOGIN START] [{profile_id}] ✗ Failed to connect Selenium")
                gologin.stop_profile(profile_id)
                return False
            
            # ← REGISTER DRIVER FOR AUTO-CLEANUP
            register_selenium_driver(driver)
            
            # Clean up old tabs from previous sessions
            print(f"[GOLOGIN START] [{profile_id}] Checking browser tabs...")
            self._cleanup_browser_tabs(driver)
            
            # Wait for browser data to settle
            print(f"[GOLOGIN START] [{profile_id}] Waiting for browser data to settle...")
            time.sleep(3)
                
            # Save profile_id
            GlobalVariables().set("GOLOGIN_PROFILE_ID", profile_id)
            print(f"[GOLOGIN START] Saved: GOLOGIN_PROFILE_ID = {profile_id}")

            # Save debugger_address for reconnect later
            GlobalVariables().set("GOLOGIN_DEBUGGER_ADDRESS", debugger_address)
            print(f"[GOLOGIN START] Saved: GOLOGIN_DEBUGGER_ADDRESS = {debugger_address}")
            
            return True
            
        except Exception as e:
            print(f"[GOLOGIN START] [{profile_id}] ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # CLEANUP DRIVER (browser stays open because it's managed by GoLogin)
            if driver:
                try:
                    # Unregister first
                    unregister_selenium_driver(driver)
                
                    # Then quit ChromeDriver
                    driver.quit()
                    print(f"[GOLOGIN START] ✓ ChromeDriver cleaned up (browser stays open)")
                except Exception as e:
                    print(f"[GOLOGIN START] ⚠ Cleanup warning: {e}")
    
    # ========== COPY NGUYÊN CÁC METHODS TỪ COLLECT ==========
    
    def _parse_profile_ids(self, profile_ids_text):
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
                    print(f"[GOLOGIN START] Warning: Variable '{var_name}' is empty")
            else:
                profile_list.append(part)
        return profile_list
    
    def _select_profile(self, profile_list, how_to_get):
        """Select profile based on method"""
        print(f"how_to_gethow_to_gethow_to_gethow_to_gethow_to_gethow_to_gethow_to_get'{how_to_get}' is empty")
        if how_to_get == "Sequential by loop":
            # Get current index from global variable
            loop_index = GlobalVariables().get("loop_index", "0")
            try:
                index = int(loop_index) % len(profile_list)
                return profile_list[index]
            except:
                return profile_list[0]
        else:
            # Random
            return random.choice(profile_list)
    
    def _import_cookies_if_provided(self, gologin, profile_id):
        """Import cookies if folder path provided"""
        try:
            # Get cookies folder
            cookies_folder = None
            cookies_folder_var = self.params.get("cookies_folder_variable", "").strip()
            if cookies_folder_var:
                cookies_folder = GlobalVariables().get(cookies_folder_var, "")
            
            if not cookies_folder:
                cookies_folder = self.params.get("cookies_folder", "").strip()
            
            if not cookies_folder or not os.path.exists(cookies_folder):
                return False
            
            # Get all JSON files
            json_files = [f for f in os.listdir(cookies_folder) if f.endswith('.json')]
            if not json_files:
                print(f"[GOLOGIN START] No JSON files found in cookies folder")
                return False
            
            # Random pick one file
            selected_file = random.choice(json_files)
            cookies_file_path = os.path.join(cookies_folder, selected_file)
            print(f"[GOLOGIN START] Randomly selected cookies file: {selected_file}")
            
            # Load cookies from file
            with open(cookies_file_path, 'r', encoding='utf-8') as f:
                cookies_from_file = json.load(f)
            
            if not cookies_from_file:
                print(f"[GOLOGIN START] ⚠ Cookies file is empty")
                return False
            
            print(f"[GOLOGIN START] Loaded {len(cookies_from_file)} cookies from file")
            
            # Parse to GoLogin format
            cookies_for_api = self._parse_cookies_to_gologin_format(cookies_from_file)
            if not cookies_for_api:
                print(f"[GOLOGIN START] ⚠ No valid cookies after parsing")
                return False
            
            print(f"[GOLOGIN START] Parsed {len(cookies_for_api)} valid cookies")
            
            # Import cookies via API
            success, result = gologin.update_cookies(profile_id, cookies_for_api, replace_all=True)
            if success:
                print(f"[GOLOGIN START] ✓ Imported {len(cookies_for_api)} cookies from {selected_file}")
                return True
            else:
                print(f"[GOLOGIN START] ⚠ Failed to import cookies: {result}")
                return False
                
        except Exception as e:
            print(f"[GOLOGIN START] Error importing cookies: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _parse_cookies_to_gologin_format(self, cookies_from_file):
        """Parse cookies from Selenium/browser format to GoLogin API format"""
        try:
            cookies_for_api = []
            for cookie in cookies_from_file:
                # Skip invalid cookies
                if not cookie.get("name") or not cookie.get("domain"):
                    continue
                
                # Build GoLogin API format
                api_cookie = {
                    "name": cookie.get("name"),
                    "value": cookie.get("value", ""),
                    "domain": cookie.get("domain"),
                    "path": cookie.get("path", "/"),
                    "secure": cookie.get("secure", False),
                    "httpOnly": cookie.get("httpOnly", False),
                    "hostOnly": cookie.get("hostOnly", False),
                    "session": cookie.get("session", False)
                }
                
                # Add expirationDate if not session cookie
                if not cookie.get("session", False):
                    if "expirationDate" in cookie:
                        api_cookie["expirationDate"] = cookie["expirationDate"]
                    elif "expiry" in cookie:
                        api_cookie["expirationDate"] = cookie["expiry"]
                
                # Add sameSite if present
                if "sameSite" in cookie:
                    same_site = cookie["sameSite"]
                    if same_site and same_site.lower() != "unspecified":
                        api_cookie["sameSite"] = same_site
                
                cookies_for_api.append(api_cookie)
            
            return cookies_for_api
            
        except Exception as e:
            print(f"[GOLOGIN START] Error parsing cookies: {e}")
            return []
    
    def _start_selenium_profile(self, debugger_address):
        """Connect Selenium to GoLogin Orbita browser - COPY TỪ COLLECT"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", debugger_address)
            
            # Detect Chrome version
            chrome_version = self._get_chrome_version_from_debugger(debugger_address)
            
            if chrome_version:
                print(f"[GOLOGIN START] Installing ChromeDriver for Chrome {chrome_version}...")
                service = Service(ChromeDriverManager(driver_version=chrome_version).install())
            else:
                print(f"[GOLOGIN START] Installing ChromeDriver with auto-detection...")
                service = Service(ChromeDriverManager().install())
            
            # Disable ChromeDriver logs
            service.log_output = None
            
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print(f"[GOLOGIN START] ✓ Selenium connected to Orbita")
            return driver
            
        except Exception as e:
            print(f"[GOLOGIN START] Selenium connection error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _cleanup_browser_tabs(self, driver):
        """Close all tabs except first one - COPY TỪ COLLECT"""
        try:
            all_handles = driver.window_handles
            if len(all_handles) > 1:
                print(f"[GOLOGIN START] Found {len(all_handles)} tabs, closing old tabs...")
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
                print(f"[GOLOGIN START] ✓ Cleaned up tabs, using main tab")
            else:
                print(f"[GOLOGIN START] ✓ Only 1 tab, no cleanup needed")
            return True
        except Exception as e:
            print(f"[GOLOGIN START] ⚠ Tab cleanup error: {e}")
            return False
    
    def _get_chrome_version_from_debugger(self, debugger_address):
        """Get Chrome version from debugger - COPY TỪ COLLECT"""
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
                    print(f"[GOLOGIN START] Detected Chrome version: {version}")
                    return major_version
        except Exception as e:
            print(f"[GOLOGIN START] Failed to detect Chrome version: {e}")
        return None
    
    def _inject_cookies_via_cdp(self, driver, profile_id):
        """Inject cookies using Chrome DevTools Protocol - COPY TỪ COLLECT"""
        try:
            # Get cookies folder
            cookies_folder = None
            cookies_folder_var = self.params.get("cookies_folder_variable", "").strip()
            if cookies_folder_var:
                cookies_folder = GlobalVariables().get(cookies_folder_var, "")
            
            if not cookies_folder:
                cookies_folder = self.params.get("cookies_folder", "").strip()
            
            if not cookies_folder or not os.path.exists(cookies_folder):
                print(f"[GOLOGIN START] [{profile_id}] No cookies folder")
                return False
            
            # Get all JSON files
            json_files = [f for f in os.listdir(cookies_folder) if f.endswith('.json')]
            if not json_files:
                print(f"[GOLOGIN START] [{profile_id}] No JSON files found")
                return False
            
            # Random pick one file
            selected_file = random.choice(json_files)
            cookies_file_path = os.path.join(cookies_folder, selected_file)
            print(f"[GOLOGIN START] [{profile_id}] Injecting cookies via CDP from: {selected_file}")
            
            # Load cookies from file
            with open(cookies_file_path, 'r', encoding='utf-8') as f:
                cookies_from_file = json.load(f)
            
            if not cookies_from_file:
                print(f"[GOLOGIN START] [{profile_id}] Cookies file is empty")
                return False
            
            print(f"[GOLOGIN START] [{profile_id}] Loaded {len(cookies_from_file)} cookies")
            
            # Get CDP connection
            try:
                driver.execute_cdp_cmd("Network.enable", {})
                print(f"[GOLOGIN START] [{profile_id}] ✓ CDP connection established")
            except Exception as cdp_err:
                print(f"[GOLOGIN START] [{profile_id}] ✗ CDP not available: {cdp_err}")
                return False
            
            # Inject cookies using CDP
            injected_count = 0
            failed_count = 0
            
            for cookie in cookies_from_file:
                try:
                    # Build CDP cookie format
                    cdp_cookie = {
                        "name": cookie.get("name"),
                        "value": cookie.get("value", ""),
                        "domain": cookie.get("domain"),
                        "path": cookie.get("path", "/"),
                        "secure": cookie.get("secure", False),
                        "httpOnly": cookie.get("httpOnly", False)
                    }
                    
                    # Add expiry if exists
                    if "expirationDate" in cookie and not cookie.get("session", False):
                        cdp_cookie["expires"] = cookie["expirationDate"]
                    
                    # Add sameSite if valid
                    if "sameSite" in cookie:
                        same_site = cookie["sameSite"]
                        if same_site and same_site.lower() != "unspecified":
                            cdp_cookie["sameSite"] = same_site.capitalize()
                    
                    # Execute CDP command
                    driver.execute_cdp_cmd("Network.setCookie", cdp_cookie)
                    injected_count += 1
                    
                except Exception as cookie_err:
                    failed_count += 1
                    continue
            
            print(f"[GOLOGIN START] [{profile_id}] ✓ CDP injection complete: {injected_count} success, {failed_count} failed")
            return injected_count > 0
            
        except Exception as e:
            print(f"[GOLOGIN START] [{profile_id}] Error injecting cookies via CDP: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _close_all_tabs(self, driver):
        """Close all tabs except last one - COPY TỪ COLLECT"""
        try:
            all_handles = driver.window_handles
            if len(all_handles) <= 1:
                print(f"[GOLOGIN START] Only 1 tab open, no need to close")
                return True
            
            print(f"[GOLOGIN START] Closing {len(all_handles) - 1} tabs...")
            
            # Keep the first tab, close all others
            first_handle = all_handles[0]
            for handle in all_handles[1:]:
                try:
                    driver.switch_to.window(handle)
                    driver.close()
                    time.sleep(0.5)
                except Exception as e:
                    print(f"[GOLOGIN START] ⚠ Failed to close tab: {e}")
            
            # Switch back to first tab
            try:
                driver.switch_to.window(first_handle)
            except:
                pass
            
            print(f"[GOLOGIN START] ✓ All tabs closed")
            return True
            
        except Exception as e:
            print(f"[GOLOGIN START] ⚠ Error closing tabs: {e}")
            return False
    
    def set_variable(self, success):
        """Set variable with result"""
        variable = self.params.get("variable", "")
        if variable:
            GlobalVariables().set(variable, "true" if success else "false")
