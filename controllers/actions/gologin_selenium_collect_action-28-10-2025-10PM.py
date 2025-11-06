# controllers/actions/gologin_selenium_collect_action.py

from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from models.gologin_api import get_gologin_api
import random
import os
import time

# Import helpers
from helpers.gologin_profile_helper import GoLoginProfileHelper
from helpers.selenium_registry import register_selenium_driver, unregister_selenium_driver

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
            
            # ========== CHECK AND UPDATE PROXY IF PROVIDED ==========
            self._update_proxy_if_provided(profile_list, api_token)
            
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
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Error: {e}")
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
                print("[GOLOGIN WARMUP] No proxy configuration provided, skipping proxy update")
                return
            
            print("[GOLOGIN WARMUP] ========== PROXY UPDATE ==========")
            print("[GOLOGIN WARMUP] Proxy configuration detected, retrieving values...")
            
            # Get actual values from GlobalVariables
            proxy_mode = GlobalVariables().get(proxy_mode_var, "")
            proxy_host = GlobalVariables().get(proxy_host_var, "")
            proxy_port = GlobalVariables().get(proxy_port_var, "")
            proxy_username = GlobalVariables().get(proxy_username_var, "")
            proxy_password = GlobalVariables().get(proxy_password_var, "")
            
            # Check if all values are non-empty
            if not (proxy_mode and proxy_host and proxy_port and proxy_username and proxy_password):
                print("[GOLOGIN WARMUP] ⚠ Some proxy variables are empty, skipping proxy update")
                return
            
            proxy_config = {
                "mode": proxy_mode,
                "host": proxy_host,
                "port": proxy_port,
                "username": proxy_username,
                "password": proxy_password
            }
            
            print(f"[GOLOGIN WARMUP] Proxy: {proxy_mode}://{proxy_host}:{proxy_port}")
            
            # Get GoLogin API instance
            gologin_api = get_gologin_api(api_token)
            
            # Call GoLoginAPI method to update proxy
            proxy_success, proxy_message = gologin_api.update_proxy_for_profiles(
                profile_list, proxy_config
            )
            
            if proxy_success:
                print(f"[GOLOGIN WARMUP] ✓ {proxy_message}")
            else:
                print(f"[GOLOGIN WARMUP] ⚠ Warning: {proxy_message}")
            
            print("[GOLOGIN WARMUP] ===================================")
        except Exception as e:
            print(f"[GOLOGIN WARMUP] ⚠ Proxy update error: {e}")
    
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
            
            try:
                gologin.stop_profile(profile_id)  # This will force kill + cleanup
                print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Zombie cleanup completed")
            except Exception as zombie_err:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ Zombie cleanup warning: {zombie_err}")
        
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
        
            # Load websites list
            websites = GoLoginProfileHelper.load_websites(self.params, "[GOLOGIN WARMUP]")
            if not websites:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ No websites to browse")
                driver.quit()
                time.sleep(5)
                gologin.stop_profile(profile_id)
                return False
        
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

    
    
    
    def _search_on_site(self, driver, url, keywords):
        """Perform search if on Google or YouTube"""
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            from urllib.parse import urlparse
            
            if not keywords:
                return False
            
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check if Google or YouTube
            is_google = 'google.com' in domain or 'google' in domain
            is_youtube = 'youtube.com' in domain or 'youtu.be' in domain
            
            if not (is_google or is_youtube):
                return False
            
            # Random pick keyword
            keyword = random.choice(keywords)
            print(f"[GOLOGIN WARMUP] Searching for: '{keyword}'")
            
            # Find search box
            search_box = None
            if is_google:
                selectors = ['textarea[name="q"]', 'input[name="q"]', 'input[title="Search"]']
                for selector in selectors:
                    try:
                        search_box = driver.find_element(By.CSS_SELECTOR, selector)
                        if search_box:
                            break
                    except:
                        continue
            elif is_youtube:
                selectors = ['input#search', 'input[name="search_query"]', 'input[placeholder*="Search"]']
                for selector in selectors:
                    try:
                        search_box = driver.find_element(By.CSS_SELECTOR, selector)
                        if search_box:
                            break
                    except:
                        continue
            
            if not search_box:
                print(f"[GOLOGIN WARMUP] ⚠ Search box not found")
                return False
            
            # Clear and type keyword
            search_box.clear()
            time.sleep(random.uniform(0.5, 1))
            
            # Type with human-like delay
            for char in keyword:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            time.sleep(random.uniform(0.5, 1))
            search_box.send_keys(Keys.RETURN)
            print(f"[GOLOGIN WARMUP] ✓ Search submitted")
            
            # Wait for results
            time.sleep(random.uniform(2, 4))
            return True
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Error searching: {e}")
            return False
        
    def _browse_websites(self, driver, websites, total_seconds, keywords=None, profile_id=""):
        """Browse websites with human-like actions - IMPROVED VERSION"""
        try:
            from helpers.selenium_actions import SeleniumHumanActions
            from selenium.common.exceptions import TimeoutException
        
            print(f"[GOLOGIN WARMUP] [{profile_id}] Starting browsing for {total_seconds}s...")
        
            human = SeleniumHumanActions(driver)
            how_to_get_websites = self.params.get("how_to_get_websites", "Random")          
        
            start_time = time.time()
            visit_count = 0
            action_count = 0
            current_index = 0
            ssl_error_sites = set()
        
            while True:
                # Check driver validity
                try:
                    driver.current_url
                except Exception as session_err:
                    error_msg = str(session_err).lower()
                    if "invalid session" in error_msg or "session deleted" in error_msg:
                        print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ Driver session invalid, stopping browse")
                        break
            
                # Check time limit
                elapsed = time.time() - start_time
                if elapsed >= total_seconds:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Browsing completed after {int(elapsed)}s")
                    break
            
                # Select URL
                if how_to_get_websites == "Sequential by loop":
                    url = websites[current_index % len(websites)]
                    current_index += 1
                else:
                    url = random.choice(websites)
            
                # Skip sites with previous SSL errors
                if url in ssl_error_sites:
                    continue
            
                # ========== NAVIGATE TO URL ==========
                page_loaded_successfully = False
                try:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] [{visit_count+1}] Navigating to: {url}")
                    driver.set_page_load_timeout(15)
                
                    try:
                        driver.get(url)
                        time.sleep(1)
                    
                        # Check for error page
                        page_source = driver.page_source.lower()
                        current_url = driver.current_url
                    
                        if "err_connection_timed_out" in page_source or \
                           "this site can't be reached" in page_source or \
                           "took too long to respond" in page_source or \
                           "chrome-error://" in current_url:
                            print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ ERR_CONNECTION_TIMED_OUT: {url}")
                            ssl_error_sites.add(url)
                            continue
                    
                        print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Page loaded: {url}")
                        page_loaded_successfully = True
                    
                    except TimeoutException:
                        print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ Page load timeout: {url}")
                        try:
                            driver.execute_script("window.stop();")
                            time.sleep(0.5)
                            page_source = driver.page_source.lower()
                            current_url = driver.current_url
                        
                            if "err_connection_timed_out" in page_source or \
                               "this site can't be reached" in page_source or \
                               "chrome-error://" in current_url:
                                print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ Connection error after timeout: {url}")
                                ssl_error_sites.add(url)
                                continue
                        
                            if current_url and current_url not in ["data:,", "about:blank"]:
                                print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Page partially loaded, continuing...")
                                page_loaded_successfully = True
                        except Exception as stop_err:
                            pass
                    
                        if not page_loaded_successfully:
                            ssl_error_sites.add(url)
                            print(f"[GOLOGIN WARMUP] [{profile_id}] → Skipping to next website...")
                            time.sleep(1)
                            continue
                        
                except Exception as nav_err:
                    error_msg = str(nav_err).lower()
                    if any(kw in error_msg for kw in ['ssl', 'certificate', 'connection', 'net::err_']):
                        print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ Connection error: {url}")
                        ssl_error_sites.add(url)
                        print(f"[GOLOGIN WARMUP] [{profile_id}] → Skipping to next website...")
                        time.sleep(1)
                        continue
            
                # Page loaded successfully
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
            
                # Perform search if Google/YouTube
                search_performed = self._search_on_site(driver, url, keywords)
                if search_performed:
                    time.sleep(random.uniform(2, 3))
                    try:
                        human.scroll_random()
                        time.sleep(random.uniform(1, 2))
                        human.click_random_element()
                    except:
                        pass
            
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
                if time.time() - start_time < total_seconds:
                    self._perform_deeper_clicks(driver, human, start_time, total_seconds, profile_id)
                # ==============================================
            
                # Stay on page
                stay_time = random.uniform(5.0, 10.0)
                print(f"[GOLOGIN WARMUP] [{profile_id}] Staying on page for {stay_time:.1f}s...")
                time.sleep(stay_time)
            
                if time.time() - start_time >= total_seconds:
                    break
        
            print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Visited {visit_count} pages, performed {action_count} actions")
            print(f"[GOLOGIN WARMUP] [{profile_id}] SSL error sites: {len(ssl_error_sites)}")
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] [{profile_id}] Error during browsing: {e}")
            import traceback
            traceback.print_exc()
            

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
