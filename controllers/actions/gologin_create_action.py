# controllers/actions/gologin_create_action.py
from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
import random
import string
import re
import time
from models.gologin_api import get_gologin_api, start_gologin_app

class GoLoginCreateAction(BaseAction):
    """Handler for GoLogin Create Profile action"""
    
    def prepare_play(self):
        """Execute GoLogin create profile"""
        try:

            # Get API token from variable name
            api_key_variable = self.params.get("api_key_variable", "").strip()
            if not api_key_variable:
                print("[GOLOGIN CREATE] Error: API key variable name is required")
                self.set_variable(False)
                return
            
            # Get API token value from GlobalVariables
            api_token = GlobalVariables().get(api_key_variable, "")
            if not api_token:
                print(f"[GOLOGIN CREATE] Error: Variable '{api_key_variable}' is empty or not set")
                self.set_variable(False)
                return
            
            print(f"[GOLOGIN CREATE] Using API token from variable: {api_key_variable}")
            
            # Get profile names
            profile_names_raw = self.params.get("profile_names", "").strip()
            if not profile_names_raw:
                print("[GOLOGIN CREATE] Error: Profile names is required")
                self.set_variable(False)
                return
            
            # Parse text list (separated by ;)
            text_items = [item.strip() for item in profile_names_raw.split(";") if item.strip()]
            
            if not text_items:
                print("[GOLOGIN CREATE] Error: No valid profile names found")
                self.set_variable(False)
                return
            
            # Get how_to_get method
            how_to_get = self.params.get("how_to_get", "Random")
            
            # Select text based on method
            selected_text = self._select_text(text_items, how_to_get)
            
            # Process special formats
            profile_name = self._process_text(selected_text)
            
            print(f"[GOLOGIN CREATE] Selected profile name: {profile_name}")
            
            # Get profile settings
            os_type = self.params.get("os", "win")
            language = self.params.get("language", "en-US")
            enable_proxy = self.params.get("enable_proxy", False)
            country_code = self.params.get("country_code", "US")
            
            # Initialize GoLogin API
            gologin = get_gologin_api(api_token)  # ← Dùng singleton
            
            # Create profile
            print(f"[GOLOGIN CREATE] Creating profile: {profile_name}")
            success, result = gologin.create_profile(
                profile_name=profile_name,
                os_type=os_type,
                language=language,
                enable_proxy=enable_proxy,
                country_code=country_code
            )
            
            if success:
                profile_id = result
                print(f"[GOLOGIN CREATE] ✓ Profile created successfully!")
                print(f"[GOLOGIN CREATE] Profile ID: {profile_id}")
                print(f"[GOLOGIN CREATE] Profile Name: {profile_name}")
    
                # ← BỎ: time.sleep(10)
                # ← BỎ: print waiting message
    
                # ASSIGN TO MULTIPLE VARIABLES
                variable_name = self.params.get("variable", "")
                if variable_name:
                    self._assign_to_multiple_variables(variable_name, profile_id)
    
                GlobalVariables().set("gologin_profile_id", profile_id)
                self.set_variable(True)
            else:
                print(f"[GOLOGIN CREATE] ✗ Failed: {result}")
                self.set_variable(False)
            
        except Exception as e:
            print(f"[GOLOGIN CREATE] Error: {e}")
            import traceback
            traceback.print_exc()
            self.set_variable(False)
    
    def _assign_to_multiple_variables(self, variables_str, value):
        """
        Assign value to multiple variables based on loop_index from For Action
        Example: variables_str = "PROFILE_1;PROFILE_2;PROFILE_3"
    
        Loop 0 -> PROFILE_1
        Loop 1 -> PROFILE_2
        Loop 2 -> PROFILE_3
        Loop 3+ -> Skip (không gán)
    
        Nếu chỉ có 2 variables nhưng loop 5 lần:
        Loop 0 -> PROFILE_1
        Loop 1 -> PROFILE_2
        Loop 2,3,4 -> Skip (không gán)
        """
        # Parse variables string
        variable_names = [v.strip() for v in variables_str.split(';') if v.strip()]
    
        if not variable_names:
            print("[GOLOGIN CREATE] No variables specified")
            return
    
        globals_var = GlobalVariables()
    
        # Get loop index from For Action
        loop_index_str = globals_var.get("loop_index", "0")
        try:
            loop_index = int(loop_index_str)
        except:
            loop_index = 0
    
        # ✅ CHỈ GÁN NẾU loop_index < số variables
        if loop_index < len(variable_names):
            selected_var = variable_names[loop_index]
            globals_var.set(selected_var, value)
            print(f"[GOLOGIN CREATE] Loop {loop_index}: Set variable '{selected_var}' = '{value}'")
        else:
            # Loop index vượt quá số variables -> BỎ QUA
            print(f"[GOLOGIN CREATE] Loop {loop_index}: Skip assignment (no variable at index {loop_index})")

    
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
        """Process special formats"""
        # Pattern 1: <variable_name> - replace with variable value
        if text.startswith("<") and text.endswith(">"):
            var_name = text[1:-1]
            return str(GlobalVariables().get(var_name, ""))
        
        # Pattern 2: [min-max:type] - random characters/numbers/both
        pattern = r'\[(\d+)-(\d+):([CNB])\]'
        match = re.match(pattern, text)
        if match:
            min_len = int(match.group(1))
            max_len = int(match.group(2))
            char_type = match.group(3)
            length = random.randint(min_len, max_len)
            
            if char_type == 'C':  # Characters only
                return ''.join(random.choices(string.ascii_letters, k=length))
            elif char_type == 'N':  # Numbers only
                return ''.join(random.choices(string.digits, k=length))
            elif char_type == 'B':  # Both characters and numbers
                return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        
        # Pattern 3: [min-max] - random number in range
        pattern = r'\[(\d+)-(\d+)\]'
        match = re.match(pattern, text)
        if match:
            min_val = int(match.group(1))
            max_val = int(match.group(2))
            return str(random.randint(min_val, max_val))
        
        # No special format, return as is
        return text
    
    def set_variable(self, success):
        """Set variable with result - chỉ set false nếu failed"""
        # Không set variable ở đây nữa vì đã set trong _assign_to_multiple_variables
        pass
