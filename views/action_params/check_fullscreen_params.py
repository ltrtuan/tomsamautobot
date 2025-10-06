# views/action_params/check_fullscreen_params.py
import tkinter as tk
from tkinter import ttk
import config as cfg
from views.action_params.base_params import BaseActionParams

class CheckFullscreenParams(BaseActionParams):
    """UI for Check Fullscreen action parameters."""
    
    def __init__(self, parent_frame, parameters=None):
        """
        Create UI for check fullscreen parameters
        
        Args:
            parent_frame: The parent frame to place UI elements
            parameters: Dictionary containing parameters (if editing an action)
        """
        super().__init__(parent_frame, parameters)
    
    def create_params(self):
        """Create UI for check fullscreen parameters"""
        # Clear any existing widgets
        self.clear_frame()
        
        # ========== INFO LABEL ==========
        self.create_info_section()
        
        # ========== COMMON PARAMETERS ==========
        self.create_common_params()
        
        # ========== BREAK CONDITIONS ==========
        self.create_break_conditions()
        
        # ========== PROGRAM SELECTOR ==========
        select_program_button = self.create_program_selector()
        
        return {
            'select_program_button': select_program_button
        }
    
    def create_info_section(self):
        """Create info label explaining the action"""
        info_frame = tk.LabelFrame(
            self.parent_frame,
            text="Action Information",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        info_frame.pack(fill=tk.X, pady=10)
        
        info_text = (
            "Kiểm tra xem foreground window có đang ở chế độ fullscreen hay không.\n\n"
            "Kết quả:\n"
            "• True: Nếu window đang fullscreen (ví dụ: đang xem video fullscreen, game fullscreen)\n"
            "• False: Nếu window không fullscreen (desktop bình thường, windowed app)\n\n"
            "Lưu kết quả vào Variable ở phần tham số chung bên dưới."
        )
        
        label = tk.Label(
            info_frame,
            text=info_text,
            bg=cfg.LIGHT_BG_COLOR,
            justify=tk.LEFT,
            wraplength=500,
            font=("Segoe UI", 9)
        )
        label.pack(anchor=tk.W, padx=5, pady=5)
    
    def get_parameters(self):
        """Collect parameters"""
        params = super().get_parameters()
        # No additional params for this action
        return params
