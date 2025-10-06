# controllers/actions/check_fullscreen_action.py
from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
import win32gui
import win32api
import win32con

class CheckFullscreenAction(BaseAction):
    """Handler để kiểm tra xem foreground window có đang fullscreen không"""
    
    def prepare_play(self):
        """Kiểm tra fullscreen sau khi trì hoãn"""
        
        try:
            # Kiểm tra xem có fullscreen không
            is_fullscreen = self.is_foreground_fullscreen()
            
            # Gán vào variable nếu user có input
            variable = self.params.get("variable", "")
            if variable:
                GlobalVariables().set(variable, "true" if is_fullscreen else "false")
                print(f"[CHECK_FULLSCREEN] Set variable '{variable}' = {'true' if is_fullscreen else 'false'}")
            
            print(f"[CHECK_FULLSCREEN] Is fullscreen: {is_fullscreen}")
            
        except Exception as e:
            print(f"[CHECK_FULLSCREEN] Error: {e}")
            import traceback
            traceback.print_exc()
            
            # Set variable = false nếu có lỗi
            variable = self.params.get("variable", "")
            if variable:
                GlobalVariables().set(variable, "false")
    
    def is_foreground_fullscreen(self):
        """
        Kiểm tra xem foreground window có đang fullscreen không
        Tương tự IsForegroundFullScreen trong C#
        
        Returns:
            bool: True nếu fullscreen, False nếu không
        """
        try:
            # Lấy foreground window handle
            hwnd = win32gui.GetForegroundWindow()
            
            if hwnd == 0:
                return False
            
            # Bỏ qua desktop và shell windows
            class_name = win32gui.GetClassName(hwnd)
            if class_name in ["Progman", "WorkerW", "Shell_TrayWnd"]:
                return False
            
            # Lấy kích thước window
            try:
                rect = win32gui.GetWindowRect(hwnd)
                window_width = rect[2] - rect[0]
                window_height = rect[3] - rect[1]
            except:
                return False
            
            # Lấy kích thước màn hình chính
            screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
            screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            
            # Kiểm tra xem window có phủ toàn màn hình không
            # Allow tolerance 1-2 pixels for borders
            is_fullscreen = (
                abs(window_width - screen_width) <= 2 and
                abs(window_height - screen_height) <= 2 and
                rect[0] <= 1 and  # Window starts at or near left edge
                rect[1] <= 1      # Window starts at or near top edge
            )
            
            if is_fullscreen:
                window_title = win32gui.GetWindowText(hwnd)
                print(f"[CHECK_FULLSCREEN] Detected fullscreen window: '{window_title}' ({window_width}x{window_height})")
            
            return is_fullscreen
            
        except Exception as e:
            print(f"[CHECK_FULLSCREEN] Error checking fullscreen: {e}")
            return False
