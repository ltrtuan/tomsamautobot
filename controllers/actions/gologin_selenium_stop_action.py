# controllers/actions/gologin_selenium_stop_action.py

from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from models.gologin_api import get_gologin_api
import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from helpers.selenium_registry import unregister_selenium_driver

class GoLoginSeleniumStopAction(BaseAction):
    """Handler for GoLogin Selenium Stop action - Stop profile and export cookies"""
    
    def prepare_play(self):
        """Execute GoLogin Selenium Stop"""
        try:
            # Get API token from variable name
            api_key_variable = self.params.get("api_key_variable", "").strip()
            if not api_key_variable:
                print("[GOLOGIN STOP] Error: API key variable name is required")
                self.set_variable(False)
                return
            
            # Get API token value from GlobalVariables
            api_token = GlobalVariables().get(api_key_variable, "")
            if not api_token:
                print(f"[GOLOGIN STOP] Error: Variable '{api_key_variable}' is empty or not set")
                self.set_variable(False)
                return
            
            print(f"[GOLOGIN STOP] Using API token from variable: {api_key_variable}")
            
            # ========== GET PROFILE_ID AND DEBUGGER_ADDRESS FROM GLOBAL ==========
            profile_id = GlobalVariables().get("GOLOGIN_PROFILE_ID", "")
            debugger_address = GlobalVariables().get("GOLOGIN_DEBUGGER_ADDRESS", "")
            
            if not profile_id:
                print("[GOLOGIN STOP] Error: GOLOGIN_PROFILE_ID not found in GlobalVariables")
                print("[GOLOGIN STOP] Hint: Run 'GoLogin Selenium Start' action first")
                self.set_variable(False)
                return
            
            if not debugger_address:
                print("[GOLOGIN STOP] Error: GOLOGIN_DEBUGGER_ADDRESS not found in GlobalVariables")
                print("[GOLOGIN STOP] Hint: Run 'GoLogin Selenium Start' action first")
                self.set_variable(False)
                return
            
            print(f"[GOLOGIN STOP] Retrieved from GlobalVariables:")
            print(f"[GOLOGIN STOP] Profile ID: {profile_id}")
            print(f"[GOLOGIN STOP] Debugger Address: {debugger_address}")
            
            # Stop profile
            success = self._stop_single_profile(profile_id, debugger_address, api_token)
            self.set_variable(success)
            
        except Exception as e:
            print(f"[GOLOGIN STOP] Error: {e}")
            import traceback
            traceback.print_exc()
            self.set_variable(False)
    
    def _stop_single_profile(self, profile_id, debugger_address, api_token):
        """Stop a single profile - save cookies, quit driver, close profile"""
        driver = None
        gologin = None
        
        try:
            print(f"\n[GOLOGIN STOP] [{profile_id}] Starting stop sequence...")
            
            # Get GoLogin API instance
            gologin = get_gologin_api(api_token)
            
            # ========== STEP 1: RECONNECT TO BROWSER ==========
            print(f"[GOLOGIN STOP] [{profile_id}] Reconnecting to browser...")
            driver = self._reconnect_selenium(debugger_address)
            
            if not driver:
                print(f"[GOLOGIN STOP] [{profile_id}] ⚠ Cannot reconnect to browser, skipping cookies export")
                # Continue to stop profile anyway
            else:
                print(f"[GOLOGIN STOP] [{profile_id}] ✓ Reconnected to browser")
                
               
                # ========== STEP 2: GET ALL COOKIES VIA CDP (THAY ĐỔI NÀY) ==========
                print(f"[GOLOGIN STOP] [{profile_id}] Getting ALL cookies via CDP...")
                all_cookies = []
                try:
                    # Enable Network domain
                    driver.execute_cdp_cmd("Network.enable", {})
                
                    # Get ALL cookies from browser using CDP
                    result = driver.execute_cdp_cmd("Network.getAllCookies", {})
                    cdp_cookies = result.get("cookies", [])
                
                    # Convert CDP format to Selenium format
                    for cdp_cookie in cdp_cookies:
                        selenium_cookie = {
                            "name": cdp_cookie.get("name"),
                            "value": cdp_cookie.get("value", ""),
                            "domain": cdp_cookie.get("domain"),
                            "path": cdp_cookie.get("path", "/"),
                            "secure": cdp_cookie.get("secure", False),
                            "httpOnly": cdp_cookie.get("httpOnly", False),
                        }
                    
                        # Add expiry if not session cookie
                        if "expires" in cdp_cookie and cdp_cookie["expires"] > 0:
                            selenium_cookie["expiry"] = int(cdp_cookie["expires"])
                    
                        # Add sameSite if present
                        if "sameSite" in cdp_cookie:
                            selenium_cookie["sameSite"] = cdp_cookie["sameSite"]
                    
                        all_cookies.append(selenium_cookie)
                
                    print(f"[GOLOGIN STOP] [{profile_id}] Retrieved {len(all_cookies)} cookies from ALL domains")
                
                except Exception as e:
                    print(f"[GOLOGIN STOP] [{profile_id}] ⚠ Failed to get cookies via CDP: {e}")
                    print(f"[GOLOGIN STOP] [{profile_id}] Falling back to Selenium get_cookies()...")
                    all_cookies = driver.get_cookies()
                    print(f"[GOLOGIN STOP] [{profile_id}] Retrieved {len(all_cookies)} cookies (current domain only)")
                    
                
                # ========== STEP 3: CLOSE ALL TABS ==========
                print(f"[GOLOGIN STOP] [{profile_id}] Closing all tabs...")
                self._close_all_tabs(driver)
                time.sleep(2)
                
                # ========== STEP 4: QUIT DRIVER ==========
                print(f"[GOLOGIN STOP] [{profile_id}] Closing ChromeDriver...")
                try:
                    # Unregister from auto-cleanup first
                    unregister_selenium_driver(driver)
                    # Quit driver
                    driver.quit()
                    print(f"[GOLOGIN STOP] [{profile_id}] ✓ ChromeDriver closed")
                except Exception as cleanup_err:
                    print(f"[GOLOGIN STOP] [{profile_id}] ⚠ Driver cleanup warning: {cleanup_err}")
                
                driver = None  # Mark as closed
                
                # Wait for Chrome cleanup
                print(f"[GOLOGIN STOP] [{profile_id}] Waiting for Chrome process cleanup...")
                time.sleep(3)
                
                # ========== STEP 5: SAVE COOKIES TO FILE ==========
                if all_cookies:
                    print(f"[GOLOGIN STOP] [{profile_id}] Saving cookies to file...")
                    cookies_saved = self._save_cookies_to_file(profile_id, all_cookies)
                    if cookies_saved:
                        print(f"[GOLOGIN STOP] [{profile_id}] ✓ Cookies saved: {cookies_saved}")
                    else:
                        print(f"[GOLOGIN STOP] [{profile_id}] ⚠ Failed to save cookies")
            
            # ========== STEP 6: STOP PROFILE VIA API ==========
            print(f"[GOLOGIN STOP] [{profile_id}] Stopping profile via GoLogin API...")
            try:
                success, msg = gologin.stop_profile(profile_id)
                if success:
                    print(f"[GOLOGIN STOP] [{profile_id}] ✓ Profile stopped and data synced")
                    # Wait for cloud sync
                    print(f"[GOLOGIN STOP] [{profile_id}] Waiting for cloud sync...")
                    time.sleep(5)
                else:
                    print(f"[GOLOGIN STOP] [{profile_id}] ✗ Stop failed: {msg}")
                    return False
            except Exception as stop_err:
                print(f"[GOLOGIN STOP] [{profile_id}] ⚠ Stop profile error: {stop_err}")
                return False
            
            print(f"[GOLOGIN STOP] [{profile_id}] ✓ Stop sequence completed successfully")
            return True
            
        except Exception as e:
            print(f"[GOLOGIN STOP] [{profile_id}] ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # ========== CLEANUP BLOCK - ALWAYS RUN ==========
            print(f"[GOLOGIN STOP] [{profile_id}] Running final cleanup...")
            
            # Close driver if still open
            if driver:
                try:
                    unregister_selenium_driver(driver)
                    driver.quit()
                    print(f"[GOLOGIN STOP] [{profile_id}] ✓ Driver cleanup done")
                except Exception as e:
                    print(f"[GOLOGIN STOP] [{profile_id}] ⚠ Final cleanup warning: {e}")
            
            # Stop profile if not already stopped
            if gologin and profile_id:
                try:
                    gologin.stop_profile(profile_id)
                except:
                    pass
            
            print(f"[GOLOGIN STOP] [{profile_id}] ✓ Final cleanup completed")
    
    def _reconnect_selenium(self, debugger_address):
        """Reconnect Selenium to running GoLogin browser"""
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
                print(f"[GOLOGIN STOP] Installing ChromeDriver for Chrome {chrome_version}...")
                service = Service(ChromeDriverManager(driver_version=chrome_version).install())
            else:
                print(f"[GOLOGIN STOP] Installing ChromeDriver with auto-detection...")
                service = Service(ChromeDriverManager().install())
            
            # Disable ChromeDriver logs
            service.log_output = None
            
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print(f"[GOLOGIN STOP] ✓ Selenium reconnected to browser")
            
            return driver
            
        except Exception as e:
            print(f"[GOLOGIN STOP] Selenium reconnection error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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
                    print(f"[GOLOGIN STOP] Detected Chrome version: {version}")
                    return major_version
        except Exception as e:
            print(f"[GOLOGIN STOP] Failed to detect Chrome version: {e}")
        
        return None
    
    def _close_all_tabs(self, driver):
        """Close all tabs except the last one"""
        try:
            all_handles = driver.window_handles
            if len(all_handles) <= 1:
                print(f"[GOLOGIN STOP] Only 1 tab open, no need to close")
                return True
            
            print(f"[GOLOGIN STOP] Closing {len(all_handles) - 1} tabs...")
            
            # Keep the first tab, close all others
            first_handle = all_handles[0]
            for handle in all_handles[1:]:
                try:
                    driver.switch_to.window(handle)
                    driver.close()
                    time.sleep(0.5)
                except Exception as e:
                    print(f"[GOLOGIN STOP] ⚠ Failed to close tab: {e}")
            
            # Switch back to first tab
            try:
                driver.switch_to.window(first_handle)
            except:
                pass
            
            print(f"[GOLOGIN STOP] ✓ All tabs closed")
            return True
            
        except Exception as e:
            print(f"[GOLOGIN STOP] ⚠ Error closing tabs: {e}")
            return False
    
    def _save_cookies_to_file(self, profile_id, cookies_list):
        """
        Save cookies from Selenium directly to JSON file
        :param profile_id: Profile ID
        :param cookies_list: List of cookies from driver.get_cookies()
        :return: File path if success, None if failed
        """
        try:
            if not cookies_list:
                print(f"[GOLOGIN STOP] No cookies provided")
                return None
            
            # Get output folder
            output_folder = None
            folder_var = self.params.get("folder_variable", "").strip()
            if folder_var:
                output_folder = GlobalVariables().get(folder_var, "")
                if output_folder:
                    print(f"[GOLOGIN STOP] Using output folder from variable '{folder_var}': {output_folder}")
            
            if not output_folder:
                output_folder = self.params.get("folder_path", "").strip()
                if output_folder:
                    print(f"[GOLOGIN STOP] Using output folder from direct path: {output_folder}")
            
            if not output_folder:
                print(f"[GOLOGIN STOP] No output folder specified")
                return None
            
            # Create folder if not exists
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            # Generate filename: cookies_profileID_DD_MM_YYYY_HH_MM_SS.json
            now = datetime.now()
            filename = f"cookies_{profile_id}_{now.strftime('%d_%m_%Y_%H_%M_%S')}.json"
            filepath = os.path.join(output_folder, filename)
            
            # Save cookies to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cookies_list, f, indent=2, ensure_ascii=False)
            
            print(f"[GOLOGIN STOP] ✓ Saved {len(cookies_list)} cookies to: {filename}")
            return filepath
            
        except Exception as e:
            print(f"[GOLOGIN STOP] Error saving cookies: {e}")
            return None
    
    def set_variable(self, success):
        """Set variable with result"""
        variable = self.params.get("variable", "")
        if variable:
            GlobalVariables().set(variable, "true" if success else "false")
