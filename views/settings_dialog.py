# views/settings_dialog.py
import tkinter as tk
from tkinter import ttk, filedialog
import config

class SettingsDialog:
    def __init__(self, parent):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Cài đặt")
        self.dialog.geometry("450x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
        # Căn giữa dialog
        self.center_dialog()
        
    def center_dialog(self):
        # Cập nhật các tác vụ đang chờ xử lý
        self.dialog.update_idletasks()
        
        # Lấy kích thước của dialog
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        
        # Lấy kích thước màn hình
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        
        # Tính toán vị trí để căn giữa
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Đặt vị trí mới
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_widgets(self):
        # Main header
        main_label = ttk.Label(self.dialog, text="Thông số chính", font=("Arial", 12, "bold"))
        main_label.pack(pady=10)
        
        # File path frame
        file_frame = ttk.Frame(self.dialog)
        file_frame.pack(fill="x", padx=20, pady=5)
        
        file_label = ttk.Label(file_frame, text="Đường dẫn file và hình:")
        file_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # Frame chứa path display và browse button
        path_browse_frame = ttk.Frame(file_frame)
        path_browse_frame.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Biến lưu đường dẫn
        self.file_path_var = tk.StringVar(value=config.FILE_PATH)
        
        # Label hiển thị đường dẫn đã chọn
        self.path_display = ttk.Label(path_browse_frame, textvariable=self.file_path_var, 
                                      width=25, background="#f0f0f0", relief="sunken")
        self.path_display.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Nút browse
        browse_button = ttk.Button(path_browse_frame, text="Browse", command=self.browse_folder)
        browse_button.pack(side="left")
        
        # Button frame
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=20)
        
        save_button = ttk.Button(button_frame, text="Save", command=self.save_settings)
        save_button.pack(side="left", padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Hủy", command=self.dialog.destroy)
        cancel_button.pack(side="left", padx=5)
    
    def browse_folder(self):
        """Mở hộp thoại chọn thư mục và cập nhật đường dẫn"""
        folder_path = filedialog.askdirectory(title="Chọn thư mục")
        if folder_path:  # Kiểm tra nếu user đã chọn thư mục (không nhấn Cancel)
            self.file_path_var.set(folder_path)
    
    def save_settings(self):
        # Lưu biến toàn cục
        config.FILE_PATH = self.file_path_var.get()
        
        # Lưu cấu hình
        config.save_config()
        
        # Đóng dialog
        self.dialog.destroy()
