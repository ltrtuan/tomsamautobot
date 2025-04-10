import tkinter as tk
from PIL import ImageGrab, ImageTk
import pyautogui
import time

class ScreenAreaSelector:
    def __init__(self, parent_dialog, callback=None):
        """
        Khởi tạo bộ chọn khu vực màn hình
        
        :param parent_dialog: Dialog cha cần ẩn trong quá trình chọn
        :param callback: Hàm callback khi chọn vùng xong
        """
        self.parent_dialog = parent_dialog
        self.callback = callback
        self.start_x = 0
        self.start_y = 0
        self.current_x = 0
        self.current_y = 0
        
    def show(self):
        """Hiển thị overlay để chọn khu vực"""
        # Ẩn dialog cha tạm thời
        self.parent_dialog.withdraw()
        
        # Tạo một cửa sổ fullscreen trong suốt
        self.root = tk.Toplevel()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)  # Trong suốt 70%
        self.root.attributes('-topmost', True)
        
        # Chụp màn hình để hiển thị dưới overlay
        screen_width, screen_height = pyautogui.size()
        screenshot = ImageGrab.grab()
        self.tk_image = ImageTk.PhotoImage(screenshot)
        
        # Tạo canvas để vẽ lên màn hình
        self.canvas = tk.Canvas(self.root, width=screen_width, height=screen_height)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        
        # Hiển thị hướng dẫn
        instr_text = "Nhấn chuột trái và kéo để chọn vùng. Nhấn ESC để hủy."
        self.canvas.create_text(
            screen_width // 2, 30, text=instr_text, fill="white",
            font=("Arial", 14, "bold")
        )
        
        # Tạo hình chữ nhật lựa chọn
        self.selection_rect = None
        
        # Binding các sự kiện chuột
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        # Binding phím ESC để hủy
        self.root.bind("<Escape>", self.cancel)
        
        # Đặt focus để bắt phím
        self.canvas.focus_set()
        
    def on_mouse_down(self, event):
        """Xử lý khi nhấn chuột xuống"""
        self.start_x = event.x
        self.start_y = event.y
        
        # Tạo hình chữ nhật ban đầu
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        self.selection_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2, dash=(2, 2)
        )
        
    def on_mouse_drag(self, event):
        """Xử lý khi kéo chuột"""
        self.current_x = event.x
        self.current_y = event.y
        
        # Cập nhật hình chữ nhật
        self.canvas.coords(
            self.selection_rect,
            self.start_x, self.start_y, self.current_x, self.current_y
        )
        
        # Hiển thị kích thước hiện tại
        width = abs(self.current_x - self.start_x)
        height = abs(self.current_y - self.start_y)
        
        # Xóa text kích thước cũ nếu có
        if hasattr(self, 'size_text') and self.size_text:
            self.canvas.delete(self.size_text)
            
        # Hiển thị kích thước mới
        self.size_text = self.canvas.create_text(
            (self.start_x + self.current_x) // 2,
            (self.start_y + self.current_y) // 2,
            text=f"{width} x {height}",
            fill="white", font=("Arial", 12, "bold")
        )
        
    def on_mouse_up(self, event):
        """Xử lý khi thả chuột"""
        # Tính toán tọa độ và kích thước khu vực được chọn
        x = min(self.start_x, self.current_x)
        y = min(self.start_y, self.current_y)
        width = abs(self.current_x - self.start_x)
        height = abs(self.current_y - self.start_y)
        
        # Đóng cửa sổ chọn vùng
        self.root.destroy()
        
        # Hiển thị lại dialog cha
        self.parent_dialog.deiconify()
        
        # Gọi callback với thông tin vùng đã chọn
        if self.callback and width > 10 and height > 10:  # Đảm bảo vùng đủ lớn
            self.callback(x, y, width, height)
            
    def cancel(self, event=None):
        """Hủy việc chọn vùng"""
        if hasattr(self, 'root') and self.root:
            self.root.destroy()
        
        # Hiển thị lại dialog cha
        self.parent_dialog.deiconify()
