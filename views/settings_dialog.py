# views/settings_dialog.py
import tkinter as tk
from tkinter import ttk, filedialog
import config

class SettingsDialog:
    def __init__(self, parent):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Cài đặt")
        self.dialog.geometry("500x650")
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
        # ========== SECTION 1: THÔNG SỐ CHÍNH ==========
        main_label = ttk.Label(self.dialog, text="Thông số chính", font=("Arial", 12, "bold"))
        main_label.pack(pady=10)
    
        # File path frame
        file_frame = ttk.Frame(self.dialog)
        file_frame.pack(fill="x", padx=20, pady=5)
    
        file_label = ttk.Label(file_frame, text="Đường dẫn file và hình:")
        file_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
    
        path_browse_frame = ttk.Frame(file_frame)
        path_browse_frame.grid(row=0, column=1, sticky="w", padx=5, pady=5)
    
        self.file_path_var = tk.StringVar(value=config.FILE_PATH)
    
        self.path_display = ttk.Label(
            path_browse_frame, 
            textvariable=self.file_path_var,
            width=25, 
            background="#f0f0f0", 
            relief="sunken"
        )
        self.path_display.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
        browse_button = ttk.Button(path_browse_frame, text="Browse", command=self.browse_folder)
        browse_button.pack(side="left")
    
        # Số ngày giữ logs
        log_days_frame = ttk.Frame(self.dialog)
        log_days_frame.pack(fill="x", padx=20, pady=5)
    
        log_days_label = ttk.Label(log_days_frame, text="Số ngày giữ logs:")
        log_days_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
    
        spinbox_frame = ttk.Frame(log_days_frame)
        spinbox_frame.grid(row=0, column=1, sticky="w", padx=5, pady=5)
    
        self.log_days_var = tk.IntVar(value=config.LOG_RETENTION_DAYS)
        self.log_days_spinbox = ttk.Spinbox(
            spinbox_frame,
            from_=1,
            to=365,
            textvariable=self.log_days_var,
            width=10,
            font=("Segoe UI", 10)
        )
        self.log_days_spinbox.pack(side=tk.LEFT)
        ttk.Label(spinbox_frame, text="ngày", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(5, 0))
    
        # ========== SEPARATOR ==========
        ttk.Separator(self.dialog, orient='horizontal').pack(fill='x', padx=20, pady=15)
    
        # ========== SECTION 2: CẤU HÌNH SMTP EMAIL ==========
        smtp_label = ttk.Label(self.dialog, text="Cấu hình SMTP Email", font=("Arial", 12, "bold"))
        smtp_label.pack(pady=10)
    
        # Checkbox: Bật/Tắt email alerts
        smtp_enable_frame = ttk.Frame(self.dialog)
        smtp_enable_frame.pack(fill="x", padx=20, pady=5)
    
        self.smtp_enabled_var = tk.BooleanVar(value=config.SMTP_ENABLED)
        smtp_enable_check = ttk.Checkbutton(
            smtp_enable_frame,
            text="Bật gửi email cảnh báo",
            variable=self.smtp_enabled_var,
            command=self.toggle_smtp_fields
        )
        smtp_enable_check.pack(anchor="w", padx=5)
    
        # Frame chứa tất cả SMTP fields
        self.smtp_fields_frame = ttk.Frame(self.dialog)
        self.smtp_fields_frame.pack(fill="x", padx=20, pady=5)

        # Row 1: SMTP Host
        ttk.Label(self.smtp_fields_frame, text="SMTP Host:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self.smtp_host_var = tk.StringVar(value=config.SMTP_HOST)
        self.smtp_host_entry = ttk.Entry(self.smtp_fields_frame, textvariable=self.smtp_host_var, width=30)
        self.smtp_host_entry.grid(row=0, column=1, sticky="w", padx=5, pady=3)

        # Row 2: SMTP Port + TLS
        ttk.Label(self.smtp_fields_frame, text="SMTP Port:").grid(row=1, column=0, sticky="w", padx=5, pady=3)

        port_tls_frame = ttk.Frame(self.smtp_fields_frame)
        port_tls_frame.grid(row=1, column=1, sticky="w", padx=5, pady=3)

        self.smtp_port_var = tk.IntVar(value=config.SMTP_PORT)
        self.smtp_port_entry = ttk.Entry(port_tls_frame, textvariable=self.smtp_port_var, width=10)
        self.smtp_port_entry.pack(side="left")

        self.smtp_use_tls_var = tk.BooleanVar(value=config.SMTP_USE_TLS)
        self.smtp_tls_check = ttk.Checkbutton(
            port_tls_frame,
            text="Use TLS",
            variable=self.smtp_use_tls_var
        )
        self.smtp_tls_check.pack(side="left", padx=(10, 0))

        # Row 3: SMTP Username (Login credential)
        ttk.Label(self.smtp_fields_frame, text="SMTP Username:").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        self.smtp_username_var = tk.StringVar(value=config.SMTP_USERNAME)
        self.smtp_username_entry = ttk.Entry(self.smtp_fields_frame, textvariable=self.smtp_username_var, width=30)
        self.smtp_username_entry.grid(row=2, column=1, sticky="w", padx=5, pady=3)

        # Row 4: Mật khẩu
        ttk.Label(self.smtp_fields_frame, text="Mật khẩu:").grid(row=3, column=0, sticky="w", padx=5, pady=3)

        password_frame = ttk.Frame(self.smtp_fields_frame)
        password_frame.grid(row=3, column=1, sticky="w", padx=5, pady=3)

        self.smtp_password_var = tk.StringVar(value=config.SMTP_PASSWORD)
        self.smtp_password_entry = ttk.Entry(
            password_frame, 
            textvariable=self.smtp_password_var, 
            width=25,
            show="*"
        )
        self.smtp_password_entry.pack(side="left")

        # Show/Hide password button
        self.show_password_var = tk.BooleanVar(value=False)
        self.show_password_btn = ttk.Button(
            password_frame,
            text="👁",
            width=3,
            command=self.toggle_password_visibility
        )
        self.show_password_btn.pack(side="left", padx=(5, 0))

        # Row 5: From Email (Email gửi - sender display name)
        ttk.Label(self.smtp_fields_frame, text="Email gửi (From):").grid(row=4, column=0, sticky="w", padx=5, pady=3)
        self.smtp_from_email_var = tk.StringVar(value=config.SMTP_FROM_EMAIL)
        self.smtp_from_email_entry = ttk.Entry(self.smtp_fields_frame, textvariable=self.smtp_from_email_var, width=30)
        self.smtp_from_email_entry.grid(row=4, column=1, sticky="w", padx=5, pady=3)

        # Row 6: To Email (Email nhận)
        ttk.Label(self.smtp_fields_frame, text="Email nhận (To):").grid(row=5, column=0, sticky="w", padx=5, pady=3)
        self.smtp_to_email_var = tk.StringVar(value=config.SMTP_TO_EMAIL)
        self.smtp_to_email_entry = ttk.Entry(self.smtp_fields_frame, textvariable=self.smtp_to_email_var, width=30)
        self.smtp_to_email_entry.grid(row=5, column=1, sticky="w", padx=5, pady=3)

        # Test Email Button
        test_email_frame = ttk.Frame(self.dialog)
        test_email_frame.pack(fill="x", padx=20, pady=10)

        self.test_email_btn = ttk.Button(
            test_email_frame,
            text="Gửi Email Test",
            command=self.test_smtp
        )
        self.test_email_btn.pack(anchor="w", padx=5)
        
        
        # ========== SEPARATOR ========== (THÊM MỚI)
        ttk.Separator(self.dialog, orient='horizontal').pack(fill='x', padx=20, pady=15)
        
        # ========== SECTION 3: AUTO-START DELAY (NEW) ==========
        auto_start_label = ttk.Label(
            self.dialog, 
            text="Tự động khởi động sau khi crash", 
            font=("Arial", 12, "bold")
        )
        auto_start_label.pack(pady=10)
        
        # Frame chứa field
        auto_start_frame = ttk.Frame(self.dialog)
        auto_start_frame.pack(fill="x", padx=20, pady=5)
        
        # Label bên trái
        ttk.Label(
            auto_start_frame,
            text="Delay trước khi auto-start (giây):",
            font=("Segoe UI", 10)
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # Spinbox cho delay
        self.auto_start_delay_var = tk.IntVar(value=config.get_auto_start_delay())
        self.auto_start_delay_spinbox = ttk.Spinbox(
            auto_start_frame,
            from_=0,
            to=9999,  # No limit
            textvariable=self.auto_start_delay_var,
            width=10,
            font=("Segoe UI", 10)
        )
        self.auto_start_delay_spinbox.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Help text
        help_frame = ttk.Frame(self.dialog)
        help_frame.pack(fill="x", padx=20, pady=(0, 5))
        help_text = ttk.Label(
            help_frame,
            text="(0 = tắt auto-start, mặc định: 60 giây)",
            font=("Segoe UI", 8),
            foreground="gray"
        )
        help_text.pack(anchor="w", padx=5)
        # ========================================================

    
        # ========== BUTTON FRAME (SAVE/CANCEL) ==========
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=15)
    
        save_button = ttk.Button(button_frame, text="Lưu", command=self.save_settings)
        save_button.pack(side="left", padx=5)
    
        cancel_button = ttk.Button(button_frame, text="Hủy", command=self.dialog.destroy)
        cancel_button.pack(side="left", padx=5)
    
        # Initial state của SMTP fields
        self.toggle_smtp_fields()
        

        
    def toggle_smtp_fields(self):
        """Enable/disable SMTP fields based on checkbox"""
        state = "normal" if self.smtp_enabled_var.get() else "disabled"
    
        # Update tất cả SMTP input fields
        for widget in self.smtp_fields_frame.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.config(state=state)
            elif isinstance(widget, ttk.Checkbutton):
                widget.config(state=state)
            elif isinstance(widget, ttk.Frame):
                # Nested frames (port_tls_frame, password_frame)
                for child in widget.winfo_children():
                    if isinstance(child, (ttk.Entry, ttk.Checkbutton, ttk.Button)):
                        child.config(state=state)
    
        # Test email button
        self.test_email_btn.config(state=state)


    def toggle_password_visibility(self):
        """Toggle password show/hide"""
        if self.show_password_var.get():
            # Currently showing → hide
            self.smtp_password_entry.config(show="*")
            self.show_password_var.set(False)
        else:
            # Currently hidden → show
            self.smtp_password_entry.config(show="")
            self.show_password_var.set(True)


    def test_smtp(self):
        """Test SMTP connection và gửi email test"""
        from tkinter import messagebox
        from helpers.email_notifier import test_smtp_connection
    
        # Temporarily update config với values hiện tại (không save)
        temp_smtp_host = config.SMTP_HOST
        temp_smtp_port = config.SMTP_PORT
        temp_smtp_use_tls = config.SMTP_USE_TLS
        temp_smtp_username = config.SMTP_USERNAME
        temp_smtp_password = config.SMTP_PASSWORD
        temp_smtp_to_email = config.SMTP_TO_EMAIL
        temp_smtp_from_email = config.SMTP_FROM_EMAIL
    
        try:
            # Update config với values từ UI
            config.SMTP_HOST = self.smtp_host_var.get()
            config.SMTP_PORT = self.smtp_port_var.get()
            config.SMTP_USE_TLS = self.smtp_use_tls_var.get()
            config.SMTP_USERNAME = self.smtp_username_var.get()
            config.SMTP_PASSWORD = self.smtp_password_var.get()
            config.SMTP_TO_EMAIL = self.smtp_to_email_var.get()
            config.SMTP_FROM_EMAIL = self.smtp_from_email_var.get()
        
            # Test connection
            success, message = test_smtp_connection()
        
            if success:
                messagebox.showinfo("Thành công", message)
            else:
                messagebox.showerror("Lỗi", message)
    
        finally:
            # Restore original config (chưa save vào file)
            config.SMTP_HOST = temp_smtp_host
            config.SMTP_PORT = temp_smtp_port
            config.SMTP_USE_TLS = temp_smtp_use_tls
            config.SMTP_USERNAME = temp_smtp_username
            config.SMTP_PASSWORD = temp_smtp_password
            config.SMTP_TO_EMAIL = temp_smtp_to_email
            config.SMTP_FROM_EMAIL = temp_smtp_from_email


    
    def browse_folder(self):
        """Mở hộp thoại chọn thư mục và cập nhật đường dẫn"""
        folder_path = filedialog.askdirectory(title="Chọn thư mục")
        if folder_path:  # Kiểm tra nếu user đã chọn thư mục (không nhấn Cancel)
            self.file_path_var.set(folder_path)
    
    def save_settings(self):
        # Lưu biến toàn cục - Thông số chính
        config.FILE_PATH = self.file_path_var.get()
        config.LOG_RETENTION_DAYS = self.log_days_var.get()
    
        # ========== Lưu SMTP config (NEW) ==========
        config.SMTP_ENABLED = self.smtp_enabled_var.get()
        config.SMTP_HOST = self.smtp_host_var.get()
        config.SMTP_PORT = self.smtp_port_var.get()
        config.SMTP_USE_TLS = self.smtp_use_tls_var.get()
        config.SMTP_USERNAME = self.smtp_username_var.get()
        config.SMTP_PASSWORD = self.smtp_password_var.get()
        config.SMTP_TO_EMAIL = self.smtp_to_email_var.get()
        config.SMTP_FROM_EMAIL = self.smtp_from_email_var.get()
        
        # ========== Lưu AUTO_START_DELAY (NEW) ==========
        try:
            delay = self.auto_start_delay_var.get()
            config.set_auto_start_delay(delay)
        except Exception as e:
            print(f"[SETTINGS] Failed to save AUTO_START_DELAY: {e}")
            config.set_auto_start_delay(60)  # Default
        # ================================================

        
        # Lưu cấu hình vào file
        config.save_config()
    
        # Reload logger (nếu có)
        try:
            from helpers.logger import reset_logger
            reset_logger()
        except:
            pass  # Logger chưa init hoặc không có reset_logger()
    
        # Đóng dialog
        self.dialog.destroy()

