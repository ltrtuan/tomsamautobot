import tkinter as tk
from tkinter import ttk, messagebox
import config as cfg

class MoveIndexDialog(tk.Toplevel):
    def __init__(self, parent, current_index, max_index):
        super().__init__(parent)
        self.parent = parent
        self.current_index = current_index
        self.max_index = max_index
        self.result_index = None
        
        self.title("Di Chuyển Hành Động")
        self.geometry("350x200")  # Tăng kích thước để đủ chỗ cho nút
        self.resizable(False, False)
        self.configure(bg=cfg.LIGHT_BG_COLOR)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.center_dialog()
        
    def create_widgets(self):
        # Main frame với padding lớn hơn
        main_frame = tk.Frame(self, bg=cfg.LIGHT_BG_COLOR, padx=25, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Di Chuyển Hành Động",
            font=cfg.HEADER_FONT,
            bg=cfg.LIGHT_BG_COLOR,
            fg=cfg.PRIMARY_COLOR
        )
        title_label.pack(pady=(0, 15))
        
        # Current position info
        info_label = tk.Label(
            main_frame,
            text=f"Vị trí hiện tại: {self.current_index + 1}",
            font=cfg.DEFAULT_FONT,
            bg=cfg.LIGHT_BG_COLOR
        )
        info_label.pack(pady=(0, 15))
        
        # Input frame
        input_frame = tk.Frame(main_frame, bg=cfg.LIGHT_BG_COLOR)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        input_label = tk.Label(
            input_frame,
            text="Vị trí mới (1-" + str(self.max_index) + "):",
            font=cfg.DEFAULT_FONT,
            bg=cfg.LIGHT_BG_COLOR
        )
        input_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.index_var = tk.StringVar(value=str(self.current_index + 1))
        self.entry = tk.Entry(
            input_frame,
            textvariable=self.index_var,
            font=cfg.DEFAULT_FONT,
            width=15,
            justify=tk.CENTER
        )
        self.entry.pack(fill=tk.X)
        self.entry.focus_set()
        self.entry.select_range(0, tk.END)  # Select all text
        
        # Button frame - sử dụng pack thay vì side để đảm bảo hiển thị
        button_frame = tk.Frame(main_frame, bg=cfg.LIGHT_BG_COLOR)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Cancel button
        cancel_button = tk.Button(
            button_frame,
            text="Hủy",
            bg="#f5f5f5",
            fg="#333333",
            font=cfg.DEFAULT_FONT,
            padx=20,
            pady=8,
            relief=tk.FLAT,
            bd=1,
            cursor="hand2",
            command=self.cancel
        )
        cancel_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # OK button
        ok_button = tk.Button(
            button_frame,
            text="OK",
            bg=cfg.PRIMARY_COLOR,
            fg="white",
            font=cfg.DEFAULT_FONT,
            padx=20,
            pady=8,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=self.ok_clicked
        )
        ok_button.pack(side=tk.RIGHT)
        
        # Bind Enter key to OK
        self.bind('<Return>', lambda e: self.ok_clicked())
        # Bind Escape key to Cancel
        self.bind('<Escape>', lambda e: self.cancel())
        
    def center_dialog(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        
    def ok_clicked(self):
        try:
            target_index = int(self.index_var.get()) - 1  # Convert to 0-based
            if target_index < 0 or target_index >= self.max_index:
                messagebox.showerror("Lỗi", f"Vị trí phải từ 1 đến {self.max_index}")
                self.entry.focus_set()
                self.entry.select_range(0, tk.END)
                return
            if target_index == self.current_index:
                messagebox.showinfo("Thông báo", "Vị trí mới giống vị trí hiện tại")
                self.entry.focus_set()
                self.entry.select_range(0, tk.END)
                return
            self.result_index = target_index
            self.destroy()
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập một số hợp lệ")
            self.entry.focus_set()
            self.entry.select_range(0, tk.END)
            
    def cancel(self):
        self.result_index = None
        self.destroy()
