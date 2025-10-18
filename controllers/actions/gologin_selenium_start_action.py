# controllers/actions/gologin_selenium_start_action.py

from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from models.gologin_api import get_gologin_api
import random
import time

# Import helpers
from helpers.gologin_profile_helper import GoLoginProfileHelper
from helpers.flow_youtube import YouTubeFlow
from helpers.flow_google import GoogleFlow
from helpers.selenium_registry import register_selenium_driver, unregister_selenium_driver

class GoLoginSeleniumStartAction(BaseAction):
    """Handler for GoLogin Selenium Start Profile action"""
    
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
            
            # ========== GET PROFILE LIST USING HELPER ==========
            success, result = GoLoginProfileHelper.get_profile_list(
                self.params, api_token, "[GOLOGIN START]"
            )
            
            if not success:
                print(f"[GOLOGIN START] ✗ {result}")
                self.set_variable(False)
                return
            
            profile_list = result
            print(f"[GOLOGIN START] Total profiles to start: {len(profile_list)}")
            
            # ========== CHECK AND UPDATE PROXY IF PROVIDED ==========
            self._update_proxy_if_provided(profile_list, api_token)
            
            # ========== CHECK MULTI-THREADING ==========
            enable_threading = self.params.get("enable_threading", False)
            
            if enable_threading and len(profile_list) > 1:
                # PARALLEL MODE
                print("[GOLOGIN START] ========== PARALLEL MODE ==========")
                self._start_parallel(profile_list, api_token)
            else:
                # SEQUENTIAL MODE - Select 1 profile and start
                print("[GOLOGIN START] ========== SEQUENTIAL MODE ==========")
                how_to_get = self.params.get("how_to_get", "Random")
                profile_id = GoLoginProfileHelper.select_profile(profile_list, how_to_get)
                print(f"[GOLOGIN START] Selected profile ID: {profile_id}")
                
                # Start single profile
                success = self._start_single_profile(profile_id, api_token)
                self.set_variable(success)
        
        except Exception as e:
            print(f"[GOLOGIN START] Error: {e}")
            import traceback
            traceback.print_exc()
            self.set_variable(False)
    
    def _update_proxy_if_provided(self, profile_list, api_token):
        """Update proxy for profiles if configuration provided"""
        try:
            # Get proxy variable names
            proxy_mode_var = self.params.get("proxy_mode_variable", "").strip()
            proxy_host_var = self.params.get("proxy_host_variable", "").strip()
            proxy_port_var = self.params.get("proxy_port_variable", "").strip()
            proxy_username_var = self.params.get("proxy_username_variable", "").strip()
            proxy_password_var = self.params.get("proxy_password_variable", "").strip()
            
            # Check if all 5 variable names are provided
            if not (proxy_mode_var and proxy_host_var and proxy_port_var and 
                    proxy_username_var and proxy_password_var):
                print("[GOLOGIN START] No proxy configuration provided, skipping proxy update")
                return
            
            print("[GOLOGIN START] ========== PROXY UPDATE ==========")
            print("[GOLOGIN START] Proxy configuration detected, retrieving values...")
            
            # Get actual values from GlobalVariables
            proxy_mode = GlobalVariables().get(proxy_mode_var, "")
            proxy_host = GlobalVariables().get(proxy_host_var, "")
            proxy_port = GlobalVariables().get(proxy_port_var, "")
            proxy_username = GlobalVariables().get(proxy_username_var, "")
            proxy_password = GlobalVariables().get(proxy_password_var, "")
            
            # Check if all values are non-empty
            if not (proxy_mode and proxy_host and proxy_port and proxy_username and proxy_password):
                print("[GOLOGIN START] ⚠ Some proxy variables are empty, skipping proxy update")
                return
            
            proxy_config = {
                "mode": proxy_mode,
                "host": proxy_host,
                "port": proxy_port,
                "username": proxy_username,
                "password": proxy_password
            }
            
            print(f"[GOLOGIN START] Proxy: {proxy_mode}://{proxy_host}:{proxy_port}")
            
            # Get GoLogin API instance
            gologin_api = get_gologin_api(api_token)
            
            # Call GoLoginAPI method to update proxy
            proxy_success, proxy_message = gologin_api.update_proxy_for_profiles(
                profile_list, proxy_config
            )
            
            if proxy_success:
                print(f"[GOLOGIN START] ✓ {proxy_message}")
            else:
                print(f"[GOLOGIN START] ⚠ Warning: {proxy_message}")
            
            print("[GOLOGIN START] ===================================")
        except Exception as e:
            print(f"[GOLOGIN START] ⚠ Proxy update error: {e}")
    
    def _start_single_profile(self, profile_id, api_token):
        """Start a single profile and execute actions"""
        driver = None
        gologin = None
        
        try:
            print(f"\n[GOLOGIN START] [{profile_id}] Starting profile...")
            GoLoginProfileHelper.kill_zombie_chrome_processes(profile_id, "[GOLOGIN START]")
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
            extra_params = [
                "--enable-logging",
                "--v=1",
                "--disk-cache-size=0",
                "--media-cache-size=0",
                "--enable-features=NetworkService",
                "--disable-features=CookiesWithoutSameSiteMustBeSecure"
            ]
            
            success, debugger_address = gologin.start_profile(profile_id, extra_params=extra_params)
            
            if not success:
                print(f"[GOLOGIN START] [{profile_id}] ✗ Failed to start profile: {debugger_address}")
                return False
            
            print(f"[GOLOGIN START] [{profile_id}] ✓ Profile started: {debugger_address}")
            
            # Connect Selenium using helper
            driver = GoLoginProfileHelper.connect_selenium(debugger_address, "[GOLOGIN START]")
            
            if not driver:
                print(f"[GOLOGIN START] [{profile_id}] ✗ Failed to connect Selenium")
                gologin.stop_profile(profile_id)
                return False
            
            # Register driver for auto-cleanup
            register_selenium_driver(driver)
            
            # Check and fix crashed tabs FIRST (before any other action)
            if not GoLoginProfileHelper.check_and_fix_crashed_tabs(driver, debugger_address, "[GOLOGIN START]"):
                print(f"[GOLOGIN START] [{profile_id}] ✗ Could not fix crashed tabs")
                gologin.stop_profile(profile_id)
                return False
            
            # Bring to front and maximize browser window
            GoLoginProfileHelper.bring_profile_to_front(profile_id, driver=driver, log_prefix="[GOLOGIN START]")
            
            # Clean up old tabs using helper
            GoLoginProfileHelper.cleanup_browser_tabs(driver, "[GOLOGIN START]")
            
            # Wait for browser to settle
            time.sleep(2)
            
            # ========== EXECUTE ACTION BASED ON TYPE ==========
            action_type = self.params.get("action_type", "None")
            action_success = self._execute_action(driver, profile_id, action_type)
            
            if not action_success:
                print(f"[GOLOGIN START] [{profile_id}] ⚠ Action execution had issues")
            
            # Save profile info to global variables
            GlobalVariables().set("GOLOGIN_PROFILE_ID", profile_id)
            GlobalVariables().set("GOLOGIN_DEBUGGER_ADDRESS", debugger_address)
            print(f"[GOLOGIN START] ✓ Saved profile info to variables")
            
            return True
        
        except Exception as e:
            print(f"[GOLOGIN START] [{profile_id}] ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # CLEANUP DRIVER (browser stays open)
            if driver:
                try:
                    unregister_selenium_driver(driver)
                    driver.quit()
                    print(f"[GOLOGIN START] ✓ ChromeDriver cleaned up (browser stays open)")
                except Exception as e:
                    print(f"[GOLOGIN START] ⚠ Cleanup warning: {e}")
    
    def _execute_action(self, driver, profile_id, action_type):
        """
        Execute action based on action_type parameter using switch-case logic
        
        Args:
            driver: Selenium WebDriver instance
            profile_id: Profile ID for logging
            action_type: Type of action (None, Youtube, Google)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Switch-case logic for action types
            if action_type == "None":
                print(f"[GOLOGIN START] [{profile_id}] No action required, profile started")
                return True
            
            elif action_type == "Youtube":
                # Load keywords using helper
                keywords = GoLoginProfileHelper.load_keywords(self.params, "[GOLOGIN START]")
                if not keywords:
                    print(f"[GOLOGIN START] [{profile_id}] ✗ No keywords available for YouTube")
                    return False
                
                # Pick random keyword
                keyword = random.choice(keywords)
                
                # Execute YouTube flow
                return YouTubeFlow.execute(driver, keyword, profile_id)
            
            elif action_type == "Google":
                # Load keywords using helper
                keywords = GoLoginProfileHelper.load_keywords(self.params, "[GOLOGIN START]")
                if not keywords:
                    print(f"[GOLOGIN START] [{profile_id}] ✗ No keywords available for Google")
                    return False
                
                # Pick random keyword
                keyword = random.choice(keywords)
                
                # Execute Google flow
                return GoogleFlow.execute(driver, keyword, profile_id)
            
            else:
                print(f"[GOLOGIN START] [{profile_id}] ✗ Unknown action type: {action_type}")
                return False
        
        except Exception as e:
            print(f"[GOLOGIN START] [{profile_id}] ✗ Error executing action: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _start_parallel(self, profile_list, api_token):
        """Start multiple profiles in parallel using threading"""
        from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
        
        max_workers_str = self.params.get("max_workers", "3")
        try:
            max_workers = int(max_workers_str)
        except:
            max_workers = 2
        
        max_workers = min(max_workers, len(profile_list))
        
        print(f"[GOLOGIN START] Starting {len(profile_list)} profiles with {max_workers} parallel threads")
        
        # Store results
        results = []
        completed_profiles = []
        timeout_profiles = []
        
        # Create thread pool
        executor = ThreadPoolExecutor(max_workers=max_workers)
        
        try:
            # Submit all profiles to thread pool
            future_to_profile = {}
            for i, profile_id in enumerate(profile_list):
                if i > 0:
                    time.sleep(2)  # Stagger submissions
                
                future = executor.submit(
                    self._start_single_profile_with_focus, 
                    profile_id, 
                    api_token
                )
                future_to_profile[future] = profile_id
                print(f"[GOLOGIN START] Submitted thread {i+1}/{len(profile_list)}: {profile_id}")
            
            # Wait for all threads to complete
            for future in as_completed(future_to_profile, timeout=600):
                profile_id = future_to_profile[future]
                try:
                    success = future.result(timeout=60)
                    results.append(success)
                    completed_profiles.append(profile_id)
                    
                    if success:
                        print(f"[GOLOGIN START] ✓ Profile {profile_id} completed successfully")
                    else:
                        print(f"[GOLOGIN START] ✗ Profile {profile_id} failed")
                
                except TimeoutError:
                    print(f"[GOLOGIN START] ✗ Profile {profile_id} TIMEOUT")
                    results.append(False)
                    timeout_profiles.append(profile_id)
                
                except Exception as e:
                    print(f"[GOLOGIN START] ✗ Profile {profile_id} exception: {e}")
                    results.append(False)
        
        except Exception as e:
            print(f"[GOLOGIN START] ⚠ Parallel execution error: {e}")
        
        finally:
            executor.shutdown(wait=False)
        
        # Summary
        success_count = sum(results) if results else 0
        print(f"\n[GOLOGIN START] ========== SUMMARY ==========")
        print(f"[GOLOGIN START] Total: {len(profile_list)} profiles")
        print(f"[GOLOGIN START] Success: {success_count}")
        print(f"[GOLOGIN START] Failed: {len(results) - success_count}")
        print(f"[GOLOGIN START] Timeout: {len(timeout_profiles)}")
        print(f"[GOLOGIN START] ============================\n")
        
        self.set_variable(success_count > 0)
    
    def _start_single_profile_with_focus(self, profile_id, api_token):
        """
        Start single profile and bring to front (for parallel mode)
        
        Args:
            profile_id: Profile ID to start
            api_token: GoLogin API token
            
        Returns:
            bool: True if successful
        """
        """Start a single profile and execute actions"""
        
        try:
            # Start profile normally
            success = self._start_single_profile(profile_id, api_token)
            
            if not success:
                return False
            
            # Bring window to front if action is not None
            action_type = self.params.get("action_type", "None")
            if action_type != "None":
                time.sleep(1)  # Wait for window to fully open
                GoLoginProfileHelper.bring_profile_to_front(profile_id, driver=None, log_prefix="[GOLOGIN START]")
                time.sleep(1)  # Wait after bringing to front
            
            return True
        
        except Exception as e:
            print(f"[GOLOGIN START] [{profile_id}] Error in parallel start: {e}")
            return False
    
    def set_variable(self, success):
        """Set variable with result"""
        variable = self.params.get("variable", "")
        if variable:
            GlobalVariables().set(variable, "true" if success else "false")
