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
        # Biến theo dõi trạng thái
        self.start_x = 0
        self.start_y = 0
        self.rect = None
        self.text_id = None
        self.is_selecting = False
        
    def show(self):
        # Ẩn dialog cha tạm thời
        self.parent_dialog.withdraw()
    
        # Tạo cửa sổ overlay trong suốt
        self.overlay = tk.Toplevel()
        self.overlay.title("Chọn khu vực")
        self.overlay.attributes('-fullscreen', True)
        self.overlay.attributes('-alpha', 0.3)  # Trong suốt 70%
        self.overlay.attributes('-topmost', True)
        self.overlay.configure(bg='black')
    
        # Tạo canvas cho việc vẽ
        self.canvas = tk.Canvas(
            self.overlay, 
            bg='black', 
            highlightthickness=0, 
            cursor='cross'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
    
        # Thêm hướng dẫn
        self.instruction = tk.Label(
            self.overlay, 
            text="Kéo chuột chọn khu vực - ESC thoát",
            font=('Arial', 16, 'bold'),
            bg='black', 
            fg='white'
        )
        self.instruction.place(relx=0.5, rely=0.05, anchor=tk.CENTER)
    
        # QUAN TRỌNG: Binding phím ESC
        self.overlay.bind("<Escape>", lambda e: self.close())
    
        # Binding các sự kiện chuột
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
    
        # Set focus để nhận phím ESC
        self.overlay.focus_set()
        
        # Thêm frame cho button đảm bảo nổi lên trên
        self.button_frame = tk.Frame(self.overlay, bg='black')
        self.button_frame.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

        # Nút Đồng ý
        self.ok_button = tk.Button(
            self.button_frame, 
            text="Đồng ý", 
            bg='#4285f4', 
            fg='white',
            font=('Arial', 12),
            padx=20, 
            pady=5, 
            command=self.on_ok
        )
        self.ok_button.pack(pady=10)

        # QUAN TRỌNG: Thêm protocol xử lý đóng cửa sổ
        self.overlay.protocol("WM_DELETE_WINDOW", self.close)

        # Đảm bảo overlay có focus để nhận sự kiện phím
        self.overlay.after(100, self.overlay.focus_force)
        
    def on_mouse_down(self, event):
        # Xóa hình chữ nhật cũ nếu có
        if self.rect:
            self.canvas.delete(self.rect)
        if self.text_id:
            self.canvas.delete(self.text_id)
        
        # Lưu điểm bắt đầu
        self.start_x = event.x
        self.start_y = event.y
        self.is_selecting = True
    
        # Vẽ hình chữ nhật mới
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2, fill='red', stipple='gray25'
        )
    
        # Vẽ chữ Select Area giữa
        self.text_id = self.canvas.create_text(
            self.start_x, self.start_y,
            text="Select Area", fill='white', font=('Arial', 12, 'bold')
        )
        
    def on_mouse_move(self, event):
        if not self.is_selecting or not self.rect:
            return
        
        # Cập nhật hình chữ nhật khi di chuyển chuột
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
    
        # Cập nhật vị trí text giữa hình chữ nhật
        center_x = (self.start_x + event.x) / 2
        center_y = (self.start_y + event.y) / 2
        self.canvas.coords(self.text_id, center_x, center_y)
    
    def on_mouse_up(self, event):
        if not self.is_selecting:
            return
        
        self.is_selecting = False
    
        # Lấy tọa độ cuối
        end_x = event.x
        end_y = event.y
    
        # Đảm bảo tọa độ hợp lệ (width và height dương)
        if end_x < self.start_x:
            self.start_x, end_x = end_x, self.start_x
        if end_y < self.start_y:
            self.start_y, end_y = end_y, self.start_y
        
        # Chỉ xử lý nếu khu vực lớn (tránh click nhầm)
        width = end_x - self.start_x
        height = end_y - self.start_y
    
        if width > 10 and height > 10:
            # Highlight khu vực chọn rõ ràng hơn
            self.canvas.itemconfig(
                self.rect, 
                outline='lime', 
                width=3, 
                stipple='gray50'
            )
        
            # Lưu kích thước sử dụng khi nhấn OK
            self.selected_area = (self.start_x, self.start_y, width, height)
            
    def on_ok(self):
        # Kiểm tra xem đã chọn khu vực chưa
        if hasattr(self, 'selected_area'):
            x, y, width, height = self.selected_area
            if self.callback:
                self.callback(x, y, width, height)
        self.close()
    
    def close(self, event=None):
        # Đóng overlay và hiển thị lại cửa sổ chính
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.destroy()
        
        # Hiển thị lại cửa sổ cha
        self.parent_dialog.deiconify()
        self.parent_dialog.focus_force()
