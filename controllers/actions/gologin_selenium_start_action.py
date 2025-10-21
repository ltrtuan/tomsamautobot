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
        """
        Execute parallel mode với ROUND-ROBIN ARCHITECTURE
    
        NEW WORKFLOW:
        Phase 1: Open tất cả profiles song song (parallel opening)
        Phase 2: Tạo flow iterator cho mỗi profile
        Phase 3: Round-robin execution:
            - Profile A → Execute chain 1 (LOCKED) → Release
            - Profile B → Execute chain 1 (LOCKED) → Release
            - Profile A → Execute chain 2 (LOCKED) → Release
            - Profile B → Execute chain 2 (LOCKED) → Release
            - ... (repeat cho đến khi tất cả profiles hết chains)
        Phase 4: Close tất cả profiles
    
        Args:
            profile_list: List of profile IDs to execute
        """
        import threading
        from helpers.flow_youtube import YouTubeFlow
        from helpers.flow_google import GoogleFlow
    
        print("\n" + "="*80)
        print("[PARALLEL MODE] 🚀 STARTING ROUND-ROBIN EXECUTION")
        print("="*80)
    
        # ========== PHASE 1: OPEN ALL PROFILES (PARALLEL OPENING) ==========
        print("\n[PHASE 1] Opening all profiles in parallel...")
    
        profile_data = {}  # {profile_id: {'driver': ..., 'debugger': ..., 'status': ...}}
        open_threads = []
        open_lock = threading.Lock()
    
        def open_profile_thread(profile_id):
            """Thread function để open 1 profile"""
            try:
                print(f"[PARALLEL][{profile_id}] Opening profile...")
            
                # Start profile qua GoLogin API
                success, result = self.gologin_api.start_profile(profile_id)
                if not success:
                    print(f"[PARALLEL][{profile_id}] ✗ Failed to start: {result}")
                    with open_lock:
                        profile_data[profile_id] = {'status': 'failed', 'error': result}
                    return
            
                debugger_address = result
                print(f"[PARALLEL][{profile_id}] ✓ Got debugger: {debugger_address}")
            
                # Connect Selenium
                driver = GoLoginProfileHelper.connect_selenium(
                    debugger_address, 
                    f"[PARALLEL][{profile_id}]"
                )
            
                if not driver:
                    print(f"[PARALLEL][{profile_id}] ✗ Failed to connect Selenium")
                    self.gologin_api.stop_profile(profile_id)
                    with open_lock:
                        profile_data[profile_id] = {'status': 'failed', 'error': 'Selenium connection failed'}
                    return
            
                # Register driver
                register_selenium_driver(driver, profile_id)
            
                # Cleanup tabs
                print(f"[PARALLEL][{profile_id}] Cleaning up browser tabs...")
                GoLoginProfileHelper.cleanup_browser_tabs(driver, f"[PARALLEL][{profile_id}]")
                time.sleep(1)
            
                # Store profile data
                with open_lock:
                    profile_data[profile_id] = {
                        'driver': driver,
                        'debugger_address': debugger_address,
                        'status': 'opened'
                    }
            
                print(f"[PARALLEL][{profile_id}] ✓ Profile opened successfully")
            
            except Exception as e:
                print(f"[PARALLEL][{profile_id}] ✗ Exception while opening: {e}")
                import traceback
                traceback.print_exc()
                with open_lock:
                    profile_data[profile_id] = {'status': 'error', 'error': str(e)}
    
        # Start opening all profiles in parallel threads
        for i, profile_id in enumerate(profile_list):
            if i > 0:
                time.sleep(2)  # Stagger profile opening để tránh overwhelm
        
            thread = threading.Thread(target=open_profile_thread, args=(profile_id,))
            thread.start()
            open_threads.append(thread)
            print(f"[PHASE 1] Submitted opening thread {i+1}/{len(profile_list)}: {profile_id}")
    
        # Wait for tất cả profiles open xong
        print(f"[PHASE 1] Waiting for all profiles to open...")
        for thread in open_threads:
            thread.join()
    
        # Check kết quả opening
        opened_profiles = [pid for pid, data in profile_data.items() if data.get('status') == 'opened']
        failed_profiles = [pid for pid, data in profile_data.items() if data.get('status') != 'opened']
    
        print(f"\n[PHASE 1] Opening results:")
        print(f"  ✓ Successfully opened: {len(opened_profiles)}/{len(profile_list)}")
        if failed_profiles:
            print(f"  ✗ Failed to open: {failed_profiles}")
    
        if not opened_profiles:
            print("[PARALLEL MODE] ✗ No profiles opened successfully, aborting")
            self.set_variable(False)
            return
    
        # ========== PHASE 2: CREATE FLOW ITERATORS ==========
        print("\n[PHASE 2] Creating flow iterators for opened profiles...")
    
        flow_iterators = {}  # {profile_id: FlowIterator}
        action_type = self.params.get("action_type", "None")
    
        if action_type == "None":
            print("[PHASE 2] Action type is 'None', skipping flow creation")
            print("[PARALLEL MODE] ✓ All profiles opened, no actions to execute")
            self.set_variable(True)
            return
    
        # Load keywords
        keywords = GoLoginProfileHelper.load_keywords(self.params, "[PARALLEL]")
        if not keywords:
            print("[PHASE 2] ✗ Failed to load keywords")
            self._cleanup_profiles(profile_data)
            self.set_variable(False)
            return
    
        # Create flow iterator cho mỗi opened profile
        for profile_id in opened_profiles:
            driver = profile_data[profile_id]['driver']
            debugger_address = profile_data[profile_id]['debugger_address']
            keyword = random.choice(keywords)
        
            try:
                # Tạo flow iterator dựa trên action type
                if action_type == "Youtube":
                    flow_iterator = YouTubeFlow.create_flow_iterator(
                        driver=driver,
                        keyword=keyword,
                        profile_id=profile_id,
                        debugger_address=debugger_address,
                        log_prefix=f"[PARALLEL][{profile_id}]"
                    )
                elif action_type == "Google":
                    flow_iterator = GoogleFlow.create_flow_iterator(
                        driver=driver,
                        keyword=keyword,
                        profile_id=profile_id,
                        debugger_address=debugger_address,
                        log_prefix=f"[PARALLEL][{profile_id}]"
                    )
                else:
                    print(f"[PHASE 2][{profile_id}] ✗ Unknown action type: {action_type}")
                    continue
            
                flow_iterators[profile_id] = flow_iterator
                print(f"[PHASE 2][{profile_id}] ✓ Flow iterator created (keyword: '{keyword}')")
            
            except Exception as e:
                print(f"[PHASE 2][{profile_id}] ✗ Failed to create flow iterator: {e}")
                import traceback
                traceback.print_exc()
    
        if not flow_iterators:
            print("[PHASE 2] ✗ No flow iterators created")
            self._cleanup_profiles(profile_data)
            self.set_variable(False)
            return
    
        print(f"[PHASE 2] ✓ Created {len(flow_iterators)} flow iterators")
    
        # ========== PHASE 3: ROUND-ROBIN CHAIN EXECUTION ==========
        print("\n[PHASE 3] Starting round-robin chain execution...")
        print("="*80)
    
        round_num = 1
        active_profiles = list(flow_iterators.keys())
    
        # Loop cho đến khi tất cả profiles hết chains
        while active_profiles:
            print(f"\n{'='*80}")
            print(f"[ROUND {round_num}] Active profiles: {len(active_profiles)}/{len(flow_iterators)}")
            print(f"{'='*80}\n")
        
            profiles_to_remove = []
        
            # Execute 1 chain cho mỗi active profile
            for profile_id in active_profiles:
                flow_iterator = flow_iterators[profile_id]
            
                # Check xem profile còn chain nào chưa
                if not flow_iterator.has_next_chain():
                    print(f"[ROUND {round_num}][{profile_id}] ✓ All chains completed")
                    profiles_to_remove.append(profile_id)
                    continue
            
                # Show progress
                progress = flow_iterator.get_progress()
                print(f"[ROUND {round_num}][{profile_id}] Progress: {progress['current']}/{progress['total']} chains ({progress['percentage']:.1f}%)")
            
                # Bring profile window to front trước khi execute
                driver = profile_data[profile_id]['driver']
                try:
                    driver.switch_to.window(driver.current_window_handle)
                    # Maximize window để đảm bảo visible
                    driver.maximize_window()
                    print(f"[ROUND {round_num}][{profile_id}] ✓ Window brought to front")
                except Exception as e:
                    print(f"[ROUND {round_num}][{profile_id}] ⚠ Could not bring window to front: {e}")
            
                # Execute next chain (ActionChainManager tự động acquire/release lock)
                print(f"\n[ROUND {round_num}][{profile_id}] >>> ACQUIRING LOCK & EXECUTING CHAIN <<<")
            
                try:
                    result = flow_iterator.execute_next_chain()
                
                    if result:
                        print(f"[ROUND {round_num}][{profile_id}] ✓ Chain executed successfully")
                    else:
                        print(f"[ROUND {round_num}][{profile_id}] ⚠ Chain failed, but continuing...")
                    
                except Exception as e:
                    print(f"[ROUND {round_num}][{profile_id}] ✗ Exception during chain execution: {e}")
                    import traceback
                    traceback.print_exc()
            
                print(f"[ROUND {round_num}][{profile_id}] >>> LOCK RELEASED <<<\n")
            
                # Small delay giữa các profiles trong cùng round
                time.sleep(2)
        
            # Remove profiles đã hoàn thành tất cả chains
            for profile_id in profiles_to_remove:
                active_profiles.remove(profile_id)
        
            round_num += 1
        
            # Safety check để tránh infinite loop
            if round_num > 100:
                print("[PHASE 3] ⚠ Safety limit reached (100 rounds), breaking loop")
                break
    
        print("\n" + "="*80)
        print("[PHASE 3] ✓ All profiles completed all chains")
        print("="*80)
    
        # ========== PHASE 4: CLEANUP PROFILES ==========
        print("\n[PHASE 4] Cleaning up and closing profiles...")
        self._cleanup_profiles(profile_data)
    
        print("\n[PARALLEL MODE] ✅ ROUND-ROBIN EXECUTION COMPLETED")
        self.set_variable(len(opened_profiles) > 0)

    def _cleanup_profiles(self, profile_data):
        """
        Helper method để cleanup và close tất cả profiles
    
        Process:
        1. Unregister Selenium driver
        2. Quit driver (close browser connection)
        3. Stop profile qua GoLogin API
    
        Args:
            profile_data: Dict chứa profile data với format:
                         {profile_id: {'driver': ..., 'debugger_address': ..., 'status': ...}}
        """
        print("\n[CLEANUP] Starting profile cleanup...")
    
        for profile_id, data in profile_data.items():
            # Chỉ cleanup profiles đã mở thành công
            if data.get('status') != 'opened':
                continue
        
            try:
                print(f"[CLEANUP][{profile_id}] Closing profile...")
            
                # Step 1: Unregister driver
                try:
                    unregister_selenium_driver(profile_id)
                    print(f"[CLEANUP][{profile_id}]   ✓ Driver unregistered")
                except Exception as e:
                    print(f"[CLEANUP][{profile_id}]   ⚠ Failed to unregister driver: {e}")
            
                # Step 2: Quit driver (close browser connection)
                if 'driver' in data:
                    try:
                        data['driver'].quit()
                        print(f"[CLEANUP][{profile_id}]   ✓ Driver quit")
                    except Exception as e:
                        print(f"[CLEANUP][{profile_id}]   ⚠ Failed to quit driver: {e}")
            
                # Wait for driver cleanup to complete (critical for parallel execution)
                print(f"[CLEANUP][{profile_id}] Waiting 5s for driver cleanup...")
                time.sleep(5)  # Give browser time to close gracefully
                
                # Step 3: Stop profile qua API
                try:
                    self.gologin_api.stop_profile(profile_id)
                    print(f"[CLEANUP][{profile_id}]   ✓ Profile stopped via API")
                except Exception as e:
                    print(f"[CLEANUP][{profile_id}]   ⚠ Failed to stop profile: {e}")
            
                print(f"[CLEANUP][{profile_id}] ✓ Cleanup completed")
            
            except Exception as e:
                print(f"[CLEANUP][{profile_id}] ✗ Error during cleanup: {e}")
                import traceback
                traceback.print_exc()
    
        print("[CLEANUP] ✓ All profiles cleanup completed")


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
