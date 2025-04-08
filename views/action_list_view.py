import tkinter as tk
from tkinter import ttk, messagebox
import config as cfg

class ActionItemFrame(tk.Frame):
    def __init__(self, parent, action, index, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Thiết lập style cho frame
        self.config(
            bg=cfg.LIGHT_BG_COLOR,
            padx=cfg.SMALL_PADDING,    # Giảm padding
            pady=cfg.SMALL_PADDING,    # Giảm padding
            highlightbackground=cfg.BORDER_COLOR,
            highlightthickness=1,
            relief=tk.FLAT,            # Thay đổi relief
            bd=1,
            height=60  # Thêm chiều cao cố định
        )
        
        # Lưu trữ các thuộc tính quan trọng
        self.action = action
        self.index = index
        self.on_reorder_callback = None
        
        # Tạo layout với Grid để kiểm soát vị trí các phần tử
        self.columnconfigure(1, weight=1)
        
        # Thêm nút kéo thả (drag handle) nhỏ hơn
        self.drag_handle = tk.Label(
            self, 
            text="⋮⋮",
            font=("Segoe UI", 10, "bold"),
            bg=cfg.LIGHT_BG_COLOR,
            fg="#666666",
            padx=2,
            cursor="fleur"
        )
        self.drag_handle.grid(row=0, column=0, rowspan=2, sticky=tk.NS, padx=(0, 5))
        
        # Header frame
        header_frame = tk.Frame(self, bg=cfg.LIGHT_BG_COLOR)
        header_frame.grid(row=0, column=1, sticky=tk.EW, pady=(2, 2))
        
        # Số thứ tự
        self.index_label = tk.Label(
            header_frame, 
            text=f"{index}.", 
            font=("Segoe UI", 10, "bold"),
            bg=cfg.LIGHT_BG_COLOR,
            fg=cfg.PRIMARY_COLOR,
            width=2
        )
        self.index_label.pack(side=tk.LEFT)
        
        # Thêm icon hành động - giống Power Automate
        action_icon = "🔍" if action.action_type == "Tìm Hình Ảnh" else "🖱️"
        icon_label = tk.Label(
            header_frame, 
            text=action_icon, 
            font=("Segoe UI", 10),
            bg=cfg.LIGHT_BG_COLOR
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 2))
        
        # Loại hành động
        action_type_label = tk.Label(
            header_frame, 
            text=action.action_type, 
            font=("Segoe UI", 10, "bold"),
            bg=cfg.LIGHT_BG_COLOR,
            fg=cfg.PRIMARY_COLOR
        )
        action_type_label.pack(side=tk.LEFT)
        
        # Thông tin tham số - nhỏ gọn hơn
        params_text = self._get_params_text(action)
        params_label = tk.Label(
            self, 
            text=params_text, 
            justify=tk.LEFT,
            anchor=tk.W,
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9),  # Font nhỏ hơn
            wraplength=380
        )
        params_label.grid(row=1, column=1, sticky=tk.W)
        
        # Frame chứa các nút hành động - nhỏ gọn hơn với icon
        button_frame = tk.Frame(self, bg=cfg.LIGHT_BG_COLOR)
        button_frame.grid(row=1, column=2, sticky=tk.E, padx=(5, 0))
        
        # Nút chỉnh sửa nhỏ gọn với icon
        self.edit_button = tk.Button(
            button_frame, 
            text="✏️", 
            bg=cfg.LIGHT_BG_COLOR, 
            fg=cfg.SECONDARY_COLOR,
            padx=3,
            pady=0,
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground=cfg.HOVER_COLOR
        )
        self.edit_button.pack(side=tk.LEFT, padx=(0, 2))
        
        # Nút xóa nhỏ gọn với icon
        self.delete_button = tk.Button(
            button_frame, 
            text="🗑️", 
            bg=cfg.LIGHT_BG_COLOR, 
            fg=cfg.DANGER_COLOR,
            padx=3,
            pady=0,
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            activebackground=cfg.HOVER_COLOR
        )
        self.delete_button.pack(side=tk.LEFT)
        
        # Binding sự kiện hover
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        
        # Binding sự kiện kéo thả
        self.drag_handle.bind("<ButtonPress-1>", self.on_drag_start)
        self.drag_handle.bind("<B1-Motion>", self.on_drag_motion)
        self.drag_handle.bind("<ButtonRelease-1>", self.on_drag_end)
        
     # Thêm phương thức mới để cập nhật số thứ tự
    def update_index(self, new_index):
        self.index = new_index
        self.index_label.config(text=f"{new_index}.")
        
    def _get_params_text(self, action):
        if action.action_type == "Tìm Hình Ảnh":
            path = action.parameters.get('path', '')
            accuracy = action.parameters.get('accuracy', '80')
        
            # Hiển thị tên file thay vì đường dẫn đầy đủ
            import os
            filename = os.path.basename(path) if path else "Không có hình"
        
            # Đảm bảo hiển thị giá trị % đúng
            try:
                # Nếu accuracy được lưu dưới dạng thập phân (0-1)
                acc_value = float(accuracy)
                if acc_value <= 1.0:
                    accuracy_display = f"{acc_value * 100:.0f}%"
                else:
                    accuracy_display = f"{acc_value:.0f}%"
            except ValueError:
                accuracy_display = f"{accuracy}%"
            
            return f"Hình: {filename} | Độ chính xác: {accuracy_display}"
        elif action.action_type == "Di Chuyển Chuột":
            return f"X: {action.parameters.get('x', '')}, Y: {action.parameters.get('y', '')} | Thời gian: {action.parameters.get('duration', '')}s"
        return ""
        
    def _on_hover(self, event):
        if hasattr(self, '_dragging') and self._dragging:
            return
            
        self.config(bg=cfg.HOVER_COLOR)
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.config(bg=cfg.HOVER_COLOR)
                for subwidget in widget.winfo_children():
                    if isinstance(subwidget, tk.Label):
                        subwidget.config(bg=cfg.HOVER_COLOR)
            elif isinstance(widget, tk.Label):
                widget.config(bg=cfg.HOVER_COLOR)
                
    def _on_leave(self, event):
        if hasattr(self, '_dragging') and self._dragging:
            return
            
        self.config(bg=cfg.LIGHT_BG_COLOR)
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.config(bg=cfg.LIGHT_BG_COLOR)
                for subwidget in widget.winfo_children():
                    if isinstance(subwidget, tk.Label):
                        subwidget.config(bg=cfg.LIGHT_BG_COLOR)
            elif isinstance(widget, tk.Label):
                widget.config(bg=cfg.LIGHT_BG_COLOR)
    
    def on_drag_start(self, event):
        """Xử lý sự kiện bắt đầu kéo"""
        # Ghi nhớ vị trí ban đầu và widget đang kéo
        self._drag_data = {
            "x_start": event.x,
            "y_start": event.y,
            "widget": self,
            "index": self.index - 1  # Chuyển index hiển thị sang index thực tế
        }
    
        # Đổi từ pack sang place để kéo
        self.pack_info_saved = self.pack_info()
        self.pack_forget()
        
        # Đặt vị trí ban đầu
        initial_y = self.master.winfo_y() + self._drag_data["y_start"]
        self.place(x=0, y=initial_y, relwidth=1)
        self.lift()  # Đưa lên trên cùng
    
        # Hiệu ứng kéo
        self.config(bg="#e3f2fd")  # Màu nền nhẹ hơn khi kéo
    
        # Đánh dấu đang kéo
        self.is_dragging = True
        
        # Cập nhật UI thường xuyên để tránh giật lag
        self.update_idletasks()
        

    def on_drag_motion(self, event):
        """Xử lý sự kiện đang kéo"""
        if not hasattr(self, '_drag_data') or not self.is_dragging:
            return
        
        # Tính vị trí mới
        delta_y = event.y - self._drag_data["y_start"]
        new_y = self.winfo_y() + delta_y
    
        # Di chuyển widget theo chuột
        self.place(x=0, y=new_y, relwidth=1)
        self.lift()  # Đảm bảo widget hiển thị trên cùng
    
        # Hiệu ứng visual
        self.config(bg="#e3f2fd")  # Giữ nguyên màu nền khi kéo
    
        # Xử lý placeholder và cập nhật index
        parent = self.master
       
        visible_frames = []
        for child in parent.winfo_children():
            if isinstance(child, ActionItemFrame) and child != self:
                # Thêm điều kiện để đảm bảo chỉ xem xét các frame đã được pack
                try:
                    child.pack_info()  # Kiểm tra xem widget đã được pack chưa
                    visible_frames.append(child)
                except:
                    pass  # Bỏ qua các widget chưa được pack

        # Đảm bảo sắp xếp theo vị trí y để xác định đúng vị trí
        visible_frames.sort(key=lambda f: f.winfo_y())
        
 
        # Tìm vị trí mới dựa trên vị trí con trỏ và phần giao nhau
        new_index = len(visible_frames)  # Mặc định là cuối cùng
        original_index = self._drag_data["index"]

        # Vị trí con trỏ chuột trong hệ tọa độ của canvas
        mouse_y = self.winfo_y() + event.y

        # Tính toán khoảng cách và vị trí thả
        min_distance = float('inf')
        best_index = new_index

        for i, frame in enumerate(visible_frames):
            # Tính toán điểm trên và dưới của frame
            frame_top = frame.winfo_y()
            frame_bottom = frame.winfo_y() + frame.winfo_height()
    
            # Tính khoảng cách từ chuột đến điểm chính giữa của frame
            top_distance = abs(mouse_y - frame_top)
            bottom_distance = abs(mouse_y - frame_bottom)
    
            # Chọn khoảng cách nhỏ nhất
            if top_distance < min_distance:
                min_distance = top_distance
                best_index = i
    
            if bottom_distance < min_distance and i == len(visible_frames)-1:
                min_distance = bottom_distance
                best_index = i + 1

        # Cập nhật vị trí mới
        new_index = best_index
                
    
        # Cập nhật placeholder
        if hasattr(parent, '_placeholder'):
            parent._placeholder.destroy()
    
        parent._placeholder = tk.Frame(
            parent,
            height=self.winfo_height(),
            bg=cfg.DRAG_PLACEHOLDER_COLOR,
            highlightthickness=0
        )
    
        # Chèn placeholder vào vị trí chính xác
        try:
            if new_index < len(visible_frames):
                # Kiểm tra trạng thái pack trước khi sử dụng before
                try:
                    visible_frames[new_index].pack_info()  # Kiểm tra xem widget đã được pack chưa
                    parent._placeholder.pack(before=visible_frames[new_index], fill=tk.X, pady=2)
                except:
                    # Nếu widget chưa được pack, đặt placeholder ở cuối
                    parent._placeholder.pack(fill=tk.X, pady=2)
            else:
                parent._placeholder.pack(fill=tk.X, pady=2)
        
            # Đảm bảo item đang kéo nằm trên placeholder
            self.lift()  # Đưa item đang kéo lên trên cùng sau khi đặt placeholder
        except Exception as e:
            print(f"Lỗi khi đặt placeholder: {e}")
            # Nếu vẫn gặp lỗi, thử cách khác - đặt placeholder ở cuối
            try:
                parent._placeholder.pack(fill=tk.X, pady=2)
                self.lift()
            except:
                pass

        # Cập nhật placeholder và lưu new_index
        self._drag_data["new_index"] = new_index


    def on_drag_end(self, event):
        """Xử lý sự kiện kết thúc kéo"""
        if not hasattr(self, '_drag_data') or not self.is_dragging:
            return
    
        # Đặt lại cấu hình
        self.config(bg=cfg.LIGHT_BG_COLOR)  # Đặt lại màu nền
    
        # Chuyển từ place về pack
        self.place_forget()
    
        # Lấy vị trí cũ và mới
        old_index = self._drag_data["index"]
        new_index = self._drag_data.get("new_index", old_index)
    
        # Xóa placeholder
        if hasattr(self.master, '_placeholder') and self.master._placeholder:
            self.master._placeholder.destroy()
            delattr(self.master, '_placeholder')
    
        # THÊM MỚI: Luôn đặt lại item với pack()
        # Nếu vị trí không thay đổi, chỉ pack lại item đó
        if old_index == new_index:
            self.pack(fill=tk.X, pady=2, padx=2)
        # Nếu vị trí thay đổi, gọi callback để cập nhật
        elif hasattr(self, 'on_reorder_callback') and self.on_reorder_callback:
            self.on_reorder_callback(old_index, new_index)
        else:
            # Trường hợp có thay đổi nhưng không có callback
            self.pack(fill=tk.X, pady=2, padx=2)
    
        # Đặt lại các biến trạng thái
        self.is_dragging = False
        delattr(self, '_drag_data')



class ActionListView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=cfg.SMALL_PADDING)  # Giảm padding chung
        self.parent = parent
        self.action_frames = []
    
        # Thiết lập style
        style = ttk.Style()
        style.configure("TFrame", background=cfg.LIGHT_BG_COLOR)
        style.configure("TLabelframe", background=cfg.LIGHT_BG_COLOR)
        style.configure("TLabelframe.Label", background=cfg.LIGHT_BG_COLOR, font=cfg.HEADER_FONT)
    
        # Tạo layout chính - giống Power Automate Desktop
        main_frame = tk.Frame(self, bg=cfg.LIGHT_BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True)
    
        # Phân chia thành hai phần: sidebar và content (giữ nguyên cấu trúc)
        # Thu nhỏ sidebar một chút
        sidebar = tk.Frame(main_frame, bg="#f0f0f0", width=180)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)  # Giữ kích thước cố định
    
        content = tk.Frame(main_frame, bg=cfg.LIGHT_BG_COLOR)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
        # Sidebar header - nhỏ gọn hơn
        sidebar_header = tk.Label(
            sidebar,
            text="TomSamAutobot",
            font=("Segoe UI", 12, "bold"),  # Giảm kích thước font
            fg=cfg.PRIMARY_COLOR,
            bg="#f0f0f0",
            pady=8  # Giảm padding
        )
        sidebar_header.pack(fill=tk.X)
    
        # Các nút trong sidebar - nhỏ gọn hơn
        actions_btn = tk.Button(
            sidebar,
            text="Hành động",
            bg=cfg.PRIMARY_COLOR,
            fg="white",
            font=("Segoe UI", 9),  # Giảm kích thước font
            relief=tk.FLAT,
            padx=4,  # Giảm padding
            pady=4,
            cursor="hand2"
        )
        actions_btn.pack(fill=tk.X, padx=4, pady=2)
    
        variables_btn = tk.Button(
            sidebar,
            text="Biến",
            bg="#f0f0f0",
            fg="#333333",
            font=("Segoe UI", 9),  # Giảm kích thước font
            relief=tk.FLAT,
            padx=4,  # Giảm padding
            pady=4,
            cursor="hand2"
        )
        variables_btn.pack(fill=tk.X, padx=4, pady=2)
    
        # Thêm nút Cài đặt - phong cách PAD
        settings_btn = tk.Button(
            sidebar,
            text="Cài đặt",
            bg="#f0f0f0",
            fg="#333333",
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=4,
            pady=4,
            cursor="hand2"
        )
        settings_btn.pack(fill=tk.X, padx=4, pady=2)
    
        # Content area header - nhỏ gọn hơn
        content_header = tk.Frame(content, bg=cfg.LIGHT_BG_COLOR)
        content_header.pack(fill=tk.X, padx=8, pady=(8, 4))  # Giảm padding
    
        # Thêm icon cho dòng chính - phong cách PAD
        flow_icon = tk.Label(
            content_header,
            text="📊",  # Icon biểu đồ
            font=("Segoe UI", 12),
            fg=cfg.PRIMARY_COLOR,
            bg=cfg.LIGHT_BG_COLOR
        )
        flow_icon.pack(side=tk.LEFT, padx=(0, 2))
    
        flow_label = tk.Label(
            content_header,
            text="Dòng chính",
            font=("Segoe UI", 11, "bold"),  # Giảm kích thước font
            fg=cfg.PRIMARY_COLOR,
            bg=cfg.LIGHT_BG_COLOR
        )
        flow_label.pack(side=tk.LEFT)
    
        # Nút thêm hành động mới - nhỏ gọn hơn
        self.add_button = tk.Button(
            content_header, 
            text="+ Thêm Hành Động",
            bg=cfg.PRIMARY_COLOR,
            fg="white",
            font=("Segoe UI", 9),
            padx=8,  # Giảm padding
            pady=2,
            relief=tk.FLAT,
            activebackground=cfg.SECONDARY_COLOR,
            activeforeground="white",
            cursor="hand2"
        )
        self.add_button.pack(side=tk.RIGHT)
    
        # Canvas và scrollbar cho danh sách hành động - nhỏ gọn hơn
        list_container = tk.Frame(content, bg=cfg.LIGHT_BG_COLOR, padx=8)  # Giảm padding
        list_container.pack(fill=tk.BOTH, expand=True)
    
        # Thêm tiêu đề cho khu vực danh sách
        list_header = tk.Label(
            list_container,
            text="Các bước thực hiện",
            font=("Segoe UI", 9),
            fg="#666666",
            bg=cfg.LIGHT_BG_COLOR,
            anchor=tk.W
        )
        list_header.pack(fill=tk.X, pady=(0, 2), anchor=tk.W)
    
        # Thêm đường kẻ phân cách nhẹ
        separator = ttk.Separator(list_container, orient='horizontal')
        separator.pack(fill=tk.X, pady=2)
    
        self.canvas = tk.Canvas(list_container, bg=cfg.LIGHT_BG_COLOR, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
    
        self.action_list_frame = tk.Frame(self.canvas, bg=cfg.LIGHT_BG_COLOR)
        self.action_list_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
    
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.action_list_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
    
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        # Canvas resize binding
        self.canvas.bind("<Configure>", self._on_canvas_resize)
    
        # Button bar dưới cùng - nhỏ gọn hơn
        button_bar = tk.Frame(content, bg="#f0f0f0", height=36)  # Giảm chiều cao
        button_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
       
    
        # Run button - nhỏ gọn hơn
        self.run_button = tk.Button(
            button_bar, 
            text="▶️ Chạy",
            bg=cfg.SUCCESS_COLOR,
            fg="white",
            font=("Segoe UI", 9),  # Giảm kích thước font
            padx=12,  # Giảm padding
            pady=2,
            relief=tk.FLAT,
            activebackground="#0b8043",
            activeforeground="white",
            cursor="hand2"
        )
        self.run_button.pack(side=tk.RIGHT, padx=8, pady=4)  # Giảm padding
    
        # Thêm status bar - phong cách PAD
        status_bar = tk.Label(
            content,
            text="Sẵn sàng",
            font=("Segoe UI", 8),
            fg="#666666",
            bg="#f8f8f8",
            anchor=tk.W,
            padx=5,
            pady=1
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
        # Callbacks
        self.edit_callback = None
        self.delete_callback = None
        self.drag_callback = None
        
    def update_listbox(self, actions):
        # Clear existing frames
        for frame in self.action_frames:
            frame.destroy()
        self.action_frames = []
        
        # Add new action frames với spacing nhỏ hơn
        for i, action in enumerate(actions):
            frame = ActionItemFrame(self.action_list_frame, action, i+1)
            frame.pack(fill=tk.X, pady=(0, 3), padx=2)  # Giảm padding
            
            # Set callbacks for action frame
            frame.on_reorder_callback = self._on_reorder
            frame.edit_button.config(command=lambda idx=i: self._on_edit(idx))
            frame.delete_button.config(command=lambda idx=i: self._on_delete(idx))
            
            self.action_frames.append(frame)
        
    def _on_canvas_resize(self, event):
        # Resize canvas window to fill available space
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)   
        
    
    def _on_reorder(self, from_index, to_index):
        if from_index == to_index:
            return
        
        # Điều chỉnh to_index nếu cần
        if from_index < to_index:
            to_index -= 1
        
        # Gọi callback để cập nhật model
        if self.drag_callback:
            self.drag_callback(from_index, to_index)
    
        # Cập nhật UI và số thứ tự
        # Di chuyển item trong danh sách action_frames
        item = self.action_frames.pop(from_index)
        self.action_frames.insert(to_index, item)
    
        # Hiển thị lại các frame theo thứ tự mới
        for i, frame in enumerate(self.action_frames):
            frame.pack_forget()  # Xóa khỏi UI
    
        # Thêm lại vào UI với số thứ tự đã cập nhật
        for i, frame in enumerate(self.action_frames):
            frame.index = i + 1
            if hasattr(frame, 'index_label'):
                frame.index_label.config(text=f"{i+1}.")
            frame.pack(fill=tk.X, pady=2, padx=2)
    
        # Force update
        self.update_idletasks()
        

    
    # Thêm phương thức mới để cập nhật số thứ tự cho tất cả các frame
    def update_all_indices(self):
        for i, frame in enumerate(self.action_frames):
            frame.update_index(i+1)
        
    def _on_edit(self, index):
        if self.edit_callback:
            self.edit_callback(index)
            
    def _on_delete(self, index):
        if self.delete_callback:
            self.delete_callback(index)
        
    def get_selected_index(self):
        # Since we're not tracking selection in this implementation,
        # we return None or could implement a selection mechanism
        return None
        
    def show_message(self, title, message):
        messagebox.showinfo(title, message)
        
    def ask_yes_no(self, title, message):
        return messagebox.askyesno(title, message)
            
    def set_callbacks(self, add_callback, edit_callback, delete_callback, run_callback, drag_callback):
        self.add_button.config(command=add_callback)
        self.run_button.config(command=run_callback)
        self.edit_callback = edit_callback
        self.delete_callback = delete_callback
        self.drag_callback = drag_callback
