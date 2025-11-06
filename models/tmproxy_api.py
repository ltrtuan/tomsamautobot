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

    @staticmethod
    def get_proxy_static(api_key, proxy_type):
        """
        Static method to get proxy details directly from TMProxy API.
        Args:
            api_key (str): TMProxy API key
            proxy_type (str): 'socks5' or 'http'/'https' (will map 'https' to 'http')
        Returns:
            dict: {'mode': str, 'host': str, 'port': int, 'username': str, 'password': str} or None if error
        """
        try:
            # Map proxy_type: 'https' -> 'http' for consistency (GoLogin uses 'http' for HTTPS proxies)
            if proxy_type == 'https':
                mapped_type = 'http'
            else:
                mapped_type = proxy_type  # 'socks5' or 'http'

            # Use TMProxy base_url and endpoint (align with get_new_proxy method)
            base_url = "https://tmproxy.com/api/proxy"
            url = f"{base_url}/get-new-proxy"
        
            # Headers (same as get_new_proxy)
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json"
            }
        
            # JSON body with api_key (no extra params for static call)
            body = {
                "api_key": api_key
            }
        
            print(f"TMProxy API: Calling POST {url} with api_key=...{api_key[-8:]} for type={proxy_type} (mapped: {mapped_type})")
        
            # Send POST request (align with get_new_proxy: timeout=30s for safety)
            response = requests.post(url, headers=headers, json=body, timeout=30)
        
            print(f"TMProxy API: Response status: {response.status_code}")
            print(f"TMProxy API: Response body: {response.text[:500]}")  # Log first 500 chars for debug
        
            response.raise_for_status()  # Raise if HTTP 4xx/5xx
        
            # Parse JSON response
            data = response.json()
        
            # Check success: code == 0 (same as get_new_proxy)
            if data.get("code") != 0:
                error_msg = data.get("message", "Unknown error")
                print(f"TMProxy API error (code={data.get('code')}): {error_msg}")
                return None
        
            # Extract proxy_data
            proxy_data = data.get("data", {})
            if not proxy_data:
                print("TMProxy API: No 'data' in response")
                return None
        
            # Select endpoint based on mapped_type: 'socks5' or 'https' field
            # Note: 'https' field = HTTP/HTTPS proxy; use it for 'http' too
            endpoint_key = 'socks5' if mapped_type == 'socks5' else 'https'
            endpoint = proxy_data.get(endpoint_key, "")
        
            if not endpoint:
                print(f"TMProxy API: No endpoint for mapped_type '{mapped_type}' (key: {endpoint_key}) in response")
                return None
        
            # Parse IP:PORT from endpoint (e.g., "27.64.124.75:42993" -> host, port)
            host_port = endpoint.split(':')
            if len(host_port) != 2:
                print(f"TMProxy API: Invalid endpoint format '{endpoint}' (expected IP:PORT)")
                return None
        
            host = host_port[0].strip()
            try:
                port = int(host_port[1].strip())
            except ValueError:
                print(f"TMProxy API: Invalid port '{host_port[1]}' in endpoint '{endpoint}'")
                return None
        
            # Extract username and password (same as response)
            username = proxy_data.get('username', '').strip()
            password = proxy_data.get('password', '').strip()
        
            if not username or not password:
                print("TMProxy API: Missing username or password in response")
                return None
        
            # Optional: Extract and log ports like get_new_proxy (for consistency)
            socks5_str = proxy_data.get("socks5", "")
            https_str = proxy_data.get("https", "")
            socks5_port = socks5_str.split(':')[-1] if ':' in socks5_str else ""
            https_port = https_str.split(':')[-1] if ':' in https_str else ""
        
            print(f"TMProxy API: ✓ Success - Username: {username}, Password: {password[:4]}..., Public IP: {proxy_data.get('public_ip')}")
            print(f"TMProxy API: SOCKS5: {socks5_str} (Port: {socks5_port}), HTTPS: {https_str} (Port: {https_port})")
            print(f"TMProxy API: Selected for {mapped_type}: {endpoint} -> {host}:{port}")
            print(f"TMProxy API: Location: {proxy_data.get('location_name')}, ISP: {proxy_data.get('isp_name')}")
        
            # Return full dict for GoLogin (including 'mode')
            return {
                'mode': mapped_type,  # 'socks5' or 'http'
                'host': host,
                'port': port,
                'username': username,
                'password': password
            }
        
        except requests.RequestException as e:
            print(f"TMProxy API request error: {e}")
            return None
        except (KeyError, ValueError, TypeError) as e:
            print(f"TMProxy API parse error: {e}")
            return None
        except Exception as e:
            print(f"TMProxy API unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return None


