from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
import logging
logger = logging.getLogger('TomSamAutobot')

class ForAction(BaseAction):
    def prepare_play(self):
        """For action được xử lý trực tiếp trong ActionController.run_sequence()"""
        print(f"[FOR ACTION] For action prepare_play() - Logic được xử lý trong controller")
        # ===== CHECK STOP FLAG AT START OF BATCH (FIX) =====
        if self.controller and hasattr(self.controller, 'is_execution_stopped') and self.controller.is_execution_stopped:
            logger.info(f"[ForAction prepare_play PAUSE/BREAK")
            return False
        # ====================================================
        return False  # Không cần xử lý gì thêm ở đây

    def set_loop_index(self, current_iteration, total_iterations):
        """
        Lưu index của vòng lặp hiện tại vào biến global
        0-BASED INDEX: iteration 0,1,2,... (chuẩn lập trình)
        """
        variable_name = self.params.get("index_variable", "loop_index")
        if not variable_name:
            variable_name = "loop_index"
    
        globals_var = GlobalVariables()
    
        # ← 0-BASED: Lưu trực tiếp current_iteration (0,1,2,...)
        globals_var.set(variable_name, str(current_iteration))
        globals_var.set(f"{variable_name}_total", str(total_iterations))
    
        print(f"[FOR ACTION] Set {variable_name} = {current_iteration} (of {total_iterations})")
