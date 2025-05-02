
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
        # Kiểm tra Random Skip Action
        random_skip = int(self.params.get("random_skip", "0"))
        if random_skip > 0:
            import random
            skip_value = random.randint(0, random_skip)
            if skip_value == 0:
                # Hiển thị thông báo action bị bỏ qua
                if hasattr(self, 'action_frame') and self.action_frame:
                    self.action_frame.show_temporary_notification("Hành động được bỏ qua (Random Skip)")
                return  # Thoát khỏi phương thức, không thực thi action
        
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
        self.delay_execution()
    
    def prepare_play(self):
        """
        Hook method - các lớp con có thể ghi đè phương thức này 
        để thêm logic đặc thù trước khi thực thi
        """
        pass

    def show_message(self, title, message):
        """Hiển thị thông báo qua view"""
        self.view.show_message(title, message)
    
    def delay_execution(self, default_delay=2):
        
        """Trì hoãn thực thi dựa trên tham số random_time"""
        # Lấy giá trị random_time từ tham số
        random_time = int(self.params.get("random_time", "0"))
    
        # Nếu random_time > 0, tạo delay ngẫu nhiên từ 1 đến random_time
        if random_time > 0:
            import random
            delay_seconds = random.randint(1, random_time)
        
            if hasattr(self, 'action_frame') and self.action_frame:
                self.action_frame.show_temporary_notification(
                    f"Chờ {delay_seconds} giây trước khi thực thi..."
                )
        else:
            # Nếu random_time = 0, sử dụng default_delay
            delay_seconds = default_delay
            
        def execute_after_delay():
            self.setup_esc_handler()  # Thiết lập bắt sự kiện ESC
            self.execute_action()
            self.is_running = False  # Đặt lại trạng thái sau khi chạy xong
            self.cleanup_esc_handler()  # Hủy bắt sự kiện ESC
        
        self.is_running = True  # Đánh dấu đang chạy
        self.stop_requested = False  # Reset cờ dừng
        self.root.after(int(delay_seconds * 1000), execute_after_delay)
        
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
            
            # Kiểm tra xem có yêu cầu double click không
            if self.params.get("double_click", False):
                # Thêm delay ngẫu nhiên từ 1-3 giây trước khi double click
                if hasattr(self, 'action_frame') and self.action_frame:
                    delay = random.uniform(1, 3)
                    self.action_frame.show_temporary_notification(
                        f"Chờ {delay:.1f} giây trước khi double click..."
                    )
                else:
                    delay = random.uniform(1, 3)
                
                # Thực hiện delay
                time.sleep(delay)
            
                # Kiểm tra lại nếu người dùng đã yêu cầu dừng trong thời gian delay
                if self.should_stop():
                    return target_x, target_y
                
                # Thực hiện double click
                pyautogui.doubleClick()
                
            return target_x, target_y
        except:
            return None, None  # Trả về None nếu di chuyển bị dừng
