from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
import pyautogui
import pyperclip
import random
import string
import re
import time

class InputTextAction(BaseAction):
    """Handler for input text action."""
    
    def prepare_play(self):
        """Execute input text action after delay"""
        if self.should_stop():
            return
        
        # Get text list parameter
        text_list_str = self.params.get("text_list", "")
        if not text_list_str:
            return
        
        # Parse text list (separated by ;)
        text_items = [item.strip() for item in text_list_str.split(";") if item.strip()]
        if not text_items:
            return
        
        # Get how_to_get method
        how_to_get = self.params.get("how_to_get", "Random")
        
        # Select text based on method
        selected_text = self._select_text(text_items, how_to_get)
        
        # Process special formats
        processed_text = self._process_text(selected_text)
        
        # Save to variable if specified
        variable = self.params.get("variable", "")
        if variable:
            globals_var = GlobalVariables()
            globals_var.set(variable, processed_text)
        
        # Get how_to_input method and execute
        how_to_input = self.params.get("how_to_input", "Random")
        self._input_text(processed_text, how_to_input)
    
    def _select_text(self, text_items, how_to_get):
        """Select text based on how_to_get method"""
        if how_to_get == "Random":
            return random.choice(text_items)
        elif how_to_get == "Sequential by loop":
            # Get loop index from global variables
            globals_var = GlobalVariables()
            loop_index_str = globals_var.get("loop_index", "0")
            try:
                loop_index = int(loop_index_str)
                # Use modulo to loop through text_items (1-based index)
                index = loop_index % len(text_items)
                return text_items[index]
            except:
                # Fallback to first item
                return text_items[0]
        else:
            # Default: first item
            return text_items[0]
    
    def _process_text(self, text):
        """Process special text formats"""
        # Replace <VARIABLE_NAME> with variable value
        globals_var = GlobalVariables()
        
        # ✅ FIXED: Pattern for <VARIABLE_NAME>
        def replace_variable(match):
            var_name = match.group(1)
            value = globals_var.get(var_name, None)  # ← Return None if not found
        
            if value is not None:
                print(f"[INPUT_TEXT] Replaced <{var_name}> with '{value}'")
                return str(value)
            else:
                # ❌ DON'T return <var_name>, return empty or keep original
                print(f"[INPUT_TEXT] WARNING: Variable '{var_name}' not found!")
                return f"<{var_name}>"  # Keep original to show error
        
        text = re.sub(r'<([^>]+)>', replace_variable, text)
        
        # Pattern: [1-10:CN] - random 1-10 chars/numbers/both
        def replace_random_chars(match):
            min_val = int(match.group(1))
            max_val = int(match.group(2))
            char_type = match.group(3).upper()
            
            length = random.randint(min_val, max_val)
            
            if char_type == 'C':  # Characters only
                return ''.join(random.choices(string.ascii_letters, k=length))
            elif char_type == 'N':  # Numbers only
                return ''.join(random.choices(string.digits, k=length))
            elif char_type == 'CN':  # Both characters and numbers
                return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
            else:
                return match.group(0)  # Keep original if unknown type
        
        text = re.sub(r'\[(\d+)-(\d+):([CNcn]+)\]', replace_random_chars, text)
        
        # Pattern: [1-10] - random number from 1 to 10
        def replace_random_number(match):
            min_val = int(match.group(1))
            max_val = int(match.group(2))
            return str(random.randint(min_val, max_val))
        
        text = re.sub(r'\[(\d+)-(\d+)\]', replace_random_number, text)
        
        return text
    
    def _input_text(self, text, how_to_input):
        """Input text using specified method"""
        if how_to_input == "Random":
            # Randomly choose between the three methods
            how_to_input = random.choice(["Copy & Paste", "Press Keyboard"])
        
        if how_to_input == "Copy & Paste":
            # Use clipboard
            pyperclip.copy(text)
            time.sleep(0.1)  # Small delay
            pyautogui.hotkey('ctrl', 'v')
            
        elif how_to_input == "Press Keyboard":
            # Type character by character
            for char in text:
                if self.should_stop():
                    break
                pyautogui.write(char, interval=random.uniform(0.05, 0.15))
