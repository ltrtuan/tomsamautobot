# actions/play_handlers/tao_bien_handler.py
from controllers.actions.base_action import BaseAction

class TaoBienAction(BaseAction):
    """Handler để thực thi hành động tạo biến"""
    
    def prepare_play(self):
        """Thực hiện tạo biến sau khi trì hoãn"""
        if self.should_stop():
            return
        
        # Lấy thông tin biến từ tham số
        variable_name = self.params.get("variable", "")
        variable_value = self.params.get("result_action", "")
        
        # Nếu không có tên biến thì không làm gì
        if not variable_name:
            if hasattr(self, 'action_frame') and self.action_frame:
                self.action_frame.show_temporary_notification("Tên biến không được để trống")
            return
        
        # Tạo biến trong GlobalVariables
        from models.global_variables import GlobalVariables
        globals_var = GlobalVariables()
        globals_var.set(variable_name, variable_value)
        
        # Hiển thị thông báo thành công
        if hasattr(self, 'action_frame') and self.action_frame:
            self.action_frame.show_temporary_notification(
                f"Đã tạo biến: {variable_name} = {variable_value}"
            )
