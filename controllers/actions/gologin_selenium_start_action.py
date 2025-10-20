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
            
            # ========== INITIALIZE GOLOGIN API INSTANCE ==========
            self.gologin_api = get_gologin_api(api_token)
            # ====================================================
            
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
                self._start_parallel(profile_list)
            else:
                # SEQUENTIAL MODE - Select 1 profile and start
                print("[GOLOGIN START] ========== SEQUENTIAL MODE ==========")
                how_to_get = self.params.get("how_to_get", "Random")
                profile_id = GoLoginProfileHelper.select_profile(profile_list, how_to_get)
                print(f"[GOLOGIN START] Selected profile ID: {profile_id}")
                
                # Start single profile
                success = self._start_single_profile(profile_id)
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
    
    def _start_parallel(self, profile_list):
        """Start multiple profiles in parallel - NO TIMEOUT"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        max_workers = min(int(self.params.get("max_workers", "3")), len(profile_list))
        print(f"[GOLOGIN START] Starting {len(profile_list)} profiles with {max_workers} threads")
        
        results = []
        success_count = [0]  # Use list for mutable counter
        
        executor = ThreadPoolExecutor(max_workers=max_workers)
        try:
            # Submit all threads
            future_to_profile = {}
            for i, profile_id in enumerate(profile_list):
                if i > 0:
                    time.sleep(3)  # Stagger 3s
                
                future = executor.submit(self._start_single_profile, profile_id)
                future_to_profile[future] = profile_id
                print(f"[GOLOGIN START] Submitted {i+1}/{len(profile_list)}: {profile_id}")
            
            # Wait for all threads WITHOUT TIMEOUT
            for future in as_completed(future_to_profile):
                profile_id = future_to_profile[future]
                try:
                    success = future.result()  # No timeout - wait indefinitely
                    results.append(success)
                    if success:
                        success_count[0] += 1
                    print(f"[GOLOGIN START] {'✓' if success else '✗'} Profile {profile_id} completed")
                except Exception as e:
                    print(f"[GOLOGIN START] ✗ Profile {profile_id} exception: {e}")
                    results.append(False)
        
        finally:
            executor.shutdown(wait=True)
        
        # Summary
        print(f"\n[GOLOGIN START] ========== SUMMARY ==========")
        print(f"[GOLOGIN START] Success: {success_count[0]}/{len(profile_list)}")
        print(f"[GOLOGIN START] ============================\n")
        
        self.set_variable(success_count[0] > 0)
    
    def _start_single_profile(self, profile_id):
        """Start profile and execute action - Profile stays alive"""
        driver = None
        try:
            # ========== START PROFILE USING GOLOGIN API ==========
            print(f"[GOLOGIN START] [{profile_id}] Starting profile...")
            success, result = self.gologin_api.start_profile(profile_id)
        
            if not success:
                print(f"[GOLOGIN START] [{profile_id}] ✗ Failed to start: {result}")
                return False
        
            # result is debugger_address string, not dict
            debugger_address = result
            print(f"[GOLOGIN START] [{profile_id}] ✓ Got debugger: {debugger_address}")
            # ====================================================
        
            # Connect Selenium
            driver = GoLoginProfileHelper.connect_selenium(debugger_address, "[GOLOGIN START]")
            if not driver:
                print(f"[GOLOGIN START] [{profile_id}] ✗ Failed to connect Selenium")
                # Stop profile if connection failed
                self.gologin_api.stop_profile(profile_id)
                return False
        
            # Register driver
            register_selenium_driver(driver, profile_id)
            
        
            # Cleanup tabs (after crash fix)
            print(f"[GOLOGIN START] [{profile_id}] Checking browser tabs...")
            GoLoginProfileHelper.cleanup_browser_tabs(driver, "[GOLOGIN START]")
            time.sleep(2)        
            
        
            # Execute action chain
            action_type = self.params.get("action_type", "None")
            action_success = self._execute_action(driver, profile_id, action_type, debugger_address)
        
            print(f"[GOLOGIN START] [{profile_id}] ✓ Profile continues running")
            return action_success
        
        except Exception as e:
            print(f"[GOLOGIN START] [{profile_id}] ✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
            # Cleanup on error (giống collect action)
            if driver:
                try:
                    unregister_selenium_driver(profile_id)
                except:
                    pass
                try:
                    driver.quit()
                except:
                    pass
        
            # Try to stop profile if started
            try:
                self.gologin_api.stop_profile(profile_id)
            except:
                pass
        
            return False
    
        finally:
            # Unregister driver but DON'T close it (profile stays alive)
            if driver:
                try:
                    unregister_selenium_driver(profile_id)
                except:
                    pass

    
    def _execute_action(self, driver, profile_id, action_type, debugger_address):
        """Execute action based on type"""
        try:
            if action_type == "None":
                print(f"[GOLOGIN START] [{profile_id}] No action required")
                return True
            
            elif action_type == "Youtube":
                keywords = GoLoginProfileHelper.load_keywords(self.params, "[GOLOGIN START]")
                if not keywords:
                    return False
                keyword = random.choice(keywords)
                return YouTubeFlow.execute_main_flow(driver, keyword, profile_id, debugger_address, "[GOLOGIN START]")
            
            elif action_type == "Google":
                keywords = GoLoginProfileHelper.load_keywords(self.params, "[GOLOGIN START]")
                if not keywords:
                    return False
                keyword = random.choice(keywords)
                return GoogleFlow.execute_main_flow(driver, keyword, profile_id, debugger_address, "[GOLOGIN START]")
            
            else:
                print(f"[GOLOGIN START] [{profile_id}] ✗ Unknown action type")
                return False
                
        except Exception as e:
            print(f"[GOLOGIN START] [{profile_id}] ✗ Error executing action: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def set_variable(self, success):
        """Set variable with result"""
        variable = self.params.get("variable", "")
        if variable:
            GlobalVariables().set(variable, "true" if success else "false")
