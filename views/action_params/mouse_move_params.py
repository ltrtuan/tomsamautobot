# views/action_params/mouse_move_params.py
import tkinter as tk
from tkinter import ttk
import config as cfg
from views.action_params.base_params import BaseActionParams

class MouseMoveParams(BaseActionParams):
    def __init__(self, parent_frame, parameters=None):
        """
        Create UI for mouse movement parameters
        
        Args:
            parent_frame: The parent frame to place UI elements
            parameters: Dictionary containing parameters (if editing an action)
        """
        super().__init__(parent_frame, parameters)
        
    def create_params(self):
        """Create UI for mouse movement parameters"""
        # Clear any existing widgets
        self.clear_frame()
            
        # ========== PHẦN TỌA ĐỘ CHUỘT ==========
        self.create_coordinate_inputs()
        
        # ========== PHẦN THỜI GIAN DI CHUYỂN ==========
        self.create_duration_slider()
        
        # ========== PHẦN THAM SỐ CHUNG ==========
        self.create_common_params()
        
        # ========== PHẦN BREAK ACTION IF ==========
        self.create_break_conditions()
        
        # ========== PHẦN CHỌN CHƯƠNG TRÌNH ==========
        select_program_button = self.create_program_selector()        
       
        return {            
            'select_program_button': select_program_button,
            'select_area_button': self.select_area_button
        }
    
    def create_coordinate_inputs(self):
        """Create UI for mouse coordinates using the common region inputs"""
        self.select_area_button = None
        region_result = self.create_region_inputs(
            self.parent_frame, 
            title="Tọa độ di chuyển chuột",
            include_select_button=True
        )
    
        # Lấy các thành phần từ dictionary kết quả
        region_frame = region_result['region_frame']
        self.select_area_button = region_result['select_area_button']
    
        # Description
        description = ttk.Label(
            region_frame,
            text="Tọa độ là vị trí trên màn hình nơi chuột sẽ di chuyển đến",
            background=cfg.LIGHT_BG_COLOR
        )
        description.pack(pady=5)

    
    def create_duration_slider(self):
        """Create UI for movement duration slider"""
        duration_frame = tk.LabelFrame(self.parent_frame, text="Thời gian di chuyển", bg=cfg.LIGHT_BG_COLOR, pady=10, padx=10)
        duration_frame.pack(fill=tk.X, pady=10)
        
        # Duration slider
        slider_frame = tk.Frame(duration_frame, bg=cfg.LIGHT_BG_COLOR)
        slider_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(slider_frame, text="Thời gian (giây):", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
        
        self.variables["duration_var"] = tk.StringVar(value=self.parameters.get("duration", "0.1"))
        duration_scale = ttk.Scale(
            slider_frame,
            from_=0.0,
            to=5.0,
            orient=tk.HORIZONTAL,
            command=lambda v: self.variables["duration_var"].set(f"{float(v):.1f}")
        )
        duration_scale.set(float(self.variables["duration_var"].get()))
        duration_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        duration_value = ttk.Entry(
            slider_frame,
            textvariable=self.variables["duration_var"],
            width=5,
            validate="key",
            validatecommand=self.validate_float_cmd
        )
        duration_value.pack(side=tk.LEFT, padx=5)
        
        # Update scale when entry is changed
        def update_scale(*args):
            try:
                value = float(self.variables["duration_var"].get())
                if 0 <= value <= 5:
                    duration_scale.set(value)
            except ValueError:
                pass
        
        self.variables["duration_var"].trace_add("write", update_scale)
        
        # Description
        description = ttk.Label(
            duration_frame,
            text="Thời gian di chuyển ảnh hưởng đến tốc độ chuột. 0 = di chuyển ngay lập tức.",
            background=cfg.LIGHT_BG_COLOR
        )
        description.pack(pady=5)
