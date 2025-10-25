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
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    
    # def _start_parallel(self, profile_list):
    #     """
    #     Execute parallel mode với ROUND-ROBIN ARCHITECTURE
    
    #     NEW WORKFLOW:
    #     Phase 1: Open tất cả profiles song song (parallel opening)
    #     Phase 2: Tạo flow iterator cho mỗi profile
    #     Phase 3: Round-robin execution:
    #         - Profile A → Execute chain 1 (LOCKED) → Release
    #         - Profile B → Execute chain 1 (LOCKED) → Release
    #         - Profile A → Execute chain 2 (LOCKED) → Release
    #         - Profile B → Execute chain 2 (LOCKED) → Release
    #         - ... (repeat cho đến khi tất cả profiles hết chains)
    #     Phase 4: Close tất cả profiles
    
    #     Args:
    #         profile_list: List of profile IDs to execute
    #     """
    #     import threading
    #     from helpers.flow_youtube import YouTubeFlow
    #     from helpers.flow_google import GoogleFlow
    
    #     # Get max parallel profiles from params
    #     max_parallel_profiles = int(self.params.get("max_workers", 2))
    
    #     print("\n" + "="*80)
    #     print(f"[PARALLEL MODE] 🚀 STARTING CONTROLLED EXECUTION (max {max_parallel_profiles} concurrent)")
    #     print("="*80)
    
    #     # ========== PHASE 1: OPEN PROFILES (CONTROLLED PARALLEL) ==========
    #     print(f"\n[PHASE 1] Opening profiles (max {max_parallel_profiles} concurrent)...")
    #     profile_data = {}  # {profile_id: {'driver': ..., 'debugger': ..., 'status': ...}}
    #     open_lock = threading.Lock()

    #     def open_profile_thread(profile_id):
    #         """Thread function to open 1 profile"""
    #         try:
    #             print(f"[PARALLEL][{profile_id}] Opening profile...")
    #             # Start profile via GoLogin API
    #             success, result = self.gologin_api.start_profile(profile_id)
    #             if not success:
    #                 print(f"[PARALLEL][{profile_id}] ✗ Failed to start: {result}")
    #                 with open_lock:
    #                     profile_data[profile_id] = {'status': 'failed', 'error': result}
    #                 return
        
    #             debugger_address = result
    #             print(f"[PARALLEL][{profile_id}] ✓ Got debugger: {debugger_address}")
        
    #             # Connect Selenium
    #             driver = GoLoginProfileHelper.connect_selenium(
    #                 debugger_address,
    #                 f"[PARALLEL][{profile_id}]"
    #             )
        
    #             if not driver:
    #                 print(f"[PARALLEL][{profile_id}] ✗ Failed to connect Selenium")
    #                 self.gologin_api.stop_profile(profile_id)
    #                 with open_lock:
    #                     profile_data[profile_id] = {'status': 'failed', 'error': 'Selenium connection failed'}
    #                 return
        
    #             # Register driver
    #             register_selenium_driver(driver, profile_id)
        
    #             # Cleanup tabs
    #             print(f"[PARALLEL][{profile_id}] Cleaning up browser tabs...")
    #             GoLoginProfileHelper.cleanup_browser_tabs(driver, f"[PARALLEL][{profile_id}]")
    #             time.sleep(1)
        
    #             # Store profile data
    #             with open_lock:
    #                 profile_data[profile_id] = {
    #                     'driver': driver,
    #                     'debugger_address': debugger_address,
    #                     'status': 'opened'
    #                 }
        
    #             print(f"[PARALLEL][{profile_id}] ✓ Profile opened successfully")
        
    #         except Exception as e:
    #             print(f"[PARALLEL][{profile_id}] ✗ Exception while opening: {e}")
    #             import traceback
    #             traceback.print_exc()
    #             with open_lock:
    #                 profile_data[profile_id] = {'status': 'error', 'error': str(e)}
                    

    
    #     # Use ThreadPoolExecutor with CONTROLLED SUBMISSION (like Collect action)
    #     executor = ThreadPoolExecutor(max_workers=max_parallel_profiles)
    #     try:
    #         # Submit profiles với stagger delay để control concurrency
    #         future_to_profile = {}
    #         for i, profile_id in enumerate(profile_list):
    #             # Stagger delay 2s giữa các submission (trừ profile đầu tiên)
    #             if i > 0:
    #                 time.sleep(2)
        
    #             future = executor.submit(open_profile_thread, profile_id)
    #             future_to_profile[future] = profile_id
    #             print(f"[PHASE 1] Submitted thread {i+1}/{len(profile_list)}: {profile_id}")
        
    #             # Cooling period sau mỗi batch max_workers profiles
    #             # if (i + 1) % max_parallel_profiles == 0 and (i + 1) < len(profile_list):
    #             #     print(f"[PHASE 1] ⏸ Cooling down for 30 seconds after {i+1} profiles...")
    #             #     time.sleep(30)
    
    #         # Wait for all submissions to complete
    #         for future in as_completed(future_to_profile):
    #             profile_id = future_to_profile[future]
    #             try:
    #                 future.result()  # This will raise exception if thread failed
    #             except Exception as e:
    #                 print(f"[PHASE 1] ✗ Thread for {profile_id} raised exception: {e}")

    #     finally:
    #         # Ensure executor is properly shut down
    #         executor.shutdown(wait=True)
    #         print(f"[PHASE 1] ✓ Thread pool shut down")
    

    
    #     # Check opening results
    #     opened_profiles = [pid for pid, data in profile_data.items() if data.get('status') == 'opened']
    #     failed_profiles = [pid for pid, data in profile_data.items() if data.get('status') != 'opened']
    
    #     print(f"\n[PHASE 1] Opening results:")
    #     print(f"  ✓ Successfully opened: {len(opened_profiles)}/{len(profile_list)}")
    #     if failed_profiles:
    #         print(f"  ✗ Failed to open: {failed_profiles}")
    
    #     if not opened_profiles:
    #         print("[PARALLEL MODE] ✗ No profiles opened successfully, aborting")
    #         self.set_variable(False)
    #         return
    
    #     # ========== PHASE 2: CREATE FLOW ITERATORS ==========
    #     print("\n[PHASE 2] Creating flow iterators for opened profiles...")
    #     flow_iterators = {}  # {profile_id: FlowIterator}
    
    #     action_type = self.params.get("action_type", "None")
    #     if action_type == "None":
    #         print("[PHASE 2] Action type is 'None', skipping flow creation")
    #         print("[PARALLEL MODE] ✓ All profiles opened, no actions to execute")
    #         self.set_variable(True)
    #         return
    
    #     # Load keywords
    #     keywords = GoLoginProfileHelper.load_keywords(self.params, "[PARALLEL]")
    #     if not keywords:
    #         print("[PHASE 2] ✗ Failed to load keywords")
    #         self._cleanup_profiles(profile_data)
    #         self.set_variable(False)
    #         return
    
    #     # Create flow iterator for each opened profile
    #     for profile_id in opened_profiles:
    #         driver = profile_data[profile_id]['driver']
    #         debugger_address = profile_data[profile_id]['debugger_address']
        
    #         try:
    #             # Create flow iterator based on action type
    #             if action_type == "Youtube":
    #                 flow_iterator = YouTubeFlow.create_flow_iterator(
    #                     driver=driver,
    #                     keywords=keywords,
    #                     profile_id=profile_id,
    #                     debugger_address=debugger_address,
    #                     log_prefix=f"[PARALLEL][{profile_id}]"
    #                 )
    #             elif action_type == "Google":
    #                 flow_iterator = GoogleFlow.create_flow_iterator(
    #                     driver=driver,
    #                     keywords=keywords,
    #                     profile_id=profile_id,
    #                     debugger_address=debugger_address,
    #                     log_prefix=f"[PARALLEL][{profile_id}]"
    #                 )
    #             else:
    #                 print(f"[PHASE 2][{profile_id}] ✗ Unknown action type: {action_type}")
    #                 continue
            
    #             flow_iterators[profile_id] = flow_iterator
            
    #         except Exception as e:
    #             print(f"[PHASE 2][{profile_id}] ✗ Failed to create flow iterator: {e}")
    #             import traceback
    #             traceback.print_exc()
    
    #     if not flow_iterators:
    #         print("[PHASE 2] ✗ No flow iterators created")
    #         self._cleanup_profiles(profile_data)
    #         self.set_variable(False)
    #         return
    
    #     print(f"[PHASE 2] ✓ Created {len(flow_iterators)} flow iterators")
    
    #     # ========== PHASE 3: ROUND-ROBIN CHAIN EXECUTION ==========
    #     print("\n[PHASE 3] Starting round-robin chain execution...")
    #     print("="*80)
    
    #     round_num = 1
    #     active_profiles = list(flow_iterators.keys())
    
    #     # Loop until all profiles complete all chains
    #     while active_profiles:
    #         print(f"\n{'='*80}")
    #         print(f"[ROUND {round_num}] Active profiles: {len(active_profiles)}/{len(flow_iterators)}")
    #         print(f"{'='*80}\n")
        
    #         profiles_to_remove = []
        
    #         # Execute 1 chain for each active profile
    #         for profile_id in active_profiles:
    #             flow_iterator = flow_iterators[profile_id]
            
    #             # Check if profile has more chains
    #             if not flow_iterator.has_next_chain():
    #                 print(f"[ROUND {round_num}][{profile_id}] ✓ All chains completed")
    #                 profiles_to_remove.append(profile_id)
    #                 continue
            
    #             # Show progress
    #             progress = flow_iterator.get_progress()
    #             print(f"[ROUND {round_num}][{profile_id}] Progress: {progress['current']}/{progress['total']} chains ({progress['percentage']:.1f}%)")
            
    #             # Bring profile window to front before execute
    #             driver = profile_data[profile_id]['driver']
    #             try:
    #                 driver.switch_to.window(driver.current_window_handle)
    #                 # Maximize window to ensure visible
    #                 driver.maximize_window()
    #                 print(f"[ROUND {round_num}][{profile_id}] ✓ Window brought to front")
    #             except Exception as e:
    #                 print(f"[ROUND {round_num}][{profile_id}] ⚠ Could not bring window to front: {e}")
            
    #             # Execute next chain (ActionChainManager auto acquire/release lock)
    #             print(f"\n[ROUND {round_num}][{profile_id}] >>> ACQUIRING LOCK & EXECUTING CHAIN <<<")
    #             try:
    #                 result = flow_iterator.execute_next_chain()
    #                 if result:
    #                     print(f"[ROUND {round_num}][{profile_id}] ✓ Chain executed successfully")
    #                 else:
    #                     print(f"[ROUND {round_num}][{profile_id}] ⚠ Chain failed, but continuing...")
    #             except Exception as e:
    #                 print(f"[ROUND {round_num}][{profile_id}] ✗ Exception during chain execution: {e}")
    #                 import traceback
    #                 traceback.print_exc()
            
    #             print(f"[ROUND {round_num}][{profile_id}] >>> LOCK RELEASED <<<\n")
            
    #             # Small delay between profiles in same round
    #             time.sleep(2)
        
    #         # Remove profiles that completed all chains
    #         for profile_id in profiles_to_remove:
    #             active_profiles.remove(profile_id)
        
    #         round_num += 1
        
    #         # Safety check to avoid infinite loop
    #         if round_num > 100:
    #             print("[PHASE 3] ⚠ Safety limit reached (100 rounds), breaking loop")
    #             break
    
    #     print("\n" + "="*80)
    #     print("[PHASE 3] ✓ All profiles completed all chains")
    #     print("="*80)
    
    #     # ========== PHASE 4: CLEANUP PROFILES (CONTROLLED PARALLEL) ==========
    #     print(f"\n[PHASE 4] Cleaning up profiles (max {max_parallel_profiles} concurrent)...")
    #     self._cleanup_profiles(profile_data)
    
    #     print("\n[PARALLEL MODE] ✅ CONTROLLED EXECUTION COMPLETED")
    #     self.set_variable(len(opened_profiles) > 0)
        
        
    def _start_parallel(self, profile_list):
        """
        Execute parallel mode with BATCH PROCESSING
    
        NEW WORKFLOW:
        - Divide profiles into batches of size = max_workers
        - For each batch:
          1. Open all profiles in batch (parallel)
          2. Execute all chains round-robin (with lock) - if action_type != "None"
          3. Close all profiles in batch (parallel) - if action_type != "None"
        - Repeat until all profiles processed
    
        Args:
            profile_list: List of profile IDs to execute
        """
        import threading
        from concurrent.futures import ThreadPoolExecutor, as_completed
    
        max_parallel_profiles = int(self.params.get("max_workers", "1"))
        action_type = self.params.get("action_type", "None")
    
        print("\n[GOLOGIN START] ========== PARALLEL MODE ==========")
        print("=" * 80)
        print(f"[PARALLEL MODE] 🚀 BATCH PROCESSING (batch size = {max_parallel_profiles})")
        print(f"[PARALLEL MODE] Total profiles: {len(profile_list)}")
        print(f"[PARALLEL MODE] Action type: {action_type}")
        print("=" * 80)
    
        # Divide profiles into batches
        batches = []
        for i in range(0, len(profile_list), max_parallel_profiles):
            batch = profile_list[i:i + max_parallel_profiles]
            batches.append(batch)
    
        print(f"[PARALLEL MODE] Divided into {len(batches)} batch(es)")
        print()
    
        total_success = 0
        total_failed = 0
    
        # Process each batch
        for batch_num, batch_profiles in enumerate(batches, 1):
            print("=" * 80)
            print(f"[BATCH {batch_num}/{len(batches)}] Processing {len(batch_profiles)} profile(s): {batch_profiles}")
            print("=" * 80)
            print()
        
            # ========== PHASE 1: OPEN BATCH PROFILES ==========
            print(f"[BATCH {batch_num}][PHASE 1] Opening {len(batch_profiles)} profile(s) (max {max_parallel_profiles} concurrent)...")
        
            profile_data = {}  # {profile_id: {'driver': ..., 'debugger': ..., 'status': ...}}
            open_lock = threading.Lock()
        
            def open_profile_thread(profile_id):
                """Thread function to open 1 profile"""
                try:
                    print(f"[BATCH {batch_num}][{profile_id}] Opening profile...")
                
                    # Start profile via GoLogin API
                    success, result = self.gologin_api.start_profile(profile_id)
                    if not success:
                        print(f"[BATCH {batch_num}][{profile_id}] ✗ Failed to start: {result}")
                        with open_lock:
                            profile_data[profile_id] = {'status': 'failed', 'error': result}
                        return
                
                    debugger_address = result
                    print(f"[BATCH {batch_num}][{profile_id}] ✓ Got debugger: {debugger_address}")
                
                    # Connect Selenium
                    driver = GoLoginProfileHelper.connect_selenium(
                        debugger_address,
                        f"[BATCH {batch_num}][{profile_id}]"
                    )
                
                    if not driver:
                        print(f"[BATCH {batch_num}][{profile_id}] ✗ Failed to connect Selenium")
                        self.gologin_api.stop_profile(profile_id)
                        with open_lock:
                            profile_data[profile_id] = {'status': 'failed', 'error': 'Selenium connection failed'}
                        return
                
                    # Register driver
                    register_selenium_driver(driver, profile_id)
                
                    # Cleanup tabs
                    print(f"[BATCH {batch_num}][{profile_id}] Cleaning up browser tabs...")
                    GoLoginProfileHelper.cleanup_browser_tabs(driver, f"[BATCH {batch_num}][{profile_id}]")
                    time.sleep(1)
                
                    # Store profile data
                    with open_lock:
                        profile_data[profile_id] = {
                            'driver': driver,
                            'debugger_address': debugger_address,
                            'status': 'opened'
                        }
                
                    print(f"[BATCH {batch_num}][{profile_id}] ✓ Profile opened successfully")
                
                except Exception as e:
                    print(f"[BATCH {batch_num}][{profile_id}] ✗ Exception while opening: {e}")
                    import traceback
                    traceback.print_exc()
                    with open_lock:
                        profile_data[profile_id] = {'status': 'error', 'error': str(e)}
        
            # Use ThreadPoolExecutor to open profiles
            
            executor = ThreadPoolExecutor(max_workers=max_parallel_profiles)
            try:
                future_to_profile = {}
                for i, profile_id in enumerate(batch_profiles):
                    if i > 0:
                        time.sleep(2)  # Stagger delay
                
                    future = executor.submit(open_profile_thread, profile_id)
                    future_to_profile[future] = profile_id
                    print(f"[BATCH {batch_num}][PHASE 1] Submitted thread {i+1}/{len(batch_profiles)}: {profile_id}")
            
                # Wait for all to complete
                for future in as_completed(future_to_profile):
                    profile_id = future_to_profile[future]
                    try:
                        future.result()
                    except Exception as e:
                        print(f"[BATCH {batch_num}][PHASE 1] ✗ Thread for {profile_id} raised exception: {e}")
        
            finally:
                executor.shutdown(wait=True)
                print(f"[BATCH {batch_num}][PHASE 1] ✓ Thread pool shut down")
        
            # Check opening results
            opened_profiles = [pid for pid, data in profile_data.items() if data.get('status') == 'opened']
            failed_profiles = [pid for pid, data in profile_data.items() if data.get('status') in ['failed', 'error']]
        
            print(f"\n[BATCH {batch_num}][PHASE 1] Opening results:")
            print(f"  ✓ Successfully opened: {len(opened_profiles)}/{len(batch_profiles)}")
            if failed_profiles:
                print(f"  ✗ Failed: {len(failed_profiles)}")
            print()
        
            if not opened_profiles:
                print(f"[BATCH {batch_num}] ✗ No profiles opened successfully, skipping to next batch")
                total_failed += len(batch_profiles)
                continue
            
            # ========== CHECK ACTION TYPE ==========
            if action_type == "None":
                print(f"[BATCH {batch_num}][PHASE 2] Action type is 'None', skipping flow creation and execution")
                print(f"[BATCH {batch_num}] ✓ Batch profiles opened and kept running (no cleanup)")
                total_success += len(opened_profiles)
                total_failed += len(failed_profiles)
                continue  # Skip to next batch, profiles stay open
        
            # ========== PHASE 2: CREATE FLOW ITERATORS ==========
            print(f"[BATCH {batch_num}][PHASE 2] Creating flow iterators for opened profiles...")
            
            # Load keywords
            keywords = GoLoginProfileHelper.load_keywords(self.params, "[PARALLEL]")
            if not keywords:
                print("[PHASE 2] ✗ Failed to load keywords")
                GoLoginProfileHelper.cleanup_profiles(profile_data, self.gologin_api, "[CLEANUP]")
                self.set_variable(False)
                return
            
            flow_iterators = {}  # {profile_id: flow_iterator}
        
            
            for profile_id in opened_profiles:
                driver = profile_data[profile_id]['driver']
                debugger_address = profile_data[profile_id]['debugger_address']
                try:
                    # Create flow iterator based on action type
                    if action_type == "Youtube":
                        flow_iterator = YouTubeFlow.create_flow_iterator(
                            driver=driver,
                            keywords=keywords,
                            profile_id=profile_id,
                            debugger_address=debugger_address,
                            log_prefix=f"[BATCH {batch_num}][{profile_id}]"
                        )
                    elif action_type == "Google":
                        flow_iterator = GoogleFlow.create_flow_iterator(
                            driver=driver,
                            keywords=keywords,
                            profile_id=profile_id,
                            debugger_address=debugger_address,
                            log_prefix=f"[BATCH {batch_num}][{profile_id}]"
                        )
                    else:
                        print(f"[BATCH {batch_num}][{profile_id}] ✗ Unknown action type: {action_type}")
                        continue
        
                    flow_iterators[profile_id] = flow_iterator
        
                except Exception as e:
                    print(f"[BATCH {batch_num}][{profile_id}] ✗ Failed to create flow iterator: {e}")
                    import traceback
                    traceback.print_exc()
                    # Remove from opened_profiles
                    opened_profiles.remove(profile_id)
        
            print(f"[BATCH {batch_num}][PHASE 2] ✓ Created {len(flow_iterators)} flow iterators")
        
            # ========== PHASE 3: EXECUTE CHAINS ROUND-ROBIN ==========
            print(f"[BATCH {batch_num}][PHASE 3] Starting round-robin chain execution...")
            print("=" * 80)
        
            active_profiles = opened_profiles.copy()
            round_num = 0
        
            while active_profiles:
                round_num += 1
                print()
                print("=" * 80)
                print(f"[BATCH {batch_num}][ROUND {round_num}] Active profiles: {len(active_profiles)}/{len(opened_profiles)}")
                print("=" * 80)
                print()
            
                profiles_to_remove = []
            
                for profile_id in active_profiles:
                    flow = flow_iterators[profile_id]
                
                    # Check if profile completed all chains
                    if not flow.has_next_chain():
                        print(f"[BATCH {batch_num}][ROUND {round_num}][{profile_id}] ✓ All chains completed")
                        profiles_to_remove.append(profile_id)                           
    
                        continue

                
                    # Show progress
                    progress = flow.get_progress()
                    print(f"[BATCH {batch_num}][ROUND {round_num}][{profile_id}] Progress: {progress['current']}/{progress['total']} chains ({progress['percentage']:.1f}%)")

                
                    # Bring window to front
                    try:
                        GoLoginProfileHelper.bring_profile_to_front(
                            profile_id,
                            driver=profile_data[profile_id]['driver'],
                            log_prefix=f"[BATCH {batch_num}][ROUND {round_num}][{profile_id}]"
                        )
                        print(f"[BATCH {batch_num}][ROUND {round_num}][{profile_id}] ✓ Window brought to front")
                    except Exception as e:
                        print(f"[BATCH {batch_num}][ROUND {round_num}][{profile_id}] ⚠ Could not bring to front: {e}")
                
                    # Execute one chain (with LOCK)
                    print(f"\n[BATCH {batch_num}][ROUND {round_num}][{profile_id}] >>> ACQUIRING LOCK & EXECUTING CHAIN <<<")
                
                    try:
                        success = flow.execute_next_chain()
                    
                        if success:
                            print(f"[BATCH {batch_num}][ROUND {round_num}][{profile_id}] ✓ Chain executed successfully")
                        else:
                            print(f"[BATCH {batch_num}][ROUND {round_num}][{profile_id}] ✗ Chain execution failed")
                            profiles_to_remove.append(profile_id)
                    
                    except Exception as e:
                        print(f"[BATCH {batch_num}][ROUND {round_num}][{profile_id}] ✗ Exception during chain execution: {e}")
                        import traceback
                        traceback.print_exc()
                        profiles_to_remove.append(profile_id)
                
                    print(f"[BATCH {batch_num}][ROUND {round_num}][{profile_id}] >>> LOCK RELEASED <<<\n")
            
                # Remove completed/failed profiles
                # for profile_id in profiles_to_remove:
                #     active_profiles.remove(profile_id)
                # Convert to set for O(1) lookup
                profiles_to_remove_set = set(profiles_to_remove)
                active_profiles = [pid for pid in active_profiles if pid not in profiles_to_remove_set]

        
            print()
            print("=" * 80)
            print(f"[BATCH {batch_num}][PHASE 3] ✓ All profiles completed all chains")
            print("=" * 80)
            print()
        
            
            # ========== PHASE 4: CLEANUP TẤT CẢ (KHÔNG KIỂM TRA 'cleaned_up'!) ==========
            print(f"[BATCH {batch_num}][PHASE 4] Cleaning up {len(opened_profiles)} profile(s)...")

            # Use centralized helper method (handles all profiles sequentially with proper wait times)
            cleanup_results = GoLoginProfileHelper.cleanup_profiles(
                profile_data={pid: profile_data[pid] for pid in opened_profiles},
                gologin_api=self.gologin_api,
                log_prefix=f"[BATCH {batch_num}][CLEANUP]"
            )

            # Count results
            cleanup_success = sum(1 for r in cleanup_results.values() if r)
            print(f"[BATCH {batch_num}][PHASE 4] ✓ Cleanup completed: {cleanup_success}/{len(cleanup_results)}")
            # Update batch statistics
            total_success += cleanup_success
            total_failed += (len(batch_profiles) - cleanup_success)

    
        # ========== FINAL SUMMARY ==========
        print()
        print("=" * 80)
        print("[PARALLEL MODE] ✓ ALL BATCHES COMPLETED")
        print("=" * 80)
        print(f"Total profiles processed: {len(profile_list)}")
        print(f"  ✓ Success: {total_success}")
        print(f"  ✗ Failed: {total_failed}")
        print("=" * 80)
    
        # Set result variable
        self.set_variable(True)



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
            # ========== CLEANUP: STOP PROFILE ==========
            # Skip cleanup if action_type is None (keep profiles running)
            action_type = self.params.get("action_type", "None")
            if action_type == "None":
                print(f"[GOLOGIN START] [{profile_id}] ⚠ Action type is 'None', profile will remain open (no cleanup)")
                return action_success if 'action_success' in locals() else False
    
            # Use centralized cleanup method from helper
            if driver:
                try:
                    GoLoginProfileHelper.cleanup_profiles(
                        profile_data={"profile_id": profile_id, "driver": driver},
                        gologin_api=self.gologin_api,
                        log_prefix="[CLEANUP]"
                    )
                except Exception as cleanup_err:
                    print(f"[CLEANUP][{profile_id}] ✗ Cleanup error: {cleanup_err}")
                    import traceback
                    traceback.print_exc()



    
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
                return YouTubeFlow.execute_main_flow(driver, keywords, profile_id, debugger_address, "[GOLOGIN START]")
            
            elif action_type == "Google":
                keywords = GoLoginProfileHelper.load_keywords(self.params, "[GOLOGIN START]")
                if not keywords:
                    return False
                return GoogleFlow.execute_main_flow(driver, keywords, profile_id, debugger_address, "[GOLOGIN START]")
            
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
