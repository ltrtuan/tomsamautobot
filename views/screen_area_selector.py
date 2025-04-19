import tkinter as tk
from PIL import ImageGrab, ImageTk
import pyautogui
import time
import traceback  # Thêm để bắt lỗi chi tiết

class ScreenAreaSelector:
    def __init__(self, parent_dialog, callback=None):
        self.parent_dialog = parent_dialog
        self.callback = callback
        
        # Biến theo dõi trạng thái
        self.start_x = 0
        self.start_y = 0
        self.rect = None
        self.text_id = None
        self.is_selecting = False
        
        # Debug info
        print("ScreenAreaSelector initialized")
        
    def show(self):
        try:
            # Lưu trạng thái dialog cha
            if hasattr(self.parent_dialog, 'winfo_ismapped') and self.parent_dialog.winfo_ismapped():
                self.parent_was_visible = True
            else:
                self.parent_was_visible = False
                
            # Ẩn dialog cha tạm thời
            try:
                self.parent_dialog.withdraw()
                print("Parent dialog withdrawn")
            except Exception as e:
                print(f"Error withdrawing parent dialog: {e}")
                if hasattr(self.parent_dialog, 'winfo_toplevel'):
                    try:
                        self.parent_dialog.winfo_toplevel().withdraw()
                        print("Parent toplevel withdrawn")
                    except Exception as e2:
                        print(f"Error withdrawing parent toplevel: {e2}")
            
            # Tạo cửa sổ overlay trong suốt
            self.overlay = tk.Toplevel()
            self.overlay.title("Chọn khu vực")
            self.overlay.attributes('-fullscreen', True)
            self.overlay.attributes('-alpha', 0.3)
            self.overlay.attributes('-topmost', 1)  # Số 1 thay vì True
            self.overlay.configure(bg='black')
            
            # QUAN TRỌNG: Binding ESC TOÀN CỤC - không chỉ cho overlay
            self.overlay.bind_all("<Escape>", self.close)
            
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
            
            # Binding sự kiện chuột 
            self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
            self.canvas.bind("<B1-Motion>", self.on_mouse_move)
            self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
            
            # Nút Đồng ý - đặt trong frame riêng
            self.button_frame = tk.Frame(self.overlay, bg='black')
            self.button_frame.pack(side=tk.BOTTOM, pady=20, fill=tk.X)
            
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
            
            # Grab tất cả input cho overlay
            self.overlay.grab_set()
            
            # Protocol khi đóng cửa sổ
            self.overlay.protocol("WM_DELETE_WINDOW", self.close)
            
            # Đảm bảo focus ban đầu
            self.overlay.focus_force()
            
            # Kiểm tra focus liên tục
            self.check_focus_id = self.overlay.after(100, self.check_focus)
            
            # Đảm bảo button frame nổi lên trên
            self.button_frame.lift()
        
        except Exception as e:
            print(f"Error in show(): {e}")
            traceback.print_exc()
            self.restore_parent()
    
    def check_focus(self):
        """Kiểm tra và đảm bảo overlay luôn có focus"""
        try:
            if self.overlay.winfo_exists():
                self.overlay.focus_force()
                # Tiếp tục kiểm tra sau mỗi 500ms
                self.check_focus_id = self.overlay.after(500, self.check_focus)
        except:
            pass  # Overlay đã bị hủy
        
    def on_mouse_down(self, event):
        try:
            print(f"Mouse down at {event.x}, {event.y}")
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
                outline='red', width=2, fill='red'  # Bỏ stipple để tránh lỗi
            )
            
            # Vẽ chữ Select Area giữa
            self.text_id = self.canvas.create_text(
                self.start_x, self.start_y,
                text="Select Area", fill='white', font=('Arial', 12, 'bold')
            )
        except Exception as e:
            print(f"Error in on_mouse_down: {e}")
        
    def on_mouse_move(self, event):
        try:
            # Chỉ xử lý khi đang trong trạng thái chọn
            if not self.is_selecting or not self.rect:
                return
                
            # Cập nhật hình chữ nhật khi di chuyển chuột
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
            
            # Cập nhật vị trí text giữa hình chữ nhật
            center_x = (self.start_x + event.x) / 2
            center_y = (self.start_y + event.y) / 2
            self.canvas.coords(self.text_id, center_x, center_y)
        except Exception as e:
            print(f"Error in on_mouse_move: {e}")
        
    def on_mouse_up(self, event):
        try:
            print(f"Mouse up at {event.x}, {event.y}")
            # Chỉ xử lý khi đang trong trạng thái chọn
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
                    width=3
                )
                
                # Lưu kích thước sử dụng khi nhấn OK
                self.selected_area = (int(self.start_x), int(self.start_y), int(width), int(height))
                print(f"Selected area: {self.selected_area}")
                
                # Đảm bảo nút Đồng ý hiển thị rõ
                self.button_frame.lift()
        except Exception as e:
            print(f"Error in on_mouse_up: {e}")
            
    def on_ok(self):
        try:
            # Kiểm tra xem đã chọn khu vực chưa
            if hasattr(self, 'selected_area'):
                x, y, width, height = self.selected_area
                if self.callback:
                    self.callback(x, y, width, height)
            self.close()
        except Exception as e:
            print(f"Error in on_ok: {e}")
            self.close()
        
    def close(self, event=None):
        try:
            # Hủy lịch check focus
            if hasattr(self, 'check_focus_id') and self.check_focus_id:
                self.overlay.after_cancel(self.check_focus_id)
            
            # Giải phóng grab nếu có
            if hasattr(self, 'overlay') and self.overlay.winfo_exists():
                try:
                    self.overlay.grab_release()
                except:
                    pass
                
                # Đóng overlay
                self.overlay.destroy()
            
            # Hiển thị lại cửa sổ cha
            self.restore_parent()
        except Exception as e:
            print(f"Error in close: {e}")
            # Đảm bảo luôn khôi phục parent dialog
            self.restore_parent()
    
    def restore_parent(self):
        """Khôi phục cửa sổ cha"""
        try:
            # Chỉ hiển thị lại nếu trước đó đã visible
            if hasattr(self, 'parent_was_visible') and self.parent_was_visible:
                if hasattr(self.parent_dialog, 'deiconify'):
                    self.parent_dialog.deiconify()
                    print("Parent dialog deiconified")
                elif hasattr(self.parent_dialog, 'winfo_toplevel'):
                    self.parent_dialog.winfo_toplevel().deiconify()
                    print("Parent toplevel deiconified")
                
                # Đảm bảo focus
                try:
                    self.parent_dialog.focus_force()
                except:
                    if hasattr(self.parent_dialog, 'winfo_toplevel'):
                        self.parent_dialog.winfo_toplevel().focus_force()
        except Exception as e:
            print(f"Error restoring parent: {e}")
