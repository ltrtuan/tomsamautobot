import os
import sys
import tkinter as tk
from tkinter import messagebox  # Thêm dòng này
from models.action_model import ActionModel
from views.action_list_view import ActionListView
from controllers.action_controller import ActionController
import config as cfg
from login_window import LoginWindow
import atexit

import sys
import traceback
from helpers.email_notifier import send_email, format_crash_email
import logging
logger = logging.getLogger('TomSamAutobot')

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    Catch all uncaught exceptions and send email alert
    This is the LAST line of defense before app crash
    """
    # Skip keyboard interrupt (Ctrl+C)
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Log error
    logger.critical("UNCAUGHT EXCEPTION - APP CRASH", exc_info=(exc_type, exc_value, exc_traceback))
    
    # Format crash email
    title, content = format_crash_email(
        exception_type=exc_type.__name__,
        exception_message=str(exc_value),
        traceback_str=traceback.format_exc(),
        context={
            'App': 'TomSamAutobot',
            'Version': '1.0.0',  # Add version if you have
        }
    )
    
    # Send email (non-blocking)
    send_email(
        title=title,
        content=content,
        throttle_seconds=0  # No throttle for crashes (always send)
    )
    
    # Call default exception handler (print to console)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

# ========== INSTALL EXCEPTION HANDLER ==========
sys.excepthook = global_exception_handler


# ========== GLOBAL SELENIUM DRIVER REGISTRY ==========
_active_selenium_drivers = []  # Global list to track all Selenium drivers

def cleanup_all_selenium_drivers():
    """
    Cleanup all active Selenium drivers
    This function is automatically called when Python exits (even if app crashes)
    """
    if not _active_selenium_drivers:
        return
    
    print("[CLEANUP] ========== Cleaning up Selenium drivers ==========")
    cleaned_count = 0
    
    for driver in _active_selenium_drivers:
        try:
            driver.quit()
            cleaned_count += 1
            print(f"[CLEANUP] ✓ ChromeDriver cleaned up")
        except Exception as e:
            print(f"[CLEANUP] ⚠ Cleanup warning: {e}")
    
    _active_selenium_drivers.clear()
    print(f"[CLEANUP] ✓ Total cleaned: {cleaned_count} ChromeDriver process(es)")
    print("[CLEANUP] ========================================")

# Register cleanup function - will run when Python exits
atexit.register(cleanup_all_selenium_drivers)
print("[INIT] ✓ Selenium cleanup handler registered")
# ========== END SELENIUM CLEANUP REGISTRY ==========


class TomSamAutobot:
    def __init__(self):
        """Khởi tạo ứng dụng TomSamAutobot"""
        # Kiểm tra xác thực trước khi khởi tạo
        if cfg.check_auth_from_env():
            # Đã xác thực, khởi tạo ứng dụng chính
            self.init_main_app()
        else:
            # Chưa xác thực, hiển thị màn hình đăng nhập
            self.login_window = LoginWindow(self.init_main_app)
            self.login_window.show()
            
    def init_main_app(self):
        """Khởi tạo giao diện chính của ứng dụng"""
        # Tạo cửa sổ chính nếu chưa tồn tại
        if not hasattr(self, 'root'):
            self.root = tk.Tk()
        else:
            # Nếu đã tồn tại (từ login), sử dụng Toplevel
            self.root = tk.Toplevel()
            
        self.root.title("Tom Sam Autobot")
        self.root.configure(bg=cfg.LIGHT_BG_COLOR)
        
        # Thiết lập kích thước cửa sổ
        window_width = 800
        window_height = 600
        
        # Tính toán vị trí ở giữa màn hình
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))
        
        # Đặt kích thước và vị trí cửa sổ
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        # Create model
        model = ActionModel()
        
        # Create view
        view = ActionListView(self.root)
        view.pack(fill=tk.BOTH, expand=True)
        
        # Create controller and set up
        controller = ActionController(self.root)
        controller.setup(model, view)
        
        # Start application
        self.root.mainloop()
    
    def exit_app(self):
        """Thoát ứng dụng"""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.destroy()
            sys.exit()
            
if __name__ == "__main__":
    # Tải cấu hình
    cfg.load_config()
    app = TomSamAutobot()