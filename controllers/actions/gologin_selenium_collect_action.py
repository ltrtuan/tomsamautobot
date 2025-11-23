# controllers/actions/gologin_selenium_collect_action.py

from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from models.gologin_api import get_gologin_api
import random
import os
import time
from exceptions.gologin_exceptions import ProxyAssignmentFailed

# Import helpers
from helpers.gologin_profile_helper import GoLoginProfileHelper
from helpers.selenium_registry import register_selenium_driver, unregister_selenium_driver

# ========== IMPORT WEBSITE MANAGER ==========
from helpers.website_manager import (
    save_collected_url,
    get_random_warmup_url
)

class GoLoginSeleniumCollectAction(BaseAction):
    """Handler for GoLogin Selenium Collect (Warm Up) action"""
    
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
            
            # ========== GET PROFILE LIST USING HELPER ==========
            success, result = GoLoginProfileHelper.get_profile_list(
                self.params, api_token, "[GOLOGIN WARMUP]"
            )
            
            if not success:
                print(f"[GOLOGIN WARMUP] ✗ {result}")
                self.set_variable(False)
                return
            
            profile_list = result
            print(f"[GOLOGIN WARMUP] Total profiles to warm up: {len(profile_list)}")
            
             # ========== INITIALIZE WARMUP CACHE (ONCE PER ACTION) ==========
            warmup_file = self.params.get("warmup_websites_file", "").strip()
            if warmup_file:
                print(f"[GOLOGIN WARMUP] Initializing warmup websites cache from: {warmup_file}")
                # This call loads URLs into cache (thread-safe, happens once)
                test_url = get_random_warmup_url(warmup_file)
                if test_url:
                    print(f"[GOLOGIN WARMUP] ✓ Warmup cache initialized (sample URL: {test_url[:50]}...)")
                else:
                    print(f"[GOLOGIN WARMUP] ⚠ Warmup cache empty (no URLs loaded)")
            else:
                print(f"[GOLOGIN WARMUP] No warmup file specified, will use keywords/default websites")
            # ==================================================================
          
            
            # ========== CHECK MULTI-THREADING ==========
            enable_threading = self.params.get("enable_threading", False)
            
            if enable_threading and len(profile_list) > 1:
                # PARALLEL MODE
                print("[GOLOGIN WARMUP] ========== PARALLEL MODE ==========")
                self._warmup_parallel(profile_list, api_token)
            else:
                # SEQUENTIAL MODE - Select 1 profile and warm up
                print("[GOLOGIN WARMUP] ========== SEQUENTIAL MODE ==========")
                how_to_get = self.params.get("how_to_get", "Random")
                profile_id = GoLoginProfileHelper.select_profile(profile_list, how_to_get)
                print(f"[GOLOGIN WARMUP] Selected profile ID: {profile_id}")
                
                # Warm up single profile
                success = self._warmup_single_profile(profile_id, api_token)
                self.set_variable(success)
                
        except ProxyAssignmentFailed as e:
            # Stop entire action if proxy critical
            print(f"[GOLOGIN WARMUP] ❌ Proxy assignment failed: {e}")
            print("[GOLOGIN WARMUP] Stopping action - no proxy means IP duplication risk")
            self.set_variable(False)
            return
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Error: {e}")
            import traceback
            traceback.print_exc()
            self.set_variable(False)
    
    

    
    def _warmup_single_profile(self, profile_id, api_token):
        """Warm up a single profile - can be called from thread"""
        driver = None
        gologin = None
        # ========== THÊM: Track warmup success ==========
        warmup_success = False
        cleanup_success = False
        # ========== TRACK START TIME ==========
        profile_start_time = time.time()
        # ====================================
    
        try:
            print(f"\n[GOLOGIN WARMUP] [{profile_id}] Starting warm up...")
            # Kill zombie processes via API (includes force kill + cleanup)
            print(f"[GOLOGIN WARMUP] [{profile_id}] Cleaning up zombie processes...")
            # Get GoLogin API instance
            gologin = get_gologin_api(api_token)
                
                
            # ========== ADD PROXY LOGIC HERE (PER-PROFILE) ==========
            proxy_file = self.params.get('proxy_file', '').strip()
            remove_proxy = self.params.get('remove_proxy', False)
        
        
            # Phase 1: Remove proxy if enabled
            if remove_proxy:
                try:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] Removing proxy...")
                    gologin.remove_proxy_for_profiles(profile_id)
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Proxy removed")
                except Exception as e:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ Remove proxy error: {e}")
        
            # Phase 2: Assign proxy from file
            if proxy_file and os.path.exists(proxy_file):
                try:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] Assigning proxy from file...")
                
                    assign_success, message = GoLoginProfileHelper.assign_proxy_to_profile(
                        profile_id,
                        proxy_file,
                        gologin,
                        True,
                        log_prefix=f"[WARMUP PROXY][{profile_id}]"
                    )
                
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Proxy assigned: {message}")
                    
                except ProxyAssignmentFailed as e:
                    # Stop warmup for this profile if proxy required
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ❌ Proxy assignment failed: {e}")
                    print(f"[GOLOGIN WARMUP] [{profile_id}] Stopping warmup - proxy required but failed")
                    raise
                except Exception as e:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ Proxy assignment error: {e}")
            elif proxy_file:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ Proxy file not found: {proxy_file}")
        
            # ========== END PROXY LOGIC ==========
        
            # Get options
            refresh_fingerprint = self.params.get("refresh_fingerprint", False)
            headless = self.params.get("headless", False)        
          
        
            # Refresh fingerprint if requested
            if refresh_fingerprint:
                print(f"[GOLOGIN WARMUP] [{profile_id}] Refreshing fingerprint...")
                success = gologin.refresh_fingerprint(profile_id)
                if success:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Fingerprint refreshed")
                else:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ Failed to refresh fingerprint")
        
            # Start profile with extra params
            print(f"[GOLOGIN WARMUP] [{profile_id}] Starting profile...")
            if headless:
                extra_params = [
                    "--headless=new",                   
                    "--mute-audio",
                    "--disable-background-networking",                   
                    "--enable-features=NetworkService",                 
                    "--disk-cache-size=0",
                    "--media-cache-size=0",
                    "--disable-features=CookiesWithoutSameSiteMustBeSecure",
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
        
            success, debugger_address = gologin.start_profile(profile_id, extra_params=extra_params)
            if not success:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ Failed to start profile: {debugger_address}")
                return False
        
            print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Profile started: {debugger_address}")
        
            # Connect Selenium using helper
            driver = GoLoginProfileHelper.connect_selenium(debugger_address, "[GOLOGIN WARMUP]")
            if not driver:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ Failed to connect Selenium")
                gologin.stop_profile(profile_id)
                return False
        
            # Register driver for auto-cleanup
            register_selenium_driver(driver, profile_id)
            
           
            # Check and fix crashed tabs FIRST
            if not GoLoginProfileHelper.check_and_fix_crashed_tabs(driver, debugger_address, "[GOLOGIN WARMUP]", use_window_lock=False):
                print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ Could not fix crashed tabs")
                driver.quit()
                gologin.stop_profile(profile_id)
                return False
        
            # Clean up old tabs
            print(f"[GOLOGIN WARMUP] [{profile_id}] Checking browser tabs...")
            GoLoginProfileHelper.cleanup_browser_tabs(driver, "[GOLOGIN WARMUP]")
        
            # ========== LOAD WEBSITES - RANDOM CHOICE BETWEEN KEYWORDS OR WARMUP ==========
            warmup_file = self.params.get("warmup_websites_file", "").strip()

            # Random choice: use keywords OR warmup (not mix)
            if warmup_file and random.choice([True, False]):  # 50% chance to use warmup
                # Option 1: Use warmup cache
                print(f"[GOLOGIN WARMUP] [{profile_id}] 🎲 Randomly selected: WARMUP CACHE")
                websites = []
    
                for _ in range(20):  # Get 20 URLs from cache
                    url = get_random_warmup_url()
                    if url:
                        websites.append(url)
    
                if not websites:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ Warmup cache empty, falling back to keywords...")
                    websites = GoLoginProfileHelper.load_websites(self.params, "[GOLOGIN WARMUP]")
                else:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Loaded {len(websites)} URLs from warmup cache")

            else:
                # Option 2: Use keywords/default websites
                print(f"[GOLOGIN WARMUP] [{profile_id}] 🎲 Randomly selected: KEYWORDS/DEFAULT")
                websites = GoLoginProfileHelper.load_websites(self.params, "[GOLOGIN WARMUP]")

            if not websites:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ No websites to browse")
                driver.quit()
                time.sleep(5)
                gologin.stop_profile(profile_id)
                return False

            print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Total websites for browsing: {len(websites)}")
            # =========================================================================

        
            # Load keywords for search (optional)
            keywords = GoLoginProfileHelper.load_keywords(self.params, "[GOLOGIN WARMUP]")
            if keywords:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Loaded {len(keywords)} search keywords")
        
            # ========== CALCULATE REMAINING TIME ==========
            duration_minutes = self.params.get("duration_minutes", "5")
            try:
                duration_minutes = float(duration_minutes)
            except:
                duration_minutes = 5
        
            target_total_seconds = int(duration_minutes * 60)
        
            # Calculate time already spent
            elapsed_overhead = time.time() - profile_start_time
        
            # Calculate remaining time for browsing
            remaining_seconds = max(30, target_total_seconds - int(elapsed_overhead))
        
            print(f"[GOLOGIN WARMUP] [{profile_id}] Target duration: {duration_minutes} min ({target_total_seconds}s)")
            print(f"[GOLOGIN WARMUP] [{profile_id}] Overhead: {elapsed_overhead:.1f}s")
            print(f"[GOLOGIN WARMUP] [{profile_id}] Browsing time: {remaining_seconds}s ({remaining_seconds/60:.1f} min)")
            # ============================================
        
            # Browse websites
            self._browse_websites(driver, websites, remaining_seconds, keywords, profile_id)
        
            # Wait for async operations to complete
            print(f"[GOLOGIN WARMUP] [{profile_id}] Waiting for browser data to settle...")
            time.sleep(5)
        
            # ========== VERIFY TOTAL DURATION ==========
            total_elapsed = time.time() - profile_start_time
            print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Total profile duration: {total_elapsed/60:.1f} minutes")
            # =========================================
            # ========== THÊM: Mark success nếu warmup pass ==========
            warmup_success = True
            return True
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            warmup_success = False
            return False
    
        finally:
            # ========== USE CENTRALIZED CLEANUP ==========
            print(f"[GOLOGIN WARMUP] [{profile_id}] Running cleanup...")
    
            if driver and gologin:
                try:
                    # ========== THAY ĐỔI: Lấy cleanup result ==========
                    cleanup_results = GoLoginProfileHelper.cleanup_profiles(
                        profile_data={"profile_id": profile_id, "driver": driver},
                        gologin_api=gologin,
                        log_prefix="[GOLOGIN WARMUP]"
                    )
                
                    # Check cleanup success for this profile
                    cleanup_success = cleanup_results.get(profile_id, False)
                
                    if not cleanup_success:
                        print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ Cleanup returned False")
                    # ==================================================
                
                except Exception as cleanup_err:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ Cleanup error: {cleanup_err}")
                    import traceback
                    traceback.print_exc()
                    cleanup_success = False
            return (warmup_success, cleanup_success)
    
    def _warmup_parallel(self, profile_list, api_token):
        """Warm up multiple profiles in parallel using threading"""
        from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
        import math
    
        max_workers_str = self.params.get("max_workers", "3")
        try:
            max_workers = int(max_workers_str)
        except:
            max_workers = 2
        max_workers = min(max_workers, len(profile_list))

        # ========== RANDOMIZE PROFILE LIST IF NEEDED ==========
        how_to_get = self.params.get("how_to_get", "Random")
    
        if how_to_get == "Random":
            print(f"[GOLOGIN WARMUP] how_to_get = Random → Creating randomized list")
            profile_list = GoLoginProfileHelper.create_randomized_profile_list(
                original_profile_list=profile_list,
                max_workers=max_workers,
                log_prefix="[GOLOGIN WARMUP]"
            )
        else:
            print(f"[GOLOGIN WARMUP] how_to_get = {how_to_get} → Using original list order")    
    
       
        print(f"[GOLOGIN WARMUP] Warming up {len(profile_list)} profiles with {max_workers} parallel threads")
    
        # Calculate timeout per profile
        duration_minutes = self.params.get("duration_minutes", "5")
        try:
            duration_minutes = float(duration_minutes)
        except:
            duration_minutes = 5
    
        timeout_per_profile = int((duration_minutes + 5) * 60)
        batches = math.ceil(len(profile_list) / max_workers)
    
        # ========== THÊM: Track failed + cleanup failures ==========
        results = []
        completed_profiles = []
        failed_profiles = []  # ← THÊM: Track failed profile IDs
        timeout_profiles = []
        connection_error_profiles = []
        cleanup_failed_profiles = []  # ← THÊM: Track cleanup failures
        # ===========================================================
    
        executor = ThreadPoolExecutor(max_workers=max_workers)
    
        try:
            # Submit all profiles to thread pool
            future_to_profile = {}
            for i, profile_id in enumerate(profile_list):
                if i > 0:
                    time.sleep(2)
            
                future = executor.submit(
                    self._warmup_single_profile,
                    profile_id,
                    api_token
                )
                future_to_profile[future] = profile_id
                print(f"[GOLOGIN WARMUP] Submitted thread {i+1}/{len(profile_list)}: {profile_id}")
                # Cooling period every max_workers profiles
                if (i + 1) % max_workers == 0:
                    print("[GOLOGIN WARMUP] ⏸ Cooling down for 20 seconds...")
                    time.sleep(20)
            # Process results
            for future in as_completed(future_to_profile):
                profile_id = future_to_profile[future]
            
                try:
                    # ========== THAY ĐỔI: Nhận cả cleanup result ==========
                    result = future.result(timeout=30)
                
                    # Check if result is tuple (warmup_success, cleanup_result)
                    if isinstance(result, tuple):
                        warmup_success, cleanup_result = result
                    else:
                        # Fallback for old return format
                        warmup_success = result
                        cleanup_result = None
                
                    results.append(warmup_success)
                    completed_profiles.append(profile_id)
                
                    if warmup_success:
                        print(f"[GOLOGIN WARMUP] ✓ Profile {profile_id} completed successfully")
                    else:
                        print(f"[GOLOGIN WARMUP] ✗ Profile {profile_id} failed")
                        failed_profiles.append(profile_id)  # ← THÊM
                
                    # ========== THÊM: Check cleanup result ==========
                    if cleanup_result is not None and not cleanup_result:
                        cleanup_failed_profiles.append(profile_id)
                        print(f"[GOLOGIN WARMUP] ⚠ Profile {profile_id} cleanup failed")
                    # ===============================================
                
                except TimeoutError:
                    print(f"[GOLOGIN WARMUP] ✗ Profile {profile_id} TIMEOUT")
                    results.append(False)
                    timeout_profiles.append(profile_id)
                    failed_profiles.append(profile_id)  # ← THÊM
                
                except Exception as e:
                    error_msg = str(e)
                    if any(err in error_msg for err in ["Max retries", "Connection refused", "ConnectionResetError"]):
                        print(f"[GOLOGIN WARMUP] ✗ Profile {profile_id} lost connection (browser crashed)")
                        connection_error_profiles.append(profile_id)
                    else:
                        print(f"[GOLOGIN WARMUP] ✗ Profile {profile_id} exception: {e}")
                        failed_profiles.append(profile_id)  # ← THÊM
                
                    results.append(False)
                    completed_profiles.append(profile_id)
                    
                except ProxyAssignmentFailed as e:
                    # Stop toàn bộ parallel execution
                    print(f"[GOLOGIN WARMUP] ❌ CRITICAL: Proxy failed - {e}")
                    print("[GOLOGIN WARMUP] Cancelling all remaining profiles...")
        
                    # Cancel pending futures
                    for pending_future in future_to_profile:
                        if not pending_future.done():
                            pending_future.cancel()
        
                    # Shutdown executor
                    executor.shutdown(wait=False)
        
                    # Re-raise để stop action
                    raise ProxyAssignmentFailed(f"Proxy assignment critical failure - stopping action")
    
        except Exception as e:
            print(f"[GOLOGIN WARMUP] ⚠ Parallel execution error: {e}")
            import traceback
            traceback.print_exc()
    
        finally:
            # Force shutdown thread pool
            print(f"[GOLOGIN WARMUP] Forcing thread pool shutdown...")
            try:
                executor.shutdown(wait=False)
                print(f"[GOLOGIN WARMUP] ✓ Thread pool shut down")
            except Exception as shutdown_err:
                print(f"[GOLOGIN WARMUP] ⚠ Shutdown error: {shutdown_err}")
        
            time.sleep(3)
        
            import threading
            active_count = threading.active_count()
            if active_count > 1:
                print(f"[GOLOGIN WARMUP] ⚠ Warning: {active_count-1} threads still active")
    
        # ========== SUMMARY - UPDATED VERSION ==========
        success_count = sum(results) if results else 0
        failed_count = len(failed_profiles)
    
        print(f"\n[GOLOGIN WARMUP] ========== SUMMARY ==========")
        print(f"[GOLOGIN WARMUP] Total: {len(profile_list)} profiles")
        print(f"[GOLOGIN WARMUP] Completed: {len(completed_profiles)}")
        print(f"[GOLOGIN WARMUP] Success: {success_count}")
        print(f"[GOLOGIN WARMUP] Failed: {failed_count}")
    
        # ========== THÊM: List failed profile IDs ==========
        if failed_profiles:
            print(f"[GOLOGIN WARMUP] Failed Profile IDs:")
            for pid in failed_profiles:
                print(f"[GOLOGIN WARMUP]   - {pid}")
        # ==================================================
    
        print(f"[GOLOGIN WARMUP] Timeout: {len(timeout_profiles)}")
        print(f"[GOLOGIN WARMUP] Connection Errors: {len(connection_error_profiles)}")
    
        # ========== THÊM: List cleanup failures ==========
        if cleanup_failed_profiles:
            print(f"[GOLOGIN WARMUP] Profiles Stop Failed: {len(cleanup_failed_profiles)}")
            for pid in cleanup_failed_profiles:
                print(f"[GOLOGIN WARMUP]   - {pid}")
        # ================================================
    
        print(f"[GOLOGIN WARMUP] ============================\n")
    
        self.set_variable(success_count > 0)

    
    
    
    def _search_on_site(self, driver, keywords):
        """Perform search if on Google or YouTube"""
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            from selenium.webdriver.common.keys import Keys
            import platform
    
            if not keywords:
                return False           
    
            # Random pick keyword
            keyword = random.choice(keywords)
            print(f"[GOLOGIN WARMUP] Searching for: '{keyword}'")
    
            # Detect OS for correct modifier key (Ctrl for Windows/Linux, Command for Mac)
            cmd_ctrl = Keys.COMMAND if platform.system() == 'Darwin' else Keys.CONTROL
    
            # Use Selenium Actions to interact directly with the browser
            actions = ActionChains(driver)
    
            # Focus address bar (Ctrl+L or Cmd+L)
            actions.key_down(cmd_ctrl).send_keys('l').key_up(cmd_ctrl).perform()
            time.sleep(0.3)
    
            # Type keyword directly using Selenium (no clipboard needed)
            actions.send_keys(keyword).perform()
    
            # Wait before Enter
            wait_before_enter = random.uniform(1, 2)
            time.sleep(wait_before_enter)
    
            # Press Enter
            actions.send_keys(Keys.ENTER).perform()
    
            # Wait for page load
            page_load_wait = random.uniform(3, 5)          
            time.sleep(page_load_wait)
            return True

        except Exception as e:
            print(f"[GOLOGIN WARMUP] Error searching: {e}")
            return False



        
    def _browse_websites(self, driver, websites, total_seconds, keywords=None, profile_id=""):
        """
        Browse websites with human-like actions - IMPROVED VERSION
        - Detect bot challenges (Cloudflare, reCAPTCHA, etc.)
        - Detect HTTP errors (404, 500, 403, etc.)
        - Skip to next website on error
        """
        try:
            from helpers.selenium_actions import SeleniumHumanActions
            from selenium.common.exceptions import TimeoutException
        
            print(f"[GOLOGIN WARMUP {profile_id}] Starting browsing for {total_seconds}s...")
        
            human = SeleniumHumanActions(driver)
            how_to_get_websites = self.params.get('how_to_get_websites', 'Random')
            
            start_time = time.time()
            visit_count = 0
            action_count = 0
            current_index = 0
            ssl_error_sites = set()
            blocked_sites = set()  # ← NEW: Track blocked/error sites
        
            while True:
                # ========== CHECK TIME LIMIT ==========
                elapsed = time.time() - start_time
                if elapsed > total_seconds:
                    print(f"[GOLOGIN WARMUP {profile_id}] Browsing completed after {int(elapsed)}s")
                    break
            
                # ========== CHECK DRIVER VALIDITY ==========
                try:
                    driver.current_url
                except Exception as session_err:
                    error_msg = str(session_err).lower()
                    if "invalid session" in error_msg or "session deleted" in error_msg:
                        print(f"[GOLOGIN WARMUP {profile_id}] Driver session invalid, stopping browse")
                        break
            
                # ========== SELECT NEXT WEBSITE ==========
                if how_to_get_websites == "Sequential (by loop)":
                    url = websites[current_index % len(websites)]
                    current_index += 1
                else:
                    url = random.choice(websites)              
                
                 
                # ========== SKIP BLOCKED/ERROR SITES ==========
                if url in ssl_error_sites or url in blocked_sites:
                    print(f"[GOLOGIN WARMUP {profile_id}] Skipping previously failed site: {url}")
                    continue
            
                # ========== NAVIGATE TO URL ==========
                page_loaded_successfully = False
            
                try:
                    print(f"[GOLOGIN WARMUP {profile_id}] ({visit_count+1}) Navigating to {url}")
                    driver.set_page_load_timeout(15)
                
                    try:
                        driver.get(url)
                        time.sleep(1)
                      
                        # self._capture_page_screenshot(driver, collect_file, profile_id)
                        # ========== CHECK FOR CONNECTION ERRORS ==========
                        page_source = driver.page_source.lower()
                        current_url = driver.current_url
                    
                        if ("err_connection_timed_out" in page_source or
                            "this site can't be reached" in page_source or
                            "took too long to respond" in page_source or
                            "chrome-error" in current_url):
                        
                            print(f"[GOLOGIN WARMUP {profile_id}] ERR_CONNECTION_TIMED_OUT: {url}")
                            ssl_error_sites.add(url)
                            continue
                    
                        print(f"[GOLOGIN WARMUP {profile_id}] Page loaded: {url}")
                        page_loaded_successfully = True
                
                    except TimeoutException:
                        print(f"[GOLOGIN WARMUP {profile_id}] Page load timeout: {url}")
                    
                        # Try to stop loading and check page
                        try:
                            driver.execute_script("window.stop()")
                            time.sleep(0.5)
                        
                            page_source = driver.page_source.lower()
                            current_url = driver.current_url
                        
                            if ("err_connection_timed_out" in page_source or
                                "this site can't be reached" in page_source or
                                "chrome-error" in current_url):
                            
                                print(f"[GOLOGIN WARMUP {profile_id}] Connection error after timeout: {url}")
                                ssl_error_sites.add(url)
                                continue
                        
                            if current_url and current_url not in ("data:,", "about:blank"):
                                print(f"[GOLOGIN WARMUP {profile_id}] Page partially loaded, continuing...")
                            
                                # Scroll to trigger content load
                                try:
                                    driver.execute_script("window.scrollBy(0, 200)")
                                    time.sleep(0.5)
                                except:
                                    pass
                            
                                page_loaded_successfully = True
                            else:
                                continue
                    
                        except Exception as stop_err:
                            pass
            
                except Exception as nav_err:
                    error_msg = str(nav_err).lower()
                
                    # SSL/Connection errors
                    if any(kw in error_msg for kw in ["ssl", "certificate", "connection", "net::err"]):
                        print(f"[GOLOGIN WARMUP {profile_id}] Connection error: {url}")
                        ssl_error_sites.add(url)
                        print(f"[GOLOGIN WARMUP {profile_id}] Skipping to next website...")
                        time.sleep(1)
                        continue
            
                # ========== SKIP IF PAGE FAILED TO LOAD ==========
                if not page_loaded_successfully:
                    ssl_error_sites.add(url)
                    print(f"[GOLOGIN WARMUP {profile_id}] Skipping to next website...")
                    time.sleep(1)
                    continue
            
                # ========== DETECT BOT CHALLENGES & HTTP ERRORS ==========
                is_blocked, block_reason = self._detect_page_issues(driver, url, profile_id)
            
                if is_blocked:
                    print(f"[GOLOGIN WARMUP {profile_id}] ⚠️ Site blocked/error: {block_reason}")
                    blocked_sites.add(url)
                    print(f"[GOLOGIN WARMUP {profile_id}] Skipping to next website...")
                    time.sleep(2)
                    continue
            
                # ========== PAGE IS OK - PROCEED WITH NORMAL BROWSING ==========
                visit_count += 1
                time.sleep(random.uniform(3, 5))
            
                # Auto accept cookie consent
                try:
                    if human.accept_cookie_consent():
                        print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Accepted cookie consent")
                        time.sleep(random.uniform(1, 2))
                except:
                    pass
            
                # Close popups
                try:
                    if human.close_popups():
                        print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Closed popup")
                        time.sleep(random.uniform(0.5, 1.0))
                except:
                    pass
            
                
                # rand_gg = random.random()
                # if rand_gg < 0.35:
                #     # Perform search if Google/YouTube - Input keyword to address bar
                #     self._search_on_site(driver, keywords)
                #     self._perform_deeper_clicks(driver, human, start_time, total_seconds, profile_id)
                    
                # Random human-like actions
                actions_on_page = random.randint(1, 3)
                for _ in range(actions_on_page):
                    if time.time() - start_time >= total_seconds:
                        break
                    try:
                        human.execute_random_action()
                        action_count += 1
                        time.sleep(random.uniform(1.5, 3.0))
                    except:
                        break
            
                # ========== IMPROVED DEEPER CLICK LOGIC ==========
                time.sleep(random.uniform(2.0, 5.0))

                remaining_seconds = time.time() - start_time
                if remaining_seconds < total_seconds:
                    next_action = random.choice([1,2])
                    if next_action == 1:
                        self._perform_deeper_clicks(driver, human, start_time, total_seconds, profile_id)
                    else:
                        self._browse_websites(driver, websites, remaining_seconds, keywords, profile_id)
                # ==============================================
            
                # Stay on page
                stay_time = random.uniform(2.0, 5.0)
                print(f"[GOLOGIN WARMUP] [{profile_id}] Staying on page for {stay_time:.1f}s...")
                time.sleep(stay_time)
            
                if time.time() - start_time >= total_seconds:
                    break

        
            print(f"[GOLOGIN WARMUP {profile_id}] Visited {visit_count} pages, performed {action_count} actions")
            print(f"[GOLOGIN WARMUP {profile_id}] SSL error sites: {len(ssl_error_sites)}")
            print(f"[GOLOGIN WARMUP {profile_id}] Blocked sites: {len(blocked_sites)}")
    
        except Exception as e:
            print(f"[GOLOGIN WARMUP {profile_id}] Error during browsing: {e}")
            import traceback
            traceback.print_exc()
            
    


    def _detect_page_issues(self, driver, url, profile_id=""):
        """
        Detect bot challenges, HTTP errors, and blocked pages
        Uses STRICT context-based detection to avoid false positives
    
        Returns:
            tuple: (is_blocked: bool, reason: str)
        """
        try:
            page_source = driver.page_source.lower()
            page_title = driver.title.lower()
            current_url = driver.current_url.lower()          
            # ========== HTTP ERRORS (ALWAYS STRICT) ==========
            # These are reliable - based on page title
        
            # HTTP 404
            if "404" in page_title and ("not found" in page_title or "error" in page_title):
                print(f"[GOLOGIN WARMUP {profile_id}] ❌ 404 Not Found: {url}")
                return True, "HTTP 404 Not Found"
        
            # HTTP 500
            if "500" in page_title and "error" in page_title:
                print(f"[GOLOGIN WARMUP {profile_id}] ❌ 500 Server Error: {url}")
                return True, "HTTP 500 Internal Server Error"
        
            # HTTP 503
            if "503" in page_title and "unavailable" in page_title:
                print(f"[GOLOGIN WARMUP {profile_id}] ❌ 503 Service Unavailable: {url}")
                return True, "HTTP 503 Service Unavailable"
        
            # Empty page
            if len(page_source.strip()) < 100:
                print(f"[GOLOGIN WARMUP {profile_id}] ⚪ Empty Page: {url}")
                return True, "Empty Page"
            
            # ========== SSL/CERTIFICATE ERROR ==========
            # "Your connection is not private" error page
            ssl_error_indicators = [
                # Chrome error page
                ("your connection is not private" in page_source),
                ("your connection is not secure" in page_source),
                # SSL error codes
                ("net::err_cert_" in page_source),  # Chrome SSL errors
                ("ssl_error_" in page_source),      # Firefox SSL errors
                # Certificate error phrases
                ("this site can't provide a secure connection" in page_source),
                ("certificate error" in page_source and "continue" in page_source),
                # Check title + URL pattern
                ("privacy error" in page_title and "chrome-error:" not in current_url),
            ]
        
            if any(ssl_error_indicators):
                print(f"[GOLOGIN WARMUP {profile_id}] 🔒 SSL Certificate Error: {url}")
                return True, "SSL Certificate Error"
        
        
            # ========== CLOUDFLARE DETECTION (STRICTER) ==========
            # Must have MULTIPLE indicators, not just "cloudflare" keyword
        
            cloudflare_strict_indicators = [
                ("checking your browser" in page_source and "cloudflare" in page_source),
                ("just a moment" in page_title and "cloudflare" in page_source),
                ("ray id" in page_source and "performance & security by cloudflare" in page_source),
                ("<title>just a moment...</title>" in page_source),
            ]
        
            if any(cloudflare_strict_indicators):
                print(f"[GOLOGIN WARMUP {profile_id}] 🛡️ Cloudflare challenge detected: {url}")
                return True, "Cloudflare Challenge"
        
            # ========== ACCESS DENIED (STRICTER) ==========
            # Must have clear denial message, not just keyword
        
            access_denied_strict = [
                ("access denied" in page_title or "403 forbidden" in page_title),
                ("your ip has been blocked" in page_source and len(page_source) < 5000),  # Short page = block page
                ("you have been blocked" in page_source and "cloudflare" in page_source),
            ]
        
            if any(access_denied_strict):
                print(f"[GOLOGIN WARMUP {profile_id}] 🚫 Access Denied/IP Blocked: {url}")
                return True, "Access Denied / IP Blocked"
        
            # ========== RATE LIMITING (STRICTER) ==========
            rate_limit_strict = [
                ("429" in page_title and "too many requests" in page_source),
                ("rate limit exceeded" in page_source and len(page_source) < 3000),
            ]
        
            if any(rate_limit_strict):
                print(f"[GOLOGIN WARMUP {profile_id}] ⏱️ Rate Limited: {url}")
                return True, "Rate Limited"        
           
        
            # ========== REDIRECT TO ERROR PAGE ==========
            if any(err in current_url for err in ["/error", "/404", "/blocked", "/denied"]):
                print(f"[GOLOGIN WARMUP {profile_id}] 🔄 Redirected to error page: {current_url}")
                return True, "Redirected to Error Page"
        
            # ========== NO ISSUES ==========
            return False, ""
    
        except Exception as e:
            print(f"[GOLOGIN WARMUP {profile_id}] Error detecting page issues: {e}")
            return False, ""

            

    def _perform_deeper_clicks(self, driver, human, start_time, total_seconds, profile_id=""):
        """
        Perform multiple deeper clicks with retry logic
        - Random click 1-3 DIFFERENT links on current page (RANDOM VỊ TRÍ)
        - Each click opens new tab, browse, then close
        - Retry 3 times if element not interactable
        - Move to next website if all retries fail
        """
        try:
            main_tab = driver.current_window_handle
        
            # Random number of deeper clicks (1-3 clicks)
            num_deeper_clicks = random.randint(1, 3)
            print(f"[GOLOGIN WARMUP] [{profile_id}] Attempting {num_deeper_clicks} deeper clicks...")
        
            successful_clicks = 0
        
            for click_index in range(num_deeper_clicks):
                if time.time() - start_time >= total_seconds:
                    break
            
                print(f"[GOLOGIN WARMUP] [{profile_id}] === Deeper click {click_index+1}/{num_deeper_clicks} ===")
            
                # Retry logic for finding clickable element
                max_retries = 3
                clicked = False
            
                for retry in range(max_retries):
                    try:
                        tabs_before = len(driver.window_handles)
                    
                        # ========== RANDOM SELECT VỊ TRÍ ==========
                        # Mỗi lần gọi click_random_link_with_retry() sẽ RANDOM chọn 1 link khác
                        # Click 1: Có thể chọn link thứ 7
                        # Click 2: Có thể chọn link thứ 2
                        # Click 3: Có thể chọn link thứ 9
                        clicked = human.click_random_link_with_retry()
                        # =========================================
                    
                        if clicked:
                            print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Deeper click {click_index+1}/{num_deeper_clicks} successful (retry {retry+1}/{max_retries})")
                            successful_clicks += 1
                            time.sleep(random.uniform(2, 4))
                            
                            
                        
                            # Check if new tab opened
                            tabs_after = len(driver.window_handles)
                            if tabs_after > tabs_before:
                                new_tab = driver.window_handles[-1]
                                driver.switch_to.window(new_tab)
                                print(f"[GOLOGIN WARMUP] [{profile_id}] → Switched to new tab")
                                time.sleep(random.uniform(3.0, 5.0))
                                
                                # ========== VALIDATE & SAVE DEEPER URL (NEW TAB) ==========
                                collect_file = self.params.get("collect_websites_file", "").strip()
                                if collect_file:
                                    try:
                                        deeper_url = driver.current_url
            
                                        # Basic URL validation
                                        if not deeper_url or deeper_url in ("data:,", "about:blank") or "chrome-error://" in deeper_url:
                                            print(f"[GOLOGIN WARMUP {profile_id}] ⚠ Skipped invalid URL: {deeper_url[:60] if deeper_url else 'None'}")
                                        else:                                          
                                            # =========================================================
                                            # Check if page loaded successfully (no bot challenges/errors)
                                            is_blocked, block_reason = self._detect_page_issues(driver, deeper_url, profile_id)
                
                                            if is_blocked:
                                                print(f"[GOLOGIN WARMUP {profile_id}] ⚠ Page has issues ({block_reason}), not saving")
                                            else:
                                                # Page is OK - save URL
                                                save_collected_url(deeper_url, collect_file)
                                                print(f"[GOLOGIN WARMUP {profile_id}] ✓ Saved deeper URL (new tab): {deeper_url[:70]}...")
                                    except Exception as save_err:
                                        print(f"[GOLOGIN WARMUP {profile_id}] ⚠ Failed to save deeper URL: {save_err}")
                                # =========================================================
                            
                                # Actions on new page
                                deeper_actions = random.randint(1, 3)
                                print(f"[GOLOGIN WARMUP] [{profile_id}] Performing {deeper_actions} actions on deeper page...")
                                for action_idx in range(deeper_actions):
                                    if time.time() - start_time >= total_seconds:
                                        break
                                    try:
                                        human.execute_random_action()
                                        time.sleep(random.uniform(1.0, 2.5))
                                    except:
                                        break
                            
                                # Close deeper tab and return to main
                                try:
                                    print(f"[GOLOGIN WARMUP] [{profile_id}] Closing deeper tab...")
                                    driver.close()
                                    driver.switch_to.window(main_tab)
                                    print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Returned to main tab")
                                    time.sleep(1)
                                except Exception as close_err:
                                    print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ Error closing tab: {close_err}")
                                    # Fallback: switch to first available tab
                                    try:
                                        driver.switch_to.window(driver.window_handles[0])
                                    except:
                                        pass
                            else:
                                print(f"[GOLOGIN WARMUP] [{profile_id}] Link opened in same tab (no new tab)")
                                # ========== VALIDATE & SAVE DEEPER URL (SAME TAB) ==========
                                collect_file = self.params.get("collect_websites_file", "").strip()
                                if collect_file:
                                    try:
                                        deeper_url = driver.current_url
            
                                        # Basic URL validation
                                        if not deeper_url or deeper_url in ("data:,", "about:blank") or "chrome-error://" in deeper_url:
                                            print(f"[GOLOGIN WARMUP {profile_id}] ⚠ Skipped invalid URL: {deeper_url[:60] if deeper_url else 'None'}")
                                        else:                                           
                                            # =========================================================
                                            # Check if page loaded successfully
                                            is_blocked, block_reason = self._detect_page_issues(driver, deeper_url, profile_id)
                
                                            if is_blocked:
                                                print(f"[GOLOGIN WARMUP {profile_id}] ⚠ Page has issues ({block_reason}), not saving")
                                            else:
                                                # Page is OK - save URL
                                                save_collected_url(deeper_url, collect_file)
                                                print(f"[GOLOGIN WARMUP {profile_id}] ✓ Saved deeper URL (same tab): {deeper_url[:70]}...")
                                    except Exception as save_err:
                                        print(f"[GOLOGIN WARMUP {profile_id}] ⚠ Failed to save deeper URL: {save_err}")
                                # =========================================================
                            clicked = True
                            break  # Success, exit retry loop
                        else:
                            print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ Click failed on retry {retry+1}/{max_retries}")
                    
                    except Exception as click_err:
                        error_msg = str(click_err).lower()
                        if "element not interactable" in error_msg or "has no size" in error_msg:
                            print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ Retry {retry+1}/{max_retries}: Element not interactable")
                            time.sleep(1)
                            # Scroll page a bit to refresh elements
                            try:
                                driver.execute_script("window.scrollBy(0, 200);")
                                time.sleep(0.5)
                            except:
                                pass
                            continue
                        else:
                            print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ Click error: {click_err}")
                            break
            
                if not clicked:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ Failed to click after {max_retries} retries")
                    print(f"[GOLOGIN WARMUP] [{profile_id}] → Moving to next website...")
                    break
            
                # Small delay between multiple clicks
                if click_index < num_deeper_clicks - 1:
                    time.sleep(random.uniform(2, 4))
        
            print(f"[GOLOGIN WARMUP] [{profile_id}] === Deeper clicks summary: {successful_clicks}/{num_deeper_clicks} successful ===")
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ Deeper click flow error: {e}")
            import traceback
            traceback.print_exc()
            # Ensure we're back on main tab
            try:
                driver.switch_to.window(driver.window_handles[0])
            except:
                pass

    
        
    def set_variable(self, success):
        """Set variable with result"""
        variable = self.params.get("variable", "")
        if variable:
            GlobalVariables().set(variable, "true" if success else "false")
