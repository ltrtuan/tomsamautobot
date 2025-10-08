# views/action_params/gologin_start_params.py
import tkinter as tk
from tkinter import ttk, scrolledtext
import config as cfg
from views.action_params.base_params import BaseActionParams

class GoLoginStartParams(BaseActionParams):
    """UI for GoLogin Start Profile action"""
    
    def __init__(self, parent_frame, parameters=None):
        super().__init__(parent_frame, parameters)
    
    def create_params(self):
        """Create UI parameters"""
        self.clear_frame()
        
        # ========== API KEY VARIABLE SECTION ==========
        self.create_api_key_variable_section()
        
        # GoLogin App Path
        self.create_gologin_app_path_section()
        
        # ========== PROFILE IDs SECTION ==========
        self.create_profile_ids_section()
        
        # ========== HOW TO GET SECTION ==========
        self.create_how_to_get_section()
        
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
    
    def create_profile_ids_section(self):
        """Profile IDs textarea - GIỐNG INPUT TEXT"""
        text_frame = tk.LabelFrame(
            self.parent_frame,
            text="Profile IDs",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        label_text = (
            "Multiple profile IDs separated by ';'. Special formats:\n"
            "<variable_name> to use variable value\n"
            "Example: 68e485dd; <gologin_profile_id>; 68e486ab"
        )
        
        label = tk.Label(
            text_frame,
            text=label_text,
            bg=cfg.LIGHT_BG_COLOR,
            justify=tk.LEFT,
            wraplength=400
        )
        label.pack(anchor=tk.W, pady=(0, 5))
        
        self.profile_ids_input = scrolledtext.ScrolledText(
            text_frame,
            height=4,
            width=50,
            wrap=tk.WORD,
            font=("Segoe UI", 10)
        )
        self.profile_ids_input.pack(fill=tk.BOTH, expand=True)
        
        if self.parameters:
            profile_ids = self.parameters.get("profile_ids", "")
            self.profile_ids_input.insert("1.0", profile_ids)
    
    def create_how_to_get_section(self):
        """How to get selection"""
        get_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        get_frame.pack(fill=tk.X, pady=5)
        
        label = tk.Label(
            get_frame,
            text="How to get:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(10, 5))
        
        self.how_to_get_var = tk.StringVar()
        if self.parameters:
            self.how_to_get_var.set(self.parameters.get("how_to_get", "Random"))
        else:
            self.how_to_get_var.set("Random")
        
        combo = ttk.Combobox(
            get_frame,
            textvariable=self.how_to_get_var,
            values=["Random", "Sequential by loop"],
            state="readonly",
            width=20
        )
        combo.pack(side=tk.LEFT, padx=5)
        
    def create_gologin_app_path_section(self):
        """GoLogin App Path Variable input"""
        frame = tk.LabelFrame(
            self.parent_frame,
            text="GoLogin App Path Variable",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        frame.pack(fill=tk.X, pady=10)
    
        # Variable name input
        label = tk.Label(
            frame,
            text="Variable name containing app path:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(anchor=tk.W)
    
        self.app_path_var = tk.StringVar()
        if self.parameters:
            self.app_path_var.set(self.parameters.get("gologin_app_path_variable", ""))
    
        entry = tk.Entry(
            frame,
            textvariable=self.app_path_var,
            font=("Segoe UI", 10),
            width=40
        )
        entry.pack(fill=tk.X, pady=(5, 0))
    
        # Hint
        hint = tk.Label(
            frame,
            text="💡 Example: GOLOGIN_APP_PATH (set variable value: C:\\Program Files\\GoLogin\\GoLogin.exe)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9),
            fg="#666666",
            justify=tk.LEFT
        )
        hint.pack(anchor=tk.W, pady=(5, 0))

    
    def get_parameters(self):
        """Collect parameters"""
        params = super().get_parameters()
        
        params["api_key_variable"] = self.api_key_var.get().strip()
        params["profile_ids"] = self.profile_ids_input.get("1.0", tk.END).strip()
        params["how_to_get"] = self.how_to_get_var.get()
        params["gologin_app_path_variable"] = self.app_path_var.get().strip()  # ← THÊM
        
        return params
