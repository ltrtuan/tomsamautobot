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

    # ===== STATIC METHOD để call từ action khác =====
    @staticmethod
    def move_and_click_static(x, y, click_type=None, fast=False):
        """
        Static method để move mouse và click từ action khác
        
        Args:
            x, y: Tọa độ đích
            click_type: "single_click", "double_click" hoặc None
            fast: True để move nhanh, False để move tự nhiên
        """
        from models.human_like_movement import HumanLikeMovement
        import pyautogui
        import time
        
        # Get current position
        current_x, current_y = pyautogui.position()
        
        # Move using HumanLikeMovement
        HumanLikeMovement.move_cursor_humanlike(current_x, current_y, x, y, fast)
        
        # Click if needed
        if click_type == "single_click":
            time.sleep(1)
            pyautogui.click()
        elif click_type == "double_click":
            time.sleep(1)
            pyautogui.doubleClick()