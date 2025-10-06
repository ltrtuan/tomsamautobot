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
     
        # ========== PHẦN MOUSE CONTROL ==========
        self.create_mouse_control()
        
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