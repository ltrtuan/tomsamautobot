import tkinter as tk
from PIL import ImageGrab, ImageTk
import time

class ScreenAreaSelector:
    def __init__(self, parent_dialog, callback=None):
        """
        Khởi tạo selector với dialog cha
        
        :param parent_dialog: Dialog cha (dialog sửa hành động)
        :param callback: Hàm callback khi chọn vùng
        """
        self.parent_dialog = parent_dialog
        self.callback = callback
        
    def show(self):
        # Ẩn dialog cha (dialog sửa hành động) - quan trọng!
        self.parent_dialog.withdraw()
        
        # Tạo cửa sổ overlay
        self.overlay = tk.Toplevel()
        self.overlay.title("Chọn khu vực màn hình")
        self.overlay.attributes('-fullscreen', True)
        self.overlay.attributes('-alpha', 0.3)
        self.overlay.attributes('-topmost', True)
        self.overlay.config(bg="black")
        
        # Biến lưu tọa độ
        self.start_x = 0
        self.start_y = 0
        self.rect = None
        self.text_id = None
        
        # Canvas để vẽ
        self.canvas = tk.Canvas(self.overlay, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Hướng dẫn
        instructions = tk.Label(
            self.overlay, 
            text="Kéo chuột để chọn vùng - ESC để thoát",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="black"
        )
        instructions.place(relx=0.5, rely=0.05, anchor=tk.CENTER)
        
        # Nút Đồng ý
        self.ok_button = tk.Button(
            self.overlay,
            text="Đồng ý",
            bg="#4285f4",
            fg="white",
            font=("Arial", 12),
            padx=15,
            pady=5,
            command=self._on_ok
        )
        self.ok_button.place(relx=0.5, rely=0.9, anchor=tk.CENTER)
        
        # Binding sự kiện
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.overlay.bind("<Escape>", lambda e: self._on_close())
        
        # Xử lý khi đóng cửa sổ
        self.overlay.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Đặt focus cho overlay - quan trọng để bắt phím ESC
        self.overlay.focus_force()
        
    def _on_press(self, event):
        # Bắt đầu vẽ hình chữ nhật
        self.start_x = event.x
        self.start_y = event.y
        
        # Xóa hình cũ nếu có
        if self.rect:
            self.canvas.delete(self.rect)
        if self.text_id:
            self.canvas.delete(self.text_id)
            
        # Vẽ hình mới
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, 
            self.start_x, self.start_y,
            outline="red", width=2
        )
        
        # Hiển thị text
        self.text_id = self.canvas.create_text(
            self.start_x, self.start_y,
            text="Select Area",
            fill="white",
            font=("Arial", 12, "bold")
        )
        
    def _on_drag(self, event):
        # Cập nhật kích thước hình chữ nhật
        if self.rect:
            curr_x, curr_y = event.x, event.y
            self.canvas.coords(self.rect, self.start_x, self.start_y, curr_x, curr_y)
            
            # Cập nhật vị trí text
            center_x = (self.start_x + curr_x) / 2
            center_y = (self.start_y + curr_y) / 2
            self.canvas.coords(self.text_id, center_x, center_y)
        
    def _on_release(self, event):
        # Kết thúc kéo chuột
        if self.rect:
            end_x, end_y = event.x, event.y
            
            # Đảm bảo tọa độ đúng
            if end_x < self.start_x:
                self.start_x, end_x = end_x, self.start_x
            if end_y < self.start_y:
                self.start_y, end_y = end_y, self.start_y
                
            # Lưu khu vực đã chọn
            self.selected_area = {
                'x': int(self.start_x),
                'y': int(self.start_y),
                'width': int(end_x - self.start_x),
                'height': int(end_y - self.start_y)
            }
            
            # Đổi màu để thể hiện đã chọn
            self.canvas.itemconfig(self.rect, outline="lime", width=3)
            
    def _on_ok(self):
        # Gọi callback nếu đã chọn khu vực
        if hasattr(self, 'selected_area') and self.callback:
            area = self.selected_area
            self.callback(area['x'], area['y'], area['width'], area['height'])
            
        self._on_close()
            
    def _on_close(self):
        # Đóng overlay
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.destroy()
        
        # Hiện lại dialog sửa hành động - quan trọng!
        self.dialog.deiconify()
