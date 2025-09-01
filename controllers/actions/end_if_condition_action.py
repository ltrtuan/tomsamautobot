from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables

class EndIfConditionAction(BaseAction):
    def prepare_play(self):
        """Xử lý END_IF condition"""
        # Lấy thông tin từ GlobalVariables
        from models.global_variables import GlobalVariables
        globals_var = GlobalVariables()
        
        # Giảm cấp độ lồng của IF
        current_level = globals_var.get("__condition_stack_size", 0) - 1
        
        # Đảm bảo không âm
        current_level = max(0, current_level)
        globals_var.set("__condition_stack_size", current_level)
        
        # Debug thông tin
        if hasattr(self, 'action_frame') and self.action_frame:
            self.action_frame.show_temporary_notification(
                f"Kết thúc khối IF/ELSE IF (cấp {current_level})"
            )
        
        return False
    
    def _execute_condition_block(self, condition_id):
        """
        Phương thức này để tương thích với thiết kế mới, 
        nhưng END_IF không cần thực thi các action lồng
        """
        # END_IF không cần thực thi các action lồng
        if hasattr(self, 'action_frame') and self.action_frame:
            self.action_frame.show_temporary_notification(
                "END_IF không cần thực thi các action lồng"
            )
        return


