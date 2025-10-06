# controllers/actions/run_cmd_action.py
from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
import subprocess
import os

class RunCmdAction(BaseAction):
    """Handler để chạy Windows CMD commands"""
    
    def prepare_play(self):
        """Thực hiện chạy CMD command sau khi trì hoãn"""
        
        try:
            # Lấy command
            cmd_command = self.params.get("cmd_command", "").strip()
            
            if not cmd_command:
                print("[RUN_CMD] No command provided")
                self.set_variable(False)
                return
            
            print(f"[RUN_CMD] Executing command: {cmd_command}")
            
            # Chạy command
            success = self.run_command(cmd_command)
            
            # Set variable
            self.set_variable(success)
            
        except Exception as e:
            print(f"[RUN_CMD] Error: {e}")
            import traceback
            traceback.print_exc()
            self.set_variable(False)
    
    def run_command(self, cmd_command):
        """Chạy Windows CMD command"""
        try:
            # Method 1: subprocess.run (Python 3.5+)
            # shell=True cho phép chạy cmd commands trực tiếp
            result = subprocess.run(
                cmd_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # Timeout 30 giây
            )
            
            # Log output
            if result.stdout:
                print(f"[RUN_CMD] Output:\n{result.stdout}")
            
            if result.stderr:
                print(f"[RUN_CMD] Error output:\n{result.stderr}")
            
            # Check return code
            if result.returncode == 0:
                print(f"[RUN_CMD] Command executed successfully")
                return True
            else:
                print(f"[RUN_CMD] Command failed with return code: {result.returncode}")
                return False
        
        except subprocess.TimeoutExpired:
            print(f"[RUN_CMD] Command timeout after 30 seconds")
            return False
        
        except Exception as e:
            print(f"[RUN_CMD] Error executing command: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def set_variable(self, success):
        """Set variable với kết quả True/False"""
        variable = self.params.get("variable", "")
        if variable:
            GlobalVariables().set(variable, "true" if success else "false")
            print(f"[RUN_CMD] Variable '{variable}' = {'true' if success else 'false'}")
