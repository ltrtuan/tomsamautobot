import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import config as cfg
from constants import ActionType
from views.action_params.image_search_params import ImageSearchParams
from views.action_params.mouse_move_params import MouseMoveParams

class ActionDialogView(tk.Toplevel):
    def __init__(self, parent, action=None):
        super().__init__(parent)
        self.title("Thêm/Sửa Hành Động")
        self.parent = parent
        self.result = None
        
        # Thiết lập style cho cửa sổ
        self.configure(bg=cfg.LIGHT_BG_COLOR)
        self.resizable(True, True)  # Cho phép thay đổi kích thước cửa sổ
    
        # Pre-fill if editing an existing action
        self.is_edit = action is not None
        self.current_action = action
        
        # Create main frame
        main_frame = tk.Frame(self, bg=cfg.LIGHT_BG_COLOR, padx=cfg.LARGE_PADDING, pady=cfg.LARGE_PADDING)
        main_frame.pack(fill=tk.BOTH, expand=True)
    
        # Title
        title_text = "Sửa Hành Động" if self.is_edit else "Thêm Hành Động Mới"
        title_label = tk.Label(
            main_frame, 
            text=title_text, 
            font=cfg.TITLE_FONT, 
            bg=cfg.LIGHT_BG_COLOR,
            fg=cfg.PRIMARY_COLOR
        )
        title_label.pack(anchor=tk.W, pady=(0, 15))
    
        # Action type selection
        type_frame = tk.Frame(main_frame, bg=cfg.LIGHT_BG_COLOR)
        type_frame.pack(fill=tk.X, pady=(0, 10))
    
        type_label = tk.Label(
            type_frame, 
            text="Loại Hành Động:", 
            font=cfg.DEFAULT_FONT, 
            bg=cfg.LIGHT_BG_COLOR
        )
        type_label.pack(side=tk.LEFT, padx=(0, 10))
    
        self.action_type_var = tk.StringVar()
    
        # Style cho Combobox
        self.style = ttk.Style()
        self.style.configure("TCombobox", padding=5)   
        self.action_type_combo = ttk.Combobox(
            type_frame, 
            textvariable=self.action_type_var, 
            values=ActionType.get_display_values(),
            state="readonly", 
            width=25,
            font=cfg.DEFAULT_FONT
        )
        self.action_type_combo.pack(side=tk.LEFT)
    
        # Parameter frame
        param_container = tk.Frame(main_frame, bg=cfg.LIGHT_BG_COLOR)
        param_container.pack(fill=tk.BOTH, expand=True, pady=10)
    
        param_header = tk.Label(
            param_container, 
            text="Tham Số", 
            font=cfg.HEADER_FONT, 
            bg=cfg.LIGHT_BG_COLOR,
            anchor=tk.W
        )
        param_header.pack(fill=tk.X, pady=(0, 5))
    
        # Separator
        separator = ttk.Separator(param_container, orient='horizontal')
        separator.pack(fill=tk.X, pady=5)
    
        # Thêm khung cuộn cho param_frame
        # Tạo canvas và thanh cuộn
        self.canvas = tk.Canvas(param_container, bg=cfg.LIGHT_BG_COLOR, highlightthickness=0)
        scroll_y = ttk.Scrollbar(param_container, orient="vertical", command=self.canvas.yview)
    
        # Cấu hình canvas và scroll
        self.canvas.configure(yscrollcommand=scroll_y.set)
    
        # Đặt vị trí canvas và thanh cuộn
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
        # Tạo frame bên trong canvas để chứa tham số
        self.param_frame = tk.Frame(self.canvas, bg=cfg.LIGHT_BG_COLOR, padx=10, pady=10)
    
        # Tạo cửa sổ trong canvas để hiển thị param_frame
        self.canvas_window = self.canvas.create_window((0, 0), window=self.param_frame, anchor="nw", tags="self.param_frame")
    
        # Cấu hình sự kiện khi kích thước thay đổi
        self.param_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
    
        # Hỗ trợ cuộn bằng chuột
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
        # Button frame
        button_frame = tk.Frame(main_frame, bg=cfg.LIGHT_BG_COLOR)
        button_frame.pack(fill=tk.X, pady=(15, 0))
    
        # Cancel button
        self.cancel_button = tk.Button(
            button_frame, 
            text="Hủy", 
            bg="#f5f5f5", 
            fg="#333333",
            font=cfg.DEFAULT_FONT, 
            padx=20, 
            pady=8, 
            relief=tk.FLAT,
            activebackground="#e0e0e0", 
            activeforeground="#333333",
            cursor="hand2"
        )
        self.cancel_button.pack(side=tk.LEFT)
        self.cancel_button.config(command=self.destroy)
    
        # Save button
        self.save_button = tk.Button(
            button_frame, 
            text="Lưu", 
            bg=cfg.PRIMARY_COLOR, 
            fg="white",
            font=cfg.DEFAULT_FONT, 
            padx=20, 
            pady=8, 
            relief=tk.FLAT,
            activebackground=cfg.SECONDARY_COLOR, 
            activeforeground="white",
            cursor="hand2"
        )
        self.save_button.pack(side=tk.RIGHT)        
        
        # Pre-fill if editing
        if self.is_edit:            
            self.action_type_var.set(self.current_action.action_type)
            # Hide the combobox
            self.action_type_combo.pack_forget()

            # Add a label instead
            action_type_value = tk.Label(
                type_frame,
                text=ActionType.get_action_type_display(self.current_action.action_type),
                font=cfg.DEFAULT_FONT,
                bg=cfg.LIGHT_BG_COLOR
            )
            action_type_value.pack(side=tk.LEFT)            
         
    
        # Center dialog and make it modal
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_visibility()
    
        # Set position relative to parent
        window_width = 500  # Tăng kích thước một chút
        window_height = 600
    
        # Calculate center position
        x = (parent.winfo_rootx() + (parent.winfo_width() / 2)) - (window_width / 2)
        y = (parent.winfo_rooty() + (parent.winfo_height() / 2)) - (window_height / 2)
    
        # Set window size and position
        self.geometry(f"{window_width}x{window_height}+{int(x)}+{int(y)}")
        
        self.current_params = None  # Biến chứa đối tượng tham số hiện tại
        # Map các loại action với các lớp param tương ứng
        self.param_classes = {
            ActionType.TIM_HINH_ANH: ImageSearchParams,
            ActionType.DI_CHUYEN_CHUOT: MouseMoveParams,
            # Thêm các action khác trong tương lai
        }

    # Thêm các phương thức hỗ trợ cho cuộn
    def _on_frame_configure(self, event):
        # Cập nhật scrollregion khi kích thước param_frame thay đổi
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        # Thay đổi kích thước cửa sổ trong canvas khi resize
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        # Cuộn bằng chuột
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def create_params_for_action_type(self, action_type, parameters=None):
        """Tạo UI tham số dựa trên loại hành động"""
        # Xóa các widget cũ
        for widget in self.param_frame.winfo_children():
            widget.destroy()
    
        # Lấy lớp tham số phù hợp từ dictionary
        if action_type in self.param_classes:
            param_class = self.param_classes[action_type]
            # Khởi tạo đối tượng tham số
            self.current_params = param_class(self.param_frame, parameters)
            # Tạo UI và trả về các nút
            return self.current_params.create_params()
    
        return None, None, None, None

        
    # Thêm vào class ActionDialogView
    # def get_parameter_value(self, param_name):
    #     """Lấy giá trị của tham số từ class tham số hiện tại"""
    #     action_type_display = self.action_type_var.get()
    #     action_type = ActionType.from_display_value(action_type_display)
    #     # Xác định class tham số dựa trên action_type
    #     if action_type == ActionType.TIM_HINH_ANH:
    #         if hasattr(self, 'image_params') and self.image_params:
    #             for key, var in self.image_params.variables.items():
    #                 if key.replace("_var", "") == param_name:
    #                     return var.get()
    #     elif action_type == ActionType.DI_CHUYEN_CHUOT:
    #         if hasattr(self, 'mouse_params') and self.mouse_params:
    #             for key, var in self.mouse_params.variables.items():
    #                 if key.replace("_var", "") == param_name:
    #                     return var.get()
    
    #     # Trả về None nếu không tìm thấy
        return None
    
    def set_parameter_value(self, param_name, value):
        """Set a parameter value in the current parameter object"""
        if hasattr(self, 'current_params') and self.current_params:
            if f"{param_name}_var" in self.current_params.variables:
                self.current_params.variables[f"{param_name}_var"].set(value)
            else:
                print(f"Warning: Parameter {param_name} not found in current_params")
            
    def get_all_parameters(self):
        """Lấy tất cả tham số từ class tham số hiện tại"""
        # action_type_display = self.action_type_var.get()
        # action_type = ActionType.from_display_value(action_type_display)
        
        # if action_type == ActionType.TIM_HINH_ANH:
        #     if hasattr(self, 'image_params') and self.image_params:
        #         return self.image_params.get_parameters()
        # elif action_type == ActionType.DI_CHUYEN_CHUOT:
        #     if hasattr(self, 'mouse_params') and self.mouse_params:
        #         return self.mouse_params.get_parameters()
    
        # return {}        
        if hasattr(self, 'current_params') and self.current_params:
            return self.current_params.get_parameters()
        return {}
        
    def create_image_search_params(self, parameters=None):
        """Tạo UI cho tìm kiếm hình ảnh"""       
        self.image_params = ImageSearchParams(self.param_frame, parameters)
        return self.image_params.create_params()

    def create_mouse_move_params(self, parameters=None):
        """Tạo UI cho di chuyển chuột"""
        self.mouse_params = MouseMoveParams(self.param_frame, parameters)
        return self.mouse_params.create_params()
        
    def _update_duration(self, value):
        self.duration_var.set(f"{float(value):.1f}")
            
    def get_mouse_move_params(self):
        try:
            x_coord = self.x_coord_var.get()
            y_coord = self.y_coord_var.get()
            duration = self.duration_var.get()
            
            try:
                x_val = int(x_coord)
                y_val = int(y_coord)
            except ValueError:
                messagebox.showerror("Lỗi", "Tọa độ phải là số nguyên")
                return None
            
            try:
                duration_val = float(duration)
                if duration_val < 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Lỗi", "Thời gian phải là số dương")
                return None
                
            return {"x": x_coord, "y": y_coord, "duration": duration}
        except:
            return None
    
    def add_break_condition(self, condition=None):
        if condition is None:
            condition = {"variable": "", "value": "", "logical_op": ""}
    
        # Tạo frame chứa condition
        condition_row = tk.Frame(self.break_frame, bg=cfg.LIGHT_BG_COLOR)
        condition_row.pack(fill=tk.X, pady=5)

        # Phần AND/OR dropdown (chỉ hiển thị cho condition thứ 2 trở đi)
        logical_op_var = tk.StringVar(value=condition.get("logical_op", ""))
        if len(self.break_conditions) > 0:
            logical_op = ttk.Combobox(
                condition_row, 
                textvariable=logical_op_var,
                values=["", "AND", "OR"],
                width=5,
                state="readonly"
            )
            logical_op.pack(side=tk.LEFT, padx=5)

        # Phần Variable
        tk.Label(condition_row, text="Variable:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
        variable_var = tk.StringVar(value=condition.get("variable", ""))
        variable_entry = ttk.Entry(condition_row, textvariable=variable_var, width=10)
        variable_entry.pack(side=tk.LEFT, padx=5)

        # Phần Value
        tk.Label(condition_row, text="Value:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
        value_var = tk.StringVar(value=condition.get("value", ""))
        value_entry = ttk.Entry(condition_row, textvariable=value_var, width=5)
        value_entry.pack(side=tk.LEFT, padx=5)
    
        # Thêm nút xóa condition
        delete_button = tk.Button(
            condition_row,
            text="✖",
            bg=cfg.LIGHT_BG_COLOR,
            fg="#d13438",  # Màu đỏ
            font=("Segoe UI", 8),
            relief=tk.FLAT,
            padx=2,
            pady=0,
            cursor="hand2",
            activebackground=cfg.LIGHT_BG_COLOR,
            activeforeground="#a52a2a"
        )
        delete_button.pack(side=tk.RIGHT, padx=5)

        # Lưu tham chiếu đến các biến và widget
        condition_data = {
            "row": condition_row,
            "logical_op_var": logical_op_var,
            "variable_var": variable_var,
            "value_var": value_var,
            "delete_button": delete_button
        }
    
        # Thêm vào danh sách conditions
        self.break_conditions.append(condition_data)
    
        # Cấu hình nút xóa để xóa đúng condition này
        # Sử dụng lambda với condition_row và condition_data cụ thể
        delete_button.config(command=lambda r=condition_row, d=condition_data: self._delete_condition(r, d))

    def _delete_condition(self, row, condition_data):
        """Xóa một condition row"""
        # Xóa row khỏi giao diện
        row.destroy()
    
        # Xóa condition khỏi danh sách
        if condition_data in self.break_conditions:
            self.break_conditions.remove(condition_data)
    
        # Cập nhật lại UI nếu cần
        self.param_frame.update_idletasks()
    
    def show_message(self, title, message):
        from tkinter import messagebox
        messagebox.showinfo(title, message)
        

