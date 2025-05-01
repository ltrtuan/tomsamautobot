import os
import sys
import tkinter as tk
from tkinter import messagebox  # Thêm dòng này
from models.action_model import ActionModel
from views.action_list_view import ActionListView
from controllers.action_controller import ActionController
import config as cfg
from login_window import LoginWindow

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