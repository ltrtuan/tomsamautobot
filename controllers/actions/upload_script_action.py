# controllers/actions/upload_script_action.py

import json
import os
from tkinter import messagebox
from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from models.action_model import ActionItem
from constants import ActionType

class UploadScriptAction(BaseAction):
    """Handler for Upload Script action"""
    
    @staticmethod
    def validate_script_file(file_path):
        """
        Validate script JSON file format and ActionType
        Returns: (is_valid, error_message, actions_data)
        """
        # Check file exists
        if not os.path.exists(file_path):
            return False, f"File không tồn tại: {file_path}", None
        
        try:
            # Parse JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check format: must be array
            if not isinstance(data, list):
                return False, "File JSON phải là một array chứa danh sách actions", None
            
            if len(data) == 0:
                return False, "File JSON rỗng, không có action nào", None
            
            # Validate each action
            valid_action_types = ActionType.get_display_values()
            
            for idx, action in enumerate(data):
                # Check structure
                if not isinstance(action, dict):
                    return False, f"Action #{idx+1}: Không phải dict object", None
                
                # Check required keys
                if "action_type" not in action:
                    return False, f"Action #{idx+1}: Thiếu key 'action_type'", None
                
                if "parameters" not in action:
                    return False, f"Action #{idx+1}: Thiếu key 'parameters'", None
                
                # Validate action_type
                action_type = action["action_type"]
                if action_type not in valid_action_types:
                    return False, (
                        f"Action #{idx+1}: action_type không hợp lệ\n"
                        f"'{action_type}' không tồn tại trong constants.py\n"
                        f"Valid types: {', '.join(valid_action_types[:5])}..."
                    ), None
                
                # Check parameters is dict
                if not isinstance(action["parameters"], dict):
                    return False, f"Action #{idx+1}: 'parameters' phải là dict object", None
                
                # Check optional keys
                if "is_disabled" in action and not isinstance(action["is_disabled"], bool):
                    return False, f"Action #{idx+1}: 'is_disabled' phải là boolean (true/false)", None
            
            return True, f"✓ File hợp lệ với {len(data)} actions", data
            
        except json.JSONDecodeError as e:
            return False, f"JSON syntax error:\nLine {e.lineno}: {e.msg}", None
        except Exception as e:
            return False, f"Lỗi đọc file: {str(e)}", None
    
    def prepare_play(self):
        """
        Execute Upload Script action
        Load JSON và execute tất cả actions bên trong
        """
        try:
            # ========== LẤY SCRIPT PATH ==========
            script_path_variable = self.params.get("script_path_variable", "").strip()
            script_path = ""
            
            if script_path_variable:
                script_path = GlobalVariables().get(script_path_variable, "").strip()
                if script_path:
                    print(f"[UPLOAD_SCRIPT] Using path from variable '{script_path_variable}': {script_path}")
                else:
                    print(f"[UPLOAD_SCRIPT] Variable '{script_path_variable}' is empty, trying browse...")
            
            if not script_path:
                script_path = self.params.get("script_path", "").strip()
                if script_path:
                    print(f"[UPLOAD_SCRIPT] Using path from browse: {script_path}")
            
            if not script_path:
                print("[UPLOAD_SCRIPT] Error: No script path provided")
                return
            
            # ========== VALIDATE FILE ==========
            is_valid, message, actions_data = self.validate_script_file(script_path)
            
            if not is_valid:
                print(f"[UPLOAD_SCRIPT] Validation failed: {message}")
                messagebox.showerror("Script Validation Error", message)
                return
            
            print(f"[UPLOAD_SCRIPT] {message}")
            
            # ========== EXECUTE ACTIONS ==========
            # Gọi controller để execute nested actions
            if hasattr(self.controller, 'execute_nested_actions'):
                print(f"[UPLOAD_SCRIPT] Starting execution of {len(actions_data)} actions...")
                
                # Convert dict to ActionItem objects
                action_items = []
                for action_dict in actions_data:
                    action_item = ActionItem(
                        action_type=action_dict["action_type"],
                        parameters=action_dict["parameters"]
                    )
                    if "is_disabled" in action_dict:
                        action_item.is_disabled = action_dict["is_disabled"]
                    action_items.append(action_item)
                
                # Execute nested
                success = self.controller.execute_nested_actions(action_items)
                
                if success:
                    print(f"[UPLOAD_SCRIPT] ✓ Script executed successfully")
                else:
                    print(f"[UPLOAD_SCRIPT] ✗ Script execution stopped/failed")
            else:
                print("[UPLOAD_SCRIPT] Error: Controller không hỗ trợ execute_nested_actions")
            
        except Exception as e:
            print(f"[UPLOAD_SCRIPT] Error: {e}")
            import traceback
            traceback.print_exc()
