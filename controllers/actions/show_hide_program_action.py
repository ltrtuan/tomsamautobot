# controllers/actions/show_hide_program_action.py
from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
import random
import re
import win32gui
import win32con
import win32process
import psutil
import os

class ShowHideProgramAction(BaseAction):
    """Handler để thực thi hành động show/hide/minimize/maximize program"""
    
    def prepare_play(self):
        # Lấy danh sách title program
        titles = self.get_title_programs()
    
        if not titles:
            variable = self.params.get("variable", "")
            if variable:
                GlobalVariables().set(variable, "false")
            return
    
        # ✅ ĐÚNG - Lấy từ self.params
        how_to_get = self.params.get("how_to_get", "Random")
        selected_title = self.select_title_by_mode(titles, how_to_get)
    
        # Xử lý pattern đặc biệt
        processed_title = self.process_text_pattern(selected_title)
    
        # ✅ ĐÚNG - Lấy từ self.params
        program_action = self.params.get("program_action", "Check exist")
    
        # Thực hiện action
        success = self.execute_program_action(processed_title, program_action)
    
        # Đặt variable
        variable = self.params.get("variable", "")
        if variable:
            GlobalVariables().set(variable, "true" if success else "false")

    
    def get_title_programs(self):
        """Lấy danh sách title program từ textarea"""
        title_program = self.params.get("title_program", "")
        
        # Parse theo pattern (cách nhau bởi dấu ;)
        titles = [t.strip() for t in title_program.split(';') if t.strip()]
        return titles
    
    def select_title_by_mode(self, titles, mode):
        """Chọn title theo mode"""
        if not titles:
            return ""
        
        if mode == "Random":
            return random.choice(titles)
        else:  # Sequential by loop
            # Lấy loop index từ global variables (nếu đang trong vòng lặp)
            loop_var = GlobalVariables().get("loop_index", "0")
            try:
                loop_index = int(loop_var)
            except:
                loop_index = 0
            return titles[loop_index % len(titles)]
    
    def process_text_pattern(self, text):
        """
        Xử lý các pattern đặc biệt trong text
        - <VAR_NAME>: thay thế bằng giá trị biến
        - [1-10]: số ngẫu nhiên từ 1 đến 10
        - [1-10:C]: random 1-10 ký tự chữ
        - [1-10:N]: random 1-10 ký tự số
        - [1-10:CN]: random 1-10 ký tự chữ và số
        """
        import string
        
        # Xử lý biến <VAR_NAME>
        var_pattern = r'<([^>]+)>'
        variables = re.findall(var_pattern, text)
        for var in variables:
            var_value = GlobalVariables().get(var, "")
            text = text.replace(f"<{var}>", str(var_value))
        
        # Xử lý [min-max] hoặc [min-max:type]
        range_pattern = r'\[(\d+)-(\d+)(?::([CNcn]+))?\]'
        
        def replace_range(match):
            min_val = int(match.group(1))
            max_val = int(match.group(2))
            type_val = match.group(3)
            
            if type_val is None:
                # Chỉ có số
                return str(random.randint(min_val, max_val))
            else:
                # Random chuỗi ký tự
                length = random.randint(min_val, max_val)
                type_val = type_val.upper()
                
                if type_val == 'C':
                    # Chỉ chữ
                    chars = string.ascii_letters
                elif type_val == 'N':
                    # Chỉ số
                    chars = string.digits
                elif type_val == 'CN':
                    # Cả chữ và số
                    chars = string.ascii_letters + string.digits
                else:
                    chars = string.ascii_letters + string.digits
                
                return ''.join(random.choice(chars) for _ in range(length))
        
        text = re.sub(range_pattern, replace_range, text)
        
        return text
    
    def execute_program_action(self, title, action):
        """Thực thi action trên window với title tương ứng - Luôn bring to front"""
        try:
            # Tìm window handle
            hwnd = self.find_window_by_title(title)
        
            # ===== CHECK EXIST =====
            if action == "Check exist":
                exists = hwnd is not None
                print(f"[SHOW_HIDE_PROGRAM] Check exist '{title}': {exists}")
                return exists
        
            # ===== OPEN =====
            if action == "Open":
                if hwnd is None:
                    # Nếu window chưa tồn tại, mở program từ program_path
                    program_path = self.params.get("program_path", "")
                    if program_path and os.path.exists(program_path):
                        os.startfile(program_path)
                        print(f"[SHOW_HIDE_PROGRAM] Opened program: {program_path}")
                        return True
                    else:
                        print(f"[SHOW_HIDE_PROGRAM] Program path not found: {program_path}")
                        return False
                else:
                    # Window đã tồn tại - Show và bring to front
                    self.bring_window_to_front(hwnd)
                    print(f"[SHOW_HIDE_PROGRAM] Window '{title}' brought to front")
                    return True
        
            # ===== CÁC ACTION KHÁC - CẦN WINDOW TỒN TẠI =====
            if hwnd is None:
                print(f"[SHOW_HIDE_PROGRAM] Window not found: {title}")
                return False
        
            # ===== HIDE - Không bring to front =====
            if action == "Hide":
                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                print(f"[SHOW_HIDE_PROGRAM] Hidden window '{title}'")
                return True
        
            # ===== MINIMIZE - Không bring to front =====
            if action == "Minimize":
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                print(f"[SHOW_HIDE_PROGRAM] Minimized window '{title}'")
                return True
        
            # ===== CLOSE - Không bring to front =====
            elif action == "Close":
                # Lấy process ID từ window handle
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
        
                    # Gửi WM_CLOSE trước (lịch sự)
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        
                    # Đợi 1 giây
                    import time
                    time.sleep(1)
        
                    # Force terminate nếu vẫn còn chạy
                    try:
                        process = psutil.Process(pid)
                        if process.is_running():
                            process.terminate()
                            time.sleep(1)
                
                            # Kill mạnh nếu vẫn còn
                            if process.is_running():
                                process.kill()
                                print(f"[SHOW_HIDE_PROGRAM] Force killed process '{title}' (PID: {pid})")
                            else:
                                print(f"[SHOW_HIDE_PROGRAM] Terminated process '{title}' (PID: {pid})")
                        else:
                            print(f"[SHOW_HIDE_PROGRAM] Process closed normally '{title}'")
                
                    except psutil.NoSuchProcess:
                        print(f"[SHOW_HIDE_PROGRAM] Process already closed '{title}'")
            
                    return True
        
                except Exception as e:
                    print(f"[SHOW_HIDE_PROGRAM] Error closing '{title}': {e}")
                    return False
        
            # ===== SHOW / MAXIMIZE / RESTORE - LUÔN BRING TO FRONT =====
            if action == "Show":
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                self.bring_window_to_front(hwnd)
                print(f"[SHOW_HIDE_PROGRAM] Showed and brought window '{title}' to front")
                return True
        
            elif action == "Maximize":
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                self.bring_window_to_front(hwnd)
                print(f"[SHOW_HIDE_PROGRAM] Maximized and brought window '{title}' to front")
                return True
        
            elif action == "Restore":
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                self.bring_window_to_front(hwnd)
                print(f"[SHOW_HIDE_PROGRAM] Restored and brought window '{title}' to front")
                return True
        
            # Nếu action không khớp với bất kỳ case nào
            print(f"[SHOW_HIDE_PROGRAM] Unknown action: {action}")
            return False
        
        except Exception as e:
            print(f"[SHOW_HIDE_PROGRAM] Error executing '{action}' on '{title}': {e}")
            import traceback
            traceback.print_exc()
            return False

    def bring_window_to_front(self, hwnd):
        """
        Bring window to front một cách mạnh mẽ
        Kết hợp nhiều kỹ thuật để đảm bảo window lên trước
        """
        try:
            # Bước 1: Restore nếu minimized (quan trọng cho system tray)
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        
            # Bước 2: Show window nếu hidden
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        
            # Bước 3: Attach thread input - Trick để bypass foreground lock
            current_thread = win32process.GetCurrentThreadId()
            target_thread, _ = win32process.GetWindowThreadProcessId(hwnd)
        
            if current_thread != target_thread:
                win32process.AttachThreadInput(current_thread, target_thread, True)
        
            # Bước 4: Set foreground window
            win32gui.SetForegroundWindow(hwnd)
        
            # Bước 5: Bring to top
            win32gui.BringWindowToTop(hwnd)
        
            # Bước 6: Set window pos (HWND_TOP)
            win32gui.SetWindowPos(
                hwnd, 
                win32con.HWND_TOP,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
            )
        
            # Bước 7: Detach thread input
            if current_thread != target_thread:
                win32process.AttachThreadInput(current_thread, target_thread, False)
        
            print(f"[SHOW_HIDE_PROGRAM] Successfully brought window to front")
        
        except Exception as e:
            print(f"[SHOW_HIDE_PROGRAM] Error bringing window to front: {e}")
            # Fallback: Chỉ dùng SetForegroundWindow
            try:
                win32gui.SetForegroundWindow(hwnd)
            except:
                pass


    
    def find_window_by_title(self, title):
        """Tìm window handle theo title (hỗ trợ partial match)"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                # Partial match (không phân biệt hoa thường)
                if title.lower() in window_title.lower():
                    windows.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        
        return windows[0] if windows else None
 