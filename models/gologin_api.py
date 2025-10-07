# models/gologin_api.py
from gologin import GoLogin
import requests
import time

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
    
    def create_profile(self, profile_name, os_type="win", language="en-US", enable_proxy=False, country_code="US"):
        """
        Tạo profile mới - CHỈ TẠO, không launch
        Returns: (success, profile_id or error_message)
        """
        try:
            self.gl = GoLogin({"token": self.api_token})
            
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
    
    def start_profile(self, profile_id):
        """
        Start profile đã tồn tại
        Returns: (success, debugger_address or error_message)
        """
        try:
            print(f"[GOLOGIN] Starting profile: {profile_id}")
            
            self.gl = GoLogin({
                "token": self.api_token,
                "profile_id": profile_id
            })
            
            # Start browser
            debugger_address = self.gl.start()
            
            if debugger_address:
                print(f"[GOLOGIN] ✓ Profile started!")
                print(f"[GOLOGIN] Debugger: {debugger_address}")
                return True, debugger_address
            else:
                return False, "No debugger address returned"
            
        except Exception as e:
            print(f"[GOLOGIN] Start error: {e}")
            return False, str(e)
    
    def stop_profile(self):
        """
        Stop profile đang chạy (sử dụng SDK instance)
        Returns: (success, message)
        """
        try:
            if self.gl:
                self.gl.stop()
                print(f"[GOLOGIN] ✓ Profile stopped (via SDK)")
                return True, "Stopped successfully"
            else:
                return False, "No active profile to stop"
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
