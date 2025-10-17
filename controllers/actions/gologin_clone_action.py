# controllers/actions/gologin_clone_action.py

from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from models.gologin_api import get_gologin_api
import time

class GoLoginCloneAction(BaseAction):
    """Handler for GoLogin Clone Profile action"""
    
    def prepare_play(self):
        """Execute GoLogin clone profile"""
        try:
            # Get API token from variable name
            api_key_variable = self.params.get("api_key_variable", "").strip()
            if not api_key_variable:
                print("[GOLOGIN CLONE] Error: API key variable name is required")
                self.set_variable(False)
                return
            
            # Get API token value from GlobalVariables
            api_token = GlobalVariables().get(api_key_variable, "")
            if not api_token:
                print(f"[GOLOGIN CLONE] Error: Variable '{api_key_variable}' is empty or not set")
                self.set_variable(False)
                return
            
            print(f"[GOLOGIN CLONE] Using API token from variable: {api_key_variable}")
            
            # Get profile ID to clone
            profile_id = self.params.get("profile_id", "").strip()
            if not profile_id:
                print("[GOLOGIN CLONE] Error: Profile ID is required")
                self.set_variable(False)
                return
            
            print(f"[GOLOGIN CLONE] Profile ID to clone: {profile_id}")
            
            # Initialize GoLogin API
            gologin = get_gologin_api(api_token)
            
            # Clone profile using clone_multi API
            print(f"[GOLOGIN CLONE] Cloning profile...")
            success, result = gologin.clone_profile_multi(profile_id)
            
            if not success:
                print(f"[GOLOGIN CLONE] ✗ Clone failed: {result}")
                self.set_variable(False)
                return
            
            # Check if we got profile IDs
            cloned_profile_ids = result
            
            if cloned_profile_ids and len(cloned_profile_ids) > 0:
                # Got profile ID directly from API response
                new_profile_id = cloned_profile_ids[0]
                print(f"[GOLOGIN CLONE] ✓ Profile cloned successfully!")
                print(f"[GOLOGIN CLONE] New Profile ID: {new_profile_id}")
                
                # Assign to variable
                variable_name = self.params.get("variable", "")
                if variable_name:
                    self._assign_to_multiple_variables(variable_name, new_profile_id)
                
                GlobalVariables().set("gologin_profile_id", new_profile_id)
                self.set_variable(True)
            else:
                # API returned 204 (async clone) - no profile ID returned
                print(f"[GOLOGIN CLONE] ✓ Clone request accepted (HTTP 204)")
                print(f"[GOLOGIN CLONE] ⚠ Profile ID not returned by API (async operation)")
                print(f"[GOLOGIN CLONE] Please check GoLogin dashboard to verify")
                
                GlobalVariables().set("gologin_clone_status", "success_async")
                self.set_variable(True)
                
        except Exception as e:
            print(f"[GOLOGIN CLONE] Error: {e}")
            import traceback
            traceback.print_exc()
            self.set_variable(False)
    
    def _assign_to_multiple_variables(self, variables_str, value):
        """
        Assign value to multiple variables based on loop_index from For Action
        Same logic as GoLogin Create action
        """
        # Parse variables string
        variable_names = [v.strip() for v in variables_str.split(';') if v.strip()]
        if not variable_names:
            print("[GOLOGIN CLONE] No variables specified")
            return
        
        globals_var = GlobalVariables()
        
        # Get loop index from For Action (if exists)
        loop_index_str = globals_var.get("loop_index", "0")
        try:
            loop_index = int(loop_index_str)
        except:
            loop_index = 0
        
        # Only assign if loop_index < number of variables
        if loop_index < len(variable_names):
            selected_var = variable_names[loop_index]
            globals_var.set(selected_var, value)
            print(f"[GOLOGIN CLONE] Loop {loop_index}: Set variable '{selected_var}' = '{value}'")
        else:
            # Loop index exceeds number of variables -> SKIP
            print(f"[GOLOGIN CLONE] Loop {loop_index}: Skip assignment (no variable at index {loop_index})")
    
    def set_variable(self, success):
        """Set variable with result"""
        pass
