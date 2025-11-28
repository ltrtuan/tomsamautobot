# controllers/actions/gologin_selenium_start_action.py

from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from models.gologin_api import get_gologin_api
import random
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
import pyautogui
import time
import pywinauto.findwindows as fw
import win32gui
import os
import itertools
import logging
logger = logging.getLogger('TomSamAutobot')

from exceptions.gologin_exceptions import ProxyAssignmentFailed

from controllers.actions.flow_auto.youtube_flow_factory import YouTubeFlowAutoFactory
from helpers.app_helpers import check_and_focus_window_by_title
# Import helpers
from helpers.gologin_profile_helper import GoLoginProfileHelper
from helpers.selenium_registry import register_selenium_driver, unregister_selenium_driver
from concurrent.futures import ThreadPoolExecutor, as_completed

from helpers.website_manager import get_random_warmup_url

class GoLoginAutoAction(BaseAction):
    """Handler for GoLogin Selenium Start Profile action"""
    
    def prepare_play(self):
        """Execute GoLogin Selenium Start Profile - Updated for per-profile proxy assignment with retry/stop logic."""
        # ===== CHECK STOP FLAG AT START OF BATCH (FIX) =====
        if self.controller and hasattr(self.controller, 'is_execution_stopped') and self.controller.is_execution_stopped:
            logger.info(f"[GoLoginAutoAction prepare_play PAUSE/BREAK")
            return False
        # ====================================================
        try:
            # Get API token from variable name (original)
            api_key_variable = self.params.get("api_key_variable", "").strip()
            if not api_key_variable:
                logger.error("[GOLOGIN AUTO] Error: API key variable name is required")
                self.set_variable(False)
                return
        
            # Get API token value from GlobalVariables (original)
            api_token = GlobalVariables().get(api_key_variable, "")
            if not api_token:
                logger.error(f"[GOLOGIN AUTO] Error: Variable '{api_key_variable}' is empty or not set")
                self.set_variable(False)
                
        
            logger.info(f"[GOLOGIN AUTO] Using API token from variable: {api_key_variable}")
        
            try:
                # ========== INITIALIZE GOLOGIN API INSTANCE ==========
                self.gologin_api = get_gologin_api(api_token)
                # ====================================================
        
                # ========== GET PROFILE LIST USING HELPER ==========
                success, result = GoLoginProfileHelper.get_profile_list(
                    self.params, api_token, "[GOLOGIN AUTO]"
                )
            except RuntimeError as e:  # ← Catch built-in exception
                logger.error(f"[GOLOGIN AUTO] ❌ Runtime error: {e}")
                logger.error("[GOLOGIN AUTO] Stopping action...")
                self.set_variable(False)
                raise  # ← RE-RAISE for email!
        
            except Exception as e:
                logger.error(f"[GOLOGIN AUTO] Error: {e}")
                self.set_variable(False)
                raise
              
        
            profile_list = result
            logger.info(f"[GOLOGIN START] Total profiles to start: {len(profile_list)}")        
        
            # ========== CHECK MULTI-THREADING ==========
            enable_threading = self.params.get("enable_threading", False)
            GoLoginProfileHelper.kill_all_orbita_processes(
                log_prefix="[GOLOGIN AUTO]"
            )
            if enable_threading and len(profile_list) > 1:
                # PARALLEL MODE (original, but pass proxy args)
                logger.info("[GOLOGIN START] ========== PARALLEL MODE ==========")               
            
                self._start_parallel(profile_list)
                self.set_variable(True)  # Assume success if no raise
            else:
                # SEQUENTIAL MODE - Select 1 profile and start (original, but pass proxy args)
                logger.info("[GOLOGIN START] ========== SEQUENTIAL MODE ==========")
                how_to_get = self.params.get("how_to_get", "Random")
                profile_id = GoLoginProfileHelper.select_profile(profile_list, how_to_get)
                logger.info(f"[GOLOGIN START] Selected profile ID: {profile_id}")              
            
                # Start single profile (updated call)
                single_success = self._start_single_profile(profile_id)
                self.set_variable(single_success)
                
            
        except ProxyAssignmentFailed as e:
            # New: Catch proxy fail - stop entire action (critical for YouTube IP safety)
            logger.error(f"[GOLOGIN START] ❌ Proxy assignment failed: {e}")
            logger.error("[GOLOGIN START] Stopping action - no proxy means IP duplication risk, no YouTube views")
            self.set_variable(False)
            # Optional: Cleanup (stop all if partial)
            # self.gologin_api.stop_all_active_profiles()
            # ✅ RE-RAISE để action_controller bắt được và gửi email!
            raise  # ← CRITICAL: Re-raise for email alerting!
        except Exception as e:
            # Original except
            logger.error(f"[GOLOGIN START] Error: {e}")
            import traceback
            traceback.print_exc()
            self.set_variable(False)
            raise


    def _type_profile_id_and_enter(self, profile_id, log_prefix):
        """
        Helper method: Type profile ID and press Enter in GoLogin search box
    
        Args:
            profile_id: Profile ID to type
            log_prefix: Log prefix for messages
    
        Returns:
            bool: True if typing succeeded, False otherwise
        """
        try:
            import pyperclip
            from pywinauto.keyboard import send_keys
            from helpers.app_helpers import check_and_focus_window_by_title
        
            # Clear existing text
            check_and_focus_window_by_title("Profiles - GoLogin")
            
            
            # ========== STEP 3: SEND CTRL+F TO OPEN SEARCH ==========         
            send_keys('^f')  # Ctrl+F
            time.sleep(0.5)
            
            send_keys("^a{BACKSPACE}")  # Ctrl+A (select all)
            time.sleep(0.5)
        
            # Type profile ID via clipboard (safe with special characters)
            pyperclip.copy(profile_id)
            send_keys("^v")  # Ctrl+V (paste)
            time.sleep(0.5)
        
            # Press Enter to search
            send_keys("{ENTER}")
            logger.info(f"{log_prefix} Typed profile ID and pressed Enter")
        
            return True
        
        except Exception as e:
            logger.error(f"{log_prefix} Failed to type profile ID: {e}")
            return False

    
    def _open_profile(self, profile_id, batch_num=None):
        """
        Open profile via pywinauto (Automate GoLogin App UI) - Updated with per-profile proxy assignment before UI.

        Flow:
        1. Assign proxy if file provided (new: retry all lines, raise if fail + required)
        2. Connect to GoLogin app
        3. Focus window
        4. Send Ctrl+F to open search (using pywinauto)
        5. Type profile ID + Enter (using pywinauto)
        6. Click Run button (using pywinauto)

        Args:
            profile_id: Profile ID to open
            batch_num: Batch number for logging (optional)

        Returns:
            dict: {'success': bool, 'profile_id': str, 'error': str or None} - success for UI open; proxy fail raises if required
        """
        log_prefix = f"[BATCH {batch_num}][{profile_id}]" if batch_num else f"[GOLOGIN AUTO][{profile_id}]"
        proxy_file = self.params.get('proxy_file', '').strip()
        remove_proxy = self.params.get('remove_proxy', False)
    
        # Phase 1: Remove proxy if enabled
        if remove_proxy:
            try:
                self.gologin_api.remove_proxy_for_profiles(profile_id)
            except Exception as e:
                logger.error(f"{log_prefix} ⚠ Remove proxy error: {e}")

        # Phase 2: Assign proxy from file using helper
        if proxy_file and os.path.exists(proxy_file):            
            try:
                success, message = GoLoginProfileHelper.assign_proxy_to_profile(
                    profile_id,
                    proxy_file,
                    self.gologin_api,
                    False,
                    log_prefix
                )
                logger.info(f"{log_prefix} ✓ {message}")
    
            except ProxyAssignmentFailed as e:
                # Catch exception nếu MUỐN continue (không stop action)               
                logger.error(f"{log_prefix} Proceeding without proxy (using local IP)")
                raise        

        # Original UI code (kept 100% unchanged, from refresh to end)
        try:
            # Import dependencies
            from pywinauto.application import Application
            from pywinauto.keyboard import send_keys
    
            # ========== REFRESH FINGERPRINT (OPTIONAL) ==========
            refresh_fingerprint = self.params.get("refresh_fingerprint", False)
    
            if refresh_fingerprint:               
                success = self.gologin_api.refresh_fingerprint(profile_id)        
                if not success:
                    logger.error(f"{log_prefix} ⚠️ Failed to refresh fingerprint")        
    
            # ========== STEP 2: CONNECT TO GOLOGIN APP (OPTIMIZED WITH HELPER) ==========
           

            # Use helper to find and focus window (fast, no hang)
            success = check_and_focus_window_by_title("GoLogin")
            if not success:
                logger.error(f"{log_prefix} ❌ GoLogin window not found via helper after focus attempt")
                return {
                    'success': False,
                    'profile_id': profile_id,
                    'error': 'GoLogin window not found'
                }

            app = None
            try:
                # Get current foreground window (should be GoLogin after helper focus)
                import win32gui
                hwnd = win32gui.GetForegroundWindow()
                window_title = win32gui.GetWindowText(hwnd)
    
                # Verify it's GoLogin (safety check)
                if "gologin" not in window_title.lower():
                    logger.error(f"{log_prefix} ⚠️ Foreground window mismatch: '{window_title}', searching manually...")
                    # Fallback: Manual search for GoLogin hwnd
                    import pywinauto.findwindows as fw
                    windows = fw.find_windows(title_re=".*[Gg]o[Ll]ogin.*")
                    if not windows:
                        logger.error(f"{log_prefix} ❌ No GoLogin window found in search")
                        return {
                            'success': False,
                            'profile_id': profile_id,
                            'error': 'GoLogin window not found after search'
                        }
                    hwnd = windows[0]  # Use first match
                    window_title = win32gui.GetWindowText(hwnd)
                    logger.info(f"{log_prefix} Found window via search: '{window_title}'")
    
                # Connect by handle (direct, no title search hang)
                from pywinauto.application import Application
                app = Application(backend="uia").connect(handle=hwnd)
                logger.info(f"{log_prefix} ✓ Connected via handle {hwnd} (title: '{window_title}')")

            except Exception as e:
                logger.error(f"{log_prefix} ❌ Failed to connect by handle: {e}")
                import traceback
                traceback.print_exc()
                return {
                    'success': False,
                    'profile_id': profile_id,
                    'error': f'Failed to connect by handle: {e}'
                }

            if not app:
                logger.error(f"{log_prefix} ❌ App object not created")
                return {
                    'success': False,
                    'profile_id': profile_id,
                    'error': 'App connection failed'
                }

            logger.info(f"{log_prefix} ✓ Successfully connected to GoLogin app")

            # ========== GET WINDOW OBJECT FROM APP (as before) ==========
            try:
                gologin_window = app.window(handle=hwnd)  # Use handle directly (faster than title_re search)
                gologin_window.wait('visible', timeout=5)  # Short timeout OK (window already focused)
            except Exception as e:
                print(f"{log_prefix} ❌ Failed to get window object: {e}")
                return {
                    'success': False,
                    'profile_id': profile_id,
                    'error': f'Failed to get window: {e}'
                }

            # ... (Continue with Ctrl+F, type, click Run as before - no change needed)

    
            # ========== STEP 4: TYPE PROFILE ID + ENTER ==========
            if not self._type_profile_id_and_enter(profile_id, log_prefix):
                return {'success': False, 'profile_id': profile_id, 'error': "Failed to type profile ID"}
           

            # ========== STEP 4.5: RETRY TYPING UNTIL PROFILE FOUND (SMART RETRY) ==========
            max_retries = 3  # Retry typing 3 times total (initial + 2 retries)
            retry_interval = 2  # Wait 2s between retries
            run_button = None

            for attempt in range(1, max_retries + 1):
                logger.info(f"{log_prefix} Attempt {attempt}/{max_retries}: Checking if profile found...")
    
                # Wait for profile to load after typing
                time.sleep(retry_interval)
    
                # Try to find Run button
                check_and_focus_window_by_title("GoLogin")
                try:
                    run_button = gologin_window.child_window(title="Run", control_type="Button")
                    if run_button.exists():
                        logger.info(f"{log_prefix} ✓ Profile found on attempt {attempt}")
                        break  # Exit retry loop - profile found!
                    else:
                        logger.warning(f"{log_prefix} Profile not found on attempt {attempt}")
                except Exception as e:
                    logger.warning(f"{log_prefix} Run button not accessible on attempt {attempt}: {e}")
    
                # If not last attempt, retry typing
                if attempt < max_retries:
                    logger.info(f"{log_prefix} Retrying: Type profile ID again (attempt {attempt + 1}/{max_retries})...")
        
                    # Re-type profile ID + Enter
                    if not self._type_profile_id_and_enter(profile_id, log_prefix):
                        logger.error(f"{log_prefix} Failed to type on retry attempt {attempt + 1}")
                        # Continue to next attempt anyway (maybe UI recovered)

            # Check final result
            if run_button is None or not run_button.exists():
                logger.error(f"{log_prefix} ❌ Profile not found after {max_retries} attempts - invalid profile ID or search failed")
                return {
                    'success': False, 
                    'profile_id': profile_id, 
                    'error': f"Profile not found after {max_retries} typing attempts"
                }

            logger.info(f"{log_prefix} Profile found, proceeding to click Run button")


            # ========== STEP 5: CLICK RUN BUTTON ==========
            try:
                if run_button and run_button.exists():
                    run_button.click_input()    
                    time.sleep(0.5)  # Wait for profile to open
    
                    return {
                        'success': True,
                        'profile_id': profile_id,
                        'error': None
                    }
                else:
                    logger.error(f"{log_prefix} ❌ Run button not accessible")
                    return {
                        'success': False,
                        'profile_id': profile_id,
                        'error': 'Run button not accessible'
                    }
    
            except Exception as e:
                logger.error(f"{log_prefix} ❌ Failed to click Run button: {e}")
                return {
                    'success': False,
                    'profile_id': profile_id,
                    'error': f'Failed to click: {e}'
                }


        except Exception as e:
            logger.error(f"{log_prefix} ❌ Exception in _open_profile")
            logger.error(f"{log_prefix} Error: {e}")
            import traceback
            traceback.print_exc()
    
            return {
                'success': False,
                'profile_id': profile_id,
                'error': str(e)
            }



        
    def _start_parallel(self, profile_list):
        """
        Execute parallel mode with BATCH PROCESSING - Updated to pass proxy args to open, stop if proxy fail + required.

        NEW WORKFLOW:
        - Divide profiles into batches of size max_workers
        - For each batch:
            1. Open all profiles in batch (parallel, with proxy assign per-profile)
            2. Execute all chains round-robin with lock - if action_type != None
            3. Close all profiles in batch (parallel) - if action_type != None
        - Repeat until all profiles processed; raise/stop if proxy fail + require (IP risk for YouTube)

        Args:
            profile_list: List of profile IDs to execute
        """
        import threading
        from concurrent.futures import ThreadPoolExecutor, as_completed

        max_parallel_profiles = int(self.params.get("max_workers", 1))
        action_type = self.params.get("action_type", None)
        browse_youtube = self.params.get("browse_youtube", False)

        print("[GOLOGIN AUTO] ========== PARALLEL MODE ==========")
        print("=" * 80)
        print(f"[PARALLEL MODE] BATCH PROCESSING (batch size: {max_parallel_profiles})")
        print(f"[PARALLEL MODE] Total profiles: {len(profile_list)}")
        print(f"[PARALLEL MODE] Action type: {action_type}")
        print("=" * 80)

        # ========== RANDOMIZE PROFILE LIST IF NEEDED ==========
        how_to_get = self.params.get("how_to_get", "Random")
    
        if how_to_get == "Random":
            print(f"[GOLOGIN WARMUP] how_to_get = Random → Creating randomized list")
            profile_list = GoLoginProfileHelper.create_randomized_profile_list(
                original_profile_list=profile_list,
                max_workers=max_parallel_profiles,
                log_prefix="[GOLOGIN WARMUP]"
            )
        # Divide profiles into batches
        batches = []
        for i in range(0, len(profile_list), max_parallel_profiles):
            batch = profile_list[i:i + max_parallel_profiles]
            batches.append(batch)

        print(f"[PARALLEL MODE] Divided into {len(batches)} batches\n")

        total_success = 0
        total_failed = 0
        # ========== ADD GLOBAL LOCK FOR PROFILE OPENING ==========
        profile_open_lock = threading.Lock()  # ← THÊM LOCK MỚI
        # ========== PROCESS EACH BATCH ==========
        for batch_num, batch_profiles in enumerate(batches, 1):
            # ===== CHECK STOP FLAG AT START OF BATCH (FIX) =====
            if self.controller and hasattr(self.controller, 'is_execution_stopped') and self.controller.is_execution_stopped:
                logger.info(f"[BATCH {batch_num}] PAUSE/BREAK detected at start - Skipping this batch")
                break  # Exit outer loop, không xử lý batch này nữa
            # ====================================================

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
                    with profile_open_lock:  # ← LOCK TOÀN BỘ OPEN PROCESS                

                        print(f"[BATCH {batch_num}][{profile_id}] Opening profile...")
                        
                        # ========== CALL _open_profile() METHOD (UPDATED: PASS PROXY ARGS) ==========
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
        
                except ProxyAssignmentFailed:
                    # New: Propagate proxy fail raise (stop entire action if required)
                    print(f"[BATCH {batch_num}][{profile_id}] Proxy failed - propagating stop")
                    raise  # Re-raise to as_completed
                except Exception as e:
                    print(f"[BATCH {batch_num}][{profile_id}] ❌ Exception while opening: {e}")
                    import traceback
                    traceback.print_exc()
            
                    with open_lock:
                        profile_data[profile_id] = {
                            'status': 'error',
                            'error': str(e)
                        }
                    raise
            # ========== USE THREADPOOLEXECUTOR TO OPEN PROFILES ==========
            executor = ThreadPoolExecutor(max_workers=max_parallel_profiles)
            # ========== CHECK EXCEPTIONS FROM THREADS (NEW) ==========
            exception_from_thread = None
            exception_traceback = None
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
                        # future.result() sẽ:
                        # - Block đến khi thread xong
                        # - Re-raise exception nếu thread có exception
                        future.result()
                    except (ProxyAssignmentFailed, Exception) as thread_exception:
                        # ========== EXCEPTION FROM THREAD (UPDATED) ==========
                        print("=" * 80)
                        print(f"[BATCH {batch_num}] ⚠ EXCEPTION CAUGHT FROM THREAD: {profile_id}")
                        print(f"[BATCH {batch_num}] Exception type: {type(thread_exception).__name__}")
                        print(f"[BATCH {batch_num}] Exception message: {thread_exception}")
                        print("=" * 80)
                    
                        import traceback
                        exception_traceback = traceback.format_exc()
                        print(exception_traceback)
                    
                        # LƯU EXCEPTION ĐẦU TIÊN
                        if exception_from_thread is None:
                            exception_from_thread = thread_exception
                    
                        # ===== BREAK IMMEDIATELY - KHÔNG CHỜ CÁC THREADS KHÁC =====
                        print(f"[BATCH {batch_num}] ⚠ Breaking immediately, will cleanup and re-raise")
                        break  # ← BREAK RA KHỎI LOOP NGAY
                    
                    except ProxyAssignmentFailed:
                        # New: If proxy fail raised, cleanup partial opened in this batch, then propagate stop
                        print(f"[BATCH {batch_num}] Proxy fail in thread {profile_id} - cleanup partial and stop action")
                        opened_so_far = [pid for pid, data in profile_data.items() if data.get('status') == 'opened']
                        if opened_so_far:
                            self._close_profiles_batch(opened_so_far)  # Assume helper method for close
                        raise  # Propagate to prepare_play
    
            finally:
                executor.shutdown(wait=True)
                print(f"[BATCH {batch_num}] PHASE 1: Thread pool shut down")
    
            # ========== CHECK OPENING RESULTS ==========
            if exception_from_thread is not None:
                print("=" * 80)
                print(f"[BATCH {batch_num}] ⚠ CRITICAL: Exception occurred, cleaning up...")
                print("=" * 80)
            
                # ===== CLEANUP: CLOSE ALL OPENED PROFILES IN THIS BATCH =====
                opened_profiles = [pid for pid, data in profile_data.items() if data.get('status') == 'opened']
            
                if opened_profiles:
                    print(f"[BATCH {batch_num}] Closing {len(opened_profiles)} opened profiles before re-raise...")
                
                    try:
                        for profile_id in opened_profiles:
                            try:
                                print(f"[BATCH {batch_num}][{profile_id}] Closing profile...")
                            
                                # Bring to front
                                bring_result = GoLoginProfileHelper.bring_profile_to_front(
                                    profile_id,
                                    driver=None,
                                    log_prefix=f"[BATCH {batch_num}][{profile_id}]"
                                )
                                if bring_result:
                                    time.sleep(1)
                            
                                    # Send Alt+F4
                                    pyautogui.hotkey('alt', 'f4')
                                    time.sleep(1)
                            
                                    print(f"[BATCH {batch_num}][{profile_id}] ✓ Profile closed")
                            
                            except Exception as close_err:
                                print(f"[BATCH {batch_num}][{profile_id}] ⚠ Failed to close: {close_err}")
                            
                        print(f"[BATCH {batch_num}] ✓ Cleanup completed")
                    
                    except Exception as cleanup_err:
                        print(f"[BATCH {batch_num}] ⚠ Error during cleanup: {cleanup_err}")
            
                # ===== RE-RAISE EXCEPTION TO PROPAGATE TO MAIN THREAD =====
                print("=" * 80)
                print(f"[BATCH {batch_num}] RE-RAISING EXCEPTION TO MAIN THREAD")
                print("=" * 80)
            
                raise exception_from_thread  # ← RE-RAISE ĐỂ BUBBLE UP
                # ===========================================================



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
            
            # ===== CHECK STOP FLAG AFTER PHASE 1 (NEW) =====
            if self.controller and hasattr(self.controller, 'is_execution_stopped') and self.controller.is_execution_stopped:
                logger.info(f"[BATCH {batch_num}] PAUSE/BREAK detected after PHASE 1 - Closing opened profiles")
                # Close opened profiles before exit
                for profile_id in opened_profiles:
                    try:
                        result_bring = GoLoginProfileHelper.bring_profile_to_front(profile_id, driver=None, log_prefix=f"[BATCH {batch_num}][{profile_id}]")
                        if result_bring:
                            time.sleep(1)
                            pyautogui.hotkey('alt', 'f4')
                            time.sleep(1)
                    except:
                        pass
                break  # Exit batch loop
            # ================================================
    
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
    
            flow_iterators = {}  # profile_id → flow_iterator
           
            for profile_id in opened_profiles:              
        
                try:
                    mixed_keyword, keyword_type = self._get_mixed_keyword_google()
                    if action_type == "Youtube":
                        if browse_youtube:
                            flow_iterator = YouTubeFlowAutoFactory.create_flow_iterator(
                                profile_id=profile_id,
                                parameters={**self.params, 'opened_profiles': opened_profiles, 'max_workers' : max_parallel_profiles, 'list_warmup_url' : mixed_keyword, 'keyword_type' : keyword_type},
                                log_prefix=f"[BATCH {batch_num}][{profile_id}]",
                                flow_type="browse",
                                controller = self.controller
                            )
                        else:
                            flow_iterator = YouTubeFlowAutoFactory.create_flow_iterator(
                                profile_id=profile_id,
                                parameters={**self.params, 'opened_profiles': opened_profiles, 'max_workers' : max_parallel_profiles, 'list_warmup_url' : mixed_keyword, 'keyword_type' : keyword_type},
                                log_prefix=f"[BATCH {batch_num}][{profile_id}]",
                                flow_type="search",
                                controller = self.controller
                            )
                      
                    elif action_type == "Google":
                        # TODO: Implement GoogleFlowAuto later
                        print(f"[BATCH {batch_num}][{profile_id}] Google flow not implemented for Auto Action yet")
                        continue
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
                    # ===== CHECK PAUSE/BREAK FLAG AT START (FIX) =====
                    if self.controller and hasattr(self.controller, 'is_execution_stopped') and self.controller.is_execution_stopped:
                        logger.info(f"[BATCH {batch_num}] ROUND {round_num} ESC detected - Stopping all profiles")
                        active_profiles.clear()  # Clear để thoát outer loop
                        break
                    # =========================================
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
                    
                    # ===== CHECK PAUSE/BREAK FLAG BEFORE EXECUTE (FIX) =====
                    if self.controller and hasattr(self.controller, 'is_execution_stopped') and self.controller.is_execution_stopped:
                        logger.info(f"[BATCH {batch_num}] [{profile_id}] ESC detected before execute")
                        profiles_to_remove.append(profile_id)
                        continue
                    # ===============================================
            
                    try:
                        success = flow.execute_next_chain()
                        # ===== CHECK PAUSE/BREAK FLAG AFTER EXECUTE (FIX) =====
                        if self.controller and hasattr(self.controller, 'is_execution_stopped') and self.controller.is_execution_stopped:
                            logger.info(f"[BATCH {batch_num}] [{profile_id}] ESC detected after execute")
                            profiles_to_remove.append(profile_id)
                            continue
                        # ==============================================
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
    
            # ========== PHASE 4: CLOSE BROWSERS WITH ALT+F4 (UPDATED) ==========
            print(f"[BATCH {batch_num}] PHASE 4: Closing {len(opened_profiles)} browsers with Alt+F4 (FIFO order)...")
            print(f"[BATCH {batch_num}] Order: {opened_profiles}")

            closed_count = 0
            for profile_id in opened_profiles:  # opened_profiles đã theo thứ tự FIFO
                try:
                    log_prefix = f"[BATCH {batch_num}][{profile_id}]"    
                   
                    result_bring = GoLoginProfileHelper.bring_profile_to_front(
                        profile_id,
                        driver=profile_data[profile_id]['driver'],
                        log_prefix=log_prefix
                    )
                    logger.info(f"[{profile_id}] PHASE 4: Closing browser with Alt+F4... result_bring {result_bring}")
                    if result_bring:
                        time.sleep(1)
    
                        pyautogui.hotkey('alt', 'f4')
                        time.sleep(1)
    
                        print(f"{log_prefix} ✓ Browser closed")
                        closed_count += 1
    
                except Exception as e:
                    print(f"{log_prefix} ❌ Failed to close: {e}")
                    import traceback
                    traceback.print_exc()

            print(f"[BATCH {batch_num}] PHASE 4: Closed {closed_count}/{len(opened_profiles)} browsers")
            
    
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


    def _close_profiles_batch(self, profiles):
        """
        Emergency cleanup: Close batch of opened profiles with Alt+F4 (fast, no random sleep).
        Used for partial open on proxy fail + require.

        Args:
            profiles: List of profile_ids to close (opened ones)
        """
        print(f"[EMERGENCY CLEANUP] Closing {len(profiles)} partial profiles: {profiles}")

        closed_count = 0
        for profile_id in profiles:
            try:
                log_prefix = f"[CLEANUP][{profile_id}]"
                # Bring to front
                bring_result = GoLoginProfileHelper.bring_profile_to_front(
                    profile_id,
                    driver=None,  # Manual mode
                    log_prefix=log_prefix
                )
                if bring_result:
                    time.sleep(2)
                    # Alt+F4
                    pyautogui.hotkey('alt', 'f4')
                    time.sleep(1)  # Short delay
                    print(f"{log_prefix} ✓ Closed")
                    closed_count += 1
            except Exception as e:
                print(f"{log_prefix} ❌ Close failed: {e}")
                import traceback
                traceback.print_exc()

        print(f"[EMERGENCY CLEANUP] Closed {closed_count}/{len(profiles)} profiles")


    def _get_mixed_keyword_google(self):
        """
        Get keywords by RANDOMLY choosing ONE source:
        - Option 1: ALL keywords from keywords_google_file
        - Option 2: ALL URLs from warmup_websites_file
    
        Random choice 50/50 between the 2 files (NOT mixing both)
    
        Returns:
            tuple: (keywords_list: list, type: str)
                - keywords_list: List of keywords OR URLs
                - type: "google" if from keywords file, "warmup" if from warmup file
                Returns ([], None) if both files not found
    
        Example:
            >>> keywords_list, keyword_type = self._get_mixed_keyword_google()
            >>> # Case 1: keywords_list = ["Python", "JS"], keyword_type = "google"
            >>> # Case 2: keywords_list = ["reddit.com", "github.com"], keyword_type = "warmup"
        """
    
        keywords_google_file = self.params.get("keywords_google_file", "").strip()
        warmup_websites_file = self.params.get("warmup_websites_file", "").strip()
    
        # ========== BUILD AVAILABLE SOURCES ==========
        sources = []
    
        # TEMPORARY DISABLEDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDĐ
        # if keywords_google_file and os.path.exists(keywords_google_file):
        #     sources.append("keywords_google")
    
        if warmup_websites_file and os.path.exists(warmup_websites_file):
            sources.append("warmup_websites")
    
        # No sources available
        if not sources:
            logger.warning("[MIXED KEYWORDS] No keywords or warmup files found")
            return [], None
    
        # ========== RANDOM CHOICE: SELECT 1 SOURCE ==========
        chosen_source = random.choice(sources)
        logger.info(f"[MIXED KEYWORDS] Randomly selected source: {chosen_source}")
    
        # ========== READ FROM CHOSEN SOURCE ONLY ==========
        result_list = []
        keyword_type = None
    
        if chosen_source == "keywords_google":
            # Read keywords file
            try:
                with open(keywords_google_file, 'r', encoding='utf-8') as f:
                    keywords = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
                if keywords:
                    result_list = keywords
                    keyword_type = "google"
                    logger.info(f"[MIXED KEYWORDS] Loaded {len(keywords)} keywords from Google file")
                else:
                    logger.warning("[MIXED KEYWORDS] Keywords file is empty")
        
            except Exception as e:
                logger.error(f"[MIXED KEYWORDS] Failed to read keywords Google file: {e}")
    
        elif chosen_source == "warmup_websites":
            # Read warmup file
            try:
                with open(warmup_websites_file, 'r', encoding='utf-8') as f:
                    urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
                if urls:
                    result_list = urls
                    keyword_type = "warmup"
                    logger.info(f"[MIXED KEYWORDS] Loaded {len(urls)} URLs from warmup file")
                else:
                    logger.warning("[MIXED KEYWORDS] Warmup file is empty")
        
            except Exception as e:
                logger.error(f"[MIXED KEYWORDS] Failed to read warmup file: {e}")
    
        # ========== SHUFFLE FOR RANDOMNESS ==========
        if result_list:
            random.shuffle(result_list)
            logger.info(f"[MIXED KEYWORDS] Type: {keyword_type}, Total items: {len(result_list)} (shuffled)")
    
        return result_list, keyword_type





    def _start_single_profile(self, profile_id):
        """
        Execute single mode (1 profile only) - Updated to pass proxy args to open, stop if proxy fail + required.

        Open profile, execute chains, then close

        Args:
            profile_id: Single profile ID to execute (STRING, not list)

        Returns:
            bool: Success status (UI/flow OK; proxy fail raises if required)
        """
        action_type = self.params.get("action_type", None)
        browse_youtube = self.params.get("browse_youtube", False)

        print("[GOLOGIN AUTO] ========== SINGLE MODE ==========")
        print("=" * 80)
        print(f"[SINGLE MODE] Profile ID: {profile_id}")
        print(f"[SINGLE MODE] Action type: {action_type}")
        print("=" * 80)
        print()

        # ========== PHASE 1: OPEN PROFILE (UPDATED) ==========
        print(f"[{profile_id}] PHASE 1: Opening profile...")

        try:
            # ========== CALL _open_profile() METHOD (UPDATED: PASS PROXY ARGS) ==========
            result = self._open_profile(profile_id, None)  # batch_num=None for single

            if not result['success']:
                print(f"[{profile_id}] ❌ Failed to open profile: {result['error']}")
                return False
            
            print(f"[{profile_id}] ✓ Profile opened successfully (MANUAL mode)")

        except ProxyAssignmentFailed:
            # New: Propagate proxy fail raise (stop entire action if required)
            print(f"[{profile_id}] Proxy assignment failed - stopping action")
            raise  # Re-raise to prepare_play

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

        driver = None  # ← Will be None for manual mode
        debugger_address = None  # ← Will be None for manual mode

        try:
            # ========== GET MIXED KEYWORD (NEW) ==========
            mixed_keyword, keyword_type = self._get_mixed_keyword_google()
            if action_type == "Youtube":
                if browse_youtube:
                    flow_iterator = YouTubeFlowAutoFactory.create_flow_iterator(
                        profile_id=profile_id,
                        parameters={**self.params, 'opened_profiles': [profile_id], 'max_workers' : 1, 'list_warmup_url' : mixed_keyword, 'keyword_type' : keyword_type},
                        log_prefix=f"[AUTO][{profile_id}]",
                        flow_type="browse",
                        controller = self.controller
                    )
                else:
                    flow_iterator = YouTubeFlowAutoFactory.create_flow_iterator(
                        profile_id=profile_id,
                        parameters={**self.params, 'opened_profiles': [profile_id], 'max_workers' : 1, 'list_warmup_url' : mixed_keyword, 'keyword_type' : keyword_type},
                        log_prefix=f"[AUTO][{profile_id}]",
                        flow_type="search",
                        controller = self.controller
                    )
            elif action_type == "Google":
                # TODO: Implement GoogleFlowAuto later
                print(f"[{profile_id}] Google flow not implemented for Auto Action yet")
                GoLoginProfileHelper.cleanup_profiles(profile_data, self.gologin_api, f"[{profile_id}]")
                return False
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
            # ===== CHECK PAUSE/BREAK FLAG (FIX) =====
            if self.controller and hasattr(self.controller, 'is_execution_stopped') and self.controller.is_execution_stopped:
                logger.info(f"[{profile_id}] ESC detected at start of loop - Stopping chain execution")
                break
            # =================================
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
    
            # ===== CHECK PAUSE/BREAK FLAG BEFORE EXECUTE (FIX) =====
            if self.controller and hasattr(self.controller, 'is_execution_stopped') and self.controller.is_execution_stopped:
                logger.info(f"[{profile_id}] ESC detected before executing chain {chain_num}")
                break
            # ===============================================

            # Execute chain
            try:
                success = flow_iterator.execute_next_chain()
                # ===== CHECK PAUSE/BREAK FLAG AFTER EXECUTE (FIX) =====
                if self.controller and hasattr(self.controller, 'is_execution_stopped') and self.controller.is_execution_stopped:
                    logger.info(f"[{profile_id}] ESC detected after executing chain {chain_num}")
                    break
                # ==============================================
        
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

        # ========== PHASE 4: CLOSE BROWSER WITH ALT+F4 (UPDATED) ==========
        logger.info(f"[{profile_id}] PHASE 4: Closing browser with Alt+F4...")

        try:
            # Bring profile to front          
            result_bring = GoLoginProfileHelper.bring_profile_to_front(
                profile_id,
                driver=driver,
                log_prefix=f"[{profile_id}]"
            )
            logger.info(f"[{profile_id}] PHASE 4: Closing browser with Alt+F4... result_bring {result_bring}")
            if result_bring:
                time.sleep(1)

                # Send Alt+F4
                print(f"[{profile_id}] Sending Alt+F4...")
                pyautogui.hotkey('alt', 'f4')
                time.sleep(2)  # Fixed: Added time.sleep for the random delay (original missed)

                print(f"[{profile_id}] ✓ Browser closed successfully")
                return True
            
            print(f"[{profile_id}] ❌ Failed to close browser")
            return False
        except Exception as e:
            print(f"[{profile_id}] ❌ Failed to close browser: {e}")
            import traceback
            traceback.print_exc()
            return False


    
    def set_variable(self, success):
        """Set variable with result"""
        variable = self.params.get("variable", "")
        if variable:
            GlobalVariables().set(variable, "true" if success else "false")
