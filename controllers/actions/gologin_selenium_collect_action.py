# controllers/actions/gologin_selenium_collect_action.py

from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from models.gologin_api import get_gologin_api
import random
import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from helpers.selenium_registry import register_selenium_driver, unregister_selenium_driver

class GoLoginSeleniumCollectAction(BaseAction):
    """Handler for GoLogin Selenium Warm Up action"""
    
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
        
            # ========== NEW: CHECK "ALL PROFILES" OPTION ==========
            all_profiles = self.params.get("all_profiles", False)
        
            if all_profiles:
                print("[GOLOGIN WARMUP] ========== FETCHING ALL PROFILES ==========")
                gologin_api = get_gologin_api(api_token)
            
                # Call API to get all profiles
                success, profiles_data = gologin_api.get_all_profiles()
            
                if not success:
                    print(f"[GOLOGIN WARMUP] ✗ Failed to fetch profiles: {profiles_data}")
                    self.set_variable(False)
                    return
            
                # Extract profile IDs from response
                profile_list = [profile.get("id") for profile in profiles_data if profile.get("id")]
            
                if not profile_list:
                    print("[GOLOGIN WARMUP] ✗ No profiles found in account")
                    self.set_variable(False)
                    return
            
                random.shuffle(profile_list)  # Xáo trộn list
                print(f"[GOLOGIN WARMUP] ✓ Fetched {len(profile_list)} profiles from API")
                print(f"[GOLOGIN WARMUP] Profile IDs: {', '.join(profile_list[:5])}{'...' if len(profile_list) > 5 else ''}")
        
            else:
                # Original logic: Get profile IDs from params
                profile_ids = self.params.get("profile_ids", "").strip()
                if not profile_ids:
                    print("[GOLOGIN WARMUP] Error: Profile IDs are required")
                    self.set_variable(False)
                    return
            
                # Parse profile IDs
                profile_list = self._parse_profile_ids(profile_ids)
                if not profile_list:
                    print("[GOLOGIN WARMUP] Error: No valid profile IDs found")
                    self.set_variable(False)
                    return
            
                print(f"[GOLOGIN WARMUP] Total profiles to warm up: {len(profile_list)}")
            
            # ========== CHECK AND UPDATE PROXY IF PROVIDED ==========
            # Get proxy variable names
            proxy_mode_var = self.params.get("proxy_mode_variable", "").strip()
            proxy_host_var = self.params.get("proxy_host_variable", "").strip()
            proxy_port_var = self.params.get("proxy_port_variable", "").strip()
            proxy_username_var = self.params.get("proxy_username_variable", "").strip()
            proxy_password_var = self.params.get("proxy_password_variable", "").strip()

            # Check if all 5 variable names are provided
            if proxy_mode_var and proxy_host_var and proxy_port_var and proxy_username_var and proxy_password_var:
                print("[GOLOGIN WARMUP] ========== PROXY UPDATE ==========")
                print("[GOLOGIN WARMUP] Proxy configuration detected, retrieving values from variables...")
    
                # Get actual values from GlobalVariables
                proxy_mode = GlobalVariables().get(proxy_mode_var, "")
                proxy_host = GlobalVariables().get(proxy_host_var, "")
                proxy_port = GlobalVariables().get(proxy_port_var, "")
                proxy_username = GlobalVariables().get(proxy_username_var, "")
                proxy_password = GlobalVariables().get(proxy_password_var, "")
    
                # Check if all values are non-empty
                if proxy_mode and proxy_host and proxy_port and proxy_username and proxy_password:
                    proxy_config = {
                        "mode": proxy_mode,
                        "host": proxy_host,
                        "port": proxy_port,
                        "username": proxy_username,
                        "password": proxy_password
                    }
        
                    print(f"[GOLOGIN WARMUP] Retrieved proxy values:")
                    print(f"[GOLOGIN WARMUP]   Mode: {proxy_mode} (from {proxy_mode_var})")
                    print(f"[GOLOGIN WARMUP]   Host: {proxy_host} (from {proxy_host_var})")
                    print(f"[GOLOGIN WARMUP]   Port: {proxy_port} (from {proxy_port_var})")
                    print(f"[GOLOGIN WARMUP]   Username: {proxy_username} (from {proxy_username_var})")
        
                    # Get GoLogin API instance
                    gologin_api = get_gologin_api(api_token)
        
                    # Call GoLoginAPI method to update proxy
                    proxy_success, proxy_message = gologin_api.update_proxy_for_profiles(profile_list, proxy_config)
        
                    if proxy_success:
                        print(f"[GOLOGIN WARMUP] ✓ {proxy_message}")
                    else:
                        print(f"[GOLOGIN WARMUP] ⚠ Warning: {proxy_message}")
                        print("[GOLOGIN WARMUP] Continuing without proxy update...")
                else:
                    print("[GOLOGIN WARMUP] ⚠ Warning: Some proxy variables are empty, skipping proxy update")
                    print(f"[GOLOGIN WARMUP]   Mode: {proxy_mode_var} = '{proxy_mode}'")
                    print(f"[GOLOGIN WARMUP]   Host: {proxy_host_var} = '{proxy_host}'")
                    print(f"[GOLOGIN WARMUP]   Port: {proxy_port_var} = '{proxy_port}'")
                    print(f"[GOLOGIN WARMUP]   Username: {proxy_username_var} = '{proxy_username}'")
                    print(f"[GOLOGIN WARMUP]   Password: {proxy_password_var} = '{proxy_password}'")
    
                print("[GOLOGIN WARMUP] ===================================")
            else:
                print("[GOLOGIN WARMUP] No proxy configuration provided (variable names missing), skipping proxy update")


        
            # Check if multi-threading enabled
            enable_threading = self.params.get("enable_threading", False)
        
            if enable_threading and len(profile_list) > 1:
                # PARALLEL MODE
                print("[GOLOGIN WARMUP] ========== PARALLEL MODE ==========")
                self._warmup_parallel(profile_list, api_token)
            else:
                # SEQUENTIAL MODE - Select 1 profile and warm up
                print("[GOLOGIN WARMUP] ========== SEQUENTIAL MODE ==========")
                how_to_get = self.params.get("how_to_get", "Random")
                profile_id = self._select_profile(profile_list, how_to_get)
                print(f"[GOLOGIN WARMUP] Selected profile ID: {profile_id}")
            
                # Warm up single profile
                success = self._warmup_single_profile(profile_id, api_token)
                self.set_variable(success)
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Error: {e}")
            import traceback
            traceback.print_exc()
            self.set_variable(False)

    def _warmup_single_profile(self, profile_id, api_token):
        """Warm up a single profile - can be called from thread"""
        driver = None
        gologin = None
        try:
            print(f"\n[GOLOGIN WARMUP] [{profile_id}] Starting warm up...")
            self._kill_zombie_chrome_processes(profile_id)
            # Get options
            refresh_fingerprint = self.params.get("refresh_fingerprint", False)           
            headless = self.params.get("headless", False)
        
            # Get GoLogin API instance
            gologin = get_gologin_api(api_token)
        
            # Refresh fingerprint if requested
            if refresh_fingerprint:
                print(f"[GOLOGIN WARMUP] [{profile_id}] Refreshing fingerprint...")
                success = gologin.refresh_fingerprint(profile_id)
                if success:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Fingerprint refreshed")
                else:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ Failed to refresh fingerprint")
        
            # Start profile
            print(f"[GOLOGIN WARMUP] [{profile_id}] Starting profile...")
        
            # Pass headless param to GoLogin API
            if headless:
                extra_params = [
                    "--headless=new",
                    "--mute-audio",  # Mute audio
                    "--disable-background-networking",
                    "--disable-extensions",
                    "--enable-features=NetworkService",  # Enable cookies        
                    # ← THÊM CÁC FLAG NÀY ĐỂ FORCE SAVE HISTORY                    
                    "--enable-logging",  # Enable logging
                    "--v=1",  # Verbose level
                    "--disk-cache-size=0",  # Disable cache to force writes
                    "--media-cache-size=0",
                    "--disable-features=CookiesWithoutSameSiteMustBeSecure",  # Allow all cookies
                    "--disable-dev-shm-usage",  # ← QUAN TRỌNG: Không dùng /dev/shm
                    "--disable-gpu",             # ← Tắt GPU trong headless
                    "--no-sandbox",              # ← Bỏ sandbox để tránh memory restrictions
                    "--disable-software-rasterizer",
                    "--disable-features=VizDisplayCompositor",
                    "--ignore-certificate-errors",           # Ignore SSL cert errors
                    "--ignore-ssl-errors",                   # Ignore SSL errors
                    "--disable-web-security",                # Disable web security
                    "--allow-insecure-localhost",           # Allow insecure localhost
                    "--reduce-security-for-testing",        # Reduce security for testing
                    "--disable-site-isolation-trials",      # Disable site isolation
                    # ← THÊM: Disable GCM to prevent QUOTA_EXCEEDED
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-breakpad",
                    "--disable-component-extensions-with-background-pages",
                    "--disable-features=TranslateUI,BlinkGenPropertyTrees",
                    "--disable-ipc-flooding-protection",
                    "--disable-renderer-backgrounding",
                    "--disable-sync",  # ← QUAN TRỌNG: Tắt Chrome sync
                    "--gcm-channel-status-poll-interval-seconds=0",  # ← Disable GCM polling
                ]
            else:
                extra_params = [                  
                    "--enable-features=NetworkService",
                    "--disable-features=CookiesWithoutSameSiteMustBeSecure",
                    "--enable-logging",  # Enable logging
                    "--v=1",  # Verbose level
                    "--disk-cache-size=0",  # Disable cache to force writes
                    "--media-cache-size=0",
                     # ← THÊM: Disable GCM for non-headless too
                    "--disable-sync",
                    "--gcm-channel-status-poll-interval-seconds=0",
                ]
        
            success, debugger_address = gologin.start_profile(profile_id, extra_params=extra_params)
        
            if not success:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ Failed to start profile: {debugger_address}")
                return False
        
            print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Profile started: {debugger_address}")
        
            # Connect Selenium
            driver = self._connect_selenium(debugger_address)
            if not driver:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ Failed to connect Selenium")
                gologin.stop_profile(profile_id)
                return False
            
            # ← REGISTER DRIVER FOR AUTO-CLEANUP
            register_selenium_driver(driver)
            
            # ← THÊM: Clean up old tabs from previous sessions
            print(f"[GOLOGIN WARMUP] [{profile_id}] Checking browser tabs...")
            self._cleanup_browser_tabs(driver)
            
         
        
            # Load websites list
            websites = self._load_websites()
            if not websites:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ No websites to browse")
                driver.quit()
                gologin.stop_profile(profile_id)
                return False

            # Load keywords for search (optional)
            keywords = self._load_keywords()
            if keywords:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Loaded {len(keywords)} search keywords")

        
            # Get duration
            duration_minutes = self.params.get("duration_minutes", "5")
            try:
                duration_minutes = float(duration_minutes)
            except:
                duration_minutes = 5
            total_seconds = int(duration_minutes * 60)
        
            # Browse websites
            print(f"[GOLOGIN WARMUP] [{profile_id}] Browsing websites for {duration_minutes} minutes...")
            self._browse_websites(driver, websites, total_seconds, keywords)
        
            # Wait for async operations to complete
            print(f"[GOLOGIN WARMUP] [{profile_id}] Waiting for browser data to settle...")
            time.sleep(5)
           
            return True
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


        finally:
            # ========== CLEANUP BLOCK - LUÔN CHẠY ==========
            print(f"[GOLOGIN WARMUP] [{profile_id}] Running cleanup...")
        
            # 1. Close browser
            if driver:
                try:
                    # Unregister from auto-cleanup first
                    unregister_selenium_driver(driver)
                
                    # Quit driver
                    driver.quit()
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Browser closed")
                except Exception as cleanup_err:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ Browser cleanup warning: {cleanup_err}")
                    
                finally:
                    # ← FIX: CRITICAL - Set driver to None to prevent reuse
                    driver = None
        
            # 2. Wait for Chrome cleanup
            print(f"[GOLOGIN WARMUP] [{profile_id}] Waiting for Chrome process cleanup...")
            time.sleep(5)
        
            # 3. Stop profile
            if gologin:
                try:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] Stopping profile...")
                    success, msg = gologin.stop_profile(profile_id)
                    if success:
                        print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Profile stopped and data synced")
                    
                        # Wait for cloud sync
                        print(f"[GOLOGIN WARMUP] [{profile_id}] Waiting for cookies to sync to cloud...")
                        time.sleep(5)
                    
                    else:
                        print(f"[GOLOGIN WARMUP] [{profile_id}] ✗ Stop failed: {msg}")
                except Exception as stop_err:
                    print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ Stop profile error: {stop_err}")
        
            print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Cleanup completed")
            # ========== END CLEANUP BLOCK ==========

    def _warmup_parallel(self, profile_list, api_token):
        """
        Warm up multiple profiles in parallel using threading
        WITH TIMEOUT to prevent hanging on cleanup
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
        import math
    
        # Get max workers
        max_workers_str = self.params.get("max_workers", "3")
        try:
            max_workers = int(max_workers_str)
        except:
            max_workers = 3
    
        max_workers = min(max_workers, len(profile_list))  # Don't exceed profile count
    
        print(f"[GOLOGIN WARMUP] Warming up {len(profile_list)} profiles with {max_workers} parallel threads")
        print(f"[GOLOGIN WARMUP] Profiles: {', '.join(profile_list)}")
    
        # Calculate timeout per profile
        duration_minutes = self.params.get("duration_minutes", "5")
        try:
            duration_minutes = float(duration_minutes)
        except:
            duration_minutes = 5
    
        # Timeout = browsing time + 5 minutes buffer for start/stop
        timeout_per_profile = int((duration_minutes + 5) * 60)
    
        # ← FIX: Calculate realistic timeout based on batches (not all profiles)
        batches = math.ceil(len(profile_list) / max_workers)
        total_timeout = timeout_per_profile * batches
    
        print(f"[GOLOGIN WARMUP] Timeout per profile: {timeout_per_profile}s ({timeout_per_profile/60:.1f} min)")
        print(f"[GOLOGIN WARMUP] Batches: {batches} (with {max_workers} workers)")
        print(f"[GOLOGIN WARMUP] Total timeout: {total_timeout}s ({total_timeout/60:.1f} min)")
    
        # Store results
        results = []
        completed_profiles = []
        timeout_profiles = []
    
        # Create thread pool WITHOUT context manager (for explicit control)
        executor = ThreadPoolExecutor(max_workers=max_workers)
    
        try:
            # Submit all profiles to thread pool WITH STAGGER
            future_to_profile = {}
            for i, profile_id in enumerate(profile_list):
                # Add delay between submissions to prevent race conditions
                if i > 0:
                    time.sleep(2)
            
                future = executor.submit(self._warmup_single_profile, profile_id, api_token)
                future_to_profile[future] = profile_id
                print(f"[GOLOGIN WARMUP] Submitted thread {i+1}/{len(profile_list)}: {profile_id}")
        
            print(f"[GOLOGIN WARMUP] All threads submitted, waiting for completion...")
        
            # Wait for all threads to complete WITH GLOBAL TIMEOUT
            try:
                print(f"[GOLOGIN WARMUP] Waiting for threads (timeout: {total_timeout}s)...")
            
                for future in as_completed(future_to_profile, timeout=total_timeout):
                    profile_id = future_to_profile[future]
                
                    try:
                        # Get result with individual timeout (30s)
                        success = future.result(timeout=30)
                        results.append(success)
                        completed_profiles.append(profile_id)
                    
                        if success:
                            print(f"[GOLOGIN WARMUP] ✓ Profile {profile_id} completed successfully")
                        else:
                            print(f"[GOLOGIN WARMUP] ✗ Profile {profile_id} failed")
                        
                    except TimeoutError:
                        print(f"[GOLOGIN WARMUP] ✗ Profile {profile_id} TIMEOUT (result retrieval)")
                        results.append(False)
                        timeout_profiles.append(profile_id)
                    
                    except Exception as e:
                        print(f"[GOLOGIN WARMUP] ✗ Profile {profile_id} exception: {e}")
                        results.append(False)
            
                print(f"[GOLOGIN WARMUP] ✓ All futures processed")
        
            except TimeoutError:
                print(f"[GOLOGIN WARMUP] ⚠ GLOBAL TIMEOUT reached after {total_timeout}s")
                print(f"[GOLOGIN WARMUP] Completed: {len(completed_profiles)}/{len(profile_list)}")
            
                # Mark remaining profiles as timeout
                for profile_id in profile_list:
                    if profile_id not in completed_profiles and profile_id not in timeout_profiles:
                        print(f"[GOLOGIN WARMUP] ✗ Profile {profile_id} TIMEOUT (global)")
                        results.append(False)
                        timeout_profiles.append(profile_id)
        
            except Exception as e:
                print(f"[GOLOGIN WARMUP] ⚠ Unexpected error in thread pool: {e}")
                import traceback
                traceback.print_exc()
        
            print(f"[GOLOGIN WARMUP] Exiting try block...")
    
        except Exception as e:
            print(f"[GOLOGIN WARMUP] ⚠ Outer exception: {e}")
            import traceback
            traceback.print_exc()
    
        finally:
            # CRITICAL: Force shutdown thread pool
            print(f"[GOLOGIN WARMUP] Entering finally block for cleanup...")
            print(f"[GOLOGIN WARMUP] Forcing thread pool shutdown...")
        
            try:
                # Force shutdown without waiting for hanging threads
                executor.shutdown(wait=False)
                print(f"[GOLOGIN WARMUP] ✓ Thread pool forcefully shut down")
            except Exception as shutdown_err:
                print(f"[GOLOGIN WARMUP] ⚠ Shutdown error: {shutdown_err}")
        
            # Give threads grace period to cleanup
            print(f"[GOLOGIN WARMUP] Waiting 3s grace period...")
            time.sleep(3)
        
            # Check if any threads still alive
            import threading
            active_count = threading.active_count()
            print(f"[GOLOGIN WARMUP] Active threads: {active_count}")
        
            if active_count > 1:  # > 1 because main thread counts
                print(f"[GOLOGIN WARMUP] ⚠ Warning: {active_count-1} threads still active after shutdown")
        
            print(f"[GOLOGIN WARMUP] Exiting finally block...")
    
        # Summary
        success_count = sum(results) if results else 0
        print(f"\n[GOLOGIN WARMUP] ========== SUMMARY ==========")
        print(f"[GOLOGIN WARMUP] Total: {len(profile_list)} profiles")
        print(f"[GOLOGIN WARMUP] Completed: {len(completed_profiles)}")
        print(f"[GOLOGIN WARMUP] Success: {success_count}")
        print(f"[GOLOGIN WARMUP] Failed: {len(results) - success_count if results else 0}")
        print(f"[GOLOGIN WARMUP] Timeout: {len(timeout_profiles)}")
    
        if timeout_profiles:
            print(f"[GOLOGIN WARMUP] Timeout profiles: {', '.join(timeout_profiles)}")
    
        print(f"[GOLOGIN WARMUP] ============================\n")
    
        # Set variable based on overall success
        self.set_variable(success_count > 0)



    def _kill_zombie_chrome_processes(self, profile_id):
        """
        Kill ONLY GoLogin/Orbita Chrome processes for this profile
        SAFE: Does NOT kill real Chrome browsers
        """
        try:
            import psutil
        
            print(f"[GOLOGIN WARMUP] [{profile_id}] Checking for zombie GoLogin processes...")
        
            killed_count = 0
        
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    proc_name = proc.info['name'].lower()
                    proc_exe = proc.info.get('exe', '').lower()
                    cmdline = proc.info.get('cmdline', [])
                
                    # ========== FILTER 1: MUST BE ORBITA OR GOLOGIN CHROME ==========
                    # Check executable path to ensure it's GoLogin's Chrome, not system Chrome
                    is_gologin_chrome = False
                
                    if proc_exe:
                        # GoLogin Chrome is located in specific paths:
                        # - Windows: C:\Users\xxx\AppData\Local\GoLogin\app-x.x.x\resources\chrome\...
                        # - Or: Contains 'gologin' or 'orbita' in path
                        if ('gologin' in proc_exe or 'orbita' in proc_exe):
                            is_gologin_chrome = True
                        elif 'appdata\\local\\gologin' in proc_exe:
                            is_gologin_chrome = True
                
                    # If not GoLogin Chrome, skip
                    if not is_gologin_chrome:
                        continue
                
                    # ========== FILTER 2: CHECK IF IT BELONGS TO THIS PROFILE ==========
                    # Check command line arguments for profile ID
                    has_profile_id = False
                
                    if cmdline:
                        cmdline_str = ' '.join(cmdline).lower()
                    
                        # Look for profile ID in:
                        # - --user-data-dir=C:\...\gologin_profile_<profile_id>
                        # - --profile-directory=<profile_id>
                        if profile_id.lower() in cmdline_str:
                            # Extra check: Must be in user-data-dir or profile-directory
                            if '--user-data-dir' in cmdline_str or '--profile-directory' in cmdline_str:
                                has_profile_id = True
                
                    # ========== KILL IF BOTH CONDITIONS MET ==========
                    if is_gologin_chrome and has_profile_id:
                        print(f"[GOLOGIN WARMUP] [{profile_id}] Killing zombie GoLogin Chrome PID {proc.info['pid']}")
                        proc.kill()
                        killed_count += 1
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        
            if killed_count > 0:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ Killed {killed_count} zombie process(es)")
                time.sleep(2)  # Wait for processes to terminate
            else:
                print(f"[GOLOGIN WARMUP] [{profile_id}] ✓ No zombie processes found")
        
            return True
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] [{profile_id}] ⚠ Zombie check error: {e}")
            return False



    def _parse_profile_ids(self, profile_ids_text):
        """Parse profile IDs from text, support variables"""
        profile_list = []
        parts = profile_ids_text.split(";")
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Check if variable format <VARIABLE_NAME>
            if part.startswith("<") and part.endswith(">"):
                var_name = part[1:-1]
                var_value = GlobalVariables().get(var_name, "")
                if var_value:
                    profile_list.append(var_value)
                else:
                    print(f"[GOLOGIN WARMUP] Warning: Variable '{var_name}' is empty")
            else:
                profile_list.append(part)
        
        return profile_list
    
    def _select_profile(self, profile_list, how_to_get):
        """Select profile based on method"""
        if how_to_get == "Sequential by loop":
            loop_index = GlobalVariables().get("loop_index", "0")
            try:
                index = int(loop_index) % len(profile_list)
                return profile_list[index]
            except:
                return profile_list[0]            
        else:
            # Random
            return random.choice(profile_list)    
    
        
    def _update_proxy_for_profiles(self, api_token, profile_ids, proxy_config):
        """
        Update proxy for multiple profiles before starting them
    
        Args:
            api_token: GoLogin API token
            profile_ids: List of profile IDs
            proxy_config: Dict with keys: mode, host, port, username, password
    
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import requests
        
            # Validate all 5 required fields are present
            required_fields = ["mode", "host", "port", "username", "password"]
            for field in required_fields:
                if not proxy_config.get(field):
                    print(f"[GOLOGIN WARMUP] Proxy field '{field}' is empty. Skipping proxy update.")
                    return False
        
            # Convert port to integer
            try:
                port = int(proxy_config["port"])
            except ValueError:
                print(f"[GOLOGIN WARMUP] ✗ Invalid port number: {proxy_config['port']}")
                return False
        
            # Build API request payload
            api_url = "https://api.gologin.com/browser/proxy/many/v2"
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
        
            # Build proxies array for all profiles
            proxies_array = []
            for profile_id in profile_ids:
                proxy_data = {
                    "profileId": profile_id,
                    "proxy": {
                        "id": None,  # null for new proxy
                        "mode": proxy_config["mode"],
                        "host": proxy_config["host"],
                        "port": port,
                        "username": proxy_config["username"],
                        "password": proxy_config["password"],
                        "changeIpUrl": None,  # null
                        "customName": None   # null
                    }
                }
                proxies_array.append(proxy_data)
        
            payload = {"proxies": proxies_array}
        
            print(f"[GOLOGIN WARMUP] Updating proxy for {len(profile_ids)} profiles...")
            print(f"[GOLOGIN WARMUP] Proxy: {proxy_config['mode']}://{proxy_config['host']}:{port}")
        
            # Send PATCH request
            response = requests.patch(api_url, json=payload, headers=headers, timeout=30)
        
            if response.status_code in [200, 201, 204]:
                print(f"[GOLOGIN WARMUP] ✓ Proxy updated successfully for all profiles")
                return True
            else:
                print(f"[GOLOGIN WARMUP] ✗ Proxy update failed: {response.status_code}")
                print(f"[GOLOGIN WARMUP] Response: {response.text}")
                return False
            
        except Exception as e:
            print(f"[GOLOGIN WARMUP] ✗ Error updating proxy: {e}")
            import traceback
            traceback.print_exc()
            return False        
    

    def _close_all_tabs(self, driver):
        """
        Close all tabs except the last one to avoid folder lock issues
        This helps prevent "folder in use" errors when stopping profile
        """
        try:
            all_handles = driver.window_handles
        
            if len(all_handles) <= 1:
                print(f"[GOLOGIN WARMUP] Only 1 tab open, no need to close")
                return True
        
            print(f"[GOLOGIN WARMUP] Closing {len(all_handles) - 1} tabs...")
        
            # Keep the first tab, close all others
            first_handle = all_handles[0]
        
            for handle in all_handles[1:]:
                try:
                    driver.switch_to.window(handle)
                    driver.close()
                    time.sleep(0.5)  # Small delay between closes
                except Exception as e:
                    print(f"[GOLOGIN WARMUP] ⚠ Failed to close tab: {e}")
        
            # Switch back to first tab
            try:
                driver.switch_to.window(first_handle)
            except:
                # If first tab also failed, just continue
                pass
        
            print(f"[GOLOGIN WARMUP] ✓ All tabs closed")
            return True
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] ⚠ Error closing tabs: {e}")
            return False


    def _connect_selenium(self, debugger_address):
        """
        Connect Selenium to GoLogin Orbita browser
        THREAD-SAFE: Uses lock to prevent ChromeDriver download conflicts
        """
        try:
            import threading
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
        
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", debugger_address)
        
            # Detect Chrome version
            chrome_version = self._get_chrome_version_from_debugger(debugger_address)
        
            # ========== THREAD-SAFE CHROMEDRIVER INSTALLATION ==========
            # Use class-level lock to prevent multiple threads downloading simultaneously
            if not hasattr(self.__class__, '_chromedriver_lock'):
                self.__class__._chromedriver_lock = threading.Lock()
            if not hasattr(self.__class__, '_chromedriver_path'):
                self.__class__._chromedriver_path = {}
        
            # Get or install ChromeDriver with lock
            driver_path = None
            with self.__class__._chromedriver_lock:
                # Check cache first
                cache_key = chrome_version if chrome_version else 'default'
            
                if cache_key in self.__class__._chromedriver_path:
                    driver_path = self.__class__._chromedriver_path[cache_key]
                    print(f"[GOLOGIN WARMUP] Using cached ChromeDriver: {driver_path}")
                else:
                    # Install ChromeDriver (only one thread at a time)
                    if chrome_version:
                        print(f"[GOLOGIN WARMUP] Installing ChromeDriver for Chrome {chrome_version}...")
                        driver_path = ChromeDriverManager(driver_version=chrome_version).install()
                    else:
                        print(f"[GOLOGIN WARMUP] Installing ChromeDriver with auto-detection...")
                        driver_path = ChromeDriverManager().install()
                
                    # Cache the path
                    self.__class__._chromedriver_path[cache_key] = driver_path
                    print(f"[GOLOGIN WARMUP] ✓ ChromeDriver installed and cached")
        
            # Create service with cached driver path
            service = Service(driver_path)
            service.log_output = None  # Disable ChromeDriver logs
        
            # Create driver
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print(f"[GOLOGIN WARMUP] ✓ Selenium connected to Orbita")
        
            return driver
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Selenium connection error: {e}")
            import traceback
            traceback.print_exc()
            return None

        
    def _cleanup_browser_tabs(self, driver):
        """Close all tabs except first one to avoid crashes"""
        try:
            all_handles = driver.window_handles
            if len(all_handles) > 1:
                print(f"[GOLOGIN WARMUP] Found {len(all_handles)} tabs, closing old tabs...")
            
                # Keep first tab, close others
                first_handle = all_handles[0]
                for handle in all_handles[1:]:
                    try:
                        driver.switch_to.window(handle)
                        driver.close()
                    except:
                        pass
            
                # Switch back to first tab
                driver.switch_to.window(first_handle)
                print(f"[GOLOGIN WARMUP] ✓ Cleaned up tabs, using main tab")
            else:
                print(f"[GOLOGIN WARMUP] ✓ Only 1 tab, no cleanup needed")
        
            return True
        except Exception as e:
            print(f"[GOLOGIN WARMUP] ⚠ Tab cleanup error: {e}")
            return False

    
    def _get_chrome_version_from_debugger(self, debugger_address):
        """Get Chrome version from debugger address"""
        try:
            import requests
            host, port = debugger_address.split(":")
            response = requests.get(f"http://{host}:{port}/json/version", timeout=5)
            if response.status_code == 200:
                data = response.json()
                browser_version = data.get("Browser", "")
                if "/" in browser_version:
                    version = browser_version.split("/")[1]
                    major_version = version.split(".")[0]
                    print(f"[GOLOGIN WARMUP] Detected Chrome version: {version}")
                    return major_version
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Failed to detect Chrome version: {e}")
        return None
    
    def _load_websites(self):
        """Load websites from file"""
        try:
            # Get websites file - priority: variable > direct path
            websites_file = None
            
            websites_var = self.params.get("websites_variable", "").strip()
            if websites_var:
                websites_file = GlobalVariables().get(websites_var, "")
                if websites_file:
                    print(f"[GOLOGIN WARMUP] Using websites file from variable '{websites_var}': {websites_file}")
            
            if not websites_file:
                websites_file = self.params.get("websites_file", "").strip()
                if websites_file:
                    print(f"[GOLOGIN WARMUP] Using websites file from direct path: {websites_file}")
            
            if not websites_file or not os.path.exists(websites_file):
                print(f"[GOLOGIN WARMUP] ✗ Websites file not found: {websites_file}")
                return []
            
            # Load websites from file
            websites = []
            with open(websites_file, 'r', encoding='utf-8') as f:
                for line in f:
                    url = line.strip()
                    # Skip empty lines and comments
                    if url and not url.startswith('#'):
                        # Fix URL: add https:// if missing protocol
                        if not url.startswith(('http://', 'https://')):
                            url = 'https://' + url
                        websites.append(url)
            
            if not websites:
                print(f"[GOLOGIN WARMUP] ✗ No valid URLs found in file")
                return []
            
            print(f"[GOLOGIN WARMUP] ✓ Loaded {len(websites)} websites from file")
            return websites
            
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Error loading websites: {e}")
            return []
        
    def _load_keywords(self):
        """Load search keywords from file"""
        try:
            # Get keywords file - priority: variable > direct path
            keywords_file = None
        
            keywords_var = self.params.get("keywords_variable", "").strip()
            if keywords_var:
                keywords_file = GlobalVariables().get(keywords_var, "")
                if keywords_file:
                    print(f"[GOLOGIN WARMUP] Using keywords file from variable '{keywords_var}': {keywords_file}")
        
            if not keywords_file:
                keywords_file = self.params.get("keywords_file", "").strip()
                if keywords_file:
                    print(f"[GOLOGIN WARMUP] Using keywords file from direct path: {keywords_file}")
        
            if not keywords_file or not os.path.exists(keywords_file):
                return []
        
            # Load keywords from file
            keywords = []
            with open(keywords_file, 'r', encoding='utf-8') as f:
                for line in f:
                    keyword = line.strip()
                    # Skip empty lines and comments
                    if keyword and not keyword.startswith('#'):
                        keywords.append(keyword)
        
            if keywords:
                print(f"[GOLOGIN WARMUP] ✓ Loaded {len(keywords)} keywords from file")
        
            return keywords
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Error loading keywords: {e}")
            return []
        

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
        
            # Find search box and perform search
            search_box = None
        
            if is_google:
                # Google search selectors
                selectors = ['textarea[name="q"]', 'input[name="q"]', 'input[title="Search"]']
                for selector in selectors:
                    try:
                        search_box = driver.find_element(By.CSS_SELECTOR, selector)
                        if search_box:
                            break
                    except:
                        continue
        
            elif is_youtube:
                # YouTube search selectors
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
        
            # Press Enter
            search_box.send_keys(Keys.RETURN)
            print(f"[GOLOGIN WARMUP] ✓ Search submitted")
        
            # Wait for results
            time.sleep(random.uniform(2, 4))
        
            return True
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Error searching: {e}")
            return False


    
    def _browse_websites(self, driver, websites, total_seconds, keywords=None):
        """Browse websites with human-like actions"""
        try:
            from helpers.selenium_actions import SeleniumHumanActions
            from selenium.common.exceptions import TimeoutException
        
            print(f"[GOLOGIN WARMUP] Starting browsing for {total_seconds}s...")
        
            human = SeleniumHumanActions(driver)
            how_to_get_websites = self.params.get("how_to_get_websites", "Random")
        
            start_time = time.time()
            visit_count = 0
            action_count = 0
            current_index = 0
        
            # Track SSL error sites to avoid retrying
            ssl_error_sites = set()
        
            while True:
                # CHECK DRIVER VALIDITY
                try:
                    driver.current_url
                except Exception as session_err:
                    error_msg = str(session_err).lower()
                    if "invalid session" in error_msg or "session deleted" in error_msg:
                        print(f"[GOLOGIN WARMUP] ✗ Driver session invalid, stopping browse")
                        break
            
                # Check time limit
                elapsed = time.time() - start_time
                if elapsed >= total_seconds:
                    print(f"[GOLOGIN WARMUP] ✓ Browsing completed after {int(elapsed)}s")
                    break
            
                # Select URL
                if how_to_get_websites == "Sequential by loop":
                    url = websites[current_index % len(websites)]
                    current_index += 1
                else:
                    url = random.choice(websites)
            
                # Skip sites with previous SSL errors
                if url in ssl_error_sites:
                    print(f"[GOLOGIN WARMUP] Skipping {url} (previous SSL errors)")
                    continue
            
                # ========== NAVIGATE TO URL ==========
                page_loaded_successfully = False  # ← THÊM FLAG
            
                try:
                    print(f"[GOLOGIN WARMUP] [{visit_count+1}] Navigating to: {url}")
                
                    # Set page load timeout
                    driver.set_page_load_timeout(20)
                
                    try:
                        driver.get(url)
                        print(f"[GOLOGIN WARMUP] ✓ Page loaded: {url}")
                        page_loaded_successfully = True  # ← SET FLAG
                    
                    except TimeoutException:
                        print(f"[GOLOGIN WARMUP] ⚠ Page load timeout: {url}")
                    
                        # Force stop loading
                        try:
                            driver.execute_script("window.stop();")
                            print(f"[GOLOGIN WARMUP] ✓ Forced stop page load")
                        except:
                            pass
                    
                        # Check if page partially loaded
                        try:
                            current_url = driver.current_url
                            if current_url and current_url != "data:," and current_url != "about:blank":
                                print(f"[GOLOGIN WARMUP] ✓ Page partially loaded, continuing...")
                                page_loaded_successfully = True  # ← SET FLAG
                            else:
                                print(f"[GOLOGIN WARMUP] ✗ Page failed to load, skipping...")
                                ssl_error_sites.add(url)
                                continue  # Skip this site
                        except Exception as check_err:
                            print(f"[GOLOGIN WARMUP] ✗ Cannot check page state, skipping...")
                            ssl_error_sites.add(url)
                            continue  # Skip this site
                
                    # ← FIX: If page didn't load (flag not set), handle errors below
                    if not page_loaded_successfully:
                        print(f"[GOLOGIN WARMUP] ✗ Page load failed, trying next...")
                        ssl_error_sites.add(url)
                        time.sleep(1)
                        continue
                
                except Exception as nav_err:
                    error_msg = str(nav_err).lower()
                
                    print(f"[GOLOGIN WARMUP] ⚠ Navigation error: {str(nav_err)[:100]}")
                
                    # Detect network errors
                    if any(keyword in error_msg for keyword in ['ssl', 'certificate', 'handshake', 
                                                                  'connection_reset', 'connection_timed_out',
                                                                  'cert_date_invalid', 'net::err_']):
                        print(f"[GOLOGIN WARMUP] ✗ Network/SSL error on {url}, blacklisting...")
                        ssl_error_sites.add(url)
                        time.sleep(1)
                        continue
                
                    # Check if tab crashed
                    if "tab crashed" in error_msg or "session deleted" in error_msg:
                        print(f"[GOLOGIN WARMUP] ⚠ Tab crashed, attempting recovery...")
                        recovered = self._recover_from_crash(driver)
                        if recovered:
                            print(f"[GOLOGIN WARMUP] ✓ Recovered, continuing...")
                            ssl_error_sites.add(url)
                            continue
                        else:
                            print(f"[GOLOGIN WARMUP] ✗ Recovery failed, stopping...")
                            break
                
                    # Other errors - skip this site
                    print(f"[GOLOGIN WARMUP] Skipping {url} due to error")
                    ssl_error_sites.add(url)
                    time.sleep(2)
                    continue
            
                # ========== PAGE LOADED SUCCESSFULLY - BROWSE ==========
                visit_count += 1
            
                # Wait for page ready
                try:
                    driver.execute_script("return document.readyState")
                except:
                    pass
            
                time.sleep(random.uniform(3, 5))
            
                # Auto accept cookie consent
                try:
                    if human.accept_cookie_consent():
                        print(f"[GOLOGIN WARMUP] ✓ Accepted cookie consent banner")
                        time.sleep(random.uniform(1, 2))
                except:
                    pass
            
                # Close popups/modals
                try:
                    if human.close_popups():
                        print(f"[GOLOGIN WARMUP] ✓ Closed popup")
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
            
                # Random human-like actions on page
                actions_on_page = random.randint(1, 3)
                for _ in range(actions_on_page):
                    if time.time() - start_time >= total_seconds:
                        break
                    try:
                        human.execute_random_action()
                        action_count += 1
                        time.sleep(random.uniform(1.5, 3.0))
                    except Exception as action_err:
                        print(f"[GOLOGIN WARMUP] ⚠ Action error")
                        break
            
                # Click deeper logic (50% chance)
                if random.random() < 0.5 and time.time() - start_time < total_seconds:
                    print(f"[GOLOGIN WARMUP] Trying to click a link to go deeper...")
                
                    try:
                        main_tab = driver.current_window_handle
                        tabs_before = len(driver.window_handles)
                    except:
                        print(f"[GOLOGIN WARMUP] ⚠ Cannot get window handles")
                        continue
                
                    try:
                        clicked = human.click_random_link()
                    
                        if not clicked:
                            print(f"[GOLOGIN WARMUP] ⚠ No clickable link found on {url}")
                            # Don't add to blacklist, just skip deeper navigation
                        else:
                            print(f"[GOLOGIN WARMUP] ✓ Clicked deeper link")
                        
                            # Wait and check if new tab opened
                            time.sleep(2)
                            tabs_after = len(driver.window_handles)
                        
                            if tabs_after > tabs_before:
                                print(f"[GOLOGIN WARMUP] New tab opened, switching to it...")
                                new_tab = driver.window_handles[-1]
                                driver.switch_to.window(new_tab)
                            
                                time.sleep(random.uniform(3.0, 5.0))
                            
                                # Do actions on new page
                                deeper_actions = random.randint(1, 3)
                                for i in range(deeper_actions):
                                    if time.time() - start_time >= total_seconds:
                                        break
                                    try:
                                        human.execute_random_action()
                                        action_count += 1
                                        time.sleep(random.uniform(1.0, 2.5))
                                    except:
                                        break
                            
                                # Close deeper tab and switch back
                                try:
                                    print(f"[GOLOGIN WARMUP] Switching back to main tab...")
                                    if tabs_after > tabs_before:
                                        driver.close()
                                    driver.switch_to.window(main_tab)
                                except Exception as switch_err:
                                    print(f"[GOLOGIN WARMUP] ⚠ Tab switch error")
                                    try:
                                        driver.switch_to.window(driver.window_handles[0])
                                    except:
                                        pass
                
                    except Exception as deeper_err:
                        print(f"[GOLOGIN WARMUP] ⚠ Deeper navigation error")
                        try:
                            driver.switch_to.window(main_tab)
                        except:
                            try:
                                driver.switch_to.window(driver.window_handles[0])
                            except:
                                pass
            
                # Stay on page
                stay_time = random.uniform(10.0, 20.0)
                print(f"[GOLOGIN WARMUP] Staying on page for {stay_time:.1f}s...")
                time.sleep(stay_time)
            
                # Check if time is up
                if time.time() - start_time >= total_seconds:
                    print(f"[GOLOGIN WARMUP] ✓ Time limit reached")
                    break
        
            print(f"[GOLOGIN WARMUP] ✓ Visited {visit_count} pages, performed {action_count} actions")
            print(f"[GOLOGIN WARMUP] SSL error sites: {len(ssl_error_sites)}")
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Error during browsing: {e}")
            import traceback
            traceback.print_exc()


            


    def _recover_from_crash(self, driver):
        """
        Recover from tab crash by trying multiple methods
        Returns: True if recovered, False if failed
        """
        try:
            print(f"[GOLOGIN WARMUP] Attempting to recover from tab crash...")
        
            # Method 1: Try to get current handles (check if session alive)
            try:
                handles = driver.window_handles
                if not handles:
                    print(f"[GOLOGIN WARMUP] No handles available, session dead")
                    return False
                print(f"[GOLOGIN WARMUP] Session still alive, {len(handles)} tab(s) available")
            except Exception as e:
                print(f"[GOLOGIN WARMUP] Cannot get window handles, session lost")
                return False
        
            # Method 2: Try to navigate to about:blank on current tab
            try:
                driver.get("about:blank")
                time.sleep(1)
                print(f"[GOLOGIN WARMUP] ✓ Method 1: Navigated to blank page")
                return True
            except Exception as e:
                print(f"[GOLOGIN WARMUP] Method 1 failed: {e}")
        
            # Method 3: Try to refresh current tab
            try:
                driver.refresh()
                time.sleep(1)
                print(f"[GOLOGIN WARMUP] ✓ Method 2: Refreshed current tab")
                return True
            except Exception as e:
                print(f"[GOLOGIN WARMUP] Method 2 failed: {e}")
        
            # Method 4: Close crashed tab and switch to first available
            try:
                handles = driver.window_handles
                if len(handles) > 1:
                    # Close current crashed tab
                    try:
                        driver.close()
                    except:
                        pass
                
                    # Switch to first tab
                    driver.switch_to.window(handles[0])
                    time.sleep(1)
                    print(f"[GOLOGIN WARMUP] ✓ Method 3: Closed crashed tab, switched to tab 1")
                    return True
            except Exception as e:
                print(f"[GOLOGIN WARMUP] Method 3 failed: {e}")
        
            # Method 5: Open new tab with JavaScript
            try:
                driver.execute_script("window.open('about:blank', '_blank');")
                time.sleep(1)
                handles = driver.window_handles
                if len(handles) > 0:
                    driver.switch_to.window(handles[-1])
                    print(f"[GOLOGIN WARMUP] ✓ Method 4: Opened new tab")
                    return True
            except Exception as e:
                print(f"[GOLOGIN WARMUP] Method 4 failed: {e}")
        
            print(f"[GOLOGIN WARMUP] ✗ All recovery methods failed")
            return False
        
        except Exception as e:
            print(f"[GOLOGIN WARMUP] Recovery error: {e}")
            return False


    def set_variable(self, success):
        """Set variable with result"""
        variable = self.params.get("variable", "")
        if variable:
            GlobalVariables().set(variable, "true" if success else "false")