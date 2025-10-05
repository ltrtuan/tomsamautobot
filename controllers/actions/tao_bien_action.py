# controllers/actions/tao_bien_action.py

from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
import os

class TaoBienAction(BaseAction):
    """Handler for create variable action (multi-variable support)."""
    
    def prepare_play(self):
        """Execute create variable action"""
        if self.should_stop():
            return
        
        # Get variables list
        variables = self.params.get("variables", [])
        
        if not variables:
            print("[TAO_BIEN] No variables to create")
            return
        
        globals_var = GlobalVariables()
        
        # Process each variable
        for var_data in variables:
            var_name = var_data.get("name", "").strip()
            var_value = var_data.get("value", "")
            var_file = var_data.get("file_path", "").strip()
            
            if not var_name:
                continue
            
            # ➊ PRIORITY: Use file_path if exists
            if var_file and os.path.exists(var_file):
                final_value = var_file
                print(f"[TAO_BIEN] Set variable '{var_name}' = '{final_value}' (from file path)")
            else:
                # ➋ FALLBACK: Use direct value
                final_value = var_value
                print(f"[TAO_BIEN] Set variable '{var_name}' = '{final_value}' (from value)")
            
            # Set global variable
            globals_var.set(var_name, final_value)
