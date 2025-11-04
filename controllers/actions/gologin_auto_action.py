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

from controllers.actions.flow_auto.youtube_flow_factory import YouTubeFlowAuto
from helpers.app_helpers import check_and_focus_window_by_title
# Import helpers
from helpers.gologin_profile_helper import GoLoginProfileHelper
from helpers.selenium_registry import register_selenium_driver, unregister_selenium_driver
from concurrent.futures import ThreadPoolExecutor, as_completed
from models.tmproxy_api import TMProxyAPI

class GoLoginAutoAction(BaseAction):
    """Handler for GoLogin Selenium Start Profile action"""
    
    def prepare_play(self):
        """Execute GoLogin Selenium Start Profile - Updated for per-profile proxy assignment with retry/stop logic."""
   
        try:
            # Get API token from variable name (original)
            api_key_variable = self.params.get("api_key_variable", "").strip()
            if not api_key_variable:
                print("[GOLOGIN START] Error: API key variable name is required")
                self.set_variable(False)
                return
        
            # Get API token value from GlobalVariables (original)
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
        
            # New: Proxy settings (check file existence, set require - default True for YouTube critical)
            proxy_file = self.params.get('proxy_file', '').strip()
            require_proxy = self.params.get('require_proxy', True)  # Stop action if proxy fail
            has_proxy_file = bool(proxy_file and os.path.exists(proxy_file))
            if not has_proxy_file:
                print("[GOLOGIN START] No proxy file provided or not found - proceeding without proxy assignment")
                print("[GOLOGIN START] Disabling require_proxy to avoid stop (local IP risk for YouTube views)")
                require_proxy = False  # Skip strict check/stop if no file (as per requirement)
        
            print(f"[GOLOGIN START] Proxy config: file={has_proxy_file}, require={require_proxy}")
        
            # ========== CHECK MULTI-THREADING ==========
            enable_threading = self.params.get("enable_threading", False)
        
            if enable_threading and len(profile_list) > 1:
                # PARALLEL MODE (original, but pass proxy args)
                print("[GOLOGIN START] ========== PARALLEL MODE ==========")
                self._start_parallel(profile_list, require_proxy, has_proxy_file)
                self.set_variable(True)  # Assume success if no raise
            else:
                # SEQUENTIAL MODE - Select 1 profile and start (original, but pass proxy args)
                print("[GOLOGIN START] ========== SEQUENTIAL MODE ==========")
                how_to_get = self.params.get("how_to_get", "Random")
                profile_id = GoLoginProfileHelper.select_profile(profile_list, how_to_get)
                print(f"[GOLOGIN START] Selected profile ID: {profile_id}")              
            
                # Start single profile (updated call)
                single_success = self._start_single_profile(profile_id, require_proxy, has_proxy_file)
                self.set_variable(single_success)
            
        except ProxyAssignmentFailed as e:
            # New: Catch proxy fail - stop entire action (critical for YouTube IP safety)
            print(f"[GOLOGIN START] ❌ Proxy assignment failed: {e}")
            print("[GOLOGIN START] Stopping action - no proxy means IP duplication risk, no YouTube views")
            self.set_variable(False)
            # Optional: Cleanup (stop all if partial)
            # self.gologin_api.stop_all_active_profiles()
            return
        except Exception as e:
            # Original except
            print(f"[GOLOGIN START] Error: {e}")
            import traceback
            traceback.print_exc()
            self.set_variable(False)

    
    def _assign_proxy_to_profile(self, profile_id, proxy_file):
        """
        Assign proxy to single profile from file - round-robin distribution with global session state.
        Start from next unused line (cycle), fallback to other lines if fail, mark used if success.
    
        Args:
            profile_id: Single profile to assign
            proxy_file: Path to proxy TXT file
    
        Returns:
            tuple: (bool success, str message) - success if assigned; message for log/error
        """
        log_prefix = f"[PROXY ASSIGN][{profile_id}]"
        print(f"{log_prefix} Starting proxy assignment with round-robin distribution")
    
        if not os.path.exists(proxy_file):
            return False, "Proxy file not found"
    
        # Load all configs (same as before)
        proxy_configs = []
        with open(proxy_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(';')
                if len(parts) != 3:
                    print(f"{log_prefix} Warning - Invalid format line {line_num}: {line}")
                    continue
                provider, proxy_type, api_key = [part.strip() for part in parts]
                if not provider or not proxy_type or not api_key:
                    print(f"{log_prefix} Warning - Empty values line {line_num}: {line}")
                    continue
                if proxy_type not in ['socks5', 'http', 'https']:
                    print(f"{log_prefix} Warning - Invalid type '{proxy_type}' line {line_num}")
                    continue
                proxy_configs.append({
                    'provider': provider.lower(),
                    'type': proxy_type,
                    'api_key': api_key,
                    'line_num': line_num
                })
    
        if not proxy_configs:
            return False, "No valid proxies in file"
    
        # Load global session state (per-run, non-persistent)
        current_index = GlobalVariables().get('session_proxy_index', 0)
        used_lines = GlobalVariables().get('session_used_lines', set())
    
        # Reset if all used (allow cycle for profiles > num_lines)
        if len(used_lines) >= len(proxy_configs):
            print(f"{log_prefix} All {len(proxy_configs)} lines used in session - resetting for new cycle")
            used_lines.clear()
            current_index = 0
            GlobalVariables().set('session_used_lines', set())
            GlobalVariables().set('session_proxy_index', 0)
    
        print(f"{log_prefix} Session state: index={current_index}, used={sorted(used_lines)}, available={len(proxy_configs) - len(used_lines)}")
    
        # Try unused lines first (start from current_index, cycle through unused)
        attempts = 0
        max_attempts = len(proxy_configs)  # Try all if needed (fallback to used if no unused work)
        tried_lines = set()
    
        while attempts < max_attempts:
            # Find next unused line (cycle from current_index)
            found_unused = False
            for offset in range(len(proxy_configs)):
                check_index = (current_index + offset) % len(proxy_configs)
                check_line_num = proxy_configs[check_index]['line_num']
                if check_line_num not in used_lines and check_index not in tried_lines:
                    config = proxy_configs[check_index]
                    found_unused = True
                    break
        
            if not found_unused:
                # All unused exhausted (or all tried this profile) - try used lines as fallback
                print(f"{log_prefix} No unused lines available - trying used lines as fallback")
                for offset in range(len(proxy_configs)):
                    check_index = (current_index + offset) % len(proxy_configs)
                    if check_index not in tried_lines:
                        config = proxy_configs[check_index]
                        found_unused = True  # Reuse var
                        break
        
            if not found_unused:
                break  # All lines tried this profile
        
            attempts += 1
            tried_lines.add(check_index)
            proxy_info = f"{config['provider']}:{config['type']}:...{config['api_key'][-8:]} (line {config['line_num']})"
            line_status = "used" if config['line_num'] in used_lines else "unused"
            print(f"{log_prefix} Attempt {attempts}/{max_attempts}: {proxy_info} [{line_status}]")
        
            try:
                # Get full proxy
                full_proxy = self._get_full_proxy_config(config)
                if not full_proxy:
                    print(f"{log_prefix} Failed to get details for {proxy_info} - continue to next")
                    time.sleep(1)
                    continue
            
                # Update GoLogin
                update_success, message = self.gologin_api.update_proxy_for_profiles([profile_id], full_proxy)
                if update_success:
                    # Success - mark this line as used, update index for next profile
                    used_line_num = config['line_num']
                    used_lines.add(used_line_num)
                    next_index = (check_index + 1) % len(proxy_configs)
                    GlobalVariables().set('session_used_lines', used_lines.copy())
                    GlobalVariables().set('session_proxy_index', next_index)
                    print(f"{log_prefix} ✓ Assigned {proxy_info} - marked used, next index={next_index}")
                    return True, f"Assigned {proxy_info}"
                else:
                    print(f"{log_prefix} API update failed for {proxy_info}: {message} - continue to next")
                    time.sleep(1)
                    continue
        
            except Exception as e:
                print(f"{log_prefix} Exception with {proxy_info}: {e} - continue to next")
                time.sleep(1)
                continue
    
        # All failed
        error_msg = f"All {attempts} attempts failed - no valid proxy assignable"
        print(f"{log_prefix} ❌ {error_msg}")
        return False, error_msg


            

    def _get_next_unused_proxy_index(self, proxy_configs, current_index, used_proxies_set):
        """
        Get next unused proxy config index, cycling from current_index.
        Skip used ones, return index or None if all used.
        """
        start_index = current_index
        checked = 0
        total = len(proxy_configs)
    
        while checked < total:
            candidate_index = (current_index + checked) % total
            candidate_line_num = proxy_configs[candidate_index]['line_num']
        
            if candidate_line_num not in used_proxies_set:
                print(f"GOLOGIN START: Selected unused proxy at index {candidate_index} (line {candidate_line_num})")
                return candidate_index
        
            checked += 1
    
        # All used
        print("GOLOGIN START: All proxies used, will reset on next success")
        return None  # Trigger reset
    

    def _get_full_proxy_config(self, proxy_config):
        """Helper to get full proxy details (host, port, user, pass) based on provider"""
        provider = proxy_config['provider']
        proxy_type = proxy_config['type']
        api_key = proxy_config['api_key']
    
        if provider == 'tmproxy':
            # Call static method in TMProxyAPI
            try:
                proxy_details = TMProxyAPI.get_proxy_static(api_key, proxy_type)  # Returns full: {'mode': , 'host': , 'port': , 'username': , 'password': }

                if proxy_details:
                    return proxy_details  
            except Exception as e:
                print(f"GOLOGIN START: TMProxy API error: {e}")
                return None
    
        # For other providers like 'proxyrack' - implement similar static call if needed
        elif provider == 'proxyrack':
            # Placeholder: Implement ProxyRackAPI.get_proxy_static(api_key, proxy_type) if exists
            print(f"GOLOGIN START: ProxyRack not implemented yet for {api_key}")
            return None
    
        else:
            print(f"GOLOGIN START: Unknown provider '{provider}', skipping")
            return None


            
    
    def _open_profile(self, profile_id, batch_num=None, require_proxy=False, has_proxy_file=False):
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
            require_proxy: If True, stop/raise if proxy assign fails (default False from params)
            has_proxy_file: If True, attempt proxy assignment (default False from params)

        Returns:
            dict: {'success': bool, 'profile_id': str, 'error': str or None} - success for UI open; proxy fail raises if required
        """
        log_prefix = f"[BATCH {batch_num}][{profile_id}]" if batch_num else f"[GOLOGIN AUTO][{profile_id}]"
        proxy_file = self.params.get('proxy_file', '').strip()
        remove_proxy = self.params.get('remove_proxy', False)
        
        if remove_proxy:
            self.gologin_api.remove_proxy_for_profiles(profile_id)

        # New proxy assignment phase (per-profile, before UI - only if has file)
        if has_proxy_file:
            print(f"{log_prefix} Assigning proxy from file: {proxy_file}")
            assign_success, _ = self._assign_proxy_to_profile(profile_id, proxy_file)
            if not assign_success:
                print(f"{log_prefix} Proxy assignment failed for all lines - checking require")
                if require_proxy:
                    raise ProxyAssignmentFailed(f"Cannot assign valid proxy for {profile_id} - all lines failed, IP duplication risk for YouTube views")
                else:
                    print(f"{log_prefix} Proceeding without proxy (not required)")
            else:
                print(f"{log_prefix} Proxy assigned successfully")
        else:
            print(f"{log_prefix} No proxy file - skipping assignment (using local IP)")

        # Original UI code (kept 100% unchanged, from refresh to end)
        try:
            # Import dependencies
            from pywinauto.application import Application
            from pywinauto.keyboard import send_keys
            import time
    
            print(f"{log_prefix} Opening profile via GoLogin App UI automation...")
    
            # ========== REFRESH FINGERPRINT (OPTIONAL) ==========
            refresh_fingerprint = self.params.get("refresh_fingerprint", False)
    
            if refresh_fingerprint:
                print(f"{log_prefix} Refreshing fingerprint...")
                success = self.gologin_api.refresh_fingerprint(profile_id)
        
                if success:
                    print(f"{log_prefix} ✓ Fingerprint refreshed")
                else:
                    print(f"{log_prefix} ⚠️ Failed to refresh fingerprint")        
    
            # ========== STEP 2: CONNECT TO GOLOGIN APP (OPTIMIZED WITH HELPER) ==========
            print(f"{log_prefix} Connecting to GoLogin app...")

            # Use helper to find and focus window (fast, no hang)
            success = check_and_focus_window_by_title("GoLogin")
            if not success:
                print(f"{log_prefix} ❌ GoLogin window not found via helper after focus attempt")
                return {
                    'success': False,
                    'profile_id': profile_id,
                    'error': 'GoLogin window not found'
                }

            # Window focused by helper, now get handle and connect (direct, no search hang)
            print(f"{log_prefix} Window focused by helper, connecting via handle...")

            app = None
            try:
                # Get current foreground window (should be GoLogin after helper focus)
                import win32gui
                hwnd = win32gui.GetForegroundWindow()
                window_title = win32gui.GetWindowText(hwnd)
    
                # Verify it's GoLogin (safety check)
                if "gologin" not in window_title.lower():
                    print(f"{log_prefix} ⚠️ Foreground window mismatch: '{window_title}', searching manually...")
                    # Fallback: Manual search for GoLogin hwnd
                    import pywinauto.findwindows as fw
                    windows = fw.find_windows(title_re=".*[Gg]o[Ll]ogin.*")
                    if not windows:
                        print(f"{log_prefix} ❌ No GoLogin window found in search")
                        return {
                            'success': False,
                            'profile_id': profile_id,
                            'error': 'GoLogin window not found after search'
                        }
                    hwnd = windows[0]  # Use first match
                    window_title = win32gui.GetWindowText(hwnd)
                    print(f"{log_prefix} Found window via search: '{window_title}'")
    
                # Connect by handle (direct, no title search hang)
                from pywinauto.application import Application
                app = Application(backend="uia").connect(handle=hwnd)
                print(f"{log_prefix} ✓ Connected via handle {hwnd} (title: '{window_title}')")

            except Exception as e:
                print(f"{log_prefix} ❌ Failed to connect by handle: {e}")
                import traceback
                traceback.print_exc()
                return {
                    'success': False,
                    'profile_id': profile_id,
                    'error': f'Failed to connect by handle: {e}'
                }

            if not app:
                print(f"{log_prefix} ❌ App object not created")
                return {
                    'success': False,
                    'profile_id': profile_id,
                    'error': 'App connection failed'
                }

            print(f"{log_prefix} ✓ Successfully connected to GoLogin app")

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


        

            # ========== STEP 3: SEND CTRL+F TO OPEN SEARCH ==========
            print(f"{log_prefix} Opening search with Ctrl+F...")
    
            try:              
                time.sleep(1)
        
                send_keys('^f')  # Ctrl+F
                print(f"{log_prefix} ✓ Sent Ctrl+F")
        
                time.sleep(2)
        
            except Exception as e:
                print(f"{log_prefix} ❌ Failed to send Ctrl+F: {e}")
                return {
                    'success': False,
                    'profile_id': profile_id,
                    'error': f'Failed to open search: {e}'
                }
    
            # ========== STEP 4: TYPE PROFILE ID + ENTER ==========
            print(f"{log_prefix} Typing profile ID...")
            import pyperclip
            try:
                # Clear existing text
                send_keys('^a{BACKSPACE}')
                time.sleep(0.5)

                # Type profile ID
                pyperclip.copy(profile_id)

                # Paste using Ctrl+V
                send_keys('^v')
                print(f"{log_prefix} ✓ Typed profile ID: {profile_id}")

                time.sleep(0.5)

                # Press Enter to search
                send_keys('{ENTER}')
                print(f"{log_prefix} ✓ Pressed Enter to search")

            except Exception as e:
                print(f"{log_prefix} ❌ Failed to type: {e}")
                return {
                    'success': False,
                    'profile_id': profile_id,
                    'error': f'Failed to type: {e}'
                }

            # ========== STEP 4.5: WAIT FOR RUN BUTTON (SMART TIMEOUT) ==========
            print(f"{log_prefix} Waiting for profile to appear (max 10s)...")

            run_button = None
            timeout = 10  # Max wait time in seconds
            check_interval = 0.5  # Check every 0.5 seconds
            elapsed = 0

            try:
                while elapsed < timeout:
                    try:
                        # Try to find Run button
                        run_button = gologin_window.child_window(title="Run", control_type="Button")
        
                        if run_button.exists():
                            print(f"{log_prefix} ✓ Profile found after {elapsed:.1f}s")
                            break  # Exit immediately when found!
    
                    except:
                        pass  # Button not found yet, continue waiting
    
                    time.sleep(check_interval)
                    elapsed += check_interval

                if run_button is None or not run_button.exists():
                    print(f"{log_prefix} ❌ Profile not found after {timeout}s timeout")
                    return {
                        'success': False,
                        'profile_id': profile_id,
                        'error': f'Profile not found after {timeout}s (invalid profile ID or search failed)'
                    }

            except Exception as e:
                print(f"{log_prefix} ⚠️ Error while waiting: {e}")
                # Continue anyway, try to click

            # ========== STEP 5: CLICK RUN BUTTON ==========
            print(f"{log_prefix} Clicking Run button...")

            try:
                if run_button and run_button.exists():
                    run_button.click_input()
                    print(f"{log_prefix} ✓ Clicked Run button")
    
                    time.sleep(3)  # Wait for profile to open
    
                    print(f"{log_prefix} ✓ Profile opened successfully")
                    print(f"{log_prefix} ℹ️  Browser running in MANUAL mode (no Selenium)")
    
                    return {
                        'success': True,
                        'profile_id': profile_id,
                        'error': None
                    }
                else:
                    print(f"{log_prefix} ❌ Run button not accessible")
                    return {
                        'success': False,
                        'profile_id': profile_id,
                        'error': 'Run button not accessible'
                    }
    
            except Exception as e:
                print(f"{log_prefix} ❌ Failed to click Run button: {e}")
                return {
                    'success': False,
                    'profile_id': profile_id,
                    'error': f'Failed to click: {e}'
                }


        except Exception as e:
            print(f"{log_prefix} ❌ Exception in _open_profile")
            print(f"{log_prefix} Error: {e}")
            import traceback
            traceback.print_exc()
    
            return {
                'success': False,
                'profile_id': profile_id,
                'error': str(e)
            }



        
    def _start_parallel(self, profile_list, require_proxy=False, has_proxy_file=False):
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
            require_proxy: If True, stop entire action if any proxy assign fails (default False)
            has_proxy_file: If True, attempt proxy assignment in open (default False)
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
        print(f"[PARALLEL MODE] Proxy config: require={require_proxy}, has_file={has_proxy_file}")
        print("=" * 80)

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
                        result = self._open_profile(profile_id, batch_num, require_proxy, has_proxy_file)
            
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
                    except ProxyAssignmentFailed:
                        # New: If proxy fail raised, cleanup partial opened in this batch, then propagate stop
                        print(f"[BATCH {batch_num}] Proxy fail in thread {profile_id} - cleanup partial and stop action")
                        opened_so_far = [pid for pid, data in profile_data.items() if data.get('status') == 'opened']
                        if opened_so_far:
                            self._close_profiles_batch(opened_so_far)  # Assume helper method for close
                        raise  # Propagate to prepare_play
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
    
            flow_iterators = {}  # profile_id → flow_iterator
    
            for profile_id in opened_profiles:              
        
                try:
                    if action_type == "Youtube":
                        if browse_youtube:
                            flow_iterator = YouTubeFlowAuto.create_flow_iterator(
                                profile_id=profile_id,
                                parameters=self.params,
                                log_prefix=f"[BATCH {batch_num}][{profile_id}]",
                                flow_type="browse"
                            )
                        else:
                            flow_iterator = YouTubeFlowAuto.create_flow_iterator(
                                profile_id=profile_id,
                                parameters=self.params,
                                log_prefix=f"[BATCH {batch_num}][{profile_id}]"
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
    
            # ========== PHASE 4: CLOSE BROWSERS WITH ALT+F4 (UPDATED) ==========
            print(f"[BATCH {batch_num}] PHASE 4: Closing {len(opened_profiles)} browsers with Alt+F4 (FIFO order)...")
            print(f"[BATCH {batch_num}] Order: {opened_profiles}")

            closed_count = 0
            for profile_id in opened_profiles:  # opened_profiles đã theo thứ tự FIFO
                try:
                    log_prefix = f"[BATCH {batch_num}][{profile_id}]"
    
                    # Bring profile to front
                    print(f"{log_prefix} Bringing window to front...")
                    GoLoginProfileHelper.bring_profile_to_front(
                        profile_id,
                        driver=profile_data[profile_id]['driver'],
                        log_prefix=log_prefix
                    )
                    time.sleep(1)
    
                    # Send Alt+F4
                    print(f"{log_prefix} Sending Alt+F4...")
                    pyautogui.hotkey('alt', 'f4')
                    time.sleep(2)
    
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
        import pyautogui
        import time

        closed_count = 0
        for profile_id in profiles:
            try:
                log_prefix = f"[CLEANUP][{profile_id}]"
                # Bring to front
                GoLoginProfileHelper.bring_profile_to_front(
                    profile_id,
                    driver=None,  # Manual mode
                    log_prefix=log_prefix
                )
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



    def _start_single_profile(self, profile_id, require_proxy=False, has_proxy_file=False):
        """
        Execute single mode (1 profile only) - Updated to pass proxy args to open, stop if proxy fail + required.

        Open profile, execute chains, then close

        Args:
            profile_id: Single profile ID to execute (STRING, not list)
            require_proxy: If True, stop entire action if proxy assign fails (default False)
            has_proxy_file: If True, attempt proxy assignment in open (default False)

        Returns:
            bool: Success status (UI/flow OK; proxy fail raises if required)
        """
        action_type = self.params.get("action_type", None)
        browse_youtube = self.params.get("browse_youtube", False)

        print("[GOLOGIN AUTO] ========== SINGLE MODE ==========")
        print("=" * 80)
        print(f"[SINGLE MODE] Profile ID: {profile_id}")
        print(f"[SINGLE MODE] Action type: {action_type}")
        print(f"[SINGLE MODE] Proxy config: require={require_proxy}, has_file={has_proxy_file}")
        print("=" * 80)
        print()

        # ========== PHASE 1: OPEN PROFILE (UPDATED) ==========
        print(f"[{profile_id}] PHASE 1: Opening profile...")

        try:
            # ========== CALL _open_profile() METHOD (UPDATED: PASS PROXY ARGS) ==========
            result = self._open_profile(profile_id, None, require_proxy, has_proxy_file)  # batch_num=None for single

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
            if action_type == "Youtube":
                if browse_youtube:
                    flow_iterator = YouTubeFlowAuto.create_flow_iterator(
                        profile_id=profile_id,
                        parameters=self.params,
                        log_prefix=f"[AUTO][{profile_id}]",
                        flow_type="browse"
                    )
                else:
                    flow_iterator = YouTubeFlowAuto.create_flow_iterator(
                        profile_id=profile_id,
                        parameters=self.params,
                        log_prefix=f"[AUTO][{profile_id}]"
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

        # ========== PHASE 4: CLOSE BROWSER WITH ALT+F4 (UPDATED) ==========
        print(f"[{profile_id}] PHASE 4: Closing browser with Alt+F4...")

        try:
            # Bring profile to front
            print(f"[{profile_id}] Bringing window to front...")
            GoLoginProfileHelper.bring_profile_to_front(
                profile_id,
                driver=profile_data[profile_id]['driver'],
                log_prefix=f"[{profile_id}]"
            )
            time.sleep(random.uniform(3, 8))

            # Send Alt+F4
            print(f"[{profile_id}] Sending Alt+F4...")
            pyautogui.hotkey('alt', 'f4')
            time.sleep(random.uniform(2, 5))  # Fixed: Added time.sleep for the random delay (original missed)

            print(f"[{profile_id}] ✓ Browser closed successfully")
            return True

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

class ProxyAssignmentFailed(Exception):
    """Custom exception to stop action if no proxy can be assigned for a profile."""
    pass
