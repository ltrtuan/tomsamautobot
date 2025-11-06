# models/gologin_api.py
from gologin import GoLogin
from gologin import getRandomPort
import requests
import time
import tempfile
import os
import subprocess
import psutil
import json

class GoLoginAPI:
    """Class quản lý GoLogin API - 3 methods: Create, Start, Stop"""
    
    def __init__(self, api_token):
        self.api_token = api_token
        self.gl = None
        self.base_url = "https://api.gologin.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        # ← THÊM: Dictionary lưu GoLogin instances theo profile_id
        self.active_profiles = {}  # {profile_id: GoLogin_instance}
        
        # ← FIX #1: Set tmpdir to system temp directory
        self.tmpdir = tempfile.gettempdir()  # C:\Users\xxx\AppData\Local\Temp
        print(f"[GOLOGIN] Using temp directory: {self.tmpdir}")
    
    def create_profile(self, profile_name, os_type="win", language="en-US", enable_proxy=False, country_code="US"):
        """
        Tạo profile mới - CHỈ TẠO, không launch
        Returns: (success, profile_id or error_message)
        """
        try:
            # ← FIX #2: Thêm tmpdir vào GoLogin init
            self.gl = GoLogin({
                "token": self.api_token,
                "tmpdir": self.tmpdir
            })
            
            profile_data = {
                "name": profile_name,
                "os": os_type,
                "navigator": {
                    "language": language,
                    "userAgent": "random",
                    "resolution": "1920x1080",
                }
            }
            
            # Proxy config
            if enable_proxy:
                profile_data["proxyEnabled"] = True
                profile_data["proxy"] = {
                    "mode": "gologin",
                    "autoProxyRegion": country_code.lower()
                }
            else:
                profile_data["proxyEnabled"] = False
                profile_data["proxy"] = {
                    "mode": "none",
                    "host": "",
                    "port": "",
                    "username": "",
                    "password": ""
                }
            
            print(f"[GOLOGIN] Creating profile: {profile_name}")
            
            # Create profile
            profile_id = self.gl.create(profile_data)
            
            if profile_id:
                print(f"[GOLOGIN] ✓ Profile created: {profile_id}")
                print(f"[GOLOGIN] ⚠ Wait 2-3 minutes before launching")
                return True, profile_id
            else:
                return False, "Failed to create profile"
            
        except Exception as e:
            print(f"[GOLOGIN] Create error: {e}")
            return False, str(e)
    
    def start_profile(self, profile_id, wait_for_ready=True, max_wait=180, extra_params=None):
        """
        Start profile đã tồn tại
        Args:
            profile_id: Profile ID to start
            wait_for_ready: Poll until profile ready (default True)
            max_wait: Max seconds to wait (default 180 = 3 mins)
            extra_params: List of browser flags (e.g. ['--headless=new'])
        Returns: (success, debugger_address or error_message)
        """
        try:
            # Validate profile_id
            profile_id = str(profile_id).strip()
            if ',' in profile_id or ';' in profile_id or not profile_id:
                return False, f"Invalid profile_id: {profile_id}"
        
            print(f"[GOLOGIN] Starting profile: {profile_id}")
        
            if extra_params:
                print(f"[GOLOGIN] Browser flags: {', '.join(extra_params)}")       


            # ========== THÊM: Retry mechanism ==========
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    # Initialize GoLogin with tmpdir and extra_params
                    random_port = getRandomPort()
                    gologin_config = {
                        "token": self.api_token,
                        "profile_id": profile_id,
                        # "tmpdir": self.tmpdir,                      
                        "uploadCookiesToServer": True,
                        "port": random_port
                    }
                    
                    default_extra_params = [
                        '--disable-blink-features=AutomationControlled',
                        '--disable-infobars',
                        '--start-maximized',
                        '--no-first-run',
                        '--no-default-browser-check',
                        '--disable-popup-blocking',  # Optional: Tránh popup block
                    ]

                    # Start with defaults
                    final_extra_params = default_extra_params.copy()

                    # Override/Add custom params (nếu trùng → xóa default, thêm custom vào cuối)
                    if extra_params and isinstance(extra_params, list):
                        for param in extra_params:
                            # Xóa param khỏi defaults nếu đã tồn tại (để tránh duplicate)
                            if param in final_extra_params:
                                final_extra_params.remove(param)
                            # Thêm param vào cuối (custom override default)
                            final_extra_params.append(param)

                    gologin_config["extra_params"] = final_extra_params
                
                    self.gl = GoLogin(gologin_config)
                
                    # Start browser
                    if attempt > 0:
                        print(f"[GOLOGIN] Retry attempt {attempt + 1}/{max_retries}...")
                    else:
                        print(f"[GOLOGIN] Launching browser...")
                    
                    debugger_address = self.gl.start()
                
                    if debugger_address:
                        self.active_profiles[profile_id] = self.gl
                        print(f"[GOLOGIN] ✓ Profile started!")
                        print(f"[GOLOGIN] Debugger: {debugger_address}")
                        return True, debugger_address
                
                except FileNotFoundError as e:
                    # Profile download incomplete - retry
                    if attempt < max_retries - 1:
                        print(f"[GOLOGIN] ⚠ Profile extraction issue (Preferences not found)")
                        print(f"[GOLOGIN] Cleaning temp folder and retrying...")
                    
                        # Clean up temp folder
                        import shutil
                        temp_path = os.path.join(self.tmpdir, f"gologin_{profile_id}")
                        if os.path.exists(temp_path):
                            try:
                                shutil.rmtree(temp_path)
                                print(f"[GOLOGIN] Cleaned: {temp_path}")
                            except Exception as clean_err:
                                print(f"[GOLOGIN] Cleanup warning: {clean_err}")
                    
                        time.sleep(3)  # Wait before retry
                        continue
                    else:
                        # Last attempt failed
                        raise
            
                except Exception as e:
                    # Other errors
                    if attempt < max_retries - 1:
                        print(f"[GOLOGIN] ⚠ Start error (attempt {attempt + 1}): {str(e)[:100]}")
                        time.sleep(2)
                        continue
                    else:
                        raise
        
            return False, "Failed after retries"
        
        except Exception as e:
            print(f"[GOLOGIN] Start error: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)


    
    def stop_profile(self, profile_id):
        """
        Stop profile - Close browser and cleanup processes WITH TIMEOUT
        Prevents hanging when gl.stop() doesn't return
        """
        import threading
    
        profile_id = str(profile_id).strip()
        print(f"[GOLOGIN] Stopping profile: {profile_id}")
    
        # Check if profile is active
        if profile_id not in self.active_profiles:
            print(f"[GOLOGIN] ⚠ No active instance found for {profile_id}")
            return False, "Profile not running"
    
        gl = self.active_profiles[profile_id]
    
        # Result container (shared between threads)
        stop_result = {"success": False, "message": "Unknown error", "completed": False}
        
        def _stop_internal():
            """Internal stop logic with timeout protection"""           
            try:                                 
                print(f"[GOLOGIN] Closing browser and syncing data to cloud...")
                gl.stop()
                stop_result["success"] = True
                stop_result["message"] = "Profile stopped successfully"
                print(f"[GOLOGIN] ✓ gl.stop() {profile_id} completed successfully")
                    
                # ========== NEW: FORCE KILL CHROME IMMEDIATELY ==========
                # CRITICAL: gl.stop() may not kill Chrome subprocesses!
                # Kill immediately to release DB locks for other profiles
                # print(f"[GOLOGIN] Force killing Chrome to release file locks...")
                # time.sleep(2)  # Let SDK finish file operations
                # self._force_kill_browser_processes(profile_id)
                # print(f"[GOLOGIN] ✓ Chrome killed, DB locks released")
                
            except Exception as stop_err:               
                stop_result["success"] = False
                stop_result["message"] = f"Failed STOP PROFILEEEEEEEEE: {stop_err}"
            finally:
                # ========== ALWAYS SET COMPLETED (CRITICAL!) ==========
                stop_result["completed"] = True  # ← MOVED TO FINALLY!

    
        # Run gl.stop() in separate thread with 60s timeout
        stop_thread = threading.Thread(target=_stop_internal, daemon=False)
        stop_thread.start()
        print(f"[GOLOGIN] Waiting for gl.stop() to complete (max 180s)...")
        stop_thread.join(timeout=180)
    
        # Check if thread completed
        if not stop_result["completed"]:
            # TIMEOUT - Force kill immediately
            print(f"[GOLOGIN] ⚠ gl.stop() TIMEOUT after 180s")
            print(f"[GOLOGIN] Force killing browser processes due to timeout...")
        
            try:
                self._force_kill_browser_processes(profile_id)
            except Exception as kill_err:
                print(f"[GOLOGIN] ⚠ Force kill error: {kill_err}")
        
            # stop_result["success"] = False
            # stop_result["message"] = "Stop timeout - forced cleanup"
    
        else:
            # Thread completed - check if successful or error
            if stop_result["success"]:
                # gl.stop() completed successfully
                print(f"[GOLOGIN] ✓ gl.stop() completed successfully")
                print(f"[GOLOGIN] Waiting 5s for cloud sync to complete...")
                time.sleep(5)
        
                # Check if browser processes still exist
                try:
                    import psutil
                    profile_folder = f"gologin_{profile_id}".lower()
                    browser_still_running = False
            
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        try:
                            proc_name = proc.info['name'].lower() if proc.info['name'] else ''
                            is_browser = any(name in proc_name for name in ['orbita', 'chrome', 'chromium'])
                            if is_browser and proc.info['cmdline']:
                                cmdline = ' '.join(proc.info['cmdline']).lower()
                                if profile_folder in cmdline:
                                    browser_still_running = True
                                    print(f"[GOLOGIN] ⚠ Browser process {proc.info['pid']} still running after gl.stop()")
                                    break
                        except:
                            pass
            
                    if browser_still_running:
                        print(f"[GOLOGIN] Force killing remaining browser processes...")
                        self._force_kill_browser_processes(profile_id)
                    else:
                        print(f"[GOLOGIN] ✓ Browser closed naturally")
                        # Cleanup leftover files manually (no force kill needed)
                        self._cleanup_temp_files(profile_id)
                except Exception as verify_err:
                    print(f"[GOLOGIN] ⚠ Verification warning: {verify_err}")
    
            else:
                # gl.stop() completed but with error
                error_msg = stop_result['message']
        
                # Check if error is ONLY WinError 32 on *_upload.zip (NON-CRITICAL)
                is_upload_zip_lock = ("WinError 32" in error_msg or "being used by another process" in error_msg) and "_upload.zip" in error_msg
        
                if is_upload_zip_lock:
                    # This is acceptable - cookies already synced, just file cleanup issue
                    print(f"[GOLOGIN] ℹ gl.stop() completed with file lock warning (non-critical)")
                    print(f"[GOLOGIN] → Cookies synced successfully, only temp file cleanup pending")
            
                    # Still check if browser closed
                    print(f"[GOLOGIN] Checking if browser closed...")
                    time.sleep(3)
            
                    try:
                        import psutil
                        profile_folder = f"gologin_{profile_id}".lower()
                        browser_running = False
                
                        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                            try:
                                proc_name = proc.info['name'].lower() if proc.info['name'] else ''
                                if 'chrome' in proc_name and proc.info['cmdline']:
                                    cmdline = ' '.join(proc.info['cmdline']).lower()
                                    if profile_folder in cmdline:
                                        browser_running = True
                                        break
                            except:
                                pass
                
                        if browser_running:
                            print(f"[GOLOGIN] Browser still running, force killing...")
                            self._force_kill_browser_processes(profile_id)
                        else:
                            print(f"[GOLOGIN] ✓ Browser already closed")
                            # Cleanup files with retry (after Chrome closed)
                            self._cleanup_temp_files(profile_id)
                    
                    except Exception as e:
                        print(f"[GOLOGIN] ⚠ Cleanup error: {e}")
                else:
                    # Other errors - force kill needed
                    print(f"[GOLOGIN] ⚠ gl.stop() error: {error_msg}")
                    print(f"[GOLOGIN] Force killing browser processes...")
                    try:
                        self._force_kill_browser_processes(profile_id)
                    except Exception as kill_err:
                        print(f"[GOLOGIN] ⚠ Force kill error: {kill_err}")

    
        # Remove from active profiles
        try:
            del self.active_profiles[profile_id]
        except:
            pass
    
        if stop_result["success"]:
            print(f"[GOLOGIN] ✓ Profile stopped successfully!")
            return True, "Profile stopped"
        else:
            print(f"[GOLOGIN] ⚠ Profile stopped with warnings: {stop_result['message']}")
            # Still return True because profile is cleaned up
            return False, f"Stopped with warnings: {stop_result['message']}"


    def _cleanup_temp_files(self, profile_id, max_retries=5):
        """
        Cleanup temp files WITHOUT force killing browser
        Used when browser already closed naturally
    
        Args:
            profile_id: Profile ID
            max_retries: Max retry attempts for locked files
        """
        try:
            import shutil
            print(f"[GOLOGIN] [{profile_id}] Cleaning up temp files...")
        
            profile_temp_path = os.path.join(self.tmpdir, f"gologin_{profile_id}")
            upload_zip_path = os.path.join(self.tmpdir, f"gologin_{profile_id}_upload.zip")
            debug_log = os.path.join(profile_temp_path, "chrome_debug.log")
        
            # Wait for file handles to release
            time.sleep(2)
        
            # 1. Cleanup chrome_debug.log
            if os.path.exists(debug_log):
                for attempt in range(3):
                    try:
                        os.remove(debug_log)
                        print(f"[GOLOGIN] [{profile_id}] ✓ Deleted chrome_debug.log")
                        break
                    except PermissionError:
                        if attempt < 2:
                            time.sleep(2)
                        else:
                            print(f"[GOLOGIN] [{profile_id}] ⚠ Could not delete chrome_debug.log (non-critical)")
        
            # 2. Cleanup *_upload.zip with retry
            if os.path.exists(upload_zip_path):
                for attempt in range(max_retries):
                    try:
                        os.remove(upload_zip_path)
                        print(f"[GOLOGIN] [{profile_id}] ✓ Deleted upload.zip")
                        break
                    except PermissionError:
                        if attempt < max_retries - 1:
                            wait_time = 2 + attempt  # 2s, 3s, 4s, 5s, 6s
                            print(f"[GOLOGIN] [{profile_id}] ⚠ upload.zip locked (attempt {attempt + 1}/{max_retries}), waiting {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            print(f"[GOLOGIN] [{profile_id}] ⚠ Could not delete upload.zip (non-critical)")
        
            # 3. Cleanup profile folder
            if os.path.exists(profile_temp_path):
                for attempt in range(3):
                    try:
                        shutil.rmtree(profile_temp_path)
                        print(f"[GOLOGIN] [{profile_id}] ✓ Deleted profile folder")
                        break
                    except PermissionError:
                        if attempt < 2:
                            time.sleep(2)
                        else:
                            print(f"[GOLOGIN] [{profile_id}] ⚠ Could not delete profile folder (non-critical)")
        
            print(f"[GOLOGIN] [{profile_id}] ✓ Temp file cleanup completed")
        
        except Exception as e:
            print(f"[GOLOGIN] [{profile_id}] Cleanup temp files error: {e}")

        
    def _force_kill_browser_processes(self, profile_id):
        """
        Force kill Chrome processes ONLY for THIS SPECIFIC profile
        Uses SAME LOGIC as helper's kill_zombie_chrome_processes()
        """
        try:
            import psutil
            import shutil
            killed_count = 0
        
            profile_folder = f"gologin_{profile_id}".lower()
            print(f"[GOLOGIN] [{profile_id}] Force killing Chrome processes...")
        
            # Kill Chrome processes for this profile
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'exe']):
                try:
                    proc_name = proc.info['name'].lower() if proc.info['name'] else ''
                    pid = proc.info['pid']
                    # ONLY kill chrome.exe (NOT gologin.exe)
                    if proc_name != 'chrome.exe':
                        continue
                
                    cmdline = proc.info.get('cmdline', [])
                    if not cmdline:
                        continue
                
                    cmdline_str = ' '.join(cmdline).lower()
                    exe_path = proc.info.get('exe', '').lower() if proc.info.get('exe') else ''
                
                    # Check if belongs to this profile
                    belongs_to_profile = profile_folder in cmdline_str
                    
                    if not belongs_to_profile:
                      
                        continue
                
                    # Additional safety: Must be GoLogin Orbita
                    is_gologin_orbita = (
                        ('.gologin' in exe_path and 'orbita' in exe_path) or
                        ('appdata\\local\\gologin\\browser' in exe_path) or
                        ('.gologin' in cmdline_str and 'orbita' in cmdline_str)
                    )
                
                  
                
                    if not is_gologin_orbita:
                     
                        continue
                
                    # Verify user-data-dir or profile-directory flag
                    has_profile_flag = (
                        '--user-data-dir' in cmdline_str or
                        '--profile-directory' in cmdline_str
                    )                 
                
                    if not has_profile_flag:
                        continue
                
                    # ALL checks passed - safe to kill
                    print(f"[GOLOGIN] [{profile_id}] Killing PID {proc.info['pid']} (chrome.exe)")
                    proc.kill()
                    killed_count += 1
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):                   
                    pass
        
            if killed_count > 0:
                print(f"[GOLOGIN] [{profile_id}] ✓ Killed {killed_count} Chrome process(es)")
                time.sleep(2)  # Wait for processes to die
            else:
                print(f"[GOLOGIN] [{profile_id}] No Chrome processes found")
        
            # ========== CLEANUP FILES (LIKE HELPER) ==========
            print(f"[GOLOGIN] [{profile_id}] Cleaning up profile files...")
        
            # Cleanup chrome_debug.log
            profile_temp_path = os.path.join(self.tmpdir, f"gologin_{profile_id}")
            debug_log = os.path.join(profile_temp_path, "chrome_debug.log")
        
            if os.path.exists(debug_log):
                try:
                    os.remove(debug_log)
                    print(f"[GOLOGIN] [{profile_id}] ✓ Deleted chrome_debug.log")
                except Exception as log_err:
                    print(f"[GOLOGIN] [{profile_id}] ⚠ Could not delete chrome_debug.log: {log_err}")
        
            # Cleanup profile folder
            if os.path.exists(profile_temp_path):
                try:
                    shutil.rmtree(profile_temp_path)
                    print(f"[GOLOGIN] [{profile_id}] ✓ Deleted profile folder: {profile_temp_path}")
                except Exception as folder_err:
                    print(f"[GOLOGIN] [{profile_id}] ⚠ Could not delete profile folder: {folder_err}")
        
        except Exception as e:
            print(f"[GOLOGIN] [{profile_id}] ⚠ Force kill error: {e}")
            import traceback
            traceback.print_exc()


    def remove_proxy_for_profiles(self, profile_ids):
        """
        Remove proxy (set to 'Without proxy') for multiple profiles
    
        Flow: GET profile → modify proxyEnabled + proxy object → PUT profile
        API: GET/PUT https://api.gologin.com/browser/:profileId
    
        Args:
            profile_ids: List of profile IDs or single profile_id (string)
    
        Returns:
            (success: bool, message: str)
        """
        try:
            if isinstance(profile_ids, str):
                profile_ids = [profile_ids]
        
            print(f"[GOLOGIN] Removing proxy for {len(profile_ids)} profile(s)...")
        
            failed_profiles = []
            success_count = 0
        
            for profile_id in profile_ids:
                try:
                    url = f"{self.base_url}/browser/{profile_id}"
                
                    # Step 1: GET current profile data
                    get_response = requests.get(url, headers=self.headers, timeout=30)
                
                    if get_response.status_code != 200:
                        print(f"[GOLOGIN] ✗ Failed to GET profile {profile_id[:8]}...: Status {get_response.status_code}")
                        failed_profiles.append(profile_id)
                        continue
                
                    profile_data = get_response.json()
                
                    # Step 2: Modify proxy settings (BOTH proxyEnabled AND proxy object)
                    profile_data['proxyEnabled'] = False  # ← Disable proxy
                    profile_data['proxy'] = {              # ← Reset proxy object to "none"
                        "id": None,
                        "mode": "none",
                        "host": "",
                        "port": 0,
                        "username": "",
                        "password": "",
                        "changeIpUrl": None,
                        "customName": None,
                        "autoProxyRegion": "",
                        "torProxyRegion": ""
                    }
                
                    # Step 3: PUT updated profile back (with retry)
                    max_retries = 3
                    retry_delay = 2
                
                    for attempt in range(1, max_retries + 1):
                        try:
                            put_response = requests.put(url, json=profile_data, headers=self.headers, timeout=30)
                        
                            if put_response.status_code in [200, 201, 204]:
                                print(f"[GOLOGIN] ✓ Proxy removed for profile {profile_id[:8]}...")
                                success_count += 1
                                break
                            else:
                                error_msg = f"Status {put_response.status_code}"
                                try:
                                    error_data = put_response.json()
                                    error_msg = error_data.get('message', error_msg)
                                except:
                                    pass
                            
                                if attempt == max_retries:
                                    print(f"[GOLOGIN] ✗ Failed PUT for {profile_id[:8]}...: {error_msg}")
                                    failed_profiles.append(profile_id)
                    
                        except (requests.exceptions.SSLError, ConnectionError, requests.exceptions.ConnectionError) as e:
                            if attempt < max_retries:
                                wait_time = retry_delay * (2 ** (attempt - 1))
                                print(f"[GOLOGIN] Retry {attempt}/{max_retries} for {profile_id[:8]}...")
                                time.sleep(wait_time)
                            else:
                                print(f"[GOLOGIN] ✗ SSL error for {profile_id[:8]}...")
                                failed_profiles.append(profile_id)
                    
                        except requests.exceptions.Timeout:
                            if attempt < max_retries:
                                time.sleep(retry_delay)
                            else:
                                print(f"[GOLOGIN] ✗ Timeout for {profile_id[:8]}...")
                                failed_profiles.append(profile_id)
            
                except Exception as e:
                    print(f"[GOLOGIN] ✗ Exception for {profile_id[:8]}...: {e}")
                    failed_profiles.append(profile_id)
        
            # Summary
            if failed_profiles:
                return False, f"Removed proxy for {success_count}/{len(profile_ids)} profiles. Failed: {len(failed_profiles)}"
            else:
                print(f"[GOLOGIN] ✓ Proxy removed for all {len(profile_ids)} profiles")
                return True, f"Proxy removed for {len(profile_ids)} profiles"
    
        except Exception as e:
            print(f"[GOLOGIN] Error removing proxy: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)



    # def stop_profile(self, profile_id, clean_profile=False):
    #     """Stop profile - Close browser nhưng có thể giữ profile data"""
    #     try:
    #         profile_id = str(profile_id).strip()
    #         print(f"[GOLOGIN] Stopping profile: {profile_id}")
        
    #         if profile_id in self.active_profiles:
    #             gl = self.active_profiles[profile_id]
            
    #             if not clean_profile:
    #                 # Override cleanup để không xóa folder
    #                 print(f"[GOLOGIN] Closing browser (keeping temp data)...")
                
    #                 # Save original
    #                 original_cleanup = getattr(gl, 'cleanupProfile', None)
                
    #                 # Override
    #                 gl.cleanupProfile = lambda: None
                
    #                 # Stop (sẽ KHÔNG xóa temp)
    #                 gl.stop()
                
    #                 # Restore
    #                 if original_cleanup:
    #                     gl.cleanupProfile = original_cleanup
                
    #                 print(f"[GOLOGIN] 💾 Profile data preserved")
    #             else:
    #                 # Full cleanup
    #                 print(f"[GOLOGIN] Closing browser with cleanup...")
    #                 gl.stop()
            
    #             del self.active_profiles[profile_id]
    #             print(f"[GOLOGIN] ✓ Profile stopped!")
    #             return True, "Profile stopped"
        
    #         else:
    #             print(f"[GOLOGIN] ⚠ No active instance found")
    #             return False, "Profile not running"
        
    #     except Exception as e:
    #         print(f"[GOLOGIN] Stop error: {e}")
    #         return False, str(e)

    
    def stop_profile_by_id(self, profile_id):
        """
        Stop profile by ID sử dụng REST API
        Endpoint: DELETE /browser/{id}/web
        Returns: (success, message)
        """
        try:
            # ← FIX #5: Validate profile_id
            profile_id = str(profile_id).strip()
            if ',' in profile_id or ';' in profile_id:
                return False, f"Invalid profile_id format: {profile_id}. Must be single ID"
            
            url = f"{self.base_url}/browser/{profile_id}/web"
            
            print(f"[GOLOGIN] Stopping profile via API: {profile_id}")
            
            response = requests.delete(url, headers=self.headers)
            
            # Check response status
            if response.status_code == 200 or response.status_code == 204:
                print(f"[GOLOGIN] ✓ Profile stopped successfully (via API)")
                return True, "Stopped successfully"
            else:
                error_msg = f"API returned status {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", error_msg)
                except:
                    pass
                print(f"[GOLOGIN] ✗ Stop failed: {error_msg}")
                return False, error_msg
            
        except Exception as e:
            print(f"[GOLOGIN] Stop API error: {e}")
            return False, str(e)
    
    def refresh_fingerprint(self, profile_ids):
        """
        Refresh fingerprint for profiles using GoLogin API
        API: PATCH https://api.gologin.com/browser/fingerprints
        Documentation: https://gologin.com/docs/api-reference/profile/refresh-profile-fingerprint
    
        Args:
            profile_ids: Single profile_id (string) or list of profile_ids
    
        Returns: (success: bool, message: str)
        """
        try:
            # Ensure profile_ids is a list
            if isinstance(profile_ids, str):
                profile_ids = [profile_ids]
        
            print(f"[GOLOGIN] Refreshing fingerprint for {len(profile_ids)} profile(s)...")
        
            url = f"{self.base_url}/browser/fingerprints"
        
            # Build request body with browsersIds key
            request_body = {
                "browsersIds": profile_ids
            }
        
            print(f"[DEBUG] Calling: PATCH {url}")
            print(f"[DEBUG] Request body: {request_body}")
        
            response = requests.patch(
                url,
                headers=self.headers,
                json=request_body,
                timeout=30
            )
        
            print(f"[DEBUG] Response Status: {response.status_code}")
        
            if response.status_code in [200, 201, 204]:
                print(f"[GOLOGIN] ✓ Profile fingerprint(s) refreshed successfully")
                try:
                    result = response.json()
                except:
                    pass
                return True, f"Refreshed {len(profile_ids)} profile(s) successfully"
            else:
                print(f"[GOLOGIN] Refresh error: Status {response.status_code}")
                print(f"[DEBUG] === ERROR RESPONSE ===")
                try:
                    import json
                    error_json = response.json()
                    print(json.dumps(error_json, indent=2, ensure_ascii=False)[:1500])
                except:
                    print(response.text[:1500])
                print(f"[DEBUG] === END ERROR ===")
                return False, f"Failed to refresh: Status {response.status_code}"
            
        except Exception as e:
            print(f"[GOLOGIN] Error refreshing fingerprint: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)

    def update_proxy_for_profiles(self, profile_ids, proxy_config):
        """
        Update proxy for multiple profiles using GoLogin API
    
        API: PATCH https://api.gologin.com/browser/proxy/many/v2
        Documentation: https://gologin.com/docs/api-reference/profile/update-proxy-for-multiple-profiles
    
        Args:
            profile_ids: List of profile IDs
            proxy_config: Dict with keys (mode, host, port, username, password)
    
        Returns:
            (success: bool, message: str)
        """
        try:
            # Validate inputs
            if isinstance(profile_ids, str):
                profile_ids = [profile_ids]
        
            required_fields = ['mode', 'host', 'port', 'username', 'password']
            for field in required_fields:
                if not proxy_config.get(field):
                    return False, f"Proxy field '{field}' is missing or empty"
        
            # Convert port to int
            try:
                port = int(proxy_config['port'])
            except ValueError:
                return False, f"Invalid port number: {proxy_config['port']}"
        
            print(f"[GOLOGIN] Updating proxy for {len(profile_ids)} profile(s)...")
            print(f"[GOLOGIN] Proxy: {proxy_config['mode']}://{proxy_config['host']}:{port}")
        
            # Build payload
            proxies_array = []
            for profile_id in profile_ids:
                proxy_data = {
                    "profileId": profile_id,
                    "proxy": {
                        "id": None,
                        "mode": proxy_config["mode"],
                        "host": proxy_config["host"],
                        "port": port,
                        "username": proxy_config["username"],
                        "password": proxy_config["password"],
                        "changeIpUrl": None,
                        "customName": None
                    }
                }
                proxies_array.append(proxy_data)
        
            payload = {"proxies": proxies_array}
            url = f"{self.base_url}/browser/proxy/many/v2"
        
            # RETRY LOGIC FOR SSL ERRORS (FIX)
            max_retries = 3
            retry_delay = 2  # seconds (exponential backoff)
        
            for attempt in range(1, max_retries + 1):
                try:
                    # Send PATCH request
                    response = requests.patch(url, json=payload, headers=self.headers, timeout=30)
                
                    # Check response status
                    if response.status_code in [200, 201, 204]:
                        print(f"[GOLOGIN] ✓ Proxy updated successfully for all profiles")
                        return True, f"Proxy updated for {len(profile_ids)} profiles"
                    else:
                        error_msg = f"API returned status {response.status_code}"
                        try:
                            error_data = response.json()
                            error_msg = error_data.get('message', error_msg)
                        except:
                            error_msg = f"{error_msg}: {response.text[:200]}"
                    
                        print(f"[GOLOGIN] Proxy update failed: {error_msg}")
                        return False, error_msg
            
                except (requests.exceptions.SSLError, 
                        ConnectionError, 
                        requests.exceptions.ConnectionError) as e:
                    # SSL/Connection errors - retry with backoff
                    error_str = str(e)
                    print(f"[GOLOGIN] Attempt {attempt}/{max_retries} - SSL/Connection error: {error_str[:150]}")
                
                    if attempt < max_retries:
                        wait_time = retry_delay * (2 ** (attempt - 1))  # Exponential backoff: 2s, 4s, 8s
                        print(f"[GOLOGIN] Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        # All retries exhausted
                        print(f"[GOLOGIN] ❌ All {max_retries} attempts failed - SSL/Connection error")
                        return False, f"SSL/Connection error after {max_retries} attempts: {error_str[:200]}"
            
                except requests.exceptions.Timeout:
                    # Timeout - retry
                    print(f"[GOLOGIN] Attempt {attempt}/{max_retries} - Request timeout (30s)")
                    if attempt < max_retries:
                        print(f"[GOLOGIN] Retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        return False, f"Request timeout after {max_retries} attempts"
    
        except Exception as e:
            print(f"[GOLOGIN] Error updating proxy: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)




    def update_cookies(self, profile_id, cookies, replace_all=True):
        """
        Update cookies for profile
        API: POST https://api.gologin.com/browser/{profile_id}/cookies?cleanCookies={replace_all}
        Body: [] (empty array to delete all)
        """
        try:
            url = f"{self.base_url}/browser/{profile_id}/cookies"
            params = {
                "cleanCookies": str(replace_all).lower()
            }
           
            response = requests.post(url, headers=self.headers, params=params, json=cookies, timeout=30)
        
            if response.status_code in [200, 204]:                
                return True, "Cookies updated successfully"
            else:
                return False, f"Status {response.status_code}: {response.text}"
        except Exception as e:
            return False, str(e)

    def add_cookies_to_profile(self, profile_id, cookies_file_path):
        """
        Add cookies to profile BEFORE starting using addCookiesToProfile()
        This is the CORRECT way per GoLogin docs
        :param profile_id: Profile ID
        :param cookies_file_path: Path to cookies JSON file
        :return: (success, message)
        """
        try:
            profile_id = str(profile_id).strip()
        
            # Load cookies from file
            if not os.path.exists(cookies_file_path):
                return False, "Cookies file not found"
        
            with open(cookies_file_path, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
        
            if not cookies_data:
                return False, "No cookies in file"
        
            # Convert format if needed (your format already matches)
            cookies_for_gologin = []
            for cookie in cookies_data:
                gl_cookie = {
                    "name": cookie.get("name"),
                    "value": cookie.get("value"),
                    "domain": cookie.get("domain"),
                    "path": cookie.get("path", "/"),
                    "secure": cookie.get("secure", False),
                    "httpOnly": cookie.get("httpOnly", False)
                }
            
                # Add expirationDate if not session cookie
                if not cookie.get("session", False) and "expirationDate" in cookie:
                    gl_cookie["expirationDate"] = cookie["expirationDate"]
            
                # Add sameSite if present
                if "sameSite" in cookie and cookie["sameSite"] != "unspecified":
                    gl_cookie["sameSite"] = cookie["sameSite"]
            
                cookies_for_gologin.append(gl_cookie)
        
            # Create temporary GoLogin instance for this operation
            gl = GoLogin({
                "token": self.api_token,
                "profile_id": profile_id,
                "tmpdir": self.tmpdir
            })
        
            # Add cookies using SDK method
            print(f"[GOLOGIN] Adding {len(cookies_for_gologin)} cookies to profile...")
            gl.addCookiesToProfile(profile_id, cookies_for_gologin)
        
            print(f"[GOLOGIN] ✓ Cookies added to profile")
            return True, f"Added {len(cookies_for_gologin)} cookies"
        
        except Exception as e:
            print(f"[GOLOGIN] Error adding cookies: {e}")
            return False, str(e)




    def get_cookies(self, profile_id):
        """
        Get cookies from profile using GoLogin API
        API: GET https://api.gologin.com/browser/{profile_id}/cookies
        Returns: (success: bool, cookies_data: list or error_message: str)
        """
        try:
            profile_id = str(profile_id).strip()
            url = f"{self.base_url}/browser/{profile_id}/cookies"
        
            print(f"[GOLOGIN] Getting cookies for profile: {profile_id}")
        
            response = requests.get(url, headers=self.headers, timeout=30)
        
            if response.status_code == 200:
                cookies_data = response.json()
                print(f"[GOLOGIN] ✓ Retrieved {len(cookies_data)} cookie(s)")
                return True, cookies_data
            else:
                error_msg = f"API returned status {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", error_msg)
                except:
                    pass
                print(f"[GOLOGIN] ✗ Get cookies failed: {error_msg}")
                return False, error_msg
            
        except Exception as e:
            print(f"[GOLOGIN] Get cookies error: {e}")
            return False, str(e)

    def clone_profile_multi(self, profile_id):
        """
        Clone a profile using clone_multi API
        API: POST https://api.gologin.com/browser/clone_multi
        Documentation: https://gologin.com/docs/api-reference/profile/clone-multiple-profiles
    
        Args:
            profile_id: ID of profile to clone (single profile)
    
        Returns:
            tuple: (success: bool, result: list of new profile IDs or error message)
        """
        try:
            url = f"{self.base_url}/browser/clone_multi"
        
            # Validate profile_id
            profile_id = str(profile_id).strip()
            if not profile_id:
                return False, "Profile ID is required"
        
            payload = {
                "browsersIds": [profile_id]
            }
        
            print(f"[GOLOGIN] Cloning profile via API: {profile_id}")
            print(f"[DEBUG] POST {url}")
            print(f"[DEBUG] Payload: {payload}")
        
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
        
            print(f"[DEBUG] Response Status: {response.status_code}")
        
            # HTTP 204 = Success but no content (async operation)
            if response.status_code == 204:
                print(f"[GOLOGIN] ✓ Clone request accepted (HTTP 204 - async)")
                return True, []  # Empty list indicates async operation
        
            # Try to parse response body
            try:
                response_body = response.json()
                print(f"[DEBUG] Response Body: {response_body}")
            except:
                if response.text:
                    print(f"[DEBUG] Response Text: {response.text[:200]}")
                else:
                    print(f"[DEBUG] Response: (empty body)")
        
            if response.status_code in [200, 201]:
                data = response.json()
            
                # API returns array of new profile IDs
                if isinstance(data, list) and len(data) > 0:
                    print(f"[GOLOGIN] ✓ Profile cloned! New IDs: {data}")
                    return True, data
                else:
                    print(f"[GOLOGIN] ⚠ Clone successful but no IDs in response")
                    return True, []
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", error_msg)
                except:
                    error_msg = f"{error_msg}: {response.text[:200]}"
            
                print(f"[GOLOGIN] ✗ Clone failed: {error_msg}")
                return False, error_msg
            
        except Exception as e:
            print(f"[GOLOGIN] Clone API error: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)

    def get_all_profiles(self, count=None, start_index=0):
        """
        Get profiles from GoLogin account with PRECISE range support
        API: GET https://api.gologin.com/browser/v2?page={page}&limit={limit}
    
        Args:
            count: Number of profiles to fetch (None = all)
            start_index: Start from this profile index (0-based)
    
        Returns:
            tuple: (success: bool, profiles: list or error message)
    
        Examples:
            get_all_profiles()              → Fetch ALL profiles
            get_all_profiles(30, 10)        → Fetch 30 profiles from index 10 (profiles 10-39)
            get_all_profiles(50, 0)         → Fetch first 50 profiles
        """
        try:
            # ========== CALCULATE API PARAMS ==========
            limit = 30  # GoLogin API max limit per page
        
            if count is None:
                # Fetch ALL profiles (old behavior)
                print(f"[GOLOGIN] Fetching ALL profiles with pagination...")
                return self._fetch_all_profiles_paginated()
        
            # ========== OPTIMIZED: FETCH ONLY NEEDED PROFILES ==========
            print(f"[GOLOGIN] Fetching {count} profiles starting from index {start_index}")
        
            # Calculate which pages to fetch
            # Example: start_index=10, count=30
            #   → Need profiles 10-39
            #   → Page 1 has profiles 0-29 (need 10-29 = 20 profiles)
            #   → Page 2 has profiles 30-59 (need 30-39 = 10 profiles)
        
            start_page = (start_index // limit) + 1  # Page numbers start from 1
            end_index = start_index + count - 1
            end_page = (end_index // limit) + 1
        
            print(f"[GOLOGIN] Calculated: Need pages {start_page} to {end_page}")
        
            all_profiles = []
        
            for page in range(start_page, end_page + 1):
                url = f"{self.base_url}/browser/v2"
                params = {
                    "limit": limit,
                    "page": page
                }
            
                print(f"[GOLOGIN] Fetching page {page} (limit={limit})...")
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
                if response.status_code != 200:
                    error_msg = f"HTTP {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("message", error_msg)
                    except:
                        error_msg = f"{error_msg}: {response.text[:200]}"
                
                    print(f"[GOLOGIN] ✗ Get profiles failed: {error_msg}")
                    return False, error_msg
            
                # Parse response
                data = response.json()
                profiles_page = []
                if isinstance(data, list):
                    profiles_page = data
                elif isinstance(data, dict):
                    profiles_page = data.get("profiles", data.get("data", []))
            
                print(f"[GOLOGIN] Page {page}: Retrieved {len(profiles_page)} profiles")
            
                if not profiles_page:
                    print(f"[GOLOGIN] Empty page, stopping")
                    break
            
                all_profiles.extend(profiles_page)
        
            # ========== SLICE TO EXACT RANGE ==========
            # We may have fetched extra profiles at edges, slice precisely
            # Example: Fetched pages 1-2 (60 profiles), need profiles 10-39
            #   → Slice: all_profiles[10:40] from concatenated list
        
            # Calculate offset within fetched data
            offset_in_fetched = start_index - ((start_page - 1) * limit)
            selected_profiles = all_profiles[offset_in_fetched:offset_in_fetched + count]
        
            # Extract only profile IDs (or return full profile objects)
            print(f"[GOLOGIN] ✓ SUCCESS: Selected {len(selected_profiles)} profiles")
            return True, selected_profiles
        
        except Exception as e:
            print(f"[GOLOGIN] Get profiles error: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)


    def _fetch_all_profiles_paginated(self):
        """
        Internal method: Fetch ALL profiles with pagination (old behavior)
        Used when count=None
        """
        try:
            all_profiles = []
            seen_profile_ids = set()
            page = 1
            limit = 30
            max_pages = 100
        
            print(f"[GOLOGIN] Fetching ALL profiles with pagination...")
        
            while page <= max_pages:
                url = f"{self.base_url}/browser/v2"
                params = {
                    "limit": limit,
                    "page": page
                }
            
                print(f"[GOLOGIN] Fetching page {page} (limit={limit})...")
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
                if response.status_code != 200:
                    error_msg = f"HTTP {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("message", error_msg)
                    except:
                        error_msg = f"{error_msg}: {response.text[:200]}"
                
                    print(f"[GOLOGIN] ✗ Get profiles failed: {error_msg}")
                    return False, error_msg
            
                # Parse response
                data = response.json()
                profiles_page = []
                if isinstance(data, list):
                    profiles_page = data
                elif isinstance(data, dict):
                    profiles_page = data.get("profiles", data.get("data", []))
            
                # Empty page = end
                if len(profiles_page) == 0:
                    print(f"[GOLOGIN] Empty page, stopping pagination")
                    break
            
                # Deduplicate
                new_profiles_count = 0
                duplicates_in_this_page = 0
            
                for profile in profiles_page:
                    profile_id = profile.get("id")
                    if not profile_id:
                        continue
                
                    if profile_id in seen_profile_ids:
                        duplicates_in_this_page += 1
                        continue
                
                    all_profiles.append(profile)
                    seen_profile_ids.add(profile_id)
                    new_profiles_count += 1
            
                # Log
                if duplicates_in_this_page > 0:
                    print(f"[GOLOGIN] Page {page}: Added {new_profiles_count} new profile(s), skipped {duplicates_in_this_page} duplicate(s)")
                else:
                    print(f"[GOLOGIN] Page {page}: Added {new_profiles_count} new profile(s)")
            
                # Stop if only duplicates
                if new_profiles_count == 0 and duplicates_in_this_page > 0:
                    print(f"[GOLOGIN] ⚠ Page {page} contains only duplicates, stopping pagination")
                    break
            
                page += 1
        
            print(f"[GOLOGIN] ✓ SUCCESS: Retrieved {len(all_profiles)} unique profile(s)")
            return True, all_profiles
        
        except Exception as e:
            print(f"[GOLOGIN] Get profiles error: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)




# ← SINGLETON INSTANCE - Shared across all actions
_gologin_instance = None

def get_gologin_api(api_token):
    """Get or create singleton GoLoginAPI instance"""
    global _gologin_instance
    
    if _gologin_instance is None or _gologin_instance.api_token != api_token:
        _gologin_instance = GoLoginAPI(api_token)
    
    return _gologin_instance

def is_gologin_running():
    """Check if GoLogin app is running"""
    for proc in psutil.process_iter(['name']):
        try:
            if 'gologin' in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def start_gologin_app(app_path, max_wait=60):  # ← TĂNG từ 30s lên 60s
    """
    Start GoLogin app and wait until ready
    Args:
        app_path: Full path to GoLogin.exe
        max_wait: Max seconds to wait for app ready (default 60s)
    Returns: (success: bool, message: str)
    """
    import time
    
    print(f"[GOLOGIN] Checking if GoLogin app is running...")
    
    # Check if already running
    if is_gologin_running():
        print(f"[GOLOGIN] ✓ GoLogin app already running")
        return True, "Already running"
    
    # Validate path
    if not os.path.exists(app_path):
        return False, f"GoLogin app not found at: {app_path}"
    
    try:
        print(f"[GOLOGIN] Starting GoLogin app: {app_path}")
        
        # Start app (detached process)
        subprocess.Popen(
            [app_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False
        )
        
        # Wait for app to start
        start_time = time.time()
        check_count = 0
        
        while time.time() - start_time < max_wait:
            check_count += 1
            
            if is_gologin_running():
                elapsed = int(time.time() - start_time)
                print(f"[GOLOGIN] ✓ GoLogin app started after {elapsed}s (checked {check_count} times)")
                
                # Extra wait for full initialization
                print(f"[GOLOGIN] Waiting 5s for full initialization...")
                time.sleep(5)
                
                return True, "Started successfully"
            
            # ← THÊM: Print progress
            if check_count % 5 == 0:
                print(f"[GOLOGIN] Still waiting... ({check_count} checks, {int(time.time() - start_time)}s elapsed)")
            
            time.sleep(1)
        
        # Timeout
        elapsed = int(time.time() - start_time)
        return False, f"GoLogin app did not start within {max_wait}s ({check_count} checks)"
        
    except Exception as e:
        return False, f"Failed to start: {str(e)}"
