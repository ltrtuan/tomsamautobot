# models/tmproxy_api.py

import requests

class TMProxyAPI:
    """Class to interact with TMProxy API"""
    
    def __init__(self, api_token):
        """
        Initialize TMProxy API client
        
        Args:
            api_token: TMProxy API token
        """
        self.api_token = api_token
        self.base_url = "https://tmproxy.com/api/proxy"
    
    def get_new_proxy(self, extra_params=None):
        """
        Get new proxy from TMProxy API
        Documentation: https://docs.tmproxy.com/tmproxy-apis/get-new-proxy/
        
        Args:
            extra_params: Dict of extra parameters (optional)
                - id_location: Location ID (int)
                - id_isp: ISP ID (int)
        
        Returns:
            (success: bool, data: dict or error_message: str)
            
        Response format from API:
        {
            "code": 0,
            "message": "string",
            "data": {
                "ip_allow": "string",
                "username": "string",
                "password": "string",
                "public_ip": "string",
                "isp_name": "string",
                "location_name": "string",
                "socks5": "string",
                "https": "string",
                "timeout": 0,
                "next_request": 0,
                "expired_at": 0
            }
            {"code":0,"message":"","data":{"ip_allow":"27.70.151.186","isp_name":"Viettel","location_name":"Long An","socks5":"27.64.124.75:42993","https":"27.64.124.75:42993","timeout":3600,"next_request":239,"expired_at":"23:46:58 12/10/2025","username":"tmproxyVVTLp","password":"palD7IpXix","public_ip":"27.64.124.75"}}
        }
        """
        try:
            # Build API URL
            url = f"{self.base_url}/get-new-proxy"
            
            # Build headers
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json"
            }
            
            # Build request body - API key is REQUIRED in body
            body = {
                "api_key": self.api_token
            }
            
            # Add extra params to body if provided
            if extra_params:
                # Parse integer fields if they exist
                if "id_location" in extra_params:
                    try:
                        body["id_location"] = int(extra_params["id_location"])
                    except ValueError:
                        print(f"[TMPROXY] Warning: Invalid id_location, skipping")
                
                if "id_isp" in extra_params:
                    try:
                        body["id_isp"] = int(extra_params["id_isp"])
                    except ValueError:
                        print(f"[TMPROXY] Warning: Invalid id_isp, skipping")
            
            print(f"[TMPROXY] Requesting new proxy from: {url}")
            print(f"[TMPROXY] Request body: {body}")
            
            # Send POST request with JSON body
            response = requests.post(url, headers=headers, json=body, timeout=30)
            
            print(f"[TMPROXY] Response status: {response.status_code}")
            print(f"[TMPROXY] Response text: {response.text[:500]}")  # Print first 500 chars
            
            # Parse response
            if response.status_code == 200:
                result = response.json()
                
                if result.get("code") == 0:
                    data = result.get("data", {})
    
                    # Extract ports from socks5 and https
                    # Format: "27.64.124.75:42993" -> port = "42993"
                    socks5_str = data.get("socks5", "")
                    https_str = data.get("https", "")
    
                    # Parse socks5_port
                    if ":" in socks5_str:
                        socks5_port = socks5_str.split(":")[-1]  # Get last part after ":"
                        data["socks5_port"] = socks5_port
                    else:
                        data["socks5_port"] = ""
    
                    # Parse https_port
                    if ":" in https_str:
                        https_port = https_str.split(":")[-1]  # Get last part after ":"
                        data["https_port"] = https_port
                    else:
                        data["https_port"] = ""
    
                    print(f"[TMPROXY] ✓ Successfully got new proxy")
                    print(f"[TMPROXY]   Username: {data.get('username')}")
                    print(f"[TMPROXY]   Password: {data.get('password')}")
                    print(f"[TMPROXY]   Public IP: {data.get('public_ip')}")
                    print(f"[TMPROXY]   SOCKS5: {data.get('socks5')} (Port: {data.get('socks5_port')})")
                    print(f"[TMPROXY]   HTTPS: {data.get('https')} (Port: {data.get('https_port')})")
                    print(f"[TMPROXY]   Location: {data.get('location_name')}")
                    print(f"[TMPROXY]   ISP: {data.get('isp_name')}")
                    return True, data
                else:
                    error_msg = result.get("message", "Unknown error")
                    print(f"[TMPROXY] ✗ API error (code={result.get('code')}): {error_msg}")
                    return False, error_msg
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                print(f"[TMPROXY] ✗ Request failed: {error_msg}")
                return False, error_msg
                
        except Exception as e:
            print(f"[TMPROXY] ✗ Exception occurred: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)
