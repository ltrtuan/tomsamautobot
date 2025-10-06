# models/gologin_api.py
import requests
import json

class GoLoginAPI:
    """Class quản lý các API call đến GoLogin"""
    
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api.gologin.com"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def create_profile(self, params=None):
        """Tạo profile mới với fingerprint ngẫu nhiên hoặc custom params"""
        url = f"{self.base_url}/browser"
        
        # Default params nếu không có
        if params is None:
            params = {
                "name": "Auto Profile",
                "os": "win",
                "navigator": {
                    "language": "en-US",
                    "userAgent": "random"
                }
            }
        
        try:
            response = requests.post(url, headers=self.headers, json=params)
            response.raise_for_status()
            return True, response.json()
        except Exception as e:
            print(f"[GOLOGIN] Error creating profile: {e}")
            return False, str(e)
    
    def launch_profile(self, profile_id):
        """Khởi động profile browser"""
        url = f"{self.base_url}/browser/{profile_id}"
        
        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
            return True, response.json()
        except Exception as e:
            print(f"[GOLOGIN] Error launching profile: {e}")
            return False, str(e)
    
    def add_proxy_to_profile(self, profile_id, country_code="US"):
        """Thêm GoLogin proxy vào profile"""
        url = f"{self.base_url}/browser/{profile_id}/proxy"
        
        payload = {
            "mode": "gologin",
            "country": country_code
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return True, response.json()
        except Exception as e:
            print(f"[GOLOGIN] Error adding proxy: {e}")
            return False, str(e)
    
    def delete_profile(self, profile_id):
        """Xóa profile"""
        url = f"{self.base_url}/browser/{profile_id}"
        
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return True, "Profile deleted successfully"
        except Exception as e:
            print(f"[GOLOGIN] Error deleting profile: {e}")
            return False, str(e)
