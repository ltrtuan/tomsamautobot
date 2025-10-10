# controllers/actions/gologin_get_cookies_action.py

from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from models.gologin_api import get_gologin_api
import random
import json
import os
from datetime import datetime

class GoLoginGetCookiesAction(BaseAction):
    """Handler for GoLogin Get Cookies action"""
    
    def prepare_play(self):
        """Execute GoLogin get cookies"""
        try:
            # Get API token from variable name
            api_key_variable = self.params.get("api_key_variable", "").strip()
            if not api_key_variable:
                print("[GOLOGIN GET COOKIES] Error: API key variable name is required")
                self.set_variable(False)
                return
            
            # Get API token value from GlobalVariables
            api_token = GlobalVariables().get(api_key_variable, "")
            if not api_token:
                print(f"[GOLOGIN GET COOKIES] Error: Variable '{api_key_variable}' is empty or not set")
                self.set_variable(False)
                return
            
            print(f"[GOLOGIN GET COOKIES] Using API token from variable: {api_key_variable}")
            
            # Get profile IDs
            profile_ids_raw = self.params.get("profile_ids", "").strip()
            if not profile_ids_raw:
                print("[GOLOGIN GET COOKIES] Error: Profile IDs is required")
                self.set_variable(False)
                return
            
            # Parse text list (separated by ;)
            text_items = [item.strip() for item in profile_ids_raw.split(";") if item.strip()]
            if not text_items:
                print("[GOLOGIN GET COOKIES] Error: No valid profile IDs found")
                self.set_variable(False)
                return
            
            # Get how_to_get method
            how_to_get = self.params.get("how_to_get", "Random")
            
            # Select text based on method
            selected_text = self._select_text(text_items, how_to_get)
            
            # Process special formats (mainly <variable>)
            profile_id = self._process_text(selected_text)
            
            print(f"[GOLOGIN GET COOKIES] Selected profile ID: {profile_id}")
            
            # Get cookies
            gologin = get_gologin_api(api_token)
            success, result = gologin.get_cookies(profile_id)
            
            if success:
                cookies_data = result
                print(f"[GOLOGIN GET COOKIES] ✓ Retrieved {len(cookies_data)} cookie(s)")
                
                # Get output folder path
                output_folder = self._get_output_folder()
                if not output_folder:
                    print("[GOLOGIN GET COOKIES] Error: Output folder path is required")
                    self.set_variable(False)
                    return
                
                # Create folder if not exists
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                    print(f"[GOLOGIN GET COOKIES] Created output folder: {output_folder}")
                
                # Generate filename
                filename = self._generate_filename(output_folder)
                filepath = os.path.join(output_folder, filename)
                
                # Write cookies to JSON file
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(cookies_data, f, indent=2, ensure_ascii=False)
                
                print(f"[GOLOGIN GET COOKIES] ✓ Cookies saved to: {filepath}")
                
                # Store in custom variable if provided
                variable_name = self.params.get("variable", "")
                if variable_name:
                    GlobalVariables().set(variable_name, filepath)
                    print(f"[GOLOGIN GET COOKIES] Variable '{variable_name}' = {filepath}")
                
                self.set_variable(True)
            else:
                print(f"[GOLOGIN GET COOKIES] ✗ Failed: {result}")
                self.set_variable(False)
                
        except Exception as e:
            print(f"[GOLOGIN GET COOKIES] Error: {e}")
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
        """Process special formats - mainly <variable>"""
        if text.startswith("<") and text.endswith(">"):
            var_name = text[1:-1]
            return str(GlobalVariables().get(var_name, ""))
        return text
    
    def _get_output_folder(self):
        """Get output folder path from variable (priority) or direct path"""
        # Priority 1: Variable name
        folder_variable = self.params.get("folder_variable", "").strip()
        if folder_variable:
            folder_path = GlobalVariables().get(folder_variable, "")
            if folder_path:
                print(f"[GOLOGIN GET COOKIES] Using folder path from variable '{folder_variable}': {folder_path}")
                return folder_path
        
        # Priority 2: Direct path
        folder_path = self.params.get("folder_path", "").strip()
        if folder_path:
            print(f"[GOLOGIN GET COOKIES] Using direct folder path: {folder_path}")
            return folder_path
        
        return None
    
    def _generate_filename(self, output_folder):
        """Generate unique filename with format cookies_DD_MM_YYYY_HH_MM_SS"""
        now = datetime.now()
        base_filename = now.strftime("cookies_%d_%m_%Y_%H_%M_%S.json")
        filepath = os.path.join(output_folder, base_filename)
        
        # If file exists, add counter
        if os.path.exists(filepath):
            counter = 1
            while True:
                filename = now.strftime(f"cookies_%d_%m_%Y_%H_%M_%S_{counter}.json")
                filepath = os.path.join(output_folder, filename)
                if not os.path.exists(filepath):
                    return filename
                counter += 1
        
        return base_filename
    
    def set_variable(self, success):
        """Set variable with result"""
        variable = self.params.get("variable", "")
        if variable:
            GlobalVariables().set(variable, "true" if success else "false")
