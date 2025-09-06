
import time
import pyautogui
from abc import ABC, abstractmethod
import keyboard

class BaseAction(ABC):
    """Lớp cơ sở cho tất cả các play handler"""

    def __init__(self, root, action, view, model, controller):
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
        self.model = model
        self.controller = controller
        self.params = action.parameters
        self.is_running = False  # Trạng thái đang chạy
        self.stop_requested = False  # Cờ báo hiệu dừng
    
    
    def play(self):
        """Thực thi hành động"""
        import random as rand  # Import với tên khác để tránh xung đột

        # Kiểm tra Random Skip Action
        random_skip = int(self.params.get("random_skip", "0"))
        if random_skip > 0:
            skip_value = rand.randint(0, random_skip)
            if skip_value == 0:
               
                return True  # Trả về True để biểu thị điều kiện sai

        # Kiểm tra điều kiện break
        if self.should_break_action():
            # Hiển thị thông báo hành động bị bỏ qua do điều kiện break
            if self.is_running and hasattr(self, 'action_frame') and self.action_frame:
                # Đánh dấu đã đánh giá condition để phân biệt với else
                self.condition_evaluated = False
            return True  # Trả về True để biểu thị điều kiện sai

        # Lấy action frame từ ActionListView
        for frame in self.view.action_frames:
            if frame.action.id == self.action.id:  # Cần thêm id vào ActionItem để so sánh             
                break    

        # Lấy giá trị repeat_random
        repeat_random = int(self.params.get("repeat_random", "0"))
        try:
            repeat_random = int(repeat_random)
        except (ValueError, TypeError):
            repeat_random = 0

        # Xác định số lần lặp lại
        if repeat_random <= 1:
            # Nếu <= 0, chạy một lần
            repeat_count = 1
        else:
            # Nếu > 0, random từ 0 đến repeat_random
            repeat_count = rand.randint(2, repeat_random)

        # Đánh dấu condition đã được đánh giá và là true
        self.condition_evaluated = True
        
        # Kiểm tra nếu đã được thực thi rồi thì skip
        if hasattr(self, '_already_executed') and self._already_executed:
            return self._cached_result
    
        final_result = None  # Lưu kết quả cuối cùng
        for i in range(repeat_count):
            # Hook cho các lớp con có thể thêm logic trước khi thực thi
            result = self.prepare_play()
            final_result = result  # Lưu kết quả mỗi lần lặp

            # Trì hoãn thực thi
            self.delay_execution()
            if self.stop_requested:
                return final_result  # Exit loop if stop requested

        # Đánh dấu đã thực thi và cache kết quả
        self._already_executed = True
        self._cached_result = final_result
    
        return final_result  # Return SAU KHI hoàn thành vòng lặp


    def reset_execution_state(self):
        """Reset execution state để có thể chạy lại"""
        if hasattr(self, '_already_executed'):
            delattr(self, '_already_executed')
        if hasattr(self, '_cached_result'):
            delattr(self, '_cached_result')
    
    
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
        
        else:
            # Nếu random_time = 0, sử dụng default_delay
            delay_seconds = default_delay
            
        def execute_after_delay():
            self.setup_esc_handler()  # Thiết lập bắt sự kiện ESC
             # Kiểm tra và chuyển đổi chương trình trước khi thực thi action
            if self.check_and_switch_to_program():
                pass
            
            self.is_running = False  # Đặt lại trạng thái sau khi chạy xong
            self.cleanup_esc_handler()  # Hủy bắt sự kiện ESC
        
        self.is_running = True  # Đánh dấu đang chạy
        self.stop_requested = False  # Reset cờ dừng
        self.root.after(int(delay_seconds * 1000), execute_after_delay)
        
    
    def should_break_action(self):
        """
        Đánh giá các điều kiện break để xác định có nên dừng hành động hay không
        Returns:
            bool: True nếu action nên bị dừng, False nếu nên tiếp tục thực thi
        """
        # Lấy danh sách điều kiện break từ parameters
        break_conditions = self.params.get("break_conditions", [])
    
        # Nếu không có điều kiện nào, hành động sẽ được thực thi (không break)
        if not break_conditions:
            return False
    
        # Khởi tạo các biến
        from models.global_variables import GlobalVariables
        globals_var = GlobalVariables()
    
        # Trường hợp đặc biệt: chỉ có một điều kiện
        if len(break_conditions) == 1:
            condition = break_conditions[0]
            variable_name = condition["variable"]
            expected_value = condition["value"]
        
            # Nếu biến không tồn tại, điều kiện không thỏa mãn (break action)
            if not hasattr(globals_var, 'exists') or not globals_var.exists(variable_name):
                return True # Thay đổi: Trả về True nếu biến không tồn tại
        
            # So sánh giá trị
            actual_value = globals_var.get(variable_name)
            print(variable_name+' - '+actual_value)
        
            # Trả về True nếu giá trị không khớp (break action)
            return str(actual_value) != str(expected_value)
    
        # Xử lý nhiều điều kiện
        result = None
    
        for idx, condition in enumerate(break_conditions):
            variable_name = condition["variable"]
            expected_value = condition["value"]
        
            # Dòng đầu tiên không có logical_op
            logical_op = condition.get("logical_op", "AND") if idx > 0 else None
        
            # Kiểm tra biến có tồn tại trong GlobalVariables không
            if hasattr(globals_var, 'exists') and globals_var.exists(variable_name):
                actual_value = globals_var.get(variable_name)
                # So sánh giá trị (chuyển sang chuỗi để so sánh)
                condition_result = str(actual_value) == str(expected_value)
            else:
                # Thay đổi: Nếu biến không tồn tại, condition_result = False
                condition_result = False
        
            # Kết hợp với kết quả trước đó dựa trên toán tử logic
            if idx == 0:
                # Điều kiện đầu tiên thiết lập giá trị khởi tạo
                result = condition_result
            elif logical_op == "AND":
                result = result and condition_result
            elif logical_op == "OR":
                result = result or condition_result
    
        # Đảo ngược kết quả: True = break action, False = continue
        return not result




        
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
    
    def check_and_switch_to_program(self):
        """
        Kiểm tra chương trình từ tham số, chuyển đổi và maximize cửa sổ nếu cần
    
        Returns:
            bool: True nếu thành công, False nếu không
        """
        import os
        import win32gui
        import win32process
        import psutil
    
        # Lấy đường dẫn chương trình từ tham số
        program_path = self.params.get("program", "")
    
        # Nếu không có đường dẫn, không cần xử lý
        if not program_path or not os.path.exists(program_path):
            return True
    
        # Lấy tên file thực thi từ đường dẫn
        program_name = os.path.basename(program_path).lower()
    
        # Hàm callback để kiểm tra từng cửa sổ
        def enum_windows_callback(hwnd, target_windows):
            if not win32gui.IsWindowVisible(hwnd) or not win32gui.IsWindowEnabled(hwnd):
                return True
            
            # Lấy process ID từ window handle
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process = psutil.Process(pid)
                process_name = process.name().lower()
            
                # Nếu tên process khớp với program_name, thêm vào danh sách
                if program_name == process_name or program_path.lower() == process.exe().lower():
                    target_windows.append((hwnd, process_name))
            except:
                pass
            return True
    
        # Kiểm tra cửa sổ hiện tại
        current_hwnd = win32gui.GetForegroundWindow()
        try:
            _, current_pid = win32process.GetWindowThreadProcessId(current_hwnd)
            current_process = psutil.Process(current_pid)
            current_exe = current_process.exe().lower()
        
            # Nếu cửa sổ hiện tại đã là chương trình đích, chỉ cần maximize
            if current_exe == program_path.lower() or current_process.name().lower() == program_name:
                # Maximize cửa sổ hiện tại
                win32gui.ShowWindow(current_hwnd, 3)  # SW_MAXIMIZE = 3
                # Delay 3 giây để đợi phần mềm load
                time.sleep(3)
                return True
        except:
            pass
    
        # Tìm tất cả cửa sổ của chương trình đích
        target_windows = []
        win32gui.EnumWindows(enum_windows_callback, target_windows)
    
        # Nếu tìm thấy cửa sổ, chuyển đổi và maximize
        if target_windows:
            hwnd, _ = target_windows[0]  # Lấy cửa sổ đầu tiên tìm thấy
        
            # Kiểm tra nếu cửa sổ đã maximize
            placement = win32gui.GetWindowPlacement(hwnd)
            if placement[1] != 3:  # Nếu chưa maximize
                win32gui.ShowWindow(hwnd, 3)  # SW_MAXIMIZE = 3
        
            # Đưa cửa sổ lên trước
            win32gui.SetForegroundWindow(hwnd)
            
            # Delay 3 giây để đợi phần mềm load
            time.sleep(3)
            return True   
        
    
        return False

    def get_region(self):
        """Lấy vùng quét dựa trên tham số"""
        # Kiểm tra xem có sử dụng fullscreen không
        if self.params.get("fullscreen", False):
            # Sử dụng PyAutoGUI để lấy kích thước màn hình
            import pyautogui
            screen_width, screen_height = pyautogui.size()
        
            # Trả về toàn bộ màn hình làm vùng quét
            return (0, 0, screen_width, screen_height)
        else:
            # Sử dụng giá trị x, y, width, height đã cung cấp
            x = int(self.params.get("x", 0))
            y = int(self.params.get("y", 0))
            width = int(self.params.get("width", 0)) 
            height = int(self.params.get("height", 0))
        
            return (x, y, width, height)
        

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
                delay = random.uniform(1, 3)   
            
    
                # Thực hiện delay
                time.sleep(delay)
    
                # Kiểm tra lại nếu người dùng đã yêu cầu dừng trong thời gian delay
                if self.should_stop():
                    return target_x, target_y
    
                # Kiểm tra điều kiện Is Clickable nếu được chọn
                if self.params.get("is_clickable", False):
                    # Kiểm tra xem cursor có phải là hand không
                    if not self.is_hand_cursor():                    
                        return target_x, target_y
                    
                # Thực hiện double click
                pyautogui.doubleClick()

                return target_x, target_y
        except:
            return None, None  # Trả về None nếu di chuyển bị dừng
        
    def is_hand_cursor(self):
        """Kiểm tra xem cursor hiện tại có phải là hand cursor hay không"""
        import win32gui
        
        time.sleep(0.5)
        try:
            # Lấy thông tin cursor
            cursor_info = win32gui.GetCursorInfo()
            hand_cursor_handles = [32649, 65567, 65563, 65561, 60171, 60169, 32513]
            if cursor_info[1] in hand_cursor_handles:
                return True
        except Exception as e:           
            return False


    def _execute_nested_actions(self):
        """Thực hiện các actions lồng trong điều kiện - Phương thức này đã lỗi thời, giữ lại để tương thích"""
        # Tạo ID ngẫu nhiên để tương thích với thiết kế mới
        import uuid
        condition_id = str(uuid.uuid4())
    
        # Kiểm tra nếu phương thức _execute_condition_block tồn tại trước khi gọi
        if hasattr(self, '_execute_condition_block'):
            self._execute_condition_block(condition_id)
        else:
            # Phương pháp cũ nếu không có phương thức mới
            from constants import ActionType
            from controllers.actions.action_factory import ActionFactory
        
            all_actions = self.model.get_all_actions()
            current_index = next((i for i, a in enumerate(all_actions) if a.id == self.action.id), -1)
            if current_index < 0:
                return
            
            # Biến theo dõi cấp độ lồng
            nested_level = 0
        
            # Duyệt qua các action sau action hiện tại
            next_index = current_index + 1
            while next_index < len(all_actions):
                action = all_actions[next_index]
            
                # Cập nhật nested_level dựa trên loại action
                if action.action_type == ActionType.IF_CONDITION:
                    nested_level += 1
                elif action.action_type == ActionType.END_IF_CONDITION:
                    nested_level -= 1
                    # Kết thúc khi nested_level < 0 (đã tìm thấy END_IF tương ứng)
                    if nested_level < 0:
                        break
                    
                # Tạo handler và thực thi action
                if nested_level >= 0:
                    handler = ActionFactory.get_handler(
                        self.controller.root, action, self.view, self.model, self.controller
                    )
                
                    if handler:
                        # Thiết lập action frame
                        action_frame = next((f for f in self.view.action_frames
                                           if f.action.id == action.id), None)
                        if action_frame:
                            handler.action_frame = action_frame
                    
                        # Thực thi action
                        handler.play()
            
                # Tăng chỉ số
                next_index += 1