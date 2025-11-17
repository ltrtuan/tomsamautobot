# controllers/actions/gologin_selenium_start_action.py

from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from models.gologin_api import get_gologin_api
import random
import time
import os
# Import helpers
from helpers.gologin_profile_helper import GoLoginProfileHelper
from helpers.flow_youtube import YouTubeFlow
from helpers.flow_google import GoogleFlow

from helpers.flow_youtube_headless import YouTubeFlowHeadless
from exceptions.gologin_exceptions import ProxyAssignmentFailed


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
            raise
            

    def _execute_parallel_headless(self, profile_data, batch_num, flow_type, max_workers):
        """
        Execute all chains for all profiles in parallel (headless mode)
    
        This is the coordinator method that:
        1. Filters successfully opened profiles
        2. Submits each profile to ThreadPoolExecutor
        3. Each worker executes ALL chains for its profile
        4. Waits for all workers to complete
    
        Args:
            profile_data: Dict containing all profile data (driver, status, etc.)
            batch_num: Batch number for logging
            flow_type: 'Youtube' or 'Google'
            max_workers: Maximum number of concurrent workers
        """
        print(f"\n{'='*70}")
        print(f"[BATCH {batch_num}] HEADLESS MODE: Starting parallel chain execution")
        print(f"[BATCH {batch_num}] Max workers: {max_workers}")
        print(f"[BATCH {batch_num}] Flow type: {flow_type}")
        print(f"{'='*70}\n")
    
        # ========== STEP 1: FILTER SUCCESSFULLY OPENED PROFILES ==========
        opened_profiles = {
            pid: data for pid, data in profile_data.items()
            if data.get('status') == 'opened' and data.get('driver')
        }
    
        if not opened_profiles:
            print(f"[BATCH {batch_num}] ✗ No profiles opened successfully")
            print(f"[BATCH {batch_num}] Profile statuses:")
            for pid, data in profile_data.items():
                status = data.get('status', 'unknown')
                error = data.get('error', 'N/A')
                print(f"  - {pid}: {status} (error: {error})")
            return
    
        print(f"[BATCH {batch_num}] ✓ {len(opened_profiles)} profile(s) ready for execution:")
        for pid in opened_profiles.keys():
            print(f"  - {pid}")
        print()
    
        # ========== STEP 2: SUBMIT ALL PROFILES TO THREADPOOLEXECUTOR ==========
        print(f"[BATCH {batch_num}] Submitting profiles to ThreadPoolExecutor...")
    
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all profiles
            futures = {}
        
            for profile_id, data in opened_profiles.items():
                driver = data['driver']
            
                print(f"[BATCH {batch_num}] Submitting {profile_id} to worker thread...")
            
                future = executor.submit(
                    self._execute_all_chains_for_profile,
                    profile_id,
                    driver,
                    profile_data,
                    batch_num,
                    flow_type
                )
                futures[future] = profile_id
        
            print(f"[BATCH {batch_num}] ✓ All {len(futures)} profile(s) submitted\n")
        
            # ========== STEP 3: WAIT FOR ALL FUTURES TO COMPLETE ==========
            print(f"[BATCH {batch_num}] Waiting for all workers to complete...\n")
        
            completed_count = 0
            failed_count = 0
        
            for future in as_completed(futures):
                profile_id = futures[future]
                completed_count += 1
            
                try:
                    # Get result from worker
                    success = future.result()
                
                    if success:
                        chains_executed = profile_data[profile_id].get('chains_executed', 0)
                        print(f"\n[BATCH {batch_num}][{profile_id}] "
                              f"✓ Worker completed successfully ({chains_executed} chains)")
                        print(f"[BATCH {batch_num}] Progress: {completed_count}/{len(futures)} workers completed")
                    else:
                        failed_count += 1
                        error = profile_data[profile_id].get('error', 'Unknown error')
                        print(f"\n[BATCH {batch_num}][{profile_id}] "
                              f"✗ Worker failed: {error}")
                        print(f"[BATCH {batch_num}] Progress: {completed_count}/{len(futures)} workers completed")
                    
                except Exception as e:
                    failed_count += 1
                    print(f"\n[BATCH {batch_num}][{profile_id}] "
                          f"✗ Exception in worker thread: {e}")
                    import traceback
                    traceback.print_exc()
                
                    # Update profile status
                    profile_data[profile_id]['status'] = 'error'
                    profile_data[profile_id]['error'] = str(e)
                
                    print(f"[BATCH {batch_num}] Progress: {completed_count}/{len(futures)} workers completed")
    
        # ========== STEP 4: SUMMARY ==========
        print(f"\n{'='*70}")
        print(f"[BATCH {batch_num}] HEADLESS MODE EXECUTION COMPLETED")
        print(f"[BATCH {batch_num}] Total profiles: {len(opened_profiles)}")
        print(f"[BATCH {batch_num}] Successful: {len(opened_profiles) - failed_count}")
        print(f"[BATCH {batch_num}] Failed: {failed_count}")
        print(f"{'='*70}\n")
    
        # Print detailed results
        print(f"[BATCH {batch_num}] Detailed results:")
        for profile_id, data in opened_profiles.items():
            status = data.get('status', 'unknown')
            chains_executed = data.get('chains_executed', 0)
            error = data.get('error', 'N/A')
        
            if status == 'completed':
                print(f"  ✓ {profile_id}: {status} ({chains_executed} chains)")
            else:
                print(f"  ✗ {profile_id}: {status} (error: {error})")
        print()

        

    def _execute_round_robin(self, profile_data, batch_num, flow_type):
        """
        Execute chains in round-robin fashion (GUI mode)
    
        Round-robin execution:
        - Profile A executes chain 1 → Profile B executes chain 1 → Profile C executes chain 1
        - Profile A executes chain 2 → Profile B executes chain 2 → Profile C executes chain 2
        - ... (repeat until all profiles complete all chains)
    
        Each profile executes 1 chain per round, then moves to next profile.
        This ensures fair resource distribution and allows window switching.
    
        Args:
            profile_data: Dict containing all profile data (driver, status, etc.)
            batch_num: Batch number for logging
            flow_type: 'Youtube' or 'Google'
        """
        print(f"\n{'='*70}")
        print(f"[BATCH {batch_num}] GUI MODE: Starting round-robin chain execution")
        print(f"[BATCH {batch_num}] Flow type: {flow_type}")
        print(f"{'='*70}\n")
    
        # ========== STEP 1: FILTER SUCCESSFULLY OPENED PROFILES ==========
        opened_profiles = [
            pid for pid, data in profile_data.items()
            if data.get('status') == 'opened' and data.get('driver')
        ]
    
        if not opened_profiles:
            print(f"[BATCH {batch_num}] ✗ No profiles opened successfully")
            return
    
        print(f"[BATCH {batch_num}] ✓ {len(opened_profiles)} profile(s) ready for execution")
    
        # ========== STEP 2: LOAD KEYWORDS ==========
        keywords_suffix_prefix = self.params.get("keywords_suffix_prefix", "").strip()
        keywords_youtube = GoLoginProfileHelper.load_keywords(self.params, "[Get Youtube Keywords]")
        keywords_google = GoLoginProfileHelper.load_keywords(self.params, "[Get Google Keywords]", "Google")
    
        # Get YouTube option params
        youtube_main_area_x = int(self.params.get("youtube_main_area_x", "0"))
        youtube_main_area_y = int(self.params.get("youtube_main_area_y", "0"))
        youtube_main_area_width = int(self.params.get("youtube_main_area_width", "1920"))
        youtube_main_area_height = int(self.params.get("youtube_main_area_height", "1080"))
        youtube_image_search_path = self.params.get("youtube_image_search_path", "").strip()
    
        youtube_sidebar_area_x = int(self.params.get("youtube_sidebar_area_x", "0"))
        youtube_sidebar_area_y = int(self.params.get("youtube_sidebar_area_y", "0"))
        youtube_sidebar_area_width = int(self.params.get("youtube_sidebar_area_width", "400"))
        youtube_sidebar_area_height = int(self.params.get("youtube_sidebar_area_height", "1080"))
        youtube_sidebar_image_search_path = self.params.get("youtube_sidebar_image_search_path", "").strip()
    
        keywords = {
            "keywords_youtube": keywords_youtube,
            "keywords_google": keywords_google,
            "suffix_prefix": keywords_suffix_prefix,
            # Youtube Option params
            "youtube_main_area_x": youtube_main_area_x,
            "youtube_main_area_y": youtube_main_area_y,
            "youtube_main_area_width": youtube_main_area_width,
            "youtube_main_area_height": youtube_main_area_height,
            "youtube_image_search_path": youtube_image_search_path,
            # Sidebar params
            "youtube_sidebar_area_x": youtube_sidebar_area_x,
            "youtube_sidebar_area_y": youtube_sidebar_area_y,
            "youtube_sidebar_area_width": youtube_sidebar_area_width,
            "youtube_sidebar_area_height": youtube_sidebar_area_height,
            "youtube_sidebar_image_search_path": youtube_sidebar_image_search_path,
        }
    
        if not keywords:
            print(f"[BATCH {batch_num}] ✗ Failed to load keywords")
            return
    
        # ========== STEP 3: CREATE FLOW ITERATORS ==========
        print(f"[BATCH {batch_num}] Creating flow iterators...")
    
        flow_iterators = {}  # {profile_id: flow_iterator}
    
        for profile_id in opened_profiles:
            driver = profile_data[profile_id]['driver']
            debugger_address = profile_data[profile_id]['debugger_address']
        
            try:
                # Create flow iterator based on flow type
                if flow_type == "Youtube":
                    flow_iterator = YouTubeFlow.create_flow_iterator(
                        driver=driver,
                        keywords=keywords,
                        profile_id=profile_id,
                        debugger_address=debugger_address,
                        log_prefix=f"[BATCH {batch_num}][{profile_id}]"
                    )
                elif flow_type == "Google":
                    flow_iterator = GoogleFlow.create_flow_iterator(
                        driver=driver,
                        keywords=keywords,
                        profile_id=profile_id,
                        debugger_address=debugger_address,
                        log_prefix=f"[BATCH {batch_num}][{profile_id}]"
                    )
                else:
                    print(f"[BATCH {batch_num}][{profile_id}] ✗ Unknown flow type: {flow_type}")
                    continue
            
                flow_iterators[profile_id] = flow_iterator
            
            except Exception as e:
                print(f"[BATCH {batch_num}][{profile_id}] ✗ Failed to create flow iterator: {e}")
                import traceback
                traceback.print_exc()
    
        if not flow_iterators:
            print(f"[BATCH {batch_num}] ✗ No flow iterators created")
            return
    
        print(f"[BATCH {batch_num}] ✓ Created {len(flow_iterators)} flow iterator(s)\n")
    
        # ========== STEP 4: ROUND-ROBIN EXECUTION ==========
        print(f"[BATCH {batch_num}] Starting round-robin execution...")
        print("="*70)
    
        active_profiles = list(flow_iterators.keys())
        round_num = 0
    
        # Loop until all profiles complete all chains
        while active_profiles:
            round_num += 1
        
            print()
            print("="*70)
            print(f"[BATCH {batch_num}][ROUND {round_num}] Active profiles: {len(active_profiles)}/{len(flow_iterators)}")
            print("="*70)
            print()
        
            profiles_to_remove = []
        
            # Execute 1 chain for each active profile
            for profile_id in active_profiles:
                flow = flow_iterators[profile_id]
            
                # Check if profile completed all chains
                if not flow.has_next_chain():
                    print(f"[BATCH {batch_num}][ROUND {round_num}][{profile_id}] ✓ All chains completed")
                    profiles_to_remove.append(profile_id)
                    continue
            
                # Show progress
                progress = flow.get_progress()
                print(f"[BATCH {batch_num}][ROUND {round_num}][{profile_id}] "
                      f"Progress: {progress['current']}/{progress['total']} chains "
                      f"({progress['percentage']:.1f}%)")
            
                # Bring window to front
                try:
                    GoLoginProfileHelper.bring_profile_to_front(
                        profile_id,
                        driver=profile_data[profile_id]['driver'],
                        log_prefix=f"[BATCH {batch_num}][ROUND {round_num}][{profile_id}]"
                    )
                    print(f"[BATCH {batch_num}][ROUND {round_num}][{profile_id}] ✓ Window brought to front")
                except Exception as e:
                    print(f"[BATCH {batch_num}][ROUND {round_num}][{profile_id}] "
                          f"⚠ Could not bring to front: {e}")
            
                # Execute one chain (IMPLICIT LOCK via sequential loop)
                print(f"\n[BATCH {batch_num}][ROUND {round_num}][{profile_id}] "
                      f">>> EXECUTING CHAIN (LOCKED) <<<")
            
                try:
                    success = flow.execute_next_chain()
                
                    if success:
                        print(f"[BATCH {batch_num}][ROUND {round_num}][{profile_id}] ✓ Chain executed successfully")
                    else:
                        print(f"[BATCH {batch_num}][ROUND {round_num}][{profile_id}] ✗ Chain execution failed")
                        profiles_to_remove.append(profile_id)
                    
                except Exception as e:
                    print(f"[BATCH {batch_num}][ROUND {round_num}][{profile_id}] "
                          f"✗ Exception during chain execution: {e}")
                    import traceback
                    traceback.print_exc()
                    profiles_to_remove.append(profile_id)
            
                print(f"[BATCH {batch_num}][ROUND {round_num}][{profile_id}] "
                      f">>> LOCK RELEASED <<<\n")
        
            # Remove completed/failed profiles
            profiles_to_remove_set = set(profiles_to_remove)
            active_profiles = [pid for pid in active_profiles if pid not in profiles_to_remove_set]
        
            print()
    
        print("="*70)
        print(f"[BATCH {batch_num}] ✓ All profiles completed all chains")
        print("="*70)
        print()
    
        # ========== STEP 5: CLEANUP ALL PROFILES ==========
        print(f"[BATCH {batch_num}] Cleaning up {len(opened_profiles)} profile(s)...")
    
        # Use centralized helper method
        cleanup_results = GoLoginProfileHelper.cleanup_profiles(
            profile_data={pid: profile_data[pid] for pid in opened_profiles},
            gologin_api=self.gologin_api,
            log_prefix=f"[BATCH {batch_num}][CLEANUP]"
        )
    
        # Count results
        cleanup_success = sum(1 for r in cleanup_results.values() if r)
        print(f"[BATCH {batch_num}] ✓ Cleanup completed: {cleanup_success}/{len(cleanup_results)}")



        
    def _start_parallel(self, profile_list):
        """Execute parallel mode"""
        # ========== PARSE PARAMETERS ==========
        max_parallel_profiles = int(self.params.get("max_workers", "1"))
        action_type = self.params.get("action_type", "None")
        headless = self.params.get("headless", False)
        flow_type = action_type
        how_to_get = self.params.get("how_to_get", "Random")
    
        if how_to_get == "Random":
            profile_list = GoLoginProfileHelper.create_randomized_profile_list(
                original_profile_list=profile_list,
                max_workers=max_parallel_profiles,
                log_prefix="[GOLOGIN START]"
            )
    
        print("\n[GOLOGIN START] ========== PARALLEL MODE ==========")
        print("=" * 80)
        print(f"[PARALLEL MODE] Total profiles: {len(profile_list)}")
        print(f"[PARALLEL MODE] Action type: {action_type}")
        print(f"[PARALLEL MODE] Headless mode: {headless}")
        print(f"[PARALLEL MODE] Max workers: {max_parallel_profiles}")
        print("=" * 80)
    
        # ========== BRANCH: HEADLESS vs GUI MODE ==========
        if headless:
            # ===== HEADLESS MODE: Submit ALL profiles (NO BATCH) =====
            self._start_parallel_headless_all_profiles(
                profile_list=profile_list,
                max_workers=max_parallel_profiles,
                flow_type=flow_type
            )
        else:
            # ===== GUI MODE: Batch processing with round-robin =====
            self._start_parallel_gui_with_batches(
                profile_list=profile_list,
                max_workers=max_parallel_profiles,
                flow_type=flow_type
            )
    
        # Set result
        self.set_variable(True)
        

    def _start_parallel_gui_with_batches(self, profile_list, max_workers, flow_type):
        """
        GUI mode: Batch processing with round-robin
        This is EXTRACTED from existing _start_parallel() batch processing logic
        """
        import threading
    
        # Divide into batches
        batches = []
        for i in range(0, len(profile_list), max_workers):
            batch = profile_list[i:i + max_workers]
            batches.append(batch)
    
        print(f"\n[GUI MODE] Divided into {len(batches)} batch(es)")
    
        total_success = 0
        total_failed = 0
    
        # ========== PROCESS EACH BATCH ==========
        for batch_num, batch_profiles in enumerate(batches, 1):
            print(f"\n{'='*70}")
            print(f"[BATCH {batch_num}] ========== PROCESSING BATCH {batch_num}/{len(batches)} ==========")
            print(f"[BATCH {batch_num}] Profiles in this batch: {len(batch_profiles)}")
            print(f"{'='*70}")
        
            # ===== PHASE 1: OPEN BATCH PROFILES IN PARALLEL =====
            print(f"\n[BATCH {batch_num}] Phase 1: Opening {len(batch_profiles)} profile(s)...")
        
            opened_profiles = {}
            failed_profiles = []
            profile_lock = threading.Lock()
        
            def open_profile_worker(profile_id):
                """Worker thread to open single profile"""
                try:
                    success, driver, debugger_address, error = self._open_single_profile_internal(
                        profile_id,
                        log_prefix=f"[BATCH {batch_num}]"
                    )
                
                    with profile_lock:
                        if success:
                            opened_profiles[profile_id] = {
                                'driver': driver,
                                'debugger_address': debugger_address,
                                'profile_id': profile_id
                            }
                            print(f"[BATCH {batch_num}][{profile_id}] ✓ Opened successfully")
                        else:
                            failed_profiles.append(profile_id)
                            print(f"[BATCH {batch_num}][{profile_id}] ✗ Failed to open: {error}")
                        
                except Exception as e:
                    with profile_lock:
                        failed_profiles.append(profile_id)
                        print(f"[BATCH {batch_num}][{profile_id}] ✗ Exception: {e}")
        
            # Open profiles in parallel
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for i, profile_id in enumerate(batch_profiles):
                    if i > 0:
                        time.sleep(2)  # Stagger delay
                    future = executor.submit(open_profile_worker, profile_id)
                    futures.append(future)
            
                # Wait for all to complete
                for future in futures:
                    future.result()
        
            print(f"\n[BATCH {batch_num}] ✓ Opening phase completed:")
            print(f"[BATCH {batch_num}]   - Opened: {len(opened_profiles)}")
            print(f"[BATCH {batch_num}]   - Failed: {len(failed_profiles)}")
        
            if not opened_profiles:
                print(f"[BATCH {batch_num}] ✗ No profiles opened, skipping execution...")
                total_failed += len(failed_profiles)
                continue
        
            # Prepare profile_data dict for execution
            profile_data = {}
            for profile_id, data in opened_profiles.items():
                profile_data[profile_id] = {
                    'driver': data['driver'],
                    'debugger_address': data['debugger_address'],
                    'profile_id': profile_id,
                    'status': 'opened'
                }
        
            # ===== PHASE 2: EXECUTE CHAINS (GUI ROUND-ROBIN MODE) =====
            print(f"\n[BATCH {batch_num}] Phase 2: Executing chains (GUI round-robin mode)...")
        
            if flow_type == "None":
                print(f"[BATCH {batch_num}] Action type is 'None', profiles will be kept running...")
            else:
                # Execute round-robin
                self._execute_round_robin(
                    profile_data=profile_data,
                    batch_num=batch_num,
                    flow_type=flow_type,
                    max_parallel_profiles=max_workers
                )
        
            # ===== PHASE 3: CLEANUP BATCH =====
            print(f"\n[BATCH {batch_num}] Phase 3: Cleaning up {len(opened_profiles)} profile(s)...")
        
            cleanup_results = GoLoginProfileHelper.cleanup_profiles(
                profile_data=profile_data,
                gologin_api=self.gologin_api,
                log_prefix=f"[BATCH {batch_num}][CLEANUP]"
            )
        
            cleanup_success = sum(1 for r in cleanup_results.values() if r)
            print(f"[BATCH {batch_num}][CLEANUP] ✓ Cleanup completed: {cleanup_success}/{len(cleanup_results)}")
        
            # ===== UPDATE STATISTICS =====
            completed_profiles = [
                pid for pid, data in profile_data.items()
                if data.get('status') == 'completed'
            ]
            error_profiles = [
                pid for pid, data in profile_data.items()
                if data.get('status') == 'error'
            ]
        
            total_success += len(completed_profiles)
            total_failed += len(failed_profiles) + len(error_profiles)
        
            print(f"\n[BATCH {batch_num}] ========== BATCH {batch_num} SUMMARY ==========")
            print(f"[BATCH {batch_num}] Total: {len(batch_profiles)}")
            print(f"[BATCH {batch_num}] Success: {len(completed_profiles)}")
            print(f"[BATCH {batch_num}] Failed: {len(failed_profiles) + len(error_profiles)}")
            print(f"{'='*70}\n")
    
        # ===== OVERALL SUMMARY =====
        print(f"\n{'='*80}")
        print(f"[GUI MODE] ========== OVERALL SUMMARY ==========")
        print(f"[GUI MODE] Total batches: {len(batches)}")
        print(f"[GUI MODE] Total profiles: {len(profile_list)}")
        print(f"[GUI MODE] Total success: {total_success}")
        print(f"[GUI MODE] Total failed: {total_failed}")
        print(f"{'='*80}")




    def _start_parallel_headless_all_profiles(self, profile_list, max_workers, flow_type):
        """
        Headless mode: Submit ALL profiles to ThreadPoolExecutor
        NO batch processing - workers pick profiles as available
    
        Similar to Collect Action architecture
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading
    
        print(f"\n[HEADLESS] Submitting ALL {len(profile_list)} profiles...")
        print(f"[HEADLESS] Max workers: {max_workers}")
        print(f"[HEADLESS] Flow type: {flow_type}")
    
        # Submit all profiles to thread pool
        executor = ThreadPoolExecutor(max_workers=max_workers)
    
        try:
            future_to_profile = {}
        
            # Submit ALL profiles at once (stagger delay)
            for i, profile_id in enumerate(profile_list):
                if i > 0:
                    time.sleep(2)  # Stagger delay
            
                # Each future executes: open → execute chains → cleanup
                future = executor.submit(
                    self._execute_profile_full_lifecycle_headless,
                    profile_id,
                    flow_type
                )
                future_to_profile[future] = profile_id
                print(f"[HEADLESS] Submitted {i+1}/{len(profile_list)}: {profile_id}")
        
            print(f"\n[HEADLESS] ✓ All {len(profile_list)} profiles submitted")
            print(f"[HEADLESS] Waiting for workers to complete...\n")
        
            # Wait for all to complete
            completed = 0
            succeeded = 0
            failed = 0
        
            for future in as_completed(future_to_profile):
                profile_id = future_to_profile[future]
                completed += 1
            
                try:
                    success = future.result()
                    if success:
                        succeeded += 1
                        print(f"[HEADLESS][{profile_id}] ✓ Completed ({completed}/{len(profile_list)})")
                    else:
                        failed += 1
                        print(f"[HEADLESS][{profile_id}] ✗ Failed ({completed}/{len(profile_list)})")
                except Exception as e:
                    failed += 1
                    print(f"[HEADLESS][{profile_id}] ✗ Exception: {e}")
        
            # Summary
            print(f"\n{'='*80}")
            print(f"[HEADLESS] ========== SUMMARY ==========")
            print(f"[HEADLESS] Total: {len(profile_list)}")
            print(f"[HEADLESS] Success: {succeeded}")
            print(f"[HEADLESS] Failed: {failed}")
            print(f"{'='*80}")
        
        finally:
            executor.shutdown(wait=True)
            print(f"[HEADLESS] ✓ Thread pool shut down")



    def _execute_profile_full_lifecycle_headless(self, profile_id, flow_type):
        """
        Full lifecycle for ONE profile in headless mode (runs in worker thread):
        1. Open profile
        2. Execute ALL chains
        3. Cleanup profile
    
        Returns:
            bool: True if successful
        """
        driver = None
    
        try:
            # ========== STEP 1: OPEN PROFILE ==========
            success, driver, debugger_address, error = self._open_single_profile_internal(
                profile_id,
                log_prefix=f"[HEADLESS][{profile_id}]"
            )
        
            if not success:
                print(f"[HEADLESS][{profile_id}] ✗ Failed to open: {error}")
                return False
        
            # ========== STEP 2: CHECK ACTION TYPE ==========
            if flow_type == "None":
                print(f"[HEADLESS][{profile_id}] Action type is 'None', profile kept running")
                return True
        
            # ========== STEP 3: EXECUTE ALL CHAINS ==========
            # Reuse existing _execute_all_chains_for_profile logic
            profile_data = {
                profile_id: {
                    'driver': driver,
                    'debugger_address': debugger_address,
                    'status': 'opened'
                }
            }
        
            # Execute chains (reuse existing method)
            success = self._execute_all_chains_for_profile(
                profile_id=profile_id,
                driver=driver,
                profile_data=profile_data,
                batch_num=0,  # No batch in headless
                flow_type=flow_type
            )
        
            return success
        
        except Exception as e:
            print(f"[HEADLESS][{profile_id}] ✗ Lifecycle error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
        # NOTE: Cleanup is handled in _execute_all_chains_for_profile's finally block


    def _open_single_profile_internal(self, profile_id, log_prefix="[GOLOGIN START]"):
        """
        Internal method to open profile (proxy + fingerprint + start + connect + cleanup tabs)
    
        This is a SHARED method used by:
        - _start_single_profile() (Sequential mode)
        - open_profile_thread() in _start_parallel() (Parallel mode)
    
        Returns:
            tuple: (success: bool, driver: WebDriver or None, debugger_address: str or None, error: str or None)
        """
        driver = None
    
        try:
            print(f"{log_prefix}[{profile_id}] Opening profile...")
        
            # ========== PROXY ASSIGNMENT (GIỐNG COLLECT ACTION) ==========
          
            proxy_file = self.params.get('proxy_file', '').strip()
            remove_proxy = self.params.get('remove_proxy', False)
        
            # Phase 1: Remove proxy if enabled
            if remove_proxy:
                try:
                    print(f"{log_prefix}[{profile_id}] Removing proxy...")
                    self.gologin_api.remove_proxy_for_profiles(profile_id)
                    print(f"{log_prefix}[{profile_id}] ✓ Proxy removed")
                except Exception as e:
                    print(f"{log_prefix}[{profile_id}] ⚠ Remove proxy error: {e}")
        
            # Phase 2: Assign proxy from file
            if proxy_file and os.path.exists(proxy_file):
                try:
                    print(f"{log_prefix}[{profile_id}] Assigning proxy from file...")
                    assign_success, message = GoLoginProfileHelper.assign_proxy_to_profile(
                        profile_id,
                        proxy_file,
                        self.gologin_api,
                        True,
                        log_prefix=f"[START PROXY][{profile_id}]"
                    )
                    print(f"{log_prefix}[{profile_id}] ✓ Proxy assigned: {message}")
                except ProxyAssignmentFailed as e:
                    # Stop profile if proxy required but failed
                    print(f"{log_prefix}[{profile_id}] ❌ Proxy assignment failed: {e}")
                    print(f"{log_prefix}[{profile_id}] Stopping - proxy required but failed")
                    raise  # Re-raise để stop batch/action
                except Exception as e:
                    print(f"{log_prefix}[{profile_id}] ⚠ Proxy assignment error: {e}")

            # ========== END PROXY LOGIC ==========
        
            # ========== REFRESH FINGERPRINT ==========
            refresh_fingerprint = self.params.get("refresh_fingerprint", False)
            if refresh_fingerprint:
                print(f"{log_prefix}[{profile_id}] Refreshing fingerprint...")
                success = self.gologin_api.refresh_fingerprint(profile_id)
                if success:
                    print(f"{log_prefix}[{profile_id}] ✓ Fingerprint refreshed")
                else:
                    print(f"{log_prefix}[{profile_id}] ⚠️ Failed to refresh fingerprint")
                    
        
            # ========== START PROFILE ==========
            print(f"{log_prefix}[{profile_id}] Starting profile...")

            # Get headless option
            headless = self.params.get("headless", False)
            resolution_str = ""
            # Set extra params based on headless mode
            if headless:
                try:
                    print(f"{log_prefix}[{profile_id}] Fetching profile screen resolution...")
                    success, profile_info = self.gologin_api.get_profile(profile_id)
        
                    if success:
                        # Extract resolution from navigator settings
                        resolution_str = profile_info.get('navigator', {}).get('resolution', '1920x1080')
                        width, height = resolution_str.split('x')
                        window_size_param = f"--window-size={width},{height}"
                        print(f"{log_prefix}[{profile_id}] Profile resolution: {resolution_str}")
                    else:
                        # Fallback to default
                        window_size_param = "--window-size=1920,1080"
                        print(f"{log_prefix}[{profile_id}] Could not fetch profile, using default: 1920x1080")
                except Exception as e:
                    # Fallback on any error
                    window_size_param = "--window-size=1920,1080"
                    print(f"{log_prefix}[{profile_id}] Resolution fetch error: {e}, using default: 1920x1080")
                    
                extra_params = [
                    "--headless=new",
                    window_size_param,
                    "--mute-audio",
                    "--disable-background-networking",
                    "--enable-features=NetworkService",
                    "--disk-cache-size=0",
                    "--media-cache-size=0",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--disable-software-rasterizer",
                    "--disable-features=VizDisplayCompositor",
                    "--ignore-certificate-errors",
                    "--ignore-ssl-errors",
                    "--disable-web-security",
                    "--allow-insecure-localhost",
                    "--reduce-security-for-testing",
                    "--disable-site-isolation-trials",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-breakpad",
                    "--disable-component-extensions-with-background-pages",
                    "--disable-features=TranslateUI,BlinkGenPropertyTrees",
                    "--disable-ipc-flooding-protection",
                    "--disable-renderer-backgrounding",
                    "--disable-sync",
                    "--gcm-channel-status-poll-interval-seconds=0",
                ]
            else:
                extra_params = [
                    "--enable-features=NetworkService",
                    "--disable-features=CookiesWithoutSameSiteMustBeSecure",
                    "--disk-cache-size=0",
                    "--media-cache-size=0",
                    "--disable-sync",
                    "--gcm-channel-status-poll-interval-seconds=0",
                ]

            # Start profile with extra params
            success, debugger_address = self.gologin_api.start_profile(profile_id, extra_params=extra_params)
            if not success:
                print(f"{log_prefix}[{profile_id}] ✗ Failed to start profile: {debugger_address}")
                return (False, None, None, debugger_address)

            print(f"{log_prefix}[{profile_id}] ✓ Profile started: {debugger_address}")
        
            # ========== CONNECT SELENIUM ==========
            driver = GoLoginProfileHelper.connect_selenium(debugger_address, log_prefix)
            if not driver:
                print(f"{log_prefix}[{profile_id}] ✗ Failed to connect Selenium")
                self.gologin_api.stop_profile(profile_id)
                return (False, None, debugger_address, 'Selenium connection failed')
        
            # ========== REGISTER DRIVER ==========
            register_selenium_driver(driver, profile_id)
            

            # ========== FIX: SET WINDOW SIZE VIA SELENIUM (Chrome Headless Bug Workaround) ==========
            if resolution_str:
                width, height = resolution_str.split('x')            
                # Set via Selenium API (works around Chrome 128+ bug)
                driver.set_window_size(int(width), int(height))
                time.sleep(0.5)  # Wait for resize
            
                # Verify
                actual_size = driver.get_window_size()
                print(f"{log_prefix}[{profile_id}] ✓ Window size set via Selenium: "
                        f"{actual_size['width']}x{actual_size['height']}")

            # ========== CHECK AND FIX CRASHED TABS FIRST ==========
            if not GoLoginProfileHelper.check_and_fix_crashed_tabs(driver, debugger_address, log_prefix, use_window_lock=False):
                print(f"{log_prefix}[{profile_id}] ✗ Could not fix crashed tabs")
                driver.quit()
                self.gologin_api.stop_profile(profile_id)
                return (False, None, debugger_address, 'Crashed tabs cannot be fixed')

            # ========== CLEANUP TABS ==========
            print(f"{log_prefix}[{profile_id}] Cleaning up browser tabs...")
            GoLoginProfileHelper.cleanup_browser_tabs(driver, log_prefix)
            time.sleep(1)

        
            print(f"{log_prefix}[{profile_id}] ✓ Profile opened successfully")
            return (True, driver, debugger_address, None)
        
        except Exception as e:
            print(f"{log_prefix}[{profile_id}] ✗ Exception while opening: {e}")
            import traceback
            traceback.print_exc()
            return (False, None, None, str(e))


    def _start_single_profile(self, profile_id):
        """Start profile and execute action - Profile stays alive"""
        driver = None
        try:
            # ========== OPEN PROFILE USING INTERNAL METHOD ==========
            success, driver, debugger_address, error = self._open_single_profile_internal(
                profile_id, 
                log_prefix="[GOLOGIN START]"
            )
        
            if not success:
                print(f"[GOLOGIN START][{profile_id}] ✗ Failed to open: {error}")
                return False      
            
        
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


    def _execute_all_chains_for_profile(self, profile_id, driver, profile_data, batch_num, flow_type):
        """
        Execute all chains for a single profile (for headless parallel mode)
    
        This method runs in a worker thread and:
        1. Creates flow iterator based on flow_type
        2. Executes ALL chains for this profile
        3. Cleans up profile after completion
    
        Args:
            profile_id: Profile ID to execute
            driver: Selenium driver instance
            profile_data: Shared dict to store status (thread-safe)
            batch_num: Batch number for logging
            flow_type: 'Youtube' or 'Google'
    
        Returns:
            bool: True if all chains executed successfully, False otherwise
        """
        try:
            log_prefix = f"[HEADLESS][BATCH {batch_num}][{profile_id}]"
            print(f"{log_prefix} Starting chain execution...")
        
            # ========== STEP 1: LOAD KEYWORDS ==========
            keywords_suffix_prefix = self.params.get("keywords_suffix_prefix", "").strip()
            keywords_youtube = GoLoginProfileHelper.load_keywords(self.params, "[Get Youtube Keywords]")
            keywords_google = GoLoginProfileHelper.load_keywords(self.params, "[Get Google Keywords]", "Google")
        
            # Get YouTube option params (same as round-robin)
            youtube_main_area_x = int(self.params.get("youtube_main_area_x", "0"))
            youtube_main_area_y = int(self.params.get("youtube_main_area_y", "0"))
            youtube_main_area_width = int(self.params.get("youtube_main_area_width", "1920"))
            youtube_main_area_height = int(self.params.get("youtube_main_area_height", "1080"))
            youtube_image_search_path = self.params.get("youtube_image_search_path", "").strip()
        
            youtube_sidebar_area_x = int(self.params.get("youtube_sidebar_area_x", "0"))
            youtube_sidebar_area_y = int(self.params.get("youtube_sidebar_area_y", "0"))
            youtube_sidebar_area_width = int(self.params.get("youtube_sidebar_area_width", "400"))
            youtube_sidebar_area_height = int(self.params.get("youtube_sidebar_area_height", "1080"))
            youtube_sidebar_image_search_path = self.params.get("youtube_sidebar_image_search_path", "").strip()
        
            keywords = {
                "keywords_youtube": keywords_youtube,
                "keywords_google": keywords_google,
                "suffix_prefix": keywords_suffix_prefix,
                # Youtube Option params
                "youtube_main_area_x": youtube_main_area_x,
                "youtube_main_area_y": youtube_main_area_y,
                "youtube_main_area_width": youtube_main_area_width,
                "youtube_main_area_height": youtube_main_area_height,
                "youtube_image_search_path": youtube_image_search_path,
                # Sidebar params
                "youtube_sidebar_area_x": youtube_sidebar_area_x,
                "youtube_sidebar_area_y": youtube_sidebar_area_y,
                "youtube_sidebar_area_width": youtube_sidebar_area_width,
                "youtube_sidebar_area_height": youtube_sidebar_area_height,
                "youtube_sidebar_image_search_path": youtube_sidebar_image_search_path,
            }
        
            if not keywords:
                print(f"{log_prefix} ✗ Failed to load keywords")
                profile_data[profile_id]['status'] = 'error'
                profile_data[profile_id]['error'] = 'Failed to load keywords'
                return False
        
            # ========== STEP 2: CREATE FLOW ITERATOR ==========
            debugger_address = profile_data[profile_id].get('debugger_address', '')
        
            if flow_type == "Youtube":
                flow_iterator = YouTubeFlowHeadless.create_flow_iterator(
                    driver=driver,
                    keywords=keywords,
                    profile_id=profile_id,
                    debugger_address=debugger_address,
                    log_prefix=log_prefix
                )
            elif flow_type == "Google":
                flow_iterator = GoogleFlow.create_flow_iterator(
                    driver=driver,
                    keywords=keywords,
                    profile_id=profile_id,
                    debugger_address=debugger_address,
                    log_prefix=log_prefix
                )
            else:
                print(f"{log_prefix} ✗ Unknown flow type: {flow_type}")
                profile_data[profile_id]['status'] = 'error'
                profile_data[profile_id]['error'] = f'Unknown flow type: {flow_type}'
                return False
        
            print(f"{log_prefix} ✓ Flow iterator created")
        
            # ========== STEP 3: EXECUTE ALL CHAINS ==========
            chain_count = 0
            total_chains = flow_iterator.get_progress()['total']
        
            print(f"{log_prefix} Starting execution of {total_chains} chain(s)...")
        
            while flow_iterator.has_next_chain():
                chain_count += 1
                progress = flow_iterator.get_progress()
            
                print(f"\n{log_prefix} [{chain_count}/{total_chains}] "
                      f"Executing chain (Progress: {progress['percentage']:.1f}%)...")
            
                try:
                    success = flow_iterator.execute_next_chain()
                
                    if success:
                        print(f"{log_prefix} [{chain_count}/{total_chains}] ✓ Chain executed successfully")
                    else:
                        print(f"{log_prefix} [{chain_count}/{total_chains}] ⚠ Chain failed, continuing...")
                
                    # Delay between chains (same as round-robin)
                    time.sleep(1)
                
                except Exception as chain_error:
                    print(f"{log_prefix} [{chain_count}/{total_chains}] ✗ Chain exception: {chain_error}")
                    import traceback
                    traceback.print_exc()
                    # Continue to next chain instead of breaking
        
            print(f"\n{log_prefix} ✓ Completed all {chain_count} chain(s)")
        
            # ========== STEP 4: MARK AS COMPLETED ==========
            profile_data[profile_id]['status'] = 'completed'
            profile_data[profile_id]['chains_executed'] = chain_count
        
            return True
        
        except Exception as e:
            print(f"[HEADLESS][BATCH {batch_num}][{profile_id}] ✗ Error executing chains: {e}")
            import traceback
            traceback.print_exc()
        
            # Update status
            profile_data[profile_id]['status'] = 'error'
            profile_data[profile_id]['error'] = str(e)
        
            return False
    
        finally:
            # ========== STEP 5: CLEANUP PROFILE ==========
            try:
                print(f"[HEADLESS][BATCH {batch_num}][{profile_id}] Cleaning up profile...")
            
                # Unregister driver
                unregister_selenium_driver(profile_id)
                print(f"[HEADLESS][BATCH {batch_num}][{profile_id}] ✓ Driver unregistered")
            
                # Quit driver
                if driver:
                    driver.quit()
                    print(f"[HEADLESS][BATCH {batch_num}][{profile_id}] ✓ Driver quit")
            
                # Stop profile via GoLogin API
                self.gologin_api.stop_profile(profile_id)
                print(f"[HEADLESS][BATCH {batch_num}][{profile_id}] ✓ Profile stopped")
            
                print(f"[HEADLESS][BATCH {batch_num}][{profile_id}] ✓ Cleanup completed")
            
            except Exception as cleanup_error:
                print(f"[HEADLESS][BATCH {batch_num}][{profile_id}] ⚠ Cleanup error: {cleanup_error}")




    def _execute_action(self, driver, profile_id, action_type, debugger_address):
        """Execute action based on type"""
        try:
            keywords_suffix_prefix = self.params.get("keywords_suffix_prefix", "").strip()
            keywords_youtube = GoLoginProfileHelper.load_keywords(self.params, "[Get Youtube Keywords]")
            keywords_google = GoLoginProfileHelper.load_keywords(self.params, "[Get Google Keywords]", "Google")
            
            # ========== GET YOUTUBE OPTION PARAMS ==========
            # Main Area coordinates
            youtube_main_area_x = int(self.params.get("youtube_main_area_x", "0"))
            youtube_main_area_y = int(self.params.get("youtube_main_area_y", "0"))
            youtube_main_area_width = int(self.params.get("youtube_main_area_width", "1920"))
            youtube_main_area_height = int(self.params.get("youtube_main_area_height", "1080"))
        
            # Logo image path
            youtube_image_search_path = self.params.get("youtube_image_search_path", "").strip()
        
            # Sidebar Area coordinates (for future use)
            youtube_sidebar_area_x = int(self.params.get("youtube_sidebar_area_x", "0"))
            youtube_sidebar_area_y = int(self.params.get("youtube_sidebar_area_y", "0"))
            youtube_sidebar_area_width = int(self.params.get("youtube_sidebar_area_width", "400"))
            youtube_sidebar_area_height = int(self.params.get("youtube_sidebar_area_height", "1080"))
            youtube_sidebar_image_search_path = self.params.get("youtube_sidebar_image_search_path", "").strip()
            
            keywords = {
                "keywords_youtube" : keywords_youtube,
                "keywords_google" : keywords_google,
                "suffix_prefix" : keywords_suffix_prefix,
                # Youtube Option params
                "youtube_main_area_x": youtube_main_area_x,
                "youtube_main_area_y": youtube_main_area_y,
                "youtube_main_area_width": youtube_main_area_width,
                "youtube_main_area_height": youtube_main_area_height,
                "youtube_image_search_path": youtube_image_search_path,
            
                # Sidebar params (optional)
                "youtube_sidebar_area_x": youtube_sidebar_area_x,
                "youtube_sidebar_area_y": youtube_sidebar_area_y,
                "youtube_sidebar_area_width": youtube_sidebar_area_width,
                "youtube_sidebar_area_height": youtube_sidebar_area_height,
                "youtube_sidebar_image_search_path": youtube_sidebar_image_search_path,
            }
            
            if action_type == "None":
                print(f"[GOLOGIN START] [{profile_id}] No action required")
                return True
            
            elif action_type == "Youtube":
                
                if not keywords:
                    return False
                return YouTubeFlow.execute_main_flow(driver, keywords, profile_id, debugger_address, "[GOLOGIN START]")
            
            elif action_type == "Google":                
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