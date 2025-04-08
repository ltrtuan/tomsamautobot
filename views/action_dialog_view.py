import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import config as cfg

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
    
        action_types = ["Tìm Hình Ảnh", "Di Chuyển Chuột"]
        self.action_type_combo = ttk.Combobox(
            type_frame, 
            textvariable=self.action_type_var, 
            values=action_types, 
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
    
        # Center dialog and make it modal
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_visibility()
    
        # Set position relative to parent
        window_width = 500  # Tăng kích thước một chút
        window_height = 500
    
        # Calculate center position
        x = (parent.winfo_rootx() + (parent.winfo_width() / 2)) - (window_width / 2)
        y = (parent.winfo_rooty() + (parent.winfo_height() / 2)) - (window_height / 2)
    
        # Set window size and position
        self.geometry(f"{window_width}x{window_height}+{int(x)}+{int(y)}")

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
        
    def create_image_search_params(self, parameters=None):
        # Xóa các widget cũ
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        
        # Khởi tạo giá trị mặc định
        if parameters is None:
            parameters = {}
    
        # Tạo validation function cho các trường nhập số
        def validate_number(P):
            if P == "":
                return True
            try:
                float(P)
                return True
            except ValueError:
                return False
            
        def validate_integer(P):
            if P == "":
                return True
            try:
                int(P)
                return True
            except ValueError:
                return False
    
        # Đăng ký hàm validation
        validate_float_cmd = (self.register(validate_number), '%P')
        validate_int_cmd = (self.register(validate_integer), '%P')
    
        # ========== PHẦN THÔNG TIN HÌNH ẢNH ==========
        # Frame chứa đường dẫn hình ảnh
        path_frame = tk.Frame(self.param_frame, bg=cfg.LIGHT_BG_COLOR)
        path_frame.pack(fill=tk.X, pady=(5, 10))
    
        # Label và textbox đường dẫn
        tk.Label(path_frame, text="Đường dẫn hình ảnh:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=(0, 5))
        self.image_path_var = tk.StringVar(value=parameters.get("path", ""))
        path_entry = ttk.Entry(path_frame, textvariable=self.image_path_var, width=40)
        path_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
    
        # Nút duyệt hình ảnh
        browse_button = ttk.Button(path_frame, text="Duyệt...")
        browse_button.pack(side=tk.RIGHT, padx=5)
    
        # ========== PHẦN KHU VỰC TÌM KIẾM ==========
        region_frame = tk.LabelFrame(self.param_frame, text="Khu vực tìm kiếm", bg=cfg.LIGHT_BG_COLOR, pady=10, padx=10)
        region_frame.pack(fill=tk.X, pady=10)
    
        # Frame chứa tọa độ X, Y
        coord_frame = tk.Frame(region_frame, bg=cfg.LIGHT_BG_COLOR)
        coord_frame.pack(fill=tk.X, pady=5)
    
        # Tọa độ X
        tk.Label(coord_frame, text="X:", bg=cfg.LIGHT_BG_COLOR).grid(row=0, column=0, padx=5, sticky=tk.W)
        self.x_var = tk.StringVar(value=parameters.get("x", "0"))
        ttk.Entry(coord_frame, textvariable=self.x_var, width=8, validate="key", 
                  validatecommand=validate_float_cmd).grid(row=0, column=1, padx=5)
    
        # Tọa độ Y
        tk.Label(coord_frame, text="Y:", bg=cfg.LIGHT_BG_COLOR).grid(row=0, column=2, padx=5, sticky=tk.W)
        self.y_var = tk.StringVar(value=parameters.get("y", "0"))
        ttk.Entry(coord_frame, textvariable=self.y_var, width=8, validate="key", 
                  validatecommand=validate_float_cmd).grid(row=0, column=3, padx=5)
    
        # Frame chứa Width, Height
        size_frame = tk.Frame(region_frame, bg=cfg.LIGHT_BG_COLOR)
        size_frame.pack(fill=tk.X, pady=5)
    
        # Width
        tk.Label(size_frame, text="Width:", bg=cfg.LIGHT_BG_COLOR).grid(row=0, column=0, padx=5, sticky=tk.W)
        self.width_var = tk.StringVar(value=parameters.get("width", "0"))
        ttk.Entry(size_frame, textvariable=self.width_var, width=8, validate="key", 
                  validatecommand=validate_float_cmd).grid(row=0, column=1, padx=5)
    
        # Height
        tk.Label(size_frame, text="Height:", bg=cfg.LIGHT_BG_COLOR).grid(row=0, column=2, padx=5, sticky=tk.W)
        self.height_var = tk.StringVar(value=parameters.get("height", "0"))
        ttk.Entry(size_frame, textvariable=self.height_var, width=8, validate="key", 
                  validatecommand=validate_float_cmd).grid(row=0, column=3, padx=5)
    
        # Nút chọn khu vực màn hình
        select_area_button = ttk.Button(region_frame, text="Chọn khu vực màn hình")
        select_area_button.pack(pady=10)
    
        # ========== PHẦN ĐỘ CHÍNH XÁC ==========
        accuracy_frame = tk.Frame(self.param_frame, bg=cfg.LIGHT_BG_COLOR)
        accuracy_frame.pack(fill=tk.X, pady=10)
    
        # Label độ chính xác
        tk.Label(accuracy_frame, text="Độ chính xác (%):", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
    
        # Giá trị và thanh trượt độ chính xác
        self.accuracy_var = tk.StringVar(value=parameters.get("accuracy", "80"))
        accuracy_label = tk.Label(accuracy_frame, textvariable=self.accuracy_var, width=3, bg=cfg.LIGHT_BG_COLOR)
    
        def update_accuracy(value):
            self.accuracy_var.set(str(int(float(value))))
    
        accuracy_scale = ttk.Scale(
            accuracy_frame, 
            from_=0, 
            to=100, 
            command=update_accuracy,
            value=int(float(self.accuracy_var.get()))
        )
        accuracy_scale.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        accuracy_label.pack(side=tk.LEFT, padx=5)
    
        # ========== PHẦN THAM SỐ CHUNG ==========
        common_frame = tk.LabelFrame(self.param_frame, text="Tham số chung", bg=cfg.LIGHT_BG_COLOR, pady=10, padx=10)
        common_frame.pack(fill=tk.X, pady=10)
    
        # Random Time
        random_time_frame = tk.Frame(common_frame, bg=cfg.LIGHT_BG_COLOR)
        random_time_frame.pack(fill=tk.X, pady=5)
    
        tk.Label(random_time_frame, text="Random Time:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
        self.random_time_var = tk.StringVar(value=parameters.get("random_time", "0"))
        ttk.Entry(
            random_time_frame, 
            textvariable=self.random_time_var, 
            width=6,
            validate="key", 
            validatecommand=validate_int_cmd
        ).pack(side=tk.LEFT, padx=5)
    
        # Double Click
        click_frame = tk.Frame(common_frame, bg=cfg.LIGHT_BG_COLOR)
        click_frame.pack(fill=tk.X, pady=5)
    
        self.double_click_var = tk.BooleanVar(value=parameters.get("double_click", False))
        ttk.Checkbutton(
            click_frame, 
            text="Double Click", 
            variable=self.double_click_var
        ).pack(side=tk.LEFT, padx=5)
    
        # Random Skip Action
        skip_frame = tk.Frame(common_frame, bg=cfg.LIGHT_BG_COLOR)
        skip_frame.pack(fill=tk.X, pady=5)
    
        tk.Label(skip_frame, text="Random Skip Action:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
        self.random_skip_var = tk.StringVar(value=parameters.get("random_skip", "0"))
        ttk.Entry(
            skip_frame, 
            textvariable=self.random_skip_var, 
            width=6,
            validate="key", 
            validatecommand=validate_int_cmd
        ).pack(side=tk.LEFT, padx=5)
    
        # Variable
        variable_frame = tk.Frame(common_frame, bg=cfg.LIGHT_BG_COLOR)
        variable_frame.pack(fill=tk.X, pady=5)
    
        tk.Label(variable_frame, text="Variable:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
        self.variable_var = tk.StringVar(value=parameters.get("variable", ""))
        ttk.Entry(variable_frame, textvariable=self.variable_var, width=15).pack(side=tk.LEFT, padx=5)
    
        # ========== PHẦN BREAK ACTION IF ==========
        self.break_frame = tk.LabelFrame(self.param_frame, text="Break action If", bg=cfg.LIGHT_BG_COLOR, pady=10, padx=10)
        self.break_frame.pack(fill=tk.X, pady=10)
    
        # List để lưu các condition
        self.break_conditions = []
    
        # Thêm condition đầu tiên hoặc nạp từ parameters
        if "break_conditions" in parameters and parameters["break_conditions"]:
            for condition in parameters["break_conditions"]:
                self.add_break_condition(condition)
        else:
            self.add_break_condition()
    
        # Nút thêm condition
        add_condition_button = ttk.Button(
            self.break_frame, 
            text="Add If", 
            command=self.add_break_condition
        )
        add_condition_button.pack(pady=5)
    
        # ========== PHẦN CHỌN CHƯƠNG TRÌNH ==========
        program_frame = tk.Frame(self.param_frame, bg=cfg.LIGHT_BG_COLOR)
        program_frame.pack(fill=tk.X, pady=10)
    
        tk.Label(program_frame, text="Select Program to Action:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
    
        self.program_var = tk.StringVar(value=parameters.get("program", ""))
        program_entry = ttk.Entry(program_frame, textvariable=self.program_var, width=30)
        program_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
        select_program_button = ttk.Button(program_frame, text="Browse...")
        select_program_button.pack(side=tk.RIGHT, padx=5)
    
        return browse_button, select_area_button, select_program_button

    def create_mouse_move_params(self, parameters=None):
        # Clear previous parameter widgets
        for widget in self.param_frame.winfo_children():
            widget.destroy()
            
        # X coordinate
        x_label = tk.Label(
            self.param_frame, 
            text="Tọa độ X:", 
            font=cfg.DEFAULT_FONT, 
            bg=cfg.LIGHT_BG_COLOR
        )
        x_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.x_coord_var = tk.StringVar(value="0")
        if parameters and "x" in parameters:
            self.x_coord_var.set(parameters["x"])
            
        x_entry = ttk.Entry(
            self.param_frame, 
            textvariable=self.x_coord_var, 
            width=8,
            font=cfg.DEFAULT_FONT
        )
        x_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 10))
        
        # Y coordinate
        y_label = tk.Label(
            self.param_frame, 
            text="Tọa độ Y:", 
            font=cfg.DEFAULT_FONT, 
            bg=cfg.LIGHT_BG_COLOR
        )
        y_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        self.y_coord_var = tk.StringVar(value="0")
        if parameters and "y" in parameters:
            self.y_coord_var.set(parameters["y"])
            
        y_entry = ttk.Entry(
            self.param_frame, 
            textvariable=self.y_coord_var, 
            width=8,
            font=cfg.DEFAULT_FONT
        )
        y_entry.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
        
        # Duration
        duration_label = tk.Label(
            self.param_frame, 
            text="Thời gian (giây):", 
            font=cfg.DEFAULT_FONT, 
            bg=cfg.LIGHT_BG_COLOR
        )
        duration_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        
        self.duration_var = tk.StringVar(value="0.2")
        if parameters and "duration" in parameters:
            self.duration_var.set(parameters["duration"])
            
        duration_entry = ttk.Entry(
            self.param_frame, 
            textvariable=self.duration_var, 
            width=8,
            font=cfg.DEFAULT_FONT
        )
        duration_entry.grid(row=2, column=1, sticky=tk.W, pady=(0, 10))
        
        # Duration slider
        duration_frame = tk.Frame(self.param_frame, bg=cfg.LIGHT_BG_COLOR)
        duration_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=(5, 0))
        
        # Slider labels
        slider_label_frame = tk.Frame(duration_frame, bg=cfg.LIGHT_BG_COLOR)
        slider_label_frame.pack(fill=tk.X)
        
        tk.Label(
            slider_label_frame, 
            text="Nhanh", 
            font=("Segoe UI", 8), 
            bg=cfg.LIGHT_BG_COLOR
        ).pack(side=tk.LEFT)
        
        tk.Label(
            slider_label_frame, 
            text="Chậm", 
            font=("Segoe UI", 8), 
            bg=cfg.LIGHT_BG_COLOR
        ).pack(side=tk.RIGHT)
        
        # Slider
        duration_slider = ttk.Scale(
            duration_frame, 
            from_=0, 
            to=2, 
            orient="horizontal",
            value=float(self.duration_var.get()), 
            length=300,
            command=self._update_duration
        )
        duration_slider.pack(fill=tk.X, pady=5)
        
    def _update_duration(self, value):
        self.duration_var.set(f"{float(value):.1f}")
        
    def browse_image(self):
        filename = filedialog.askopenfilename(
            title="Chọn một hình ảnh",
            filetypes=(("Tệp hình ảnh", "*.png;*.jpg;*.jpeg;*.bmp"), ("Tất cả tệp", "*.*"))
        )
        if filename:
            self.image_path_var.set(filename)
            
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
