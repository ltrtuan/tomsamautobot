
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

        # ➊ REFACTORED: Lấy giá trị repeat_fixed và repeat_random
        repeat_fixed = self.params.get("repeat_fixed", "0")
        repeat_random = self.params.get("repeat_random", "0")
    
        try:
            repeat_fixed = int(repeat_fixed)
        except (ValueError, TypeError):
            repeat_fixed = 0
    
        try:
            repeat_random = int(repeat_random)
        except (ValueError, TypeError):
            repeat_random = 0
    
        # ➋ Tính toán số lần repeat: Fixed + Random(0-X)
        if repeat_fixed <= 0 and repeat_random <= 0:
            # Cả 2 đều = 0: chạy 1 lần
            repeat_count = 1
        else:
            # Fixed + Random
            if repeat_random > 0:
                random_count = rand.randint(0, repeat_random)
            else:
                random_count = 0
        
            repeat_count = repeat_fixed + random_count
        
            # Đảm bảo ít nhất chạy 1 lần
            if repeat_count < 1:
                repeat_count = 1

        # Đánh dấu condition đã được đánh giá và là true
        self.condition_evaluated = True
        
        # Kiểm tra nếu đã được thực thi rồi thì skip
        if hasattr(self, '_already_executed') and self._already_executed:
            return self._cached_result
    
        final_result = None  # Lưu kết quả cuối cùng
        for i in range(repeat_count):
            # Trì hoãn thực thi
            self.delay_execution()
             
            if self.stop_requested:
                return final_result  # Exit loop if stop requested
            
            # Hook cho các lớp con có thể thêm logic trước khi thực thi
            result = self.prepare_play()
            final_result = result  # Lưu kết quả mỗi lần lặp
           

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
    
    def delay_execution(self, default_delay=1):
        """Trì hoãn thực thi và check program ĐỒNG BỘ"""
        # Lấy giá trị random_time từ tham số
        random_time = int(self.params.get("random_time", "0"))
    
        # Tính delay
        if random_time > 0:
            import random
            delay_seconds = random.randint(1, random_time)
        else:
            delay_seconds = default_delay
    
        # Sleep đồng bộ
        time.sleep(delay_seconds)
    
        # Check program ĐỒNG BỘ ngay sau khi sleep xong
        self.setup_esc_handler()
    
        if not self.check_and_switch_to_program():
            # Program không ready, đánh dấu để skip
            print("[PROGRAM] Program not ready, skipping this action")
            self.stop_requested = True
            self.cleanup_esc_handler()
            return
    
        self.cleanup_esc_handler()
        # ← Khi tới đây, program đã ready và prepare_play() sẽ chạy ngay sau

        
    
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
        Kiểm tra chương trình, filter theo window title nếu có
        """
        import os
        import win32gui
        import win32process
        import win32con
        import psutil
        import subprocess
        import time
        from models.global_variables import GlobalVariables
    
        # ========== ƯU TIÊN: Variable name trước cho PROGRAM PATH ==========
        program_variable = self.params.get("program_variable", "").strip()
        program_path = ""
    
        if program_variable:
            program_path = GlobalVariables().get(program_variable, "").strip()
            if program_path:
                print(f"[PROGRAM] Using path from variable '{program_variable}': {program_path}")
            else:
                print(f"[PROGRAM] Variable '{program_variable}' is empty, trying browse option...")
    
        if not program_path:
            program_path = self.params.get("program", "").strip()
            if program_path:
                print(f"[PROGRAM] Using path from browse: {program_path}")
    
        if not program_path:
            return True
    
        if not os.path.exists(program_path):
            print(f"[PROGRAM] Error: File not found: {program_path}")
            return False
    
        program_name = os.path.basename(program_path).lower()
    
        # ========== ƯU TIÊN: Variable name trước cho WINDOW TITLE ==========
        window_title_variable = self.params.get("window_title_variable", "").strip()
        window_title_filter = ""
    
        if window_title_variable:
            window_title_filter = GlobalVariables().get(window_title_variable, "").strip()
            if window_title_filter:
                print(f"[PROGRAM] Using window title from variable '{window_title_variable}': {window_title_filter}")
            else:
                print(f"[PROGRAM] Variable '{window_title_variable}' is empty, trying direct input...")
    
        # Nếu không có variable hoặc variable rỗng, dùng direct input
        if not window_title_filter:
            window_title_filter = self.params.get("window_title", "").strip()
            if window_title_filter:
                print(f"[PROGRAM] Using window title from direct input: {window_title_filter}")
    
        # Convert to lowercase for case-insensitive search
        window_title_filter_lower = window_title_filter.lower() if window_title_filter else ""
    
        # Callback để tìm windows
        def enum_windows_callback(hwnd, target_windows):
            if not win32gui.IsWindowVisible(hwnd) or not win32gui.IsWindowEnabled(hwnd):
                return True
    
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process = psutil.Process(pid)
                process_name = process.name().lower()
        
                # THAY ĐỔI: Nếu CÓ window_title_filter, CHỈ check title (bỏ qua process name)
                if window_title_filter_lower:
                    window_title = win32gui.GetWindowText(hwnd)
            
                    # Check title match (case-insensitive)
                    if window_title_filter_lower in window_title.lower():
                        target_windows.append((hwnd, process_name, window_title))
                        print(f"[PROGRAM] ✓ Matched window by title: '{window_title}' (process: {process_name})")
                else:
                    # KHÔNG CÓ filter, check process name như cũ
                    if program_name == process_name or program_path.lower() == process.exe().lower():
                        window_title = win32gui.GetWindowText(hwnd)
                        target_windows.append((hwnd, process_name, window_title))
            except:
                pass
            return True

    
        # Tìm tất cả cửa sổ của chương trình
        target_windows = []
        win32gui.EnumWindows(enum_windows_callback, target_windows)
    
        # Nếu có filter nhưng không tìm thấy
        if window_title_filter_lower and not target_windows:
            print(f"[PROGRAM] ✗ No window found with title containing: '{window_title_filter}'")
            print(f"[PROGRAM] Searching for any window of: {program_name}")
            # Thử lại không có filter
            window_title_filter_lower = ""
            target_windows = []
            win32gui.EnumWindows(enum_windows_callback, target_windows)
    
        # Nếu không tìm thấy window, start program
        if not target_windows:
            try:
                print(f"[PROGRAM] Not running, starting: {program_path}")
               
                # ẨN TẤT CẢ CMD WINDOWS
                subprocess.Popen(
                    program_path,
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
                # Đợi tối đa 10 giây
                for _ in range(20):
                    time.sleep(0.5)
                    target_windows = []
                    win32gui.EnumWindows(enum_windows_callback, target_windows)
                
                    if target_windows:
                        print(f"[PROGRAM] Started successfully")
                        break
                    
                if target_windows:
                    time.sleep(3)
            
                if not target_windows:
                    print(f"[PROGRAM] Failed to start: {program_path}")
                    return False
            except Exception as e:
                print(f"[PROGRAM] Error starting: {e}")
                return False
    
        # Nếu tìm thấy window, lấy CÁI ĐẦU TIÊN
        if target_windows:
            hwnd = target_windows[0][0]
            window_title = target_windows[0][2] if len(target_windows[0]) > 2 else "Unknown"
        
            # Log nếu có nhiều window match
            if len(target_windows) > 1:
                print(f"[PROGRAM] Found {len(target_windows)} matching windows, using first: '{window_title}'")
        
            try:
                # Restore nếu minimize
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    time.sleep(0.3)
            
                # Maximize
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                time.sleep(0.2)
            
                # Bring to foreground
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.2)
            
                print(f"[PROGRAM] ✓ Ready and maximized: '{window_title}'")
                return True
            
            except Exception as e:
                print(f"[PROGRAM] Error bringing to front: {e}")
                return False
    
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
        

    def move_mouse(self, x, y, width=0, height=0):
        """
        Di chuyển chuột đến một vị trí hoặc vùng
        
        Args:
            x, y: Tọa độ
            width, height: Kích thước vùng (nếu > 0)
            fast: nhanh hay chậm
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
        if width > 0 and height > 0:
            target_x = random.randint(x, x + width)
            target_y = random.randint(y, y + height)
        
        # Lấy giá trị fast từ params
        fast = self.params.get("fast", False)
        
        # Di chuyển chuột với human-like movement
        try:
            HumanLikeMovement.move_cursor_humanlike(current_x, current_y, target_x, target_y, fast)
            
            # Xử lý click dựa trên click_type và is_clickable
            click_type = self.params.get("click_type", "")
            is_clickable = self.params.get("is_clickable", False)

            if click_type in ["single_click", "double_click"]:              
                time.sleep(1)
    
                # Kiểm tra lại nếu người dùng đã yêu cầu dừng trong thời gian delay
                if self.should_stop():
                    return target_x, target_y
    
                # Logic is_clickable: kiểm tra cursor là hand trước khi click
                if is_clickable:
                    # Kiểm tra xem cursor có phải là hand không
                    if not self.is_hand_cursor():
                        # Nếu không phải hand cursor, không click
                        return target_x, target_y
    
                # Thực hiện click theo loại (nếu is_clickable=False hoặc cursor là hand)
                if click_type == "single_click":
                    pyautogui.click()
                elif click_type == "double_click":
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