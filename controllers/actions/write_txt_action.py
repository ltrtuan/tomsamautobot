# actions/write_txt_action.py

from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
import os
import re
import random
import string

class WriteTxtAction(BaseAction):
    """Action to append text content to existing TXT file"""
    
    def prepare_play(self):
        """Execute write txt file action after delay"""
        if self.should_stop():
            return
    
        # Get file path (priority: variable > browse)
        file_path_var = self.params.get("file_path_variable", "").strip()
        file_path = self.params.get("file_path", "").strip()
    
        # Determine final file path
        if file_path_var:
            globals_var = GlobalVariables()
            final_path = globals_var.get(file_path_var, "")
            print(f"[WRITE_TXT] Using variable '{file_path_var}': {final_path}")
        else:
            final_path = file_path
            print(f"[WRITE_TXT] Using browse path: {final_path}")
    
        # Validate file path
        if not final_path:
            print("[WRITE_TXT] No file path provided. Skipping.")
            return
    
        # ✅ CHECK: File có tồn tại không - SKIP nếu không tồn tại
        if not os.path.exists(final_path):
            print(f"[WRITE_TXT] File does not exist: {final_path}. Skipping write operation.")
            return
    
        # Get content list
        content_list_str = self.params.get("content", "").strip()
    
        if not content_list_str:
            print("[WRITE_TXT] No content to write. Skipping.")
            return
    
        # ✅ PARSE: Split by semicolon
        content_items = [item.strip() for item in content_list_str.split(";") if item.strip()]
    
        if not content_items:
            print("[WRITE_TXT] No valid content items. Skipping.")
            return
    
        # ✅ PROCESS ALL: Xử lý pattern cho TẤT CẢ items
        processed_items = []
        for item in content_items:
            processed_text = self._process_text(item)
            processed_items.append(processed_text)
    
        # ✅ WRITE ALL: Ghi với logic xuống dòng thông minh
        try:
            # Đọc content hiện tại
            with open(final_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
            # Xử lý content hiện tại: xóa dòng trắng cuối
            if existing_content:
                existing_content = existing_content.rstrip('\n')
            
                # Nếu còn content, thêm 1 xuống dòng để cách content mới
                if existing_content:
                    existing_content += '\n'
        
            # Tạo nội dung mới (các items cách nhau bởi \n)
            new_content = '\n'.join(processed_items)
        
            # Gộp content cũ + content mới
            final_content = existing_content + new_content
        
            # Ghi đè toàn bộ file
            with open(final_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
        
            print(f"[WRITE_TXT] Successfully wrote {len(processed_items)} line(s) to: {final_path}")
            for idx, content in enumerate(processed_items, 1):
                print(f"[WRITE_TXT]   Line {idx}: {content}")
        
        except Exception as e:
            print(f"[WRITE_TXT] Error writing to file: {e}")
    
    def _process_text(self, text):
        """Process special text formats (giống input_text_action)"""
        # Replace with variable value
        globals_var = GlobalVariables()
        
        # Pattern for <VARIABLE>
        def replace_variable(match):
            var_name = match.group(1)
            value = globals_var.get(var_name, None)
            
            if value is not None:
                print(f"[WRITE_TXT] Replaced <{var_name}> with '{value}'")
                return str(value)
            else:
                print(f"[WRITE_TXT] WARNING: Variable '{var_name}' not found!")
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
