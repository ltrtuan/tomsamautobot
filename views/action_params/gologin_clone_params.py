# views/action_params/gologin_clone_params.py

import tkinter as tk
from tkinter import ttk
import config as cfg
from views.action_params.base_params import BaseActionParams

class GoLoginCloneParams(BaseActionParams):
    """UI for GoLogin Clone Profile action"""
    
    def __init__(self, parent_frame, parameters=None):
        super().__init__(parent_frame, parameters)
    
    def create_params(self):
        """Create UI parameters"""
        self.clear_frame()
        
        # ========== API KEY VARIABLE SECTION ==========
        self.create_api_key_variable_section()
        
        # ========== PROFILE ID SECTION ==========
        self.create_profile_id_section()
        
        # ========== COMMON PARAMETERS ==========
        self.create_common_params(
            show_variable=True,
            show_random_time=True,
            show_repeat=True,
            show_random_skip=True
        )
        
        # ========== BREAK CONDITIONS ==========
        self.create_break_conditions()
        
        # ========== PROGRAM SELECTOR ==========
        select_program_button = self.create_program_selector()
        
        return {'select_program_button': select_program_button}
    
    def create_api_key_variable_section(self):
        """API Key Variable name input"""
        api_frame = tk.LabelFrame(
            self.parent_frame,
            text="GoLogin API Key Variable",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        api_frame.pack(fill=tk.X, pady=10)
        
        label = tk.Label(
            api_frame,
            text="Variable name containing API token:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(anchor=tk.W, pady=(0, 5))
        
        self.api_key_var = tk.StringVar(
            value=self.parameters.get("api_key_variable", "GOLOGIN_API_KEY") if self.parameters else "GOLOGIN_API_KEY"
        )
        
        entry = ttk.Entry(
            api_frame,
            textvariable=self.api_key_var,
            width=30
        )
        entry.pack(anchor=tk.W, padx=5)
        
        # QUAN TRỌNG: Lưu vào self.variables
        self.variables["api_key_var"] = self.api_key_var
    
    def create_profile_id_section(self):
        """Profile ID input - CHỈ TEXT INPUT"""
        id_frame = tk.LabelFrame(
            self.parent_frame,
            text="Profile ID to Clone",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        id_frame.pack(fill=tk.X, pady=10)
        
        label = tk.Label(
            id_frame,
            text="Enter Profile ID to clone:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(anchor=tk.W, pady=(0, 5))
        
        self.profile_id_var = tk.StringVar(
            value=self.parameters.get("profile_id", "") if self.parameters else ""
        )
        
        entry = ttk.Entry(
            id_frame,
            textvariable=self.profile_id_var,
            width=50
        )
        entry.pack(fill=tk.X, padx=5)
        
        hint = tk.Label(
            id_frame,
            text="Example: 68f07bc77af729bd30aa79ec",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="gray"
        )
        hint.pack(anchor=tk.W, pady=(2, 0))
        
        note = tk.Label(
            id_frame,
            text="Note: Cloned profile will have default name from GoLogin API.\nUse 'Repeat' parameter to clone multiple times.",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9),
            fg="#FF6B00",
            justify=tk.LEFT
        )
        note.pack(anchor=tk.W, pady=(5, 0))
        
        # QUAN TRỌNG: Lưu vào self.variables
        self.variables["profile_id_var"] = self.profile_id_var
    
    def get_parameters(self):
        """Collect parameters"""
        params = super().get_parameters()
        
        params["api_key_variable"] = self.api_key_var.get().strip()
        params["profile_id"] = self.profile_id_var.get().strip()
        
        return params
