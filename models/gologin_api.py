# models/gologin_api.py
from gologin import GoLogin
import requests
import time
import tempfile
import os

class GoLoginAPI:
    """Class quản lý GoLogin API - 3 methods: Create, Start, Stop"""
    
    def __init__(self, api_token):
        self.api_token = api_token
        self.gl = None
        self.base_url = "https://api.gologin.com"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
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
    
    def start_profile(self, profile_id, wait_for_ready=True, max_wait=180):
        """
        Start profile đã tồn tại
        Args:
            profile_id: Profile ID to start
            wait_for_ready: Poll until profile ready (default True)
            max_wait: Max seconds to wait (default 180 = 3 mins)
        Returns: (success, debugger_address or error_message)
        """
        try:
            # Validate profile_id
            profile_id = str(profile_id).strip()
            if ',' in profile_id or ';' in profile_id or not profile_id:
                return False, f"Invalid profile_id: {profile_id}"
        
            print(f"[GOLOGIN] Starting profile: {profile_id}")
        
            # ← THÊM: Check if profile is ready (polling)
            if wait_for_ready:
                print(f"[GOLOGIN] Checking profile readiness (max {max_wait}s)...")
                ready, msg = self.check_profile_ready(profile_id, max_wait)
                if not ready:
                    return False, f"Profile not ready: {msg}"
        
            # Initialize GoLogin with tmpdir
            self.gl = GoLogin({
                "token": self.api_token,
                "profile_id": profile_id,
                "tmpdir": self.tmpdir
            })
        
            # Start browser
            print(f"[GOLOGIN] Launching browser...")
            debugger_address = self.gl.start()
        
            if debugger_address:
                self.active_profiles[profile_id] = self.gl
                print(f"[GOLOGIN] ✓ Profile started!")
                print(f"[GOLOGIN] Debugger: {debugger_address}")
                return True, debugger_address
            else:
                return False, "No debugger address returned"
        
        except Exception as e:
            print(f"[GOLOGIN] Start error: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)

    
    def stop_profile(self, profile_id):
        """Stop profile sử dụng SAVED instance"""
        try:
            profile_id = str(profile_id).strip()
            print(f"[GOLOGIN] Stopping profile: {profile_id}")
            
            # ← CHECK: Có instance đã lưu không?
            if profile_id in self.active_profiles:
                gl = self.active_profiles[profile_id]
                
                # Close browser using SDK
                gl.stop()
                
                # Remove from active profiles
                del self.active_profiles[profile_id]
                
                print(f"[GOLOGIN] ✓ Profile stopped successfully!")
                return True, "Profile stopped"
            
            else:
                # ← FALLBACK: Không có instance → Try API stop
                print(f"[GOLOGIN] ⚠ No active instance found, trying API stop...")
                url = f"{self.base_url}/browser/{profile_id}/web/stop"
                
                response = requests.delete(url, headers=self.headers)
                
                if response.status_code == 200 or response.status_code == 204:
                    print(f"[GOLOGIN] ✓ Profile stopped via API!")
                    return True, "Profile stopped via API"
                else:
                    error_msg = response.text
                    print(f"[GOLOGIN] ✗ Stop failed: {error_msg}")
                    return False, error_msg
            
        except Exception as e:
            print(f"[GOLOGIN] Stop error: {e}")
            return False, str(e)
    
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

    def check_profile_ready(self, profile_id, max_wait=180, check_interval=10):
        """
        Check if profile is ready to start (polling)
        Args:
            profile_id: Profile ID to check
            max_wait: Maximum seconds to wait (default 180 = 3 mins)
            check_interval: Seconds between checks (default 10s)
        Returns: (ready: bool, message: str)
        """
        import time
    
        url = f"{self.base_url}/browser/{profile_id}"
        start_time = time.time()
    
        print(f"[GOLOGIN] ⏳ Checking if profile is ready...")
    
        attempts = 0
        while time.time() - start_time < max_wait:
            attempts += 1
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
            
                if response.status_code == 200:
                    profile_data = response.json()
                
                    # Check if profile exists and has ID
                    if profile_data.get("id") == profile_id:
                        elapsed = int(time.time() - start_time)
                        print(f"[GOLOGIN] ✓ Profile ready after {elapsed}s (attempts: {attempts})")
                        return True, "Profile ready"
                    else:
                        print(f"[GOLOGIN] ⚠ Profile data mismatch, attempt {attempts}")
            
                elif response.status_code == 404:
                    print(f"[GOLOGIN] ✗ Profile not found (404)")
                    return False, "Profile not found on server"
            
                else:
                    print(f"[GOLOGIN] ⚠ API returned {response.status_code}, attempt {attempts}")
            
            except requests.exceptions.Timeout:
                print(f"[GOLOGIN] ⚠ Request timeout, attempt {attempts}")
            except Exception as e:
                print(f"[GOLOGIN] ⚠ Check error: {e}, attempt {attempts}")
        
            # Wait before next check
            if time.time() - start_time < max_wait:
                print(f"[GOLOGIN] Waiting {check_interval}s before retry...")
                time.sleep(check_interval)
    
        # Timeout
        elapsed = int(time.time() - start_time)
        return False, f"Profile not ready after {elapsed}s timeout ({attempts} attempts)"

# ← SINGLETON INSTANCE - Shared across all actions
_gologin_instance = None

def get_gologin_api(api_token):
    """Get or create singleton GoLoginAPI instance"""
    global _gologin_instance
    
    if _gologin_instance is None or _gologin_instance.api_token != api_token:
        _gologin_instance = GoLoginAPI(api_token)
    
    return _gologin_instance