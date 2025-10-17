# views/action_params/gologin_selenium_stop_params.py

import tkinter as tk
from tkinter import ttk
import config as cfg
from views.action_params.base_params import BaseActionParams

class GoLoginSeleniumStopParams(BaseActionParams):
    """UI for GoLogin Selenium Stop action"""
    
    def __init__(self, parent_frame, parameters=None):
        super().__init__(parent_frame, parameters)
    
    def create_params(self):
        """Create UI parameters"""
        self.clear_frame()
        
        # ========== API KEY VARIABLE SECTION ==========
        self.create_api_key_variable_section()
        
        # ========== OUTPUT FOLDER SECTION ==========
        # BỎ Profile IDs section - vì dùng Global variable
        self.create_output_folder_section()
        
        # ========== COMMON PARAMETERS ==========
        self.create_common_params(
            show_variable=True,
            show_random_time=True,
            show_repeat=True,
            show_random_skip=True
        )
        
        # ========== BREAK CONDITIONS ==========
        self.create_break_conditions()
        
        # BỎ Program Selector - không cần interact với GoLogin UI
        
        return {}
    
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
        
        self.api_key_var = tk.StringVar()
        if self.parameters:
            self.api_key_var.set(self.parameters.get("api_key_variable", "GOLOGIN_API_KEY"))
        else:
            self.api_key_var.set("GOLOGIN_API_KEY")
        
        entry = ttk.Entry(
            api_frame,
            textvariable=self.api_key_var,
            width=30
        )
        entry.pack(anchor=tk.W, padx=5)
        
        # QUAN TRỌNG: Lưu vào self.variables
        self.variables["api_key_var"] = self.api_key_var
    
    def create_output_folder_section(self):
        """Output folder section for cookies"""
        folder_frame = tk.LabelFrame(
            self.parent_frame,
            text="Output Folder for Cookies",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        folder_frame.pack(fill=tk.X, pady=10)
        
        # Hint về Global Variables
        hint_global = tk.Label(
            folder_frame,
            text="💡 Profile ID will be read from Global Variable: GOLOGIN_PROFILE_ID",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8, "italic"),
            fg="#0066CC"
        )
        hint_global.pack(anchor=tk.W, pady=(0, 10))
        
        # Option 1: Browse folder
        browse_label = tk.Label(
            folder_frame,
            text="Option 1: Browse folder path:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        )
        browse_label.pack(anchor=tk.W, pady=(0, 3))
        
        browse_frame = tk.Frame(folder_frame, bg=cfg.LIGHT_BG_COLOR)
        browse_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.folder_path_var = tk.StringVar()
        if self.parameters:
            self.folder_path_var.set(self.parameters.get("folder_path", ""))
        
        folder_entry = tk.Entry(
            browse_frame,
            textvariable=self.folder_path_var,
            font=("Segoe UI", 10)
        )
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        def browse_folder():
            from tkinter import filedialog
            folder = filedialog.askdirectory(title="Select Output Folder")
            if folder:
                self.folder_path_var.set(folder)
        
        browse_button = ttk.Button(
            browse_frame,
            text="Browse",
            command=browse_folder
        )
        browse_button.pack(side=tk.LEFT)
        
        # Option 2: Variable name
        var_label = tk.Label(
            folder_frame,
            text="Option 2: Variable name containing folder path:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        )
        var_label.pack(anchor=tk.W, pady=(0, 3))
        
        self.folder_variable_var = tk.StringVar()
        if self.parameters:
            self.folder_variable_var.set(self.parameters.get("folder_variable", ""))
        
        folder_var_entry = tk.Entry(
            folder_frame,
            textvariable=self.folder_variable_var,
            font=("Segoe UI", 10)
        )
        folder_var_entry.pack(fill=tk.X, pady=(0, 5))
        
        # Hint
        hint = tk.Label(
            folder_frame,
            text="💡 File format: cookies_<profileID>_DD_MM_YYYY_HH_MM_SS.json. Priority: Variable > Direct path",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666"
        )
        hint.pack(anchor=tk.W)
        
        # QUAN TRỌNG: Lưu vào self.variables
        self.variables["folder_path_var"] = self.folder_path_var
        self.variables["folder_variable_var"] = self.folder_variable_var
    
    def get_parameters(self):
        """Collect parameters"""
        params = super().get_parameters()
        
        # API Key
        params["api_key_variable"] = self.api_key_var.get().strip()
        
        # Output folder (BỎ profile_ids)
        params["folder_path"] = self.folder_path_var.get().strip()
        params["folder_variable"] = self.folder_variable_var.get().strip()
        
        return params
