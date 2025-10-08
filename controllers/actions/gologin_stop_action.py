# controllers/actions/gologin_stop_action.py
from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from models.gologin_api import GoLoginAPI
import random
from models.gologin_api import get_gologin_api, start_gologin_app

class GoLoginStopAction(BaseAction):
    """Handler for GoLogin Stop Profile action"""
    
    def prepare_play(self):
        """Execute GoLogin stop profile"""
        try:
            # ← THÊM: Check & Start GoLogin App
            app_path_variable = self.params.get("gologin_app_path_variable", "").strip()
            if app_path_variable:
                app_path = GlobalVariables().get(app_path_variable, "")
    
                if app_path:
                    print(f"[GOLOGIN CREATE] App path from variable '{app_path_variable}': {app_path}")
        
                    # Start app if not running
                    success, msg = start_gologin_app(app_path, max_wait=60)
        
                    if not success:
                        print(f"[GOLOGIN CREATE] ✗ Failed to start GoLogin app: {msg}")
                        self.set_variable(False)
                        return
        
                    print(f"[GOLOGIN CREATE] ✓ GoLogin app ready: {msg}")
                else:
                    print(f"[GOLOGIN CREATE] ⚠ Variable '{app_path_variable}' is empty, assuming app already running")
            else:
                print(f"[GOLOGIN CREATE] No app path variable specified, assuming app already running")
                
            # Get API token from variable name
            api_key_variable = self.params.get("api_key_variable", "").strip()
            if not api_key_variable:
                print("[GOLOGIN STOP] Error: API key variable name is required")
                self.set_variable(False)
                return
            
            # Get API token value from GlobalVariables
            api_token = GlobalVariables().get(api_key_variable, "")
            if not api_token:
                print(f"[GOLOGIN STOP] Error: Variable '{api_key_variable}' is empty or not set")
                self.set_variable(False)
                return
            
            print(f"[GOLOGIN STOP] Using API token from variable: {api_key_variable}")
            
            # Get profile IDs
            profile_ids_raw = self.params.get("profile_ids", "").strip()
            if not profile_ids_raw:
                print("[GOLOGIN STOP] Error: Profile IDs is required")
                self.set_variable(False)
                return
            
            # Parse text list (separated by ;)
            text_items = [item.strip() for item in profile_ids_raw.split(";") if item.strip()]
            
            if not text_items:
                print("[GOLOGIN STOP] Error: No valid profile IDs found")
                self.set_variable(False)
                return
            
            # Get how_to_get method
            how_to_get = self.params.get("how_to_get", "Random")
            
            # Select text based on method
            selected_text = self._select_text(text_items, how_to_get)
            
            # Process special formats (mainly <variable_name>)
            profile_id = self._process_text(selected_text)
            
            clean_profile = self.params.get("clean_profile", False)
            print(f"[GOLOGIN STOP] Selected profile ID to stop: {profile_id}")
            
            # Initialize GoLogin API
            gologin = GoLoginAPI(api_token)
            
            # Stop profile by ID using REST API
            gologin = get_gologin_api(api_token)  # ← Dùng singleton
            success, result = gologin.stop_profile(profile_id,clean_profile=clean_profile)
            
            if success:
                print(f"[GOLOGIN STOP] ✓ Profile {profile_id} stopped successfully!")
                
                # Clean up variables if this is the current profile
                current_profile = GlobalVariables().get("gologin_current_profile_id", "")
                if current_profile == profile_id:
                    GlobalVariables().set("gologin_instance", None)
                    GlobalVariables().set("gologin_debugger_address", "")
                    GlobalVariables().set("gologin_current_profile_id", "")
                    print(f"[GOLOGIN STOP] Cleaned up stored variables")
                
                self.set_variable(True)
            else:
                print(f"[GOLOGIN STOP] ✗ Failed: {result}")
                self.set_variable(False)
            
        except Exception as e:
            print(f"[GOLOGIN STOP] Error: {e}")
            import traceback
            traceback.print_exc()
            self.set_variable(False)
    
    def _select_text(self, text_items, how_to_get):
        """Select text based on how_to_get method"""
        if how_to_get == "Sequential by loop":
            loop_index = GlobalVariables().get("loop_index", "0")
            try:
                index = int(loop_index) % len(text_items)
                return text_items[index]
            except:
                return text_items[0]
        else:
            # Random
            return random.choice(text_items)
    
    def _process_text(self, text):
        """Process special formats - mainly <variable_name>"""
        if text.startswith("<") and text.endswith(">"):
            var_name = text[1:-1]
            return str(GlobalVariables().get(var_name, ""))
        
        return text
    
    def set_variable(self, success):
        """Set variable with result"""
        variable = self.params.get("variable", "")
        if variable:
            GlobalVariables().set(variable, "true" if success else "false")
