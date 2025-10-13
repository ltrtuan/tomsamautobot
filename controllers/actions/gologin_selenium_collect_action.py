# controllers/actions/gologin_selenium_collect_action.py

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

class GoLoginSeleniumCollectAction(BaseAction):
    """Handler for GoLogin Selenium Warm Up action"""
    
    def prepare_play(self):
        """Execute GoLogin Selenium Warm Up"""
        try:
            # Get API token from variable name
            api_key_variable = self.params.get("api_key_variable", "").strip()
            if not api_key_variable:
                print("[GOLOGIN WARMUP] Error: API key variable name is required")
                self.set_variable(False)
                return
        
            # Get API token value from GlobalVariables
            api_token = GlobalVariables().get(api_key_variable, "")
            if not api_token:
                print(f"[GOLOGIN WARMUP] Error: Variable '{api_key_variable}' is empty or not set")
                self.set_variable(False)
                return
        
            print(f"[GOLOGIN WARMUP] Using API token from variable: {api_key_variable}")
        
            # Get profile IDs
            profile_ids = self.params.get("profile_ids", "").strip()
            if not profile_ids:
                print("[GOLOGIN WARMUP] Error: Profile IDs are required")
                self.set_variable(False)
                return
        
            # Parse profile IDs
            profile_list = self._parse_profile_ids(profile_ids)
            if not profile_list:
                print("[GOLOGIN WARMUP] Error: No valid profile IDs found")
                self.set_variable(False)
                return
        
            print(f"[GOLOGIN WARMUP] Total profiles to warm up: {len(profile_list)}")
            
            # ========== CHECK AND UPDATE PROXY IF PROVIDED ==========
            # Get proxy variable names
            proxy_mode_var = self.params.get("proxy_mode_variable", "").strip()
            proxy_host_var = self.params.get("proxy_host_variable", "").strip()
            proxy_port_var = self.params.get("proxy_port_variable", "").strip()
            proxy_username_var = self.params.get("proxy_username_variable", "").strip()
            proxy_password_var = self.params.get("proxy_password_variable", "").strip()

            # Check if all 5 variable names are provided
            if proxy_mode_var and proxy_host_var and proxy_port_var and proxy_username_var and proxy_password_var:
                print("[GOLOGIN WARMUP] ========== PROXY UPDATE ==========")
                print("[GOLOGIN WARMUP] Proxy configuration detected, retrieving values from variables...")
    
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
        
                    print(f"[GOLOGIN WARMUP] Retrieved proxy values:")
                    print(f"[GOLOGIN WARMUP]   Mode: {proxy_mode} (from {proxy_mode_var})")
                    print(f"[GOLOGIN WARMUP]   Host: {proxy_host} (from {proxy_host_var})")
                    print(f"[GOLOGIN WARMUP]   Port: {proxy_port} (from {proxy_port_var})")
                    print(f"[GOLOGIN WARMUP]   Username: {proxy_username} (from {proxy_username_var})")
        
                    # Get GoLogin API instance
                    gologin_api = get_gologin_api(api_token)
        
                    # Call GoLoginAPI method to update proxy
                    proxy_success, proxy_message = gologin_api.update_proxy_for_profiles(profile_list, proxy_config)
        
                    if proxy_success:
                        print(f"[GOLOGIN WARMUP] ✓ {proxy_message}")
                    else:
                        print(f"[GOLOGIN WARMUP] ⚠ Warning: {proxy_message}")
                        print("[GOLOGIN WARMUP] Continuing without proxy update...")
                else:
                    print("[GOLOGIN WARMUP] ⚠ Warning: Some proxy variables are empty, skipping proxy update")
                    print(f"[GOLOGIN WARMUP]   Mode: {proxy_mode_var} = '{proxy_mode}'")
                    print(f"[GOLOGIN WARMUP]   Host: {proxy_host_var} = '{proxy_host}'")
                    print(f"[GOLOGIN WARMUP]   Port: {proxy_port_var} = '{proxy_port}'")
                    print(f"[GOLOGIN WARMUP]   Username: {proxy_username_var} = '{proxy_username}'")
                    print(f"[GOLOGIN WARMUP]   Password: {proxy_password_var} = '{proxy_password}'")
    
                print("[GOLOGIN WARMUP] ===================================")
            else:
                print("[GOLOGIN WARMUP] No proxy configuration provided (variable names missing), skipping proxy update")


        
            # Check if multi-threading enabled
            enable_threading = self.params.get("enable_threading", False)
        
            if enable_threading and len(profile_list) > 1:
                # PARALLEL MODE
                print("[GOLOGIN WARMUP] ========== PARALLEL MODE ==========")
                self._warmup_parallel(profile_list, api_token)
            else:
                # SEQUENTIAL MODE - Select 1 profile and warm up
                print("[GOLOGIN WARMUP] ========== SEQUENTIAL MODE ==========")
                how_to_get = self.params.get("how_to_get", "Random")
                profile_id = self._select_profile(profile_list, how_to_get)
                print(f"[GOLOGIN WARMUP] Selected profile ID: {profile_id}")
            
                # Warm up single profile
                success = self._warmup_single_profile(profile_id, api_token)
                self.set_variable(success)
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Error: {e}")
            import traceback
            traceback.print_exc()
            self.set_variable(False)

    def _warmup_single_profile(self, profile_id, api_token):
        """Warm up a single profile - can be called from thread"""
        try:
            print(f"\n[GOLOGIN WARMUP] [{profile_id}] Starting warm up...")
        
            # Get options
            refresh_fingerprint = self.params.get("refresh_fingerprint", False)
            delete_cookies = self.params.get("delete_cookies", False)
            headless = self.params.get("headless", False)
        
            # Get GoLogin API instance
            gologin = get_gologin_api(api_token)
        
            # Refresh fingerprint if requested
            if refresh_fingerprint:
                print(f"[GOLOGIN WARMUP] [{profile_id}] Refreshing fingerprint...")
                success = gologin.refresh_fingerprint(profile_id)
                if success:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Fingerprint refreshed")
                else:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ Failed to refresh fingerprint")
        
            # Delete cookies if requested (BEFORE starting profile)
            if delete_cookies:
                print(f"[GOLOGIN WARMUP] [{profile_id}] Deleting cookies...")
                success, result = gologin.update_cookies(profile_id, [], replace_all=True)  # ✓ ĐÚNG
                if success:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Cookies deleted")
                else:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ Failed to delete cookies: {result}")

            # Import cookies if not deleting (BEFORE starting profile)
            if not delete_cookies:
                cookies_imported = self._import_cookies_if_provided(gologin, profile_id)
                if cookies_imported:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Cookies imported successfully")
        
            # Start profile
            print(f"[GOLOGIN WARMUP] [{profile_id}] Starting profile...")
        
            # Pass headless param to GoLogin API
            if headless:
                extra_params = [
                    "--headless=new",
                    "--mute-audio",  # Mute audio
                    "--disable-background-networking",
                    "--disable-extensions",
                    "--enable-features=NetworkService",  # Enable cookies
                    "--disable-features=CookiesWithoutSameSiteMustBeSecure",  # Allow all cookies
                    "--disable-dev-shm-usage",  # ← QUAN TRỌNG: Không dùng /dev/shm
                    "--disable-gpu",             # ← Tắt GPU trong headless
                    "--no-sandbox",              # ← Bỏ sandbox để tránh memory restrictions
                    "--disable-software-rasterizer",
                    "--disable-features=VizDisplayCompositor"
                ]
            else:
                extra_params = [                  
                    "--enable-features=NetworkService",
                    "--disable-features=CookiesWithoutSameSiteMustBeSecure"
                ]
        
            success, debugger_address = gologin.start_profile(profile_id, extra_params=extra_params)
        
            if not success:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ Failed to start profile: {debugger_address}")
                return False
        
            print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Profile started: {debugger_address}")
        
            # Connect Selenium
            driver = self._connect_selenium(debugger_address)
            if not driver:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ Failed to connect Selenium")
                gologin.stop_profile(profile_id)
                return False
            
            # ← THÊM: Clean up old tabs from previous sessions
            print(f"[GOLOGIN WARMUP] [{profile_id}] Checking browser tabs...")
            self._cleanup_browser_tabs(driver)
        
            # Load websites list
            websites = self._load_websites()
            if not websites:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ No websites to browse")
                driver.quit()
                gologin.stop_profile(profile_id)
                return False

            # Load keywords for search (optional)
            keywords = self._load_keywords()
            if keywords:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Loaded {len(keywords)} search keywords")

        
            # Get duration
            duration_minutes = self.params.get("duration_minutes", "5")
            try:
                duration_minutes = float(duration_minutes)
            except:
                duration_minutes = 5
            total_seconds = int(duration_minutes * 60)
        
            # Browse websites
            print(f"[GOLOGIN WARMUP] [{profile_id}] Browsing websites for {duration_minutes} minutes...")
            self._browse_websites(driver, websites, total_seconds, keywords)
        
            # Wait for async operations to complete
            print(f"[GOLOGIN WARMUP] [{profile_id}] Waiting for browser data to settle...")
            time.sleep(5)
        
            # Save cookies
            cookies_saved = self._save_cookies(gologin, profile_id)
            if cookies_saved:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Cookies saved: {cookies_saved}")
            else:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ No cookies saved")
        
            # Wait for async operations to complete
            print(f"[GOLOGIN WARMUP] [{profile_id}] Waiting for browser data to settle...")
            time.sleep(5)

            # Save cookies
            cookies_saved = self._save_cookies(gologin, profile_id)
            if cookies_saved:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Cookies saved: {cookies_saved}")
            else:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ No cookies saved")

            # ← THÊM: Close all tabs before quitting to avoid folder lock issues
            print(f"[GOLOGIN WARMUP] [{profile_id}] Closing all tabs...")
            self._close_all_tabs(driver)
            time.sleep(5)  # Wait for tabs to fully close

            # Close browser
            driver.quit()
            print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Browser closed")

            # Wait longer for Chrome cleanup (increase from 3 to 5 seconds)
            print(f"[GOLOGIN WARMUP] [{profile_id}] Waiting for Chrome process cleanup...")
            time.sleep(5)  # ← TĂNG từ 3s lên 5s

        
            # Stop profile and sync
            print(f"[GOLOGIN WARMUP] [{profile_id}] Stopping profile...")
            gologin.stop_profile(profile_id)
            print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Profile stopped and synced to cloud")
            print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Warm up completed!\n")
        
            return True
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


    def _warmup_parallel(self, profile_list, api_token):
        """Warm up multiple profiles in parallel using threading"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
    
        # Get max workers
        max_workers_str = self.params.get("max_workers", "3")
        try:
            max_workers = int(max_workers_str)
        except:
            max_workers = 3
    
        max_workers = min(max_workers, len(profile_list))  # Don't exceed profile count
    
        print(f"[GOLOGIN WARMUP] Warming up {len(profile_list)} profiles with {max_workers} parallel threads")
        print(f"[GOLOGIN WARMUP] Profiles: {', '.join(profile_list)}")
    
        # Store results
        results = []
    
        # Create thread pool
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all profiles to thread pool
            future_to_profile = {
                executor.submit(self._warmup_single_profile, profile_id, api_token): profile_id
                for profile_id in profile_list
            }
        
            # Wait for all threads to complete
            for future in as_completed(future_to_profile):
                profile_id = future_to_profile[future]
                try:
                    success = future.result()
                    results.append(success)
                    if success:
                        print(f"[GOLOGIN WARMUP] ✓ Profile {profile_id} completed successfully")
                    else:
                        print(f"[GOLOGIN WARMUP] ✗ Profile {profile_id} failed")
                except Exception as e:
                    print(f"[GOLOGIN WARMUP] ✗ Profile {profile_id} exception: {e}")
                    results.append(False)
    
        # Summary
        success_count = sum(results)
        print(f"\n[GOLOGIN WARMUP] ========== SUMMARY ==========")
        print(f"[GOLOGIN WARMUP] Total: {len(profile_list)} profiles")
        print(f"[GOLOGIN WARMUP] Success: {success_count}")
        print(f"[GOLOGIN WARMUP] Failed: {len(results) - success_count}")
        print(f"[GOLOGIN WARMUP] ============================\n")
    
        # Set variable based on overall success
        self.set_variable(success_count > 0)

    
    def _parse_profile_ids(self, profile_ids_text):
        """Parse profile IDs from text, support variables"""
        profile_list = []
        parts = profile_ids_text.split(";")
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Check if variable format <VARIABLE_NAME>
            if part.startswith("<") and part.endswith(">"):
                var_name = part[1:-1]
                var_value = GlobalVariables().get(var_name, "")
                if var_value:
                    profile_list.append(var_value)
                else:
                    print(f"[GOLOGIN WARMUP] Warning: Variable '{var_name}' is empty")
            else:
                profile_list.append(part)
        
        return profile_list
    
    def _select_profile(self, profile_list, how_to_get):
        """Select profile based on method"""
        if how_to_get == "Sequential by loop":
            # Get current index from global variable
            index_var = "GOLOGIN_PROFILE_INDEX"
            current_index = GlobalVariables().get(index_var, "0")
            try:
                current_index = int(current_index)
            except:
                current_index = 0
            
            # Select profile
            profile_id = profile_list[current_index % len(profile_list)]
            
            # Update index
            next_index = (current_index + 1) % len(profile_list)
            GlobalVariables().set(index_var, str(next_index))
            
            return profile_id
        else:
            # Random
            return random.choice(profile_list)
    
    def _import_cookies_if_provided(self, gologin, profile_id):
        """Import cookies if folder path provided"""
        try:
            # Get cookies folder - priority: variable > direct path
            cookies_folder = None
            
            cookies_folder_var = self.params.get("cookies_folder_variable", "").strip()
            if cookies_folder_var:
                cookies_folder = GlobalVariables().get(cookies_folder_var, "")
                if cookies_folder:
                    print(f"[GOLOGIN WARMUP] Using cookies folder from variable '{cookies_folder_var}': {cookies_folder}")
            
            if not cookies_folder:
                cookies_folder = self.params.get("cookies_folder", "").strip()
                if cookies_folder:
                    print(f"[GOLOGIN WARMUP] Using cookies folder from direct path: {cookies_folder}")
            
            if not cookies_folder or not os.path.exists(cookies_folder):
                return False
            
            # Get all JSON files in folder
            json_files = [f for f in os.listdir(cookies_folder) if f.endswith('.json')]
            if not json_files:
                print(f"[GOLOGIN WARMUP] No JSON files found in cookies folder")
                return False
            
            # Random pick one file
            selected_file = random.choice(json_files)
            cookies_file_path = os.path.join(cookies_folder, selected_file)
            print(f"[GOLOGIN WARMUP] Randomly selected cookies file: {selected_file}")
            
            # Load cookies from file
            with open(cookies_file_path, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            # Import cookies via API (using update_cookies with replace_all=True)
            success, result = gologin.update_cookies(profile_id, cookies_data, replace_all=True)

            if success:
                print(f"[GOLOGIN WARMUP] ✓ Imported {len(cookies_data)} cookies from {selected_file}")
                return True
            else:
                print(f"[GOLOGIN WARMUP] ⚠ Failed to import cookies: {result}")
                return False
            
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Error importing cookies: {e}")
            return False
        
    def _update_proxy_for_profiles(self, api_token, profile_ids, proxy_config):
        """
        Update proxy for multiple profiles before starting them
    
        Args:
            api_token: GoLogin API token
            profile_ids: List of profile IDs
            proxy_config: Dict with keys: mode, host, port, username, password
    
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import requests
        
            # Validate all 5 required fields are present
            required_fields = ["mode", "host", "port", "username", "password"]
            for field in required_fields:
                if not proxy_config.get(field):
                    print(f"[GOLOGIN WARMUP] Proxy field '{field}' is empty. Skipping proxy update.")
                    return False
        
            # Convert port to integer
            try:
                port = int(proxy_config["port"])
            except ValueError:
                print(f"[GOLOGIN WARMUP] ✗ Invalid port number: {proxy_config['port']}")
                return False
        
            # Build API request payload
            api_url = "https://api.gologin.com/browser/proxy/many/v2"
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
        
            # Build proxies array for all profiles
            proxies_array = []
            for profile_id in profile_ids:
                proxy_data = {
                    "profileId": profile_id,
                    "proxy": {
                        "id": None,  # null for new proxy
                        "mode": proxy_config["mode"],
                        "host": proxy_config["host"],
                        "port": port,
                        "username": proxy_config["username"],
                        "password": proxy_config["password"],
                        "changeIpUrl": None,  # null
                        "customName": None   # null
                    }
                }
                proxies_array.append(proxy_data)
        
            payload = {"proxies": proxies_array}
        
            print(f"[GOLOGIN WARMUP] Updating proxy for {len(profile_ids)} profiles...")
            print(f"[GOLOGIN WARMUP] Proxy: {proxy_config['mode']}://{proxy_config['host']}:{port}")
        
            # Send PATCH request
            response = requests.patch(api_url, json=payload, headers=headers, timeout=30)
        
            if response.status_code in [200, 201, 204]:
                print(f"[GOLOGIN WARMUP] ✓ Proxy updated successfully for all profiles")
                return True
            else:
                print(f"[GOLOGIN WARMUP] ✗ Proxy update failed: {response.status_code}")
                print(f"[GOLOGIN WARMUP] Response: {response.text}")
                return False
            
        except Exception as e:
            print(f"[GOLOGIN WARMUP] ✗ Error updating proxy: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _close_all_tabs(self, driver):
        """
        Close all tabs except the last one to avoid folder lock issues
        This helps prevent "folder in use" errors when stopping profile
        """
        try:
            all_handles = driver.window_handles
        
            if len(all_handles) <= 1:
                print(f"[GOLOGIN WARMUP] Only 1 tab open, no need to close")
                return True
        
            print(f"[GOLOGIN WARMUP] Closing {len(all_handles) - 1} tabs...")
        
            # Keep the first tab, close all others
            first_handle = all_handles[0]
        
            for handle in all_handles[1:]:
                try:
                    driver.switch_to.window(handle)
                    driver.close()
                    time.sleep(0.5)  # Small delay between closes
                except Exception as e:
                    print(f"[GOLOGIN WARMUP] ⚠ Failed to close tab: {e}")
        
            # Switch back to first tab
            try:
                driver.switch_to.window(first_handle)
            except:
                # If first tab also failed, just continue
                pass
        
            print(f"[GOLOGIN WARMUP] ✓ All tabs closed")
            return True
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] ⚠ Error closing tabs: {e}")
            return False


    def _connect_selenium(self, debugger_address):
        """Connect Selenium to GoLogin Orbita browser"""
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
                print(f"[GOLOGIN WARMUP] Installing ChromeDriver for Chrome {chrome_version}...")
                service = Service(ChromeDriverManager(driver_version=chrome_version).install())
            else:
                print(f"[GOLOGIN WARMUP] Installing ChromeDriver with auto-detection...")
                service = Service(ChromeDriverManager().install())
            
            # Disable ChromeDriver logs
            service.log_output = None
            
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print(f"[GOLOGIN WARMUP] ✓ Selenium connected to Orbita")
            return driver
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Selenium connection error: {e}")
            import traceback
            traceback.print_exc()
            return None
        
    def _cleanup_browser_tabs(self, driver):
        """Close all tabs except first one to avoid crashes"""
        try:
            all_handles = driver.window_handles
            if len(all_handles) > 1:
                print(f"[GOLOGIN WARMUP] Found {len(all_handles)} tabs, closing old tabs...")
            
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
                print(f"[GOLOGIN WARMUP] ✓ Cleaned up tabs, using main tab")
            else:
                print(f"[GOLOGIN WARMUP] ✓ Only 1 tab, no cleanup needed")
        
            return True
        except Exception as e:
            print(f"[GOLOGIN WARMUP] ⚠ Tab cleanup error: {e}")
            return False

    
    def _get_chrome_version_from_debugger(self, debugger_address):
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
                    print(f"[GOLOGIN WARMUP] Detected Chrome version: {version}")
                    return major_version
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Failed to detect Chrome version: {e}")
        return None
    
    def _load_websites(self):
        """Load websites from file"""
        try:
            # Get websites file - priority: variable > direct path
            websites_file = None
            
            websites_var = self.params.get("websites_variable", "").strip()
            if websites_var:
                websites_file = GlobalVariables().get(websites_var, "")
                if websites_file:
                    print(f"[GOLOGIN WARMUP] Using websites file from variable '{websites_var}': {websites_file}")
            
            if not websites_file:
                websites_file = self.params.get("websites_file", "").strip()
                if websites_file:
                    print(f"[GOLOGIN WARMUP] Using websites file from direct path: {websites_file}")
            
            if not websites_file or not os.path.exists(websites_file):
                print(f"[GOLOGIN WARMUP] ✗ Websites file not found: {websites_file}")
                return []
            
            # Load websites from file
            websites = []
            with open(websites_file, 'r', encoding='utf-8') as f:
                for line in f:
                    url = line.strip()
                    # Skip empty lines and comments
                    if url and not url.startswith('#'):
                        # Fix URL: add https:// if missing protocol
                        if not url.startswith(('http://', 'https://')):
                            url = 'https://' + url
                        websites.append(url)
            
            if not websites:
                print(f"[GOLOGIN WARMUP] ✗ No valid URLs found in file")
                return []
            
            print(f"[GOLOGIN WARMUP] ✓ Loaded {len(websites)} websites from file")
            return websites
            
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Error loading websites: {e}")
            return []
        
    def _load_keywords(self):
        """Load search keywords from file"""
        try:
            # Get keywords file - priority: variable > direct path
            keywords_file = None
        
            keywords_var = self.params.get("keywords_variable", "").strip()
            if keywords_var:
                keywords_file = GlobalVariables().get(keywords_var, "")
                if keywords_file:
                    print(f"[GOLOGIN WARMUP] Using keywords file from variable '{keywords_var}': {keywords_file}")
        
            if not keywords_file:
                keywords_file = self.params.get("keywords_file", "").strip()
                if keywords_file:
                    print(f"[GOLOGIN WARMUP] Using keywords file from direct path: {keywords_file}")
        
            if not keywords_file or not os.path.exists(keywords_file):
                return []
        
            # Load keywords from file
            keywords = []
            with open(keywords_file, 'r', encoding='utf-8') as f:
                for line in f:
                    keyword = line.strip()
                    # Skip empty lines and comments
                    if keyword and not keyword.startswith('#'):
                        keywords.append(keyword)
        
            if keywords:
                print(f"[GOLOGIN WARMUP] ✓ Loaded {len(keywords)} keywords from file")
        
            return keywords
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Error loading keywords: {e}")
            return []
        

    def _search_on_site(self, driver, url, keywords):
        """Perform search if on Google or YouTube"""
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            from urllib.parse import urlparse
        
            if not keywords:
                return False
        
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
        
            # Check if Google or YouTube
            is_google = 'google.com' in domain or 'google' in domain
            is_youtube = 'youtube.com' in domain or 'youtu.be' in domain
        
            if not (is_google or is_youtube):
                return False
        
            # Random pick keyword
            keyword = random.choice(keywords)
            print(f"[GOLOGIN WARMUP] Searching for: '{keyword}'")
        
            # Find search box and perform search
            search_box = None
        
            if is_google:
                # Google search selectors
                selectors = ['textarea[name="q"]', 'input[name="q"]', 'input[title="Search"]']
                for selector in selectors:
                    try:
                        search_box = driver.find_element(By.CSS_SELECTOR, selector)
                        if search_box:
                            break
                    except:
                        continue
        
            elif is_youtube:
                # YouTube search selectors
                selectors = ['input#search', 'input[name="search_query"]', 'input[placeholder*="Search"]']
                for selector in selectors:
                    try:
                        search_box = driver.find_element(By.CSS_SELECTOR, selector)
                        if search_box:
                            break
                    except:
                        continue
        
            if not search_box:
                print(f"[GOLOGIN WARMUP] ⚠ Search box not found")
                return False
        
            # Clear and type keyword
            search_box.clear()
            time.sleep(random.uniform(0.5, 1))
        
            # Type with human-like delay
            for char in keyword:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
        
            time.sleep(random.uniform(0.5, 1))
        
            # Press Enter
            search_box.send_keys(Keys.RETURN)
            print(f"[GOLOGIN WARMUP] ✓ Search submitted")
        
            # Wait for results
            time.sleep(random.uniform(2, 4))
        
            return True
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Error searching: {e}")
            return False


    
    def _browse_websites(self, driver, websites, total_seconds, keywords=None):
        """Browse websites with human-like actions"""
        try:
            from helpers.selenium_actions import SeleniumHumanActions
    
            print(f"[GOLOGIN WARMUP] Starting browsing for {total_seconds}s...")
    
            human = SeleniumHumanActions(driver)
            how_to_get_websites = self.params.get("how_to_get_websites", "Random")
    
            start_time = time.time()
            visit_count = 0
            action_count = 0
            current_index = 0
    
            while True:
                # Check time limit
                elapsed = time.time() - start_time
                if elapsed >= total_seconds:
                    print(f"[GOLOGIN WARMUP] ✓ Browsing completed after {int(elapsed)}s")
                    break
        
                # Select URL
                if how_to_get_websites == "Sequential by loop":
                    url = websites[current_index % len(websites)]
                    current_index += 1
                else:
                    url = random.choice(websites)
        
                try:
                    print(f"[GOLOGIN WARMUP] [{visit_count+1}] Visiting: {url}")
            
                    # Set page load timeout
                    driver.set_page_load_timeout(30)
            
                    # Navigate to URL
                    try:
                        driver.get(url)
                    except Exception as nav_err:
                        print(f"[GOLOGIN WARMUP] ⚠ Page load error: {str(nav_err)[:100]}")
                        time.sleep(2)
                        continue
            
                    visit_count += 1
            
                    # Wait for page to be ready
                    try:
                        driver.execute_script("return document.readyState")
                    except:
                        pass
            
                    # Wait for page to settle
                    time.sleep(random.uniform(3, 5))
                
                    # Auto accept cookie consent
                    if human.accept_cookie_consent():
                        print(f"[GOLOGIN WARMUP] ✓ Accepted cookie consent banner")
                        time.sleep(random.uniform(1, 2))
                        
                    # ← THÊM: Close popups/modals
                    if human.close_popups():
                        print(f"[GOLOGIN WARMUP] ✓ Closed popup")
                        time.sleep(random.uniform(0.5, 1.0))
            
                    # Perform search if Google/YouTube
                    search_performed = self._search_on_site(driver, url, keywords)
                    if search_performed:
                        time.sleep(random.uniform(2, 3))
                        try:
                            human.scroll_random()
                            time.sleep(random.uniform(1, 2))
                            human.click_random_element()
                        except:
                            pass
            
                    # Random human-like actions on page
                    actions_on_page = random.randint(1, 3)
                    for _ in range(actions_on_page):
                        if time.time() - start_time >= total_seconds:
                            break
                        try:
                            human.execute_random_action()
                            action_count += 1
                            time.sleep(random.uniform(1.5, 3.0))
                        except Exception as action_err:
                            print(f"[GOLOGIN WARMUP] ⚠ Action error")
                            break
            
                    # Click deeper logic (50% chance)
                    if random.random() < 0.5 and time.time() - start_time < total_seconds:
                        print(f"[GOLOGIN WARMUP] Trying to click a link to go deeper...")
                    
                        # Remember main tab before clicking
                        main_tab = driver.current_window_handle
                        tabs_before = len(driver.window_handles)
                    
                        try:
                            clicked = human.click_random_link()
                            if clicked:
                                print(f"[GOLOGIN WARMUP] ✓ Clicked deeper link")
                            
                                # Wait and check if new tab opened
                                time.sleep(2)
                                tabs_after = len(driver.window_handles)
                            
                                if tabs_after > tabs_before:
                                    print(f"[GOLOGIN WARMUP] New tab opened, switching to it...")
                                    # Switch to newest tab (last one)
                                    new_tab = driver.window_handles[-1]
                                    driver.switch_to.window(new_tab)
                            
                                # Wait for page to load
                                time.sleep(random.uniform(3.0, 5.0))
                            
                                # Check if page loaded successfully
                                try:
                                    current_url = driver.current_url
                                    driver.title
                                    print(f"[GOLOGIN WARMUP] ✓ Navigated to deeper page")
                                except:
                                    print(f"[GOLOGIN WARMUP] ⚠ Deeper page not accessible, skipping")
                                    # Switch back to main tab before continue
                                    try:
                                        driver.switch_to.window(main_tab)
                                    except:
                                        pass
                                    continue
                            
                                # Do a few more actions on new page
                                deeper_actions = random.randint(1, 3)
                                for i in range(deeper_actions):
                                    if time.time() - start_time >= total_seconds:
                                        break
                                    try:
                                        human.execute_random_action()
                                        action_count += 1
                                        time.sleep(random.uniform(1.0, 2.5))
                                    except Exception as action_err:
                                        print(f"[GOLOGIN WARMUP] ⚠ Deeper action {i+1} failed")
                                        break
                            
                                # Check if still on main tab, if not switch back
                                try:
                                    current_tab = driver.current_window_handle
                                    if current_tab != main_tab:
                                        print(f"[GOLOGIN WARMUP] Switching back to main tab...")
                                    
                                        # Close the deeper tab first
                                        if tabs_after > tabs_before:
                                            try:
                                                driver.close()
                                                print(f"[GOLOGIN WARMUP] ✓ Closed deeper tab")
                                            except:
                                                pass
                                    
                                        # Switch back to main tab
                                        driver.switch_to.window(main_tab)
                                        time.sleep(random.uniform(0.5, 1.0))
                                except Exception as switch_err:
                                    print(f"[GOLOGIN WARMUP] ⚠ Tab switch error: {str(switch_err)[:50]}")
                                    # Force switch to first tab as fallback
                                    try:
                                        driver.switch_to.window(driver.window_handles[0])
                                    except:
                                        pass
                            else:
                                print(f"[GOLOGIN WARMUP] No clickable link found")
        
                        except Exception as deeper_err:
                            print(f"[GOLOGIN WARMUP] ⚠ Deeper navigation error: {str(deeper_err)[:50]}")
                            # Make sure we're back on main tab
                            try:
                                driver.switch_to.window(main_tab)
                            except:
                                try:
                                    driver.switch_to.window(driver.window_handles[0])
                                except:
                                    pass
            
                    # Stay on page để cookies được set
                    stay_time = random.uniform(10.0, 20.0)
                    print(f"[GOLOGIN WARMUP] Staying on page for {stay_time:.1f}s...")
                    time.sleep(stay_time)
                
                    # Check if time is up
                    if time.time() - start_time >= total_seconds:
                        print(f"[GOLOGIN WARMUP] ✓ Time limit reached")
                        break
            
                except Exception as e:
                    error_msg = str(e)
                
                    # Check if tab crashed or session deleted
                    if "tab crashed" in error_msg.lower() or "session deleted" in error_msg.lower():
                        print(f"[GOLOGIN WARMUP] ✗ Browser tab crashed, stopping browse session")
                        break
                
                    print(f"[GOLOGIN WARMUP] Error browsing {url}: {str(e)[:100]}")
                    time.sleep(2)
                    continue
    
            print(f"[GOLOGIN WARMUP] ✓ Visited {visit_count} pages, performed {action_count} actions")
    
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Error during browsing: {e}")
            import traceback
            traceback.print_exc()


    
    def _save_cookies(self, gologin, profile_id):
        """
        Save cookies naturally collected by browser
        Simply get all cookies from GoLogin and save to JSON file in GoLogin format
        No filtering, no grouping - just raw cookies for later import
        """
        try:
            # Get output folder
            output_folder = None
            folder_var = self.params.get("folder_variable", "").strip()
            if folder_var:
                output_folder = GlobalVariables().get(folder_var, "")
                if output_folder:
                    print(f"[GOLOGIN WARMUP] Using output folder from variable '{folder_var}': {output_folder}")
        
            if not output_folder:
                output_folder = self.params.get("folder_path", "").strip()
                if output_folder:
                    print(f"[GOLOGIN WARMUP] Using output folder from direct path: {output_folder}")
        
            if not output_folder:
                print("[GOLOGIN WARMUP] ⚠ No output folder specified, cookies not saved")
                return None
        
            # Create folder if not exists
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                print(f"[GOLOGIN WARMUP] Created output folder: {output_folder}")
        
            # Get ALL cookies from GoLogin cloud (naturally collected during browsing)
            print(f"[GOLOGIN WARMUP] Fetching cookies from GoLogin cloud...")
            success, cookies_data = gologin.get_cookies(profile_id)
        
            if not success:
                print(f"[GOLOGIN WARMUP] ✗ Failed to get cookies: {cookies_data}")
                return None
        
            if not cookies_data or len(cookies_data) == 0:
                print("[GOLOGIN WARMUP] ⚠ No cookies found in profile")
                return None
        
            print(f"[GOLOGIN WARMUP] ✓ Retrieved {len(cookies_data)} cookies")
        
            # Generate filename: profile_id_DD_MM_YYYY_HH_MM_SS.json
            now = datetime.now()
            filename = f"cookies_{profile_id}_{now.strftime('%d_%m_%Y_%H_%M_%S')}.json"
            filepath = os.path.join(output_folder, filename)
        
            # Save cookies directly to JSON file (GoLogin format - ready for import)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cookies_data, f, indent=2, ensure_ascii=False)
        
            print(f"[GOLOGIN WARMUP] ✓ Saved {len(cookies_data)} cookies to: {filename}")
            return filepath
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Error saving cookies: {e}")
            import traceback
            traceback.print_exc()
            return None




    def set_variable(self, success):
        """Set variable with result"""
        variable = self.params.get("variable", "")
        if variable:
            GlobalVariables().set(variable, "true" if success else "false")