# controllers/actions/gologin_create_launch_action.py
from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from models.gologin_api import GoLoginAPI

class GoLoginCreateLaunchAction(BaseAction):
    """Handler for GoLogin Create and Launch Profile action"""
    
    def prepare_play(self):
        """Execute GoLogin create and launch profile"""
        try:
            # Get API token
            api_token = self.params.get("api_token", "").strip()
            if not api_token:
                print("[GOLOGIN] Error: API token is required")
                self.set_variable(False)
                return
            
            # Initialize GoLogin API
            gologin = GoLoginAPI(api_token)
            
            # Prepare profile parameters
            profile_params = {
                "name": self.params.get("profile_name", "Auto Profile"),
                "os": self.params.get("os", "win"),
                "navigator": {
                    "language": self.params.get("language", "en-US"),
                    "userAgent": "random"
                }
            }
            
            print(f"[GOLOGIN] Creating profile: {profile_params['name']}")
            
            # Step 1: Create profile
            success, result = gologin.create_profile(profile_params)
            
            if not success:
                print(f"[GOLOGIN] Failed to create profile: {result}")
                self.set_variable(False)
                return
            
            profile_id = result.get("id")
            print(f"[GOLOGIN] Profile created with ID: {profile_id}")
            
            # Store profile ID in variable
            profile_id_var_name = self.params.get("profile_id_var_name", "gologin_profile_id")
            if profile_id_var_name:
                GlobalVariables().set(profile_id_var_name, profile_id)
                print(f"[GOLOGIN] Stored profile ID in variable: {profile_id_var_name}")
            
            # Step 2: Add proxy if enabled
            if self.params.get("enable_proxy", True):
                country_code = self.params.get("country_code", "US")
                print(f"[GOLOGIN] Adding proxy with country: {country_code}")
                
                proxy_success, proxy_result = gologin.add_proxy_to_profile(profile_id, country_code)
                
                if proxy_success:
                    print(f"[GOLOGIN] Proxy added successfully")
                else:
                    print(f"[GOLOGIN] Warning: Failed to add proxy: {proxy_result}")
            
            # Step 3: Launch profile
            print(f"[GOLOGIN] Launching profile...")
            launch_success, launch_result = gologin.launch_profile(profile_id)
            
            if not launch_success:
                print(f"[GOLOGIN] Failed to launch profile: {launch_result}")
                self.set_variable(False)
                return
            
            print(f"[GOLOGIN] Profile launched successfully")
            print(f"[GOLOGIN] WebSocket URL: {launch_result.get('wsUrl', 'N/A')}")
            
            # Store WebSocket URL if available
            ws_url = launch_result.get("wsUrl")
            if ws_url:
                GlobalVariables().set("gologin_ws_url", ws_url)
            
            # Step 4: Auto delete if enabled
            if self.params.get("auto_delete", False):
                print(f"[GOLOGIN] Auto delete enabled, will delete profile after use")
                # Note: Actual deletion should be handled in a cleanup action
                GlobalVariables().set("gologin_auto_delete_flag", "true")
            
            self.set_variable(True)
            
        except Exception as e:
            print(f"[GOLOGIN] Error: {e}")
            import traceback
            traceback.print_exc()
            self.set_variable(False)
    
    def set_variable(self, success):
        """Set variable with result True/False"""
        variable = self.params.get("variable", "")
        if variable:
            GlobalVariables().set(variable, "true" if success else "false")
            print(f"[GOLOGIN] Variable '{variable}' = {'true' if success else 'false'}")
