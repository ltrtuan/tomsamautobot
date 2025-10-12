# controllers/actions/gologin_start_action.py
from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from models.gologin_api import GoLoginAPI
import random
import re
from models.gologin_api import get_gologin_api, start_gologin_app

class GoLoginStartAction(BaseAction):
    """Handler for GoLogin Start Profile action"""
    
    def prepare_play(self):
        """Execute GoLogin start profile"""
        try:          
                
            # Get API token from variable name
            api_key_variable = self.params.get("api_key_variable", "").strip()
            if not api_key_variable:
                print("[GOLOGIN START] Error: API key variable name is required")
                self.set_variable(False)
                return
            
            # Get API token value from GlobalVariables
            api_token = GlobalVariables().get(api_key_variable, "")
            if not api_token:
                print(f"[GOLOGIN START] Error: Variable '{api_key_variable}' is empty or not set")
                self.set_variable(False)
                return
            
            print(f"[GOLOGIN START] Using API token from variable: {api_key_variable}")
            
            # Get profile IDs
            profile_ids_raw = self.params.get("profile_ids", "").strip()
            if not profile_ids_raw:
                print("[GOLOGIN START] Error: Profile IDs is required")
                self.set_variable(False)
                return
            
            # Parse text list (separated by ;)
            text_items = [item.strip() for item in profile_ids_raw.split(";") if item.strip()]
            
            if not text_items:
                print("[GOLOGIN START] Error: No valid profile IDs found")
                self.set_variable(False)
                return
            
            # Get how_to_get method
            how_to_get = self.params.get("how_to_get", "Random")
            
            # Select text based on method - GIỐNG INPUT TEXT
            selected_text = self._select_text(text_items, how_to_get)
            
            # Process special formats (mainly <variable_name>)
            profile_id = self._process_text(selected_text)
            
            print(f"[GOLOGIN START] Selected profile ID: {profile_id}")          
            
            # Start profile
            print(f"[GOLOGIN START] Starting profile...")
            gologin = get_gologin_api(api_token)  # ← Dùng singleton
            
            # Check if need to refresh fingerprint (BEFORE starting profile)
            # Check and execute refresh fingerprint if enabled
            if self.params.get("refresh_fingerprint", False):
                print(f"[GOLOGIN START] Refreshing fingerprint for profile {profile_id}...")
                success, result = gologin.refresh_fingerprint([profile_id])
                if success:
                    print(f"[GOLOGIN START] ✓ Fingerprint refreshed")
                else:
                    print(f"[GOLOGIN START] ⚠ Warning: Refresh failed ({result}), continuing anyway...")
                # KHÔNG return False, luôn tiếp tục


            # Check if need to delete cookies (BEFORE starting profile)
            delete_cookies = self.params.get("delete_cookies", False)
            if delete_cookies:
                self._delete_cookies(gologin, profile_id)
                
            # Check if need to update cookies (if not deleting cookies)
            if not delete_cookies:
                cookies_path = self._get_cookies_path()
                if cookies_path:
                    self._update_cookies_from_file(gologin, profile_id, cookies_path)

                
            success, result = gologin.start_profile(profile_id, wait_for_ready=True, max_wait=180)
            
            if success:
                debugger_address = result
                print(f"[GOLOGIN START] ✓ Profile started successfully!")
                print(f"[GOLOGIN START] Debugger Address: {debugger_address}")
                
                # Store debugger address
                GlobalVariables().set("gologin_debugger_address", debugger_address)
                GlobalVariables().set("gologin_current_profile_id", profile_id)
                
                # Store GoLogin instance for stop action
                GlobalVariables().set("gologin_instance", gologin)
                
                # Store in custom variable if provided
                variable_name = self.params.get("variable", "")
                if variable_name:
                    GlobalVariables().set(variable_name, "true")
                    print(f"[GOLOGIN START] Variable '{variable_name}' = true")
                
                self.set_variable(True)
            else:
                print(f"[GOLOGIN START] ✗ Failed: {result}")
                self.set_variable(False)
            
        except Exception as e:
            print(f"[GOLOGIN START] Error: {e}")
            import traceback
            traceback.print_exc()
            self.set_variable(False)
    
    def _select_text(self, text_items, how_to_get):
        """Select text based on how_to_get method - GIỐNG INPUT TEXT"""
        if how_to_get == "Sequential by loop":
            # Get loop index from GlobalVariables
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
        # Pattern: <variable_name> - replace with variable value
        if text.startswith("<") and text.endswith(">"):
            var_name = text[1:-1]
            return str(GlobalVariables().get(var_name, ""))
        
        # No special format, return as is
        return text
    
    def set_variable(self, success):
        """Set variable with result"""
        variable = self.params.get("variable", "")
        if variable:
            GlobalVariables().set(variable, "true" if success else "false")
            

    def _refresh_fingerprint(self, gologin, profile_id):
        """Refresh profile fingerprint"""
        try:
            print(f"[GOLOGIN START] Refreshing fingerprint for profile {profile_id}...")
            success, result = gologin.refresh_fingerprint([profile_id])
            if success:
                print(f"[GOLOGIN START] ✓ Fingerprint refreshed successfully")
                return True
            else:
                print(f"[GOLOGIN START] ✗ Failed to refresh fingerprint: {result}")
                return False
        except Exception as e:
            print(f"[GOLOGIN START] Error refreshing fingerprint: {e}")
            return False

    def _delete_cookies(self, gologin, profile_id):
        """Delete all cookies by updating with empty list"""
        try:
            print(f"[GOLOGIN START] Deleting cookies for profile {profile_id}...")
            success, result = gologin.update_cookies(profile_id, [], replace_all=True)
            if success:
                print(f"[GOLOGIN START] ✓ Cookies deleted successfully")
                return True
            else:
                print(f"[GOLOGIN START] ✗ Failed to delete cookies: {result}")
                return False
        except Exception as e:
            print(f"[GOLOGIN START] Error deleting cookies: {e}")
            return False

    def _get_cookies_path(self):
        """Get random cookies file from folder (variable has priority)"""
        import os
        import random
    
        # Priority 1: Variable name containing folder path
        cookies_folder_variable = self.params.get("cookies_folder_variable", "").strip()
        cookies_folder = None
    
        if cookies_folder_variable:
            cookies_folder = GlobalVariables().get(cookies_folder_variable, "")
            if cookies_folder:
                print(f"[GOLOGIN START] Using cookies folder from variable '{cookies_folder_variable}': {cookies_folder}")
    
        # Priority 2: Direct folder path
        if not cookies_folder:
            cookies_folder = self.params.get("cookies_folder", "").strip()
            if cookies_folder:
                print(f"[GOLOGIN START] Using direct cookies folder: {cookies_folder}")
    
        # If no folder specified, return None
        if not cookies_folder:
            return None
    
        # Check if folder exists
        if not os.path.exists(cookies_folder) or not os.path.isdir(cookies_folder):
            print(f"[GOLOGIN START] ✗ Cookies folder not found or invalid: {cookies_folder}")
            return None
    
        # Get all JSON files in folder
        try:
            json_files = [f for f in os.listdir(cookies_folder) 
                         if f.lower().endswith('.json') and os.path.isfile(os.path.join(cookies_folder, f))]
        
            if not json_files:
                print(f"[GOLOGIN START] ✗ No JSON files found in folder: {cookies_folder}")
                return None
        
            # Random pick 1 file
            selected_file = random.choice(json_files)
            full_path = os.path.join(cookies_folder, selected_file)
        
            print(f"[GOLOGIN START] 🎲 Random picked cookies file: {selected_file}")
            print(f"[GOLOGIN START] Full path: {full_path}")
        
            return full_path
        
        except Exception as e:
            print(f"[GOLOGIN START] Error reading folder: {e}")
            return None

    def _update_cookies_from_file(self, gologin, profile_id, cookies_path):
        """Read cookies from JSON file and update to profile"""
        try:
            import json
            import os
        
            # Check if file exists
            if not os.path.exists(cookies_path):
                print(f"[GOLOGIN START] ✗ Cookies file not found: {cookies_path}")
                return False
        
            print(f"[GOLOGIN START] Reading cookies from file: {cookies_path}")
        
            # Read JSON file
            with open(cookies_path, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
        
            # Validate cookies is an array
            if not isinstance(cookies_data, list):
                print(f"[GOLOGIN START] ✗ Cookies file must contain a JSON array")
                return False
        
            print(f"[GOLOGIN START] Found {len(cookies_data)} cookie(s) in file")
            print(f"[GOLOGIN START] Updating cookies for profile {profile_id}...")
        
            # Update cookies to profile
            success, result = gologin.update_cookies(profile_id, cookies_data, replace_all=True)
        
            if success:
                print(f"[GOLOGIN START] ✓ Cookies updated successfully")
                return True
            else:
                print(f"[GOLOGIN START] ✗ Failed to update cookies: {result}")
                return False
            
        except json.JSONDecodeError as e:
            print(f"[GOLOGIN START] ✗ Invalid JSON format in cookies file: {e}")
            return False
        except Exception as e:
            print(f"[GOLOGIN START] Error updating cookies from file: {e}")
            import traceback
            traceback.print_exc()
            return False
