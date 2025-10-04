from views.action_params.base_params import BaseActionParams
import tkinter as tk
from tkinter import ttk
import config as cfg

class ForParams(BaseActionParams):
    def __init__(self, parent_frame, parameters=None):
        """
        Create UI for For loop parameters
        Args:
            parent_frame: The parent frame to place UI elements
            parameters: Dictionary containing parameters (if editing an action)
        """
        super().__init__(parent_frame, parameters)

    def create_params(self):
        """Create UI for For loop parameters"""
        # Clear any existing widgets
        self.clear_frame()

        # ========== PHẦN THAM SỐ VÒNG LẶP ==========
        loop_frame = tk.LabelFrame(self.parent_frame, text="Tham số vòng lặp", bg=cfg.LIGHT_BG_COLOR, pady=10, padx=10)
        loop_frame.pack(fill=tk.X, pady=10)

        # Repeat Loop
        repeat_frame = tk.Frame(loop_frame, bg=cfg.LIGHT_BG_COLOR)
        repeat_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(repeat_frame, text="Repeat Loop:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
        self.variables["repeat_loop_var"] = tk.StringVar(value=str(self.parameters.get("repeat_loop", "1")))
        repeat_entry = ttk.Entry(
            repeat_frame, 
            textvariable=self.variables["repeat_loop_var"], 
            width=10,
            validate="key",
            validatecommand=self.validate_int_cmd
        )
        repeat_entry.pack(side=tk.LEFT, padx=5)
        
        # Thêm label mô tả
        tk.Label(
            repeat_frame,
            text="(Số lần chạy cơ bản của vòng lặp)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8, "italic"),
            fg="#555555"
        ).pack(side=tk.LEFT, padx=5)

        # Random Repeat Loop
        random_repeat_frame = tk.Frame(loop_frame, bg=cfg.LIGHT_BG_COLOR)
        random_repeat_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(random_repeat_frame, text="Random Repeat Loop:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
        self.variables["random_repeat_loop_var"] = tk.StringVar(value=str(self.parameters.get("random_repeat_loop", "0")))
        random_repeat_entry = ttk.Entry(
            random_repeat_frame, 
            textvariable=self.variables["random_repeat_loop_var"], 
            width=10,
            validate="key",
            validatecommand=self.validate_int_cmd
        )
        random_repeat_entry.pack(side=tk.LEFT, padx=5)
        
        # Thêm label mô tả
        tk.Label(
            random_repeat_frame,
            text="(Random từ 0 đến X sẽ cộng thêm vào Repeat Loop. Nếu = 0 thì không random)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8, "italic"),
            fg="#555555"
        ).pack(side=tk.LEFT, padx=5)

        # ========== PHẦN BREAK ACTION IF ==========
        self.create_break_conditions()

        return {}

    @property
    def validate_int_cmd(self):
        """Validation command for integer numbers >= 0"""
        return (self.parent_frame.register(self.validate_non_negative_integer), '%P')

    @staticmethod
    def validate_non_negative_integer(P):
        """Validate if input is a non-negative integer"""
        if P == "":
            return True
        try:
            val = int(P)
            return val >= 0  # Chỉ cho phép số >= 0
        except ValueError:
            return False

    def get_parameters(self):
        """Get all parameters as a dictionary"""
        params = super().get_parameters()  # Lấy break_conditions từ BaseActionParams
        
        # Thêm các tham số riêng của For loop
        repeat_loop_str = self.variables["repeat_loop_var"].get()
        random_repeat_loop_str = self.variables["random_repeat_loop_var"].get()
        
        # Validate và set giá trị mặc định nếu cần
        try:
            params["repeat_loop"] = int(repeat_loop_str) if repeat_loop_str.isdigit() and int(repeat_loop_str) > 0 else 1
        except:
            params["repeat_loop"] = 1
            
        try:
            params["random_repeat_loop"] = int(random_repeat_loop_str) if random_repeat_loop_str.isdigit() else 0
        except:
            params["random_repeat_loop"] = 0
        
        return params
