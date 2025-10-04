from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables

class ForAction(BaseAction):
    def prepare_play(self):
        """For action được xử lý trực tiếp trong ActionController.run_sequence()"""
        print(f"[FOR ACTION] For action prepare_play() - Logic được xử lý trong controller")
        return False  # Không cần xử lý gì thêm ở đây

    def set_loop_index(self, current_iteration, total_iterations):
        """Lưu index của vòng lặp hiện tại vào biến global"""
        # Lấy tên biến từ parameters (nếu có)
        variable_name = self.params.get("index_variable", "loop_index")  # Default: "loop_index"
        
        if not variable_name:
            variable_name = "loop_index"  # Fallback default
            
        # Tạo biến trong GlobalVariables (tương tự tao_bien_action)
        globals_var = GlobalVariables()
        globals_var.set(variable_name, str(current_iteration))  # Lưu iteration hiện tại
        globals_var.set(f"{variable_name}_total", str(total_iterations))  # Bonus: total iterations
        
        print(f"[FOR ACTION] Set {variable_name} = {current_iteration} (of {total_iterations})")