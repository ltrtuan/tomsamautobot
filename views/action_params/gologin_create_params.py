# views/action_params/gologin_create_params.py
import tkinter as tk
from tkinter import ttk, scrolledtext
import config as cfg
from views.action_params.base_params import BaseActionParams

class GoLoginCreateParams(BaseActionParams):
    """UI for GoLogin Create Profile action"""
    
    def __init__(self, parent_frame, parameters=None):
        super().__init__(parent_frame, parameters)
    
    def create_params(self):
        """Create UI parameters"""
        self.clear_frame()
        
        # ========== API KEY VARIABLE SECTION ==========
        self.create_api_key_variable_section()
       
        
        # ========== PROFILE NAMES SECTION ==========
        self.create_profile_names_section()
        
        # ========== HOW TO GET SECTION ==========
        self.create_how_to_get_section()
        
        # ========== PROFILE SETTINGS ==========
        self.create_profile_settings_section()
        
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
        """API Key Variable name input - CHỈ NHẬP TÊN VARIABLE"""
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
        
        hint = tk.Label(
            api_frame,
            text="Example: GOLOGIN_API_KEY (set this variable before using action)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="gray"
        )
        hint.pack(anchor=tk.W, pady=(2, 0))
    
    def create_profile_names_section(self):
        """Profile names textarea - GIỐNG INPUT TEXT"""
        text_frame = tk.LabelFrame(
            self.parent_frame,
            text="Profile Names",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Label with instructions - GIỐNG INPUT TEXT
        label_text = (
            "Multiple profile names separated by ';'. Special formats:\n"
            "<variable_name>, [1-10:CN] random 1-10 chars/numbers/both, "
            "[1-10] random number 1-10"
        )
        
        label = tk.Label(
            text_frame,
            text=label_text,
            bg=cfg.LIGHT_BG_COLOR,
            justify=tk.LEFT,
            wraplength=400
        )
        label.pack(anchor=tk.W, pady=(0, 5))
        
        # ScrolledText widget - GIỐNG INPUT TEXT
        self.profile_names_input = scrolledtext.ScrolledText(
            text_frame,
            height=4,
            width=50,
            wrap=tk.WORD,
            font=("Segoe UI", 10)
        )
        self.profile_names_input.pack(fill=tk.BOTH, expand=True)
        
        # Load existing data
        if self.parameters:
            profile_names = self.parameters.get("profile_names", "")
            self.profile_names_input.insert("1.0", profile_names)
    
    def create_how_to_get_section(self):
        """How to get selection - GIỐNG INPUT TEXT"""
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
    
    def create_profile_settings_section(self):
        """Profile settings"""
        settings_frame = tk.LabelFrame(
            self.parent_frame,
            text="Profile Settings",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        settings_frame.pack(fill=tk.X, pady=10)
        
        # OS
        os_frame = tk.Frame(settings_frame, bg=cfg.LIGHT_BG_COLOR)
        os_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            os_frame,
            text="OS:",
            bg=cfg.LIGHT_BG_COLOR,
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5)
        
        self.os_var = tk.StringVar()
        if self.parameters:
            self.os_var.set(self.parameters.get("os", "win"))
        else:
            self.os_var.set("win")
        
        ttk.Combobox(
            os_frame,
            textvariable=self.os_var,
            values=["win", "mac", "lin"],
            state="readonly",
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Language
        lang_frame = tk.Frame(settings_frame, bg=cfg.LIGHT_BG_COLOR)
        lang_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            lang_frame,
            text="Language:",
            bg=cfg.LIGHT_BG_COLOR,
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5)
        
        self.language_var = tk.StringVar()
        if self.parameters:
            self.language_var.set(self.parameters.get("language", "en-US"))
        else:
            self.language_var.set("en-US")
        
        ttk.Entry(
            lang_frame,
            textvariable=self.language_var,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Enable Proxy
        self.enable_proxy_var = tk.BooleanVar()
        if self.parameters:
            self.enable_proxy_var.set(self.parameters.get("enable_proxy", False))
        else:
            self.enable_proxy_var.set(False)
        
        ttk.Checkbutton(
            settings_frame,
            text="Enable GoLogin Proxy",
            variable=self.enable_proxy_var
        ).pack(anchor=tk.W, pady=5)
        
        # Country Code
        country_frame = tk.Frame(settings_frame, bg=cfg.LIGHT_BG_COLOR)
        country_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            country_frame,
            text="Country Code:",
            bg=cfg.LIGHT_BG_COLOR,
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5)
        
        self.country_code_var = tk.StringVar()
        if self.parameters:
            self.country_code_var.set(self.parameters.get("country_code", "US"))
        else:
            self.country_code_var.set("US")
        
        ttk.Entry(
            country_frame,
            textvariable=self.country_code_var,
            width=10
        ).pack(side=tk.LEFT, padx=5)        
    

    
    def get_parameters(self):
        """Collect parameters - GIỐNG INPUT TEXT"""
        params = super().get_parameters()
        
        params["api_key_variable"] = self.api_key_var.get().strip()
        params["profile_names"] = self.profile_names_input.get("1.0", tk.END).strip()
        params["how_to_get"] = self.how_to_get_var.get()
        params["os"] = self.os_var.get()
        params["language"] = self.language_var.get()
        params["enable_proxy"] = self.enable_proxy_var.get()
        params["country_code"] = self.country_code_var.get()
        
        return params
