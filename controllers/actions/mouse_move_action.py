from controllers.actions.base_action import BaseAction

class MouseMoveAction(BaseAction):
    """Handler để thực thi hành động di chuyển chuột"""    
    
    def prepare_play(self):
        """Thực hiện di chuyển chuột sau khi trì hoãn"""
        if self.should_stop():
            return
       
        # Lấy thông tin vùng quét
        region = self.get_region()
        x, y, width, height = region
        
        # Di chuyển chuột (sử dụng phương thức từ lớp cơ sở)
        self.move_mouse(x, y, width, height)
