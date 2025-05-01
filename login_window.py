import tkinter as tk
from tkinter import messagebox
import config

class LoginWindow:
    def __init__(self, on_success_callback):
        """Khởi tạo cửa sổ đăng nhập"""
        self.root = tk.Tk()
        self.root.title("TomSamAutobot Login")
    
        # Thiết lập kích thước cửa sổ
        window_width = 400
        window_height = 300
    
        # Lấy kích thước màn hình
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
    
        # Tính toán vị trí để cửa sổ nằm chính giữa màn hình
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
    
        # Thiết lập kích thước và vị trí cửa sổ
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(False, False)
    
        # Đặt callback khi đăng nhập thành công
        self.on_success = on_success_callback
    
        # Tạo giao diện đăng nhập
        self.create_widgets()
    
    def create_widgets(self):
        """Tạo các thành phần giao diện đăng nhập"""
        # Tiêu đề lớn
        title_label = tk.Label(self.root, text="TomSamAutobot", 
                               font=("Arial", 24, "bold"), 
                               bg="#f0f0f0", fg="#333333")
        title_label.pack(pady=(30, 20))
        
        # Khung đăng nhập
        login_frame = tk.Frame(self.root, bg="#f0f0f0")
        login_frame.pack(pady=10)
        
        # Username
        username_label = tk.Label(login_frame, text="Username:", 
                                  font=("Arial", 12), bg="#f0f0f0")
        username_label.grid(row=0, column=0, sticky="w", pady=(10, 5), padx=5)
        
        self.username_entry = tk.Entry(login_frame, font=("Arial", 12), width=20)
        self.username_entry.grid(row=0, column=1, pady=(10, 5), padx=5)
        
        # Password
        password_label = tk.Label(login_frame, text="Password:", 
                                  font=("Arial", 12), bg="#f0f0f0")
        password_label.grid(row=1, column=0, sticky="w", pady=5, padx=5)
        
        self.password_entry = tk.Entry(login_frame, font=("Arial", 12), 
                                      width=20, show="*")
        self.password_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Login button
        login_button = tk.Button(self.root, text="Login", font=("Arial", 12),
                                bg="#4CAF50", fg="white", width=15,
                                command=self.validate_login)
        login_button.pack(pady=20)
        
        # Bind Enter key to login function
        self.root.bind('<Return>', lambda event: self.validate_login())
    
    def validate_login(self):
        """Xác thực thông tin đăng nhập"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if config.verify_credentials(username, password):
            # Lưu thông tin xác thực vào môi trường
            config.save_auth_to_env()
            messagebox.showinfo("Login Success", "Welcome to TomSamAutobot!")
            self.root.withdraw()  # Ẩn cửa sổ đăng nhập
            # Gọi callback khi đăng nhập thành công
            if self.on_success:
                self.on_success()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password!")
            # Xóa ô mật khẩu để người dùng nhập lại
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()
    
    def show(self):
        """Hiển thị cửa sổ đăng nhập"""
        self.root.deiconify()
        self.root.mainloop()
        
    def hide(self):
        """Ẩn cửa sổ đăng nhập"""
        self.root.withdraw()
