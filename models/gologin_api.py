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
                        "tmpdir": self.tmpdir,
                        "writeCookesFromServer": True,
                        "uploadCookiesToServer": True,
                        "port": random_port
                    }
                
                    # Add extra_params if provided (for headless mode)
                    if extra_params and isinstance(extra_params, list):
                        gologin_config["extra_params"] = extra_params
                
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
                print(f"[GOLOGIN] ✓ gl.stop() completed")
            except Exception as stop_err:
                print(f"[GOLOGIN] ⚠ Stop error: {stop_err}")
                stop_result["success"] = False
                stop_result["message"] = str(stop_err)
            finally:
                stop_result["completed"] = True
    
        # Run gl.stop() in separate thread with 60s timeout
        stop_thread = threading.Thread(target=_stop_internal, daemon=True)
        stop_thread.start()
        print(f"[GOLOGIN] Waiting for gl.stop() to complete (max 60s)...")
        stop_thread.join(timeout=60)
    
        # Check if thread completed
        if not stop_result["completed"]:
            # TIMEOUT - Force kill immediately
            print(f"[GOLOGIN] ⚠ gl.stop() TIMEOUT after 60s")
            print(f"[GOLOGIN] Force killing browser processes due to timeout...")
        
            try:
                self._force_kill_browser_processes(profile_id)
            except Exception as kill_err:
                print(f"[GOLOGIN] ⚠ Force kill error: {kill_err}")
        
            stop_result["success"] = False
            stop_result["message"] = "Stop timeout - forced cleanup"
    
        else:
            # Thread completed - check if successful or error
            if stop_result["success"]:
                # gl.stop() completed successfully
                print(f"[GOLOGIN] ✓ gl.stop() completed successfully")
                print(f"[GOLOGIN] Waiting 10s for cloud sync to complete...")
                time.sleep(15)
           
            
                # Check if browser processes still exist (shouldn't happen)
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
                        print(f"[GOLOGIN] ⚠ Browser didn't close naturally, force killing...")
                        self._force_kill_browser_processes(profile_id)
                    else:
                        print(f"[GOLOGIN] ✓ Browser closed naturally, no need to force kill")
                    
                except Exception as verify_err:
                    print(f"[GOLOGIN] ⚠ Verification warning: {verify_err}")
        
            else:
                # gl.stop() completed but with error
                print(f"[GOLOGIN] ⚠ gl.stop() completed with error: {stop_result['message']}")
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
            return True, f"Stopped with warnings: {stop_result['message']}"


    
        
    def _force_kill_browser_processes(self, profile_id):
        """
        Force kill Orbita/Chrome processes ONLY related to THIS SPECIFIC GoLogin profile
        SAFE: Will NOT kill user's personal Chrome browser or OTHER profiles' browsers
        """
        try:
            import psutil
            killed_count = 0
        
            # Get tmpdir path to identify GoLogin processes
            tmpdir_lower = self.tmpdir.lower()
        
            # ← FIX: Build profile-specific identifier
            profile_folder = f"gologin_{profile_id}".lower()
            print(f"[GOLOGIN] [{profile_id}] Looking for processes with folder: {profile_folder}")
        
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'exe']):
                try:
                    proc_name = proc.info['name'].lower() if proc.info['name'] else ''
                
                    # Check if it's a browser process
                    is_browser = any(name in proc_name for name in ['orbita', 'chrome', 'chromium'])
                
                    if is_browser and proc.info['cmdline']:
                        cmdline = ' '.join(proc.info['cmdline']).lower()
                    
                        # ← FIX: Check if this process belongs to THIS profile
                        belongs_to_this_profile = profile_folder in cmdline
                    
                        if not belongs_to_this_profile:
                            # This process belongs to different profile or user's Chrome
                            continue
                    
                        # Additional safety checks (must have at least 2 of these)
                        match_count = 0
                    
                        # Check 1: Profile folder in command line (already checked above)
                        if profile_folder in cmdline:
                            match_count += 1
                    
                        # Check 2: "gologin" keyword in command line or exe path
                        if 'gologin' in cmdline:
                            match_count += 1
                        elif proc.info['exe']:
                            exe_path = proc.info['exe'].lower()
                            if 'gologin' in exe_path:
                                match_count += 1
                    
                        # Check 3: Temp directory in command line
                        if tmpdir_lower in cmdline or 'appdata\\local\\temp\\gologin' in cmdline:
                            match_count += 1
                    
                        # Check 4: "orbita" in process name or path (GoLogin's browser)
                        if 'orbita' in proc_name:
                            match_count += 1
                        elif proc.info['exe'] and 'orbita' in proc.info['exe'].lower():
                            match_count += 1
                    
                        # Only kill if at least 2 conditions match AND belongs to this profile
                        if match_count >= 2:
                            print(f"[GOLOGIN] [{profile_id}] Force killing browser process: {proc.info['pid']} (matches: {match_count})")
                            proc.kill()
                            killed_count += 1
                        else:
                            # Safety check failed - don't kill
                            pass
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        
            if killed_count > 0:
                print(f"[GOLOGIN] [{profile_id}] ✓ Killed {killed_count} browser process(es) for THIS profile")
                time.sleep(2)  # Wait for processes to die
            else:
                print(f"[GOLOGIN] [{profile_id}] No browser processes found for this profile")
            
        except Exception as e:
            print(f"[GOLOGIN] [{profile_id}] ⚠ Process kill warning: {e}")



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
        
            if response.status_code in [200, 201]:
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
            proxy_config: Dict with keys: mode, host, port, username, password
                - mode: Proxy type (e.g., 'http', 'socks5')
                - host: Proxy host/IP address
                - port: Proxy port (int or str, will be converted to int)
                - username: Proxy username
                - password: Proxy password
    
        Returns:
            (success: bool, message: str)
        """
        try:
            # Validate all 5 required fields are present
            required_fields = ["mode", "host", "port", "username", "password"]
            for field in required_fields:
                if not proxy_config.get(field):
                    return False, f"Proxy field '{field}' is missing or empty"
        
            # Convert port to integer
            try:
                port = int(proxy_config["port"])
            except ValueError:
                return False, f"Invalid port number: {proxy_config['port']}"
        
            # Ensure profile_ids is a list
            if isinstance(profile_ids, str):
                profile_ids = [profile_ids]
        
            print(f"[GOLOGIN] Updating proxy for {len(profile_ids)} profile(s)...")
            print(f"[GOLOGIN] Proxy: {proxy_config['mode']}://{proxy_config['host']}:{port}")
        
            # Build API request payload
            url = f"{self.base_url}/browser/proxy/many/v2"
        
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
        
            # Send PATCH request
            response = requests.patch(url, json=payload, headers=self.headers, timeout=30)
        
            if response.status_code in [200, 201]:
                print(f"[GOLOGIN] ✓ Proxy updated successfully for all profiles")
                return True, f"Proxy updated for {len(profile_ids)} profile(s)"
            else:
                error_msg = f"API returned status {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", error_msg)
                except:
                    error_msg = f"{error_msg}: {response.text[:200]}"
            
                print(f"[GOLOGIN] ✗ Proxy update failed: {error_msg}")
                return False, error_msg
            
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
