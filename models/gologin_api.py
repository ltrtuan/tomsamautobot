# models/gologin_api.py
from gologin import GoLogin
import requests
import time
import tempfile
import os
import subprocess
import psutil

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
                    gologin_config = {
                        "token": self.api_token,
                        "profile_id": profile_id,
                        "tmpdir": self.tmpdir
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
        Stop profile - Close browser VÀ sync data lên cloud
    
        Args:
            profile_id: Profile ID to stop
            clean_profile: If True, xóa profile folder local (default False)
        """
        try:
            profile_id = str(profile_id).strip()
            print(f"[GOLOGIN] Stopping profile: {profile_id}")
        
            if profile_id in self.active_profiles:
                gl = self.active_profiles[profile_id]
            
                # ← THAY ĐỔI: GỌI gl.stop() để sync
                print(f"[GOLOGIN] Closing browser and syncing data to cloud...")
            
                try:
                    gl.stop()  # ← Sync localStorage/IndexedDB lên GoLogin cloud
                    print(f"[GOLOGIN] ✓ Data synced to cloud")
                except Exception as e:
                    print(f"[GOLOGIN] ⚠ Sync warning: {e}")
            
                # Remove from active profiles
                del self.active_profiles[profile_id]
            
                print(f"[GOLOGIN] ✓ Profile stopped!")
                return True, "Profile stopped and synced"
            else:
                print(f"[GOLOGIN] ⚠ No active instance found")
                return False, "Profile not running"
            
        except Exception as e:
            print(f"[GOLOGIN] Stop error: {e}")
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
