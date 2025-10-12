# controllers/actions/get_new_proxy_action.py

from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables

class GetNewProxyAction(BaseAction):
    """Handler for Get New Proxy action"""
    
    def prepare_play(self):
        """Execute Get New Proxy action"""
        if self.should_stop():
            return
        
        # Get parameters
        provider = self.params.get("provider", "").strip()       
        api_token = self.params.get("api_token", "").strip()
        extra_params_str = self.params.get("extra_params", "").strip()
        variables_str = self.params.get("variable", "").strip()
        
        # Validate required fields
        if not provider:
            print("[GET_PROXY] Error: Provider is required")
            return
    
        if not api_token:
            print("[GET_PROXY] Error: API Token is required")
            return
        
        # Parse extra params (format: key1=value1,key2=value2)
        extra_params = self._parse_extra_params(extra_params_str)
        
        # Switch case based on provider
        print(f"[GET_PROXY] Provider: {provider}")
        
        if provider == "TMPROXY":
            success, result = self._get_tmproxy(api_token, extra_params)
        elif provider == "PROXYRACK":
            print("[GET_PROXY] ProxyRack provider not implemented yet")
            return
        else:
            print(f"[GET_PROXY] Error: Unknown provider '{provider}'")
            return
        
        # Handle result
        if success:
            self._assign_variables(result, variables_str)
        else:
            print(f"[GET_PROXY] Failed to get proxy: {result}")
    
    def _get_tmproxy(self, api_token, extra_params):
        """
        Get proxy from TMProxy API
        
        Returns:
            (success: bool, data: dict or error_message: str)
        """
        from models.tmproxy_api import TMProxyAPI
        
        tmproxy = TMProxyAPI(api_token)
        return tmproxy.get_new_proxy(extra_params)
    
    def _parse_extra_params(self, extra_params_str):
        """
        Parse extra params string to dict
        Format: key1=value1,key2=value2
        
        Args:
            extra_params_str: String like "location=US,timeout=300"
        
        Returns:
            dict: {"location": "US", "timeout": "300"}
        """
        if not extra_params_str:
            return {}
        
        params = {}
        try:
            pairs = extra_params_str.split(',')
            for pair in pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    params[key.strip()] = value.strip()
            
            if params:
                print(f"[GET_PROXY] Parsed extra params: {params}")
            
            return params
        except Exception as e:
            print(f"[GET_PROXY] Warning: Failed to parse extra params: {e}")
            return {}
    
    def _assign_variables(self, data, variables_str):
        """
        Assign proxy data to multiple variables (semicolon-separated)
        Similar to read_csv_action
    
        Args:
            data: Dict from API response
            variables_str: String like "USERNAME;PASSWORD;PUBLIC_IP;SOCKS5_PORT;HTTPS_PORT"
    
        Mapping:
            param[0] -> username
            param[1] -> password
            param[2] -> public_ip
            param[3] -> socks5_port (NEW)
            param[4] -> https_port (NEW)
        """
        if not variables_str:
            print("[GET_PROXY] No variables specified, skipping assignment")
            return
    
        # Parse variable names: "USERNAME;PASSWORD;PUBLIC_IP;SOCKS5_PORT;HTTPS_PORT"
        variable_names = [v.strip() for v in variables_str.split(';') if v.strip()]
    
        if not variable_names:
            print("[GET_PROXY] No valid variable names found")
            return
    
        # Map indices to data keys
        value_mapping = [
            data.get("public_ip", ""),
            data.get("https_port", ""),           
            data.get("username", ""),
            data.get("password", "")
        ]
    
        globals_var = GlobalVariables()
    
        # Assign values to variables
        for i, var_name in enumerate(variable_names):
            if i < len(value_mapping):
                value = value_mapping[i]
                globals_var.set(var_name, value)
                print(f"[GET_PROXY] Set variable '{var_name}' = '{value}'")
            else:
                print(f"[GET_PROXY] Warning: No mapping for variable '{var_name}' at index {i}")
                break

