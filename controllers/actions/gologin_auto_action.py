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

class GoLoginAutoAction(BaseAction):
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
            
    
    def _open_profile(self, profile_id, batch_num=None):
        """
        Open profile via GoLogin SDK WITHOUT Selenium connection
        Profile runs in MANUAL mode (no automation)
    
        Args:
            profile_id: Profile ID to open
            batch_num: Batch number for logging (optional)
    
        Returns:
            dict: {
                'success': bool,
                'profile_id': str,
                'error': str or None
            }
        """
        log_prefix = f"[BATCH {batch_num}][{profile_id}]" if batch_num else f"[GOLOGIN AUTO][{profile_id}]"
    
        try:
            print(f"{log_prefix} Opening profile (MANUAL mode - NO Selenium)...")
            
            # ========== CHECK REFRESH FINGERPRINT OPTION (NEW) ==========
            refresh_fingerprint = self.params.get("refresh_fingerprint", False)
        
            if refresh_fingerprint:
                print(f"{log_prefix} Refreshing fingerprint...")
                success = self.gologin_api.refresh_fingerprint(profile_id)
            
                if success:
                    print(f"{log_prefix} ✓ Fingerprint refreshed")
                else:
                    print(f"{log_prefix} ⚠️ Failed to refresh fingerprint")
        
            # ========== START PROFILE VIA GOLOGIN SDK ==========
            # GoLogin SDK starts Orbita browser in background
            # Returns: (success: bool, debugger_address: str)
            success, result = self.gologin_api.start_profile(profile_id)
        
            if not success:
                print(f"{log_prefix} ❌ Failed to start profile")
                print(f"{log_prefix} Error: {result}")
                return {
                    'success': False,
                    'profile_id': profile_id,
                    'error': result
                }
        
            # ========== PROFILE STARTED SUCCESSFULLY ==========
            # result = debugger_address (e.g., "127.0.0.1:9222")
            # We don't need it since no Selenium connection
            debugger_address = result
        
            print(f"{log_prefix} ✓ Profile opened successfully")
            print(f"{log_prefix} ℹ️  Browser running in MANUAL mode")
            print(f"{log_prefix} ℹ️  Debugger: {debugger_address} (not used)")
        
            # ========== WAIT FOR BROWSER TO STABILIZE ==========
            time.sleep(2)  # Give browser time to fully launch
        
            return {
                'success': True,
                'profile_id': profile_id,
                'error': None
            }
    
        except Exception as e:
            print(f"{log_prefix} ❌ Exception while opening profile")
            print(f"{log_prefix} Error: {e}")
            import traceback
            traceback.print_exc()
        
            return {
                'success': False,
                'profile_id': profile_id,
                'error': str(e)
            }

        
    def _start_parallel(self, profile_list):
        """
        Execute parallel mode with BATCH PROCESSING
    
        NEW WORKFLOW:
        - Divide profiles into batches of size max_workers
        - For each batch:
            1. Open all profiles in batch (parallel)
            2. Execute all chains round-robin with lock - if action_type != None
            3. Close all profiles in batch (parallel) - if action_type != None
        - Repeat until all profiles processed
    
        Args:
            profile_list: List of profile IDs to execute
        """
        import threading
        from concurrent.futures import ThreadPoolExecutor, as_completed
    
        max_parallel_profiles = int(self.params.get("max_workers", 1))
        action_type = self.params.get("action_type", None)
    
        print("[GOLOGIN AUTO] ========== PARALLEL MODE ==========")
        print("=" * 80)
        print(f"[PARALLEL MODE] BATCH PROCESSING (batch size: {max_parallel_profiles})")
        print(f"[PARALLEL MODE] Total profiles: {len(profile_list)}")
        print(f"[PARALLEL MODE] Action type: {action_type}")
        print("=" * 80)
    
        # Divide profiles into batches
        batches = []
        for i in range(0, len(profile_list), max_parallel_profiles):
            batch = profile_list[i:i + max_parallel_profiles]
            batches.append(batch)
    
        print(f"[PARALLEL MODE] Divided into {len(batches)} batches\n")
    
        total_success = 0
        total_failed = 0
    
        # ========== PROCESS EACH BATCH ==========
        for batch_num, batch_profiles in enumerate(batches, 1):
            print("=" * 80)
            print(f"[BATCH {batch_num}/{len(batches)}] Processing {len(batch_profiles)} profiles: {batch_profiles}")
            print("=" * 80)
            print()
        
            # ========== PHASE 1: OPEN BATCH PROFILES (UPDATED) ==========
            print(f"[BATCH {batch_num}] PHASE 1: Opening {len(batch_profiles)} profiles (max {max_parallel_profiles} concurrent)...")
        
            profile_data = {}  # profile_id → {'driver': ..., 'debugger_address': ..., 'status': ...}
            open_lock = threading.Lock()
        
            def open_profile_thread(profile_id):
                """Thread function to open 1 profile WITHOUT Selenium"""
                try:
                    print(f"[BATCH {batch_num}][{profile_id}] Opening profile...")
                
                    # ========== CALL _open_profile() METHOD (NEW) ==========
                    result = self._open_profile(profile_id, batch_num)
                
                    with open_lock:
                        if result['success']:
                            # ========== PROFILE OPENED - SET driver=None, debugger_address=None ==========
                            # These will be defined later when implementing manual control flows
                            profile_data[profile_id] = {
                                'driver': None,  # ← NO SELENIUM CONNECTION
                                'debugger_address': None,  # ← NOT NEEDED (manual mode)
                                'status': 'opened'
                            }
                            print(f"[BATCH {batch_num}][{profile_id}] ✓ Profile opened successfully (MANUAL mode)")
                        else:
                            # ========== OPENING FAILED ==========
                            profile_data[profile_id] = {
                                'status': 'failed',
                                'error': result['error']
                            }
                            print(f"[BATCH {batch_num}][{profile_id}] ❌ Failed to open: {result['error']}")
            
                except Exception as e:
                    print(f"[BATCH {batch_num}][{profile_id}] ❌ Exception while opening: {e}")
                    import traceback
                    traceback.print_exc()
                
                    with open_lock:
                        profile_data[profile_id] = {
                            'status': 'error',
                            'error': str(e)
                        }
        
            # ========== USE THREADPOOLEXECUTOR TO OPEN PROFILES ==========
            executor = ThreadPoolExecutor(max_workers=max_parallel_profiles)
        
            try:
                future_to_profile = {}
            
                for i, profile_id in enumerate(batch_profiles):
                    if i > 0:
                        time.sleep(2)  # Stagger delay
                
                    future = executor.submit(open_profile_thread, profile_id)
                    future_to_profile[future] = profile_id
                    print(f"[BATCH {batch_num}] PHASE 1: Submitted thread {i+1}/{len(batch_profiles)}: {profile_id}")
            
                # Wait for all to complete
                for future in as_completed(future_to_profile):
                    profile_id = future_to_profile[future]
                    try:
                        future.result()
                    except Exception as e:
                        print(f"[BATCH {batch_num}] PHASE 1: Thread for {profile_id} raised exception: {e}")
        
            finally:
                executor.shutdown(wait=True)
                print(f"[BATCH {batch_num}] PHASE 1: Thread pool shut down")
        
            # ========== CHECK OPENING RESULTS ==========
            opened_profiles = [pid for pid, data in profile_data.items() if data.get('status') == 'opened']
            failed_profiles = [pid for pid, data in profile_data.items() if data.get('status') in ['failed', 'error']]
        
            print(f"[BATCH {batch_num}] PHASE 1: Opening results:")
            print(f"  ✓ Successfully opened: {len(opened_profiles)}/{len(batch_profiles)}")
        
            if failed_profiles:
                print(f"  ❌ Failed: {len(failed_profiles)}")
            print()
        
            if not opened_profiles:
                print(f"[BATCH {batch_num}] No profiles opened successfully, skipping to next batch")
                total_failed += len(batch_profiles)
                continue
        
            # ========== PHASE 2, 3, 4: KEEP EXACTLY AS ORIGINAL (START ACTION CODE) ==========
            # Check action type
            if action_type is None:
                print(f"[BATCH {batch_num}] PHASE 2: Action type is None, skipping flow creation and execution")
                print(f"[BATCH {batch_num}] Batch profiles opened and kept running (no cleanup)")
                total_success += len(opened_profiles)
                total_failed += len(failed_profiles)
                continue  # Skip to next batch, profiles stay open
        
            # ========== PHASE 2: CREATE FLOW ITERATORS (KEEP ORIGINAL) ==========
            print(f"[BATCH {batch_num}] PHASE 2: Creating flow iterators for opened profiles...")
        
            # Load keywords
            keywords_suffix_prefix = self.params.get("keywords_suffix_prefix", "").strip()
            keywords_youtube = GoLoginProfileHelper.load_keywords(self.params, "Get Youtube Keywords")
            keywords_google = GoLoginProfileHelper.load_keywords(self.params, "Get Google Keywords", "Google")
        
            # Youtube Options
            youtube_main_area_x = int(self.params.get("youtube_main_area_x", 0))
            youtube_main_area_y = int(self.params.get("youtube_main_area_y", 0))
            youtube_main_area_width = int(self.params.get("youtube_main_area_width", 1920))
            youtube_main_area_height = int(self.params.get("youtube_main_area_height", 1080))
            youtube_image_search_path = self.params.get("youtube_image_search_path", "").strip()
        
            youtube_sidebar_area_x = int(self.params.get("youtube_sidebar_area_x", 0))
            youtube_sidebar_area_y = int(self.params.get("youtube_sidebar_area_y", 0))
            youtube_sidebar_area_width = int(self.params.get("youtube_sidebar_area_width", 400))
            youtube_sidebar_area_height = int(self.params.get("youtube_sidebar_area_height", 1080))
            youtube_sidebar_image_search_path = self.params.get("youtube_sidebar_image_search_path", "").strip()
        
            keywords = {
                'keywords_youtube': keywords_youtube,
                'keywords_google': keywords_google,
                'suffix_prefix': keywords_suffix_prefix,
                'youtube_main_area_x': youtube_main_area_x,
                'youtube_main_area_y': youtube_main_area_y,
                'youtube_main_area_width': youtube_main_area_width,
                'youtube_main_area_height': youtube_main_area_height,
                'youtube_image_search_path': youtube_image_search_path,
                'youtube_sidebar_area_x': youtube_sidebar_area_x,
                'youtube_sidebar_area_y': youtube_sidebar_area_y,
                'youtube_sidebar_area_width': youtube_sidebar_area_width,
                'youtube_sidebar_area_height': youtube_sidebar_area_height,
                'youtube_sidebar_image_search_path': youtube_sidebar_image_search_path,
            }
        
            if not keywords:
                print("[PHASE 2] Failed to load keywords")
                GoLoginProfileHelper.cleanup_profiles(profile_data, self.gologin_api, "[CLEANUP]")
                self.set_variable(False)
                return
        
            flow_iterators = {}  # profile_id → flow_iterator
        
            for profile_id in opened_profiles:
                driver = profile_data[profile_id]['driver']  # ← Will be None
                debugger_address = profile_data[profile_id]['debugger_address']  # ← Will be None
            
                try:
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
                        print(f"[BATCH {batch_num}][{profile_id}] Unknown action type: {action_type}")
                        continue
                
                    flow_iterators[profile_id] = flow_iterator
            
                except Exception as e:
                    print(f"[BATCH {batch_num}][{profile_id}] Failed to create flow iterator: {e}")
                    import traceback
                    traceback.print_exc()
                    opened_profiles.remove(profile_id)
        
            print(f"[BATCH {batch_num}] PHASE 2: Created {len(flow_iterators)} flow iterators")
        
            # ========== PHASE 3: EXECUTE CHAINS ROUND-ROBIN (KEEP ORIGINAL) ==========
            print(f"[BATCH {batch_num}] PHASE 3: Starting round-robin chain execution...")
            print("=" * 80)
        
            active_profiles = opened_profiles.copy()
            round_num = 0
        
            while active_profiles:
                round_num += 1
                print()
                print("=" * 80)
                print(f"[BATCH {batch_num}] ROUND {round_num}: Active profiles ({len(active_profiles)}/{len(opened_profiles)})")
                print("=" * 80)
                print()
            
                profiles_to_remove = []
            
                for profile_id in active_profiles:
                    flow = flow_iterators[profile_id]
                
                    # Show progress
                    progress = flow.get_progress()
                    print(f"[BATCH {batch_num}] ROUND {round_num} [{profile_id}] Progress: {progress['current']}/{progress['total']} chains ({progress['percentage']:.1f}%)")
                
                    # Check if completed
                    if not flow.has_next_chain():
                        print(f"[BATCH {batch_num}] ROUND {round_num} [{profile_id}] All chains completed")
                        profiles_to_remove.append(profile_id)
                        continue
                
                    # Bring window to front
                    try:
                        GoLoginProfileHelper.bring_profile_to_front(
                            profile_id,
                            driver=profile_data[profile_id]['driver'],
                            log_prefix=f"[BATCH {batch_num}] ROUND {round_num} [{profile_id}]"
                        )
                        print(f"[BATCH {batch_num}] ROUND {round_num} [{profile_id}] Window brought to front")
                    except Exception as e:
                        print(f"[BATCH {batch_num}] ROUND {round_num} [{profile_id}] Could not bring to front: {e}")
                
                    # Execute chain with lock
                    print(f"[BATCH {batch_num}] ROUND {round_num} [{profile_id}] ========== ACQUIRING LOCK → EXECUTING CHAIN")
                
                    try:
                        success = flow.execute_next_chain()
                    
                        if success:
                            print(f"[BATCH {batch_num}] ROUND {round_num} [{profile_id}] ✓ Chain executed successfully")
                        else:
                            print(f"[BATCH {batch_num}] ROUND {round_num} [{profile_id}] ❌ Chain execution failed")
                            profiles_to_remove.append(profile_id)
                
                    except Exception as e:
                        print(f"[BATCH {batch_num}] ROUND {round_num} [{profile_id}] ❌ Exception during chain execution: {e}")
                        import traceback
                        traceback.print_exc()
                        profiles_to_remove.append(profile_id)
                
                    print(f"[BATCH {batch_num}] ROUND {round_num} [{profile_id}] ========== LOCK RELEASED")
            
                # Remove completed/failed profiles
                profiles_to_remove_set = set(profiles_to_remove)
                active_profiles = [pid for pid in active_profiles if pid not in profiles_to_remove_set]
        
            print()
            print("=" * 80)
            print(f"[BATCH {batch_num}] PHASE 3: All profiles completed all chains")
            print("=" * 80)
            print()
        
            # ========== PHASE 4: CLEANUP (KEEP ORIGINAL) ==========
            print(f"[BATCH {batch_num}] PHASE 4: Cleaning up {len(opened_profiles)} profiles...")
        
            cleanup_results = GoLoginProfileHelper.cleanup_profiles(profile_data, self.gologin_api, f"[BATCH {batch_num}]")
        
            cleanup_success = sum(1 for r in cleanup_results.values() if r)
            print(f"[BATCH {batch_num}] PHASE 4: Cleanup completed ({cleanup_success}/{len(cleanup_results)})")
        
            total_success += len(opened_profiles)
            total_failed += len(failed_profiles)
    
        # ========== FINAL SUMMARY ==========
        print()
        print("=" * 80)
        print("[PARALLEL MODE] ========== ALL BATCHES COMPLETED ==========")
        print("=" * 80)
        print(f"Total profiles processed: {len(profile_list)}")
        print(f"  ✓ Success: {total_success}")
        print(f"  ❌ Failed: {total_failed}")
        print("=" * 80)
    
        self.set_variable(total_success > 0)




    def _start_single_profile(self, profile_id):
        """
        Execute single mode (1 profile only)
        Open profile, execute chains, then close
    
        Args:
            profile_id: Single profile ID to execute (STRING, not list)
    
        Returns:
            bool: Success status
        """
        action_type = self.params.get("action_type", None)
    
        print("[GOLOGIN AUTO] ========== SINGLE MODE ==========")
        print("=" * 80)
        print(f"[SINGLE MODE] Profile ID: {profile_id}")
        print(f"[SINGLE MODE] Action type: {action_type}")
        print("=" * 80)
        print()
    
        # ========== PHASE 1: OPEN PROFILE (UPDATED) ==========
        print(f"[{profile_id}] PHASE 1: Opening profile...")
    
        result = self._open_profile(profile_id)
    
        if not result['success']:
            print(f"[{profile_id}] ❌ Failed to open profile: {result['error']}")
            return False
    
        print(f"[{profile_id}] ✓ Profile opened successfully (MANUAL mode)")
    
        # Store profile data
        profile_data = {
            profile_id: {
                'driver': None,  # ← NO SELENIUM CONNECTION
                'debugger_address': None,  # ← NOT NEEDED (manual mode)
                'status': 'opened'
            }
        }
    
        # ========== CHECK ACTION TYPE (KEEP ORIGINAL) ==========
        if action_type is None:
            print(f"[{profile_id}] PHASE 2: Action type is None, skipping flow execution")
            print(f"[{profile_id}] Profile opened and kept running (no cleanup)")
            return True  # Success - profile opened
    
        # ========== PHASE 2: CREATE FLOW ITERATOR (KEEP ORIGINAL) ==========
        print(f"[{profile_id}] PHASE 2: Creating flow iterator...")
    
        # Load keywords
        keywords_suffix_prefix = self.params.get("keywords_suffix_prefix", "").strip()
        keywords_youtube = GoLoginProfileHelper.load_keywords(self.params, "Get Youtube Keywords")
        keywords_google = GoLoginProfileHelper.load_keywords(self.params, "Get Google Keywords", "Google")
    
        # Youtube Options
        youtube_main_area_x = int(self.params.get("youtube_main_area_x", 0))
        youtube_main_area_y = int(self.params.get("youtube_main_area_y", 0))
        youtube_main_area_width = int(self.params.get("youtube_main_area_width", 1920))
        youtube_main_area_height = int(self.params.get("youtube_main_area_height", 1080))
        youtube_image_search_path = self.params.get("youtube_image_search_path", "").strip()
    
        youtube_sidebar_area_x = int(self.params.get("youtube_sidebar_area_x", 0))
        youtube_sidebar_area_y = int(self.params.get("youtube_sidebar_area_y", 0))
        youtube_sidebar_area_width = int(self.params.get("youtube_sidebar_area_width", 400))
        youtube_sidebar_area_height = int(self.params.get("youtube_sidebar_area_height", 1080))
        youtube_sidebar_image_search_path = self.params.get("youtube_sidebar_image_search_path", "").strip()
    
        keywords = {
            'keywords_youtube': keywords_youtube,
            'keywords_google': keywords_google,
            'suffix_prefix': keywords_suffix_prefix,
            'youtube_main_area_x': youtube_main_area_x,
            'youtube_main_area_y': youtube_main_area_y,
            'youtube_main_area_width': youtube_main_area_width,
            'youtube_main_area_height': youtube_main_area_height,
            'youtube_image_search_path': youtube_image_search_path,
            'youtube_sidebar_area_x': youtube_sidebar_area_x,
            'youtube_sidebar_area_y': youtube_sidebar_area_y,
            'youtube_sidebar_area_width': youtube_sidebar_area_width,
            'youtube_sidebar_area_height': youtube_sidebar_area_height,
            'youtube_sidebar_image_search_path': youtube_sidebar_image_search_path,
        }
    
        if not keywords:
            print(f"[{profile_id}] Failed to load keywords")
            GoLoginProfileHelper.cleanup_profiles(profile_data, self.gologin_api, f"[{profile_id}]")
            return False
    
        driver = None  # ← Will be None for manual mode
        debugger_address = None  # ← Will be None for manual mode
    
        try:
            if action_type == "Youtube":
                flow_iterator = YouTubeFlow.create_flow_iterator(
                    driver=driver,
                    keywords=keywords,
                    profile_id=profile_id,
                    debugger_address=debugger_address,
                    log_prefix=f"[{profile_id}]"
                )
            elif action_type == "Google":
                flow_iterator = GoogleFlow.create_flow_iterator(
                    driver=driver,
                    keywords=keywords,
                    profile_id=profile_id,
                    debugger_address=debugger_address,
                    log_prefix=f"[{profile_id}]"
                )
            else:
                print(f"[{profile_id}] Unknown action type: {action_type}")
                GoLoginProfileHelper.cleanup_profiles(profile_data, self.gologin_api, f"[{profile_id}]")
                return False
    
        except Exception as e:
            print(f"[{profile_id}] Failed to create flow iterator: {e}")
            import traceback
            traceback.print_exc()
            GoLoginProfileHelper.cleanup_profiles(profile_data, self.gologin_api, f"[{profile_id}]")
            return False
    
        print(f"[{profile_id}] ✓ Flow iterator created")
    
        # ========== PHASE 3: EXECUTE ALL CHAINS (KEEP ORIGINAL) ==========
        print(f"[{profile_id}] PHASE 3: Executing chains...")
        print("=" * 80)
    
        chain_num = 0
    
        while flow_iterator.has_next_chain():
            chain_num += 1
        
            # Show progress
            progress = flow_iterator.get_progress()
            print(f"\n[{profile_id}] Chain {chain_num}/{progress['total']} ({progress['percentage']:.1f}%)")
            print("-" * 80)
        
            # Bring window to front
            try:
                GoLoginProfileHelper.bring_profile_to_front(
                    profile_id,
                    driver=driver,
                    log_prefix=f"[{profile_id}]"
                )
                print(f"[{profile_id}] Window brought to front")
            except Exception as e:
                print(f"[{profile_id}] Could not bring to front: {e}")
        
            # Execute chain
            try:
                success = flow_iterator.execute_next_chain()
            
                if success:
                    print(f"[{profile_id}] ✓ Chain {chain_num} executed successfully")
                else:
                    print(f"[{profile_id}] ❌ Chain {chain_num} execution failed")
                    break
        
            except Exception as e:
                print(f"[{profile_id}] ❌ Exception during chain execution: {e}")
                import traceback
                traceback.print_exc()
                break
    
        print()
        print("=" * 80)
        print(f"[{profile_id}] PHASE 3: All chains completed")
        print("=" * 80)
        print()
    
        # ========== PHASE 4: CLEANUP (KEEP ORIGINAL) ==========
        print(f"[{profile_id}] PHASE 4: Cleaning up profile...")
    
        cleanup_results = GoLoginProfileHelper.cleanup_profiles(profile_data, self.gologin_api, f"[{profile_id}]")
    
        if cleanup_results.get(profile_id):
            print(f"[{profile_id}] ✓ Cleanup successful")
            return True
        else:
            print(f"[{profile_id}] ❌ Cleanup failed")
            return False


    
    def set_variable(self, success):
        """Set variable with result"""
        variable = self.params.get("variable", "")
        if variable:
            GlobalVariables().set(variable, "true" if success else "false")
