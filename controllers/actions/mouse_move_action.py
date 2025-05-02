from controllers.actions.base_action import BaseAction

class MouseMoveAction(BaseAction):
    """Handler để thực thi hành động di chuyển chuột"""
    
    def prepare_play(self):
        """Thực thi hành động di chuyển chuột"""
        pass
    
    def execute_action(self):
        """Thực hiện di chuyển chuột sau khi trì hoãn"""
        if self.should_stop():
            return
        
        # Lấy các tham số cần thiết
        x = int(self.params.get("x", 0))
        y = int(self.params.get("y", 0))
        width = int(self.params.get("width", 0))
        height = int(self.params.get("height", 0))
        duration = float(self.params.get("duration", 0.5))
        
        # Di chuyển chuột (sử dụng phương thức từ lớp cơ sở)
        self.move_mouse(x, y, width, height, duration, random_in_region=True)
