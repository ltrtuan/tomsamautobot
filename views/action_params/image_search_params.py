# views/action_params/image_search_params.py
import tkinter as tk
from tkinter import ttk
import config as cfg
from views.action_params.base_params import BaseActionParams

class ImageSearchParams(BaseActionParams):
    def __init__(self, parent_frame, parameters=None):
        """
        Create UI for image search parameters
        
        Args:
            parent_frame: The parent frame to place UI elements
            parameters: Dictionary containing parameters (if editing an action)
        """
        super().__init__(parent_frame, parameters)
        self.select_area_button = None
        
    def create_params(self):
        """Create UI for image search parameters"""
        # Clear any existing widgets
        self.clear_frame()
            
        # ========== PHẦN THÔNG TIN HÌNH ẢNH ==========
        # Frame chứa đường dẫn hình ảnh
        path_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        path_frame.pack(fill=tk.X, pady=(5, 5))
        
        # Label và textbox đường dẫn
        tk.Label(path_frame, text="Đường dẫn hình ảnh:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=(0, 5))
        self.variables["image_path_var"] = tk.StringVar(value=self.parameters.get("image_path", ""))
        path_entry = ttk.Entry(path_frame, textvariable=self.variables["image_path_var"], width=40)
        path_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        # Nút duyệt hình ảnh
        browse_button = ttk.Button(path_frame, text="Duyệt...")
        browse_button.pack(side=tk.RIGHT, padx=5)
        
        # Tạo frame mới cho nút chụp màn hình
        screenshot_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        screenshot_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Nút chụp màn hình trong frame mới
        screenshot_button = ttk.Button(screenshot_frame, text="Chụp Màn Hình")
        screenshot_button.pack(side=tk.LEFT, padx=5)
        
        # ========== PHẦN KHU VỰC TÌM KIẾM ==========
        self.create_region_section()
        
        # ========== PHẦN ĐỘ CHÍNH XÁC ==========
        self.create_accuracy_section()
        
        # ========== PHẦN THAM SỐ CHUNG ==========
        self.create_common_params()
        
        # ========== PHẦN BREAK ACTION IF ==========
        self.create_break_conditions()
        
        # ========== PHẦN CHỌN CHƯƠNG TRÌNH ==========
        select_program_button = self.create_program_selector()
        
        return {
            'browse_button': browse_button,
            'select_area_button': self.select_area_button,
            'select_program_button': select_program_button,
            'screenshot_button': screenshot_button
        }
    
    def create_region_section(self):
        """Create UI for search region selection"""
        region_frame = tk.LabelFrame(self.parent_frame, text="Khu vực tìm kiếm", bg=cfg.LIGHT_BG_COLOR, pady=10, padx=10)
        region_frame.pack(fill=tk.X, pady=10)
        
        # Coordinates inputs
        coords_frame = tk.Frame(region_frame, bg=cfg.LIGHT_BG_COLOR)
        coords_frame.pack(fill=tk.X, pady=5)
        
        # X coordinate
        tk.Label(coords_frame, text="X:", bg=cfg.LIGHT_BG_COLOR).grid(row=0, column=0, padx=5, pady=2)
        self.variables["x_var"] = tk.StringVar(value=self.parameters.get("x", "0"))
        ttk.Entry(
            coords_frame, 
            textvariable=self.variables["x_var"], 
            width=6,
            validate="key",
            validatecommand=self.validate_int_cmd
        ).grid(row=0, column=1, padx=5, pady=2)
        
        # Y coordinate
        tk.Label(coords_frame, text="Y:", bg=cfg.LIGHT_BG_COLOR).grid(row=0, column=2, padx=5, pady=2)
        self.variables["y_var"] = tk.StringVar(value=self.parameters.get("y", "0"))
        ttk.Entry(
            coords_frame, 
            textvariable=self.variables["y_var"], 
            width=6,
            validate="key",
            validatecommand=self.validate_int_cmd
        ).grid(row=0, column=3, padx=5, pady=2)
        
        # Width
        tk.Label(coords_frame, text="Width:", bg=cfg.LIGHT_BG_COLOR).grid(row=1, column=0, padx=5, pady=2)
        self.variables["width_var"] = tk.StringVar(value=self.parameters.get("width", "0"))
        ttk.Entry(
            coords_frame, 
            textvariable=self.variables["width_var"], 
            width=6,
            validate="key",
            validatecommand=self.validate_int_cmd
        ).grid(row=1, column=1, padx=5, pady=2)
        
        # Height
        tk.Label(coords_frame, text="Height:", bg=cfg.LIGHT_BG_COLOR).grid(row=1, column=2, padx=5, pady=2)
        self.variables["height_var"] = tk.StringVar(value=self.parameters.get("height", "0"))
        ttk.Entry(
            coords_frame, 
            textvariable=self.variables["height_var"], 
            width=6,
            validate="key",
            validatecommand=self.validate_int_cmd
        ).grid(row=1, column=3, padx=5, pady=2)
        
        # Nút chọn khu vực màn hình
        self.select_area_button = ttk.Button(region_frame, text="Chọn khu vực màn hình")
        self.select_area_button.pack(pady=10)
    
    def create_accuracy_section(self):
        """Create UI for accuracy settings"""
        accuracy_frame = tk.LabelFrame(self.parent_frame, text="Độ chính xác", bg=cfg.LIGHT_BG_COLOR, pady=10, padx=10)
        accuracy_frame.pack(fill=tk.X, pady=10)
        
        # Accuracy slider
        slider_frame = tk.Frame(accuracy_frame, bg=cfg.LIGHT_BG_COLOR)
        slider_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(slider_frame, text="Độ chính xác (%):", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
        
        self.variables["accuracy_var"] = tk.StringVar(value=self.parameters.get("accuracy", "80"))
        accuracy_scale = ttk.Scale(
            slider_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=lambda v: self.variables["accuracy_var"].set(str(int(float(v))))
        )
        accuracy_scale.set(int(self.variables["accuracy_var"].get()))
        accuracy_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        accuracy_value = ttk.Entry(
            slider_frame,
            textvariable=self.variables["accuracy_var"],
            width=5,
            validate="key",
            validatecommand=self.validate_int_cmd
        )
        accuracy_value.pack(side=tk.LEFT, padx=5)
        
        # Update scale when entry is changed
        def update_scale(*args):
            try:
                value = int(self.variables["accuracy_var"].get())
                if 0 <= value <= 100:
                    accuracy_scale.set(value)
            except ValueError:
                pass
        
        self.variables["accuracy_var"].trace_add("write", update_scale)
