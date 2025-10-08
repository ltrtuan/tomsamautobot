from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
import pyautogui
import pyperclip
import random
import string
import re
import time
import os

class ReadTxtAction(BaseAction):
    """Handler for read txt file action."""
    
    def prepare_play(self):
        """Execute read txt file action after delay"""
        if self.should_stop():
            return
        
        # Get file path parameter
        file_path = self._resolve_file_path()
    
        if not file_path:
            print("[READ_TXT] Error: No file path specified")
            return
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"[READ_TXT] Error: File not found: {file_path}")
            return
        
        # Read all lines from file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            print(f"[READ_TXT] Error reading file: {e}")
            return
        
        if not lines:
            print("[READ_TXT] Error: File is empty or contains no valid lines")
            return
        
        # Get how_to_get method
        how_to_get = self.params.get("how_to_get", "Random")
        
        # Select line based on method
        selected_line = self._select_line(lines, how_to_get)
        
        # Process special formats (same as Input Text)
        processed_text = self._process_text(selected_line)
        
        print(f"[READ_TXT] Selected line: {processed_text}")
        
        # Save to variable if specified
        variable = self.params.get("variable", "")
        if variable:
            globals_var = GlobalVariables()
            globals_var.set(variable, processed_text)
            print(f"[READ_TXT] Saved to variable '{variable}': {processed_text}")
        
        # Get how_to_input method and execute
        how_to_input = self.params.get("how_to_input", "Random")
        self._input_text(processed_text, how_to_input)
    
    def _select_line(self, lines, how_to_get):
        """Select line based on how_to_get method"""
        if how_to_get == "Random":
            return random.choice(lines)
        elif how_to_get == "Sequential by loop":
            # Get loop index from global variables
            globals_var = GlobalVariables()
            loop_index_str = globals_var.get("loop_index", "0")
            try:
                loop_index = int(loop_index_str)
                # Use modulo to loop through lines (1-based index)
                index = loop_index % len(lines)
                return lines[index]
            except:
                # Fallback to first line
                return lines[0]
        else:
            # Default: first line
            return lines[0]
    
    def _process_text(self, text):
        """Process special text formats (same as Input Text action)"""
        # Replace <VARIABLE_NAME> with variable value
        globals_var = GlobalVariables()
        
        # Pattern: <VARIABLE_NAME>
        def replace_variable(match):
            var_name = match.group(1)
            return globals_var.get(var_name, f"<{var_name}>")  # Keep original if not found
        
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
        """Input text using specified method (same as Input Text action)"""
        if how_to_input == "Random":
            # Randomly choose between Copy & Paste and Press Keyboard
            how_to_input = random.choice(["Copy & Paste", "Press Keyboard"])
        
        if how_to_input == "Copy & Paste":
            # Use clipboard
            pyperclip.copy(text)
            time.sleep(0.1)  # Small delay
            pyautogui.hotkey('ctrl', 'v')
            print(f"[READ_TXT] Input via Copy & Paste")
            
        elif how_to_input == "Press Keyboard":
            # Type character by character
            print(f"[READ_TXT] Input via Press Keyboard")
            for char in text:
                if self.should_stop():
                    break
                pyautogui.press(char)
                time.sleep(random.uniform(0.05, 0.15))

    def _resolve_file_path(self):
        """
        Resolve file path with priority:
        1. From global variable (if file_path_variable is set)
        2. From direct file_path parameter
        """
        from models.global_variables import GlobalVariables
    
        # ➊ Try to get from variable first (PRIORITY)
        file_path_variable = self.params.get("file_path_variable", "").strip()
    
        if file_path_variable:
            # Variable name is specified, try to get its value
            globals_var = GlobalVariables()
            file_path_from_var = globals_var.get(file_path_variable, "")
        
            if file_path_from_var:
                print(f"[READ_TXT] Using file path from variable '{file_path_variable}': {file_path_from_var}")
                return file_path_from_var
            else:
                print(f"[READ_TXT] Warning: Variable '{file_path_variable}' not found or empty")
    
        # ➋ Fallback to direct file path
        file_path = self.params.get("file_path", "").strip()
    
        if file_path:
            print(f"[READ_TXT] Using direct file path: {file_path}")
            return file_path
    
        return None
