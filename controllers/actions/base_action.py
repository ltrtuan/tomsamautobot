
import time
import pyautogui
from abc import ABC, abstractmethod
import keyboard

class BaseAction(ABC):
    """Lớp cơ sở cho tất cả các play handler"""

    def __init__(self, root, action, view):
        """
        Khởi tạo handler
        
        Args:
            root: Tkinter root window
            action: ActionItem được thực thi
            view: View để hiển thị thông báo
        """
        self.root = root
        self.action = action
        self.view = view
        self.params = action.parameters
        self.is_running = False  # Trạng thái đang chạy
        self.stop_requested = False  # Cờ báo hiệu dừng
    
    
    def play(self):
        """Thực thi hành động"""
        # Lấy action frame từ ActionListView
        for frame in self.view.action_frames:
            if frame.action.id == self.action.id:  # Cần thêm id vào ActionItem để so sánh
                # Hiển thị thông báo trên frame thay vì dialog
                frame.show_temporary_notification("Hành động đang được thực thi")
                break
    
        # Hiển thị thông báo trên action frame
        if hasattr(self, 'action_frame') and self.action_frame:
            self.action_frame.show_temporary_notification("Hành động đang được thực thi")
          
        # Hook cho các lớp con có thể thêm logic trước khi thực thi
        self.prepare_play()
        
        # Trì hoãn thực thi
        self.delay_execution(2)
    
    def prepare_play(self):
        """
        Hook method - các lớp con có thể ghi đè phương thức này 
        để thêm logic đặc thù trước khi thực thi
        """
        pass

    def show_message(self, title, message):
        """Hiển thị thông báo qua view"""
        self.view.show_message(title, message)
    
    def delay_execution(self, seconds=2):
        """Trì hoãn thực thi"""
        def execute_after_delay():
            self.setup_esc_handler()  # Thiết lập bắt sự kiện ESC
            self.execute_action()
            self.is_running = False  # Đặt lại trạng thái sau khi chạy xong
            self.cleanup_esc_handler()  # Hủy bắt sự kiện ESC
        
        self.is_running = True  # Đánh dấu đang chạy
        self.stop_requested = False  # Reset cờ dừng
        self.root.after(int(seconds * 1000), execute_after_delay)
        
    def setup_esc_handler(self):
        """Thiết lập xử lý phím ESC"""
        keyboard.on_press_key("esc", self.on_esc_pressed)
    
    def cleanup_esc_handler(self):
        """Hủy bỏ xử lý phím ESC"""
        keyboard.unhook_key("esc")
    
    def on_esc_pressed(self, event):
        """Xử lý khi phím ESC được nhấn"""
        if self.is_running:
            self.stop_requested = True
            self.show_message("Thông báo", "Đã dừng action theo yêu cầu")
            return False  # Dừng bắt sự kiện
    
    def should_stop(self):
        """Kiểm tra xem có cần dừng không"""
        return self.stop_requested
    
    
    @abstractmethod
    def execute_action(self):
        """Thực hiện hành động cụ thể sau khi trì hoãn"""
        pass

    def move_mouse(self, x, y, width=0, height=0, duration=0.5, random_in_region=False):
        """
        Di chuyển chuột đến một vị trí hoặc vùng
        
        Args:
            x, y: Tọa độ
            width, height: Kích thước vùng (nếu > 0)
            duration: Thời gian di chuyển (giây)
            random_in_region: Có di chuyển ngẫu nhiên trong vùng không
        """
        from models.human_like_movement import HumanLikeMovement
        import random
        
        # Kiểm tra nếu người dùng yêu cầu dừng
        if self.should_stop():
            return None, None
        
        # Lấy vị trí hiện tại của chuột
        current_x, current_y = pyautogui.position()
        
        # Xác định tọa độ đích
        if random_in_region and width > 0 and height > 0:
            target_x = random.randint(x, x + width)
            target_y = random.randint(y, y + height)
        else:
            target_x, target_y = x, y
        
        # Tính toán speed_factor dựa trên duration
        if duration > 0:
            speed_factor = 1.0 / duration
        else:
            speed_factor = 10.0
        
        # Di chuyển chuột với human-like movement
        try:
            HumanLikeMovement.move_cursor(current_x, current_y, target_x, target_y, speed_factor, 
                                        stop_check=self.should_stop)
            return target_x, target_y
        except:
            return None, None  # Trả về None nếu di chuyển bị dừng
