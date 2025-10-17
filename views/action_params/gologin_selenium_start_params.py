# views/action_params/gologin_selenium_start_params.py

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import config as cfg
from views.action_params.base_params import BaseActionParams

class GoLoginSeleniumStartParams(BaseActionParams):
    """UI for GoLogin Selenium Start Profile action - Fast import cookies"""
    
    def __init__(self, parent_frame, parameters=None):
        super().__init__(parent_frame, parameters)
    
    def create_params(self):
        """Create UI parameters"""
        self.clear_frame()
        
        # ========== API KEY VARIABLE SECTION ==========
        self.create_api_key_variable_section()
        
        # ========== PROFILE IDs SECTION ==========
        self.create_profile_ids_section()
        
        # ========== HOW TO GET PROFILE SECTION ==========
        self.create_how_to_get_profile_section()
        
        # ========== OPTIONS SECTION (BỎ HEADLESS VÀ MULTI-THREADING) ==========
        self.create_options_section()
       
        
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
        """Profile IDs textarea"""
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
            "<VARIABLE_NAME> to use variable value\n"
            "Example: 68e485dd;<PROFILE_ID>;68e486ab"
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
    
    def create_how_to_get_profile_section(self):
        """How to get profile selection"""
        get_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        get_frame.pack(fill=tk.X, pady=5, padx=10)
        
        label = tk.Label(
            get_frame,
            text="How to get Profile:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(0, 5))
        
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
    
    def create_options_section(self):
        """Options checkboxes and cookies import - BỎ HEADLESS VÀ MULTI-THREADING"""
        options_frame = tk.LabelFrame(
            self.parent_frame,
            text="Profile Options",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        options_frame.pack(fill=tk.X, pady=10)
        
        # Refresh fingerprint checkbox
        self.refresh_fingerprint_var = tk.BooleanVar()
        if self.parameters:
            self.refresh_fingerprint_var.set(self.parameters.get("refresh_fingerprint", False))
        else:
            self.refresh_fingerprint_var.set(False)
        
        refresh_cb = tk.Checkbutton(
            options_frame,
            text="Refresh fingerprint before warming up",
            variable=self.refresh_fingerprint_var,
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        refresh_cb.pack(anchor=tk.W, pady=2)      
        
        
        # ========== PROXY CONFIGURATION SECTION ==========
        separator2 = ttk.Separator(options_frame, orient='horizontal')
        separator2.pack(fill=tk.X, pady=10)
        
        proxy_label = tk.Label(
            options_frame,
            text="Proxy Configuration (Optional - from Variables):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        proxy_label.pack(anchor=tk.W, pady=(5, 5))
        
        # Row 1: Mode Variable, Host Variable, Port Variable
        row1 = tk.Frame(options_frame, bg=cfg.LIGHT_BG_COLOR)
        row1.pack(fill=tk.X, pady=3)
        
        tk.Label(row1, text="Mode Var:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0,5))
        
        self.proxy_mode_var = tk.StringVar()
        if self.parameters:
            self.proxy_mode_var.set(self.parameters.get("proxy_mode_variable", ""))
        else:
            self.proxy_mode_var.set("")
        
        mode_entry = ttk.Entry(row1, textvariable=self.proxy_mode_var, width=15)
        mode_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(row1, text="Host Var:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(15,5))
        
        self.proxy_host_var = tk.StringVar()
        if self.parameters:
            self.proxy_host_var.set(self.parameters.get("proxy_host_variable", ""))
        else:
            self.proxy_host_var.set("")
        
        host_entry = ttk.Entry(row1, textvariable=self.proxy_host_var, width=15)
        host_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(row1, text="Port Var:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(15,5))
        
        self.proxy_port_var = tk.StringVar()
        if self.parameters:
            self.proxy_port_var.set(self.parameters.get("proxy_port_variable", ""))
        else:
            self.proxy_port_var.set("")
        
        port_entry = ttk.Entry(row1, textvariable=self.proxy_port_var, width=15)
        port_entry.pack(side=tk.LEFT, padx=5)
        
        # Row 2: Username Variable, Password Variable
        row2 = tk.Frame(options_frame, bg=cfg.LIGHT_BG_COLOR)
        row2.pack(fill=tk.X, pady=3)
        
        tk.Label(row2, text="User Var:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0,5))
        
        self.proxy_username_var = tk.StringVar()
        if self.parameters:
            self.proxy_username_var.set(self.parameters.get("proxy_username_variable", ""))
        else:
            self.proxy_username_var.set("")
        
        user_entry = ttk.Entry(row2, textvariable=self.proxy_username_var, width=20)
        user_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(row2, text="Pass Var:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(15,5))
        
        self.proxy_password_var = tk.StringVar()
        if self.parameters:
            self.proxy_password_var.set(self.parameters.get("proxy_password_variable", ""))
        else:
            self.proxy_password_var.set("")
        
        pass_entry = ttk.Entry(row2, textvariable=self.proxy_password_var, width=20)
        pass_entry.pack(side=tk.LEFT, padx=5)
        
        # Hint
        proxy_hint = tk.Label(
            options_frame,
            text="💡 Enter variable NAMES (e.g., proxy_mode, proxy_host). Fill all 5 to update proxy for ALL profiles before starting.",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666",
            wraplength=500,
            justify=tk.LEFT
        )
        proxy_hint.pack(anchor=tk.W, pady=(2,0))
    
    
    def get_parameters(self):
        """Collect parameters - COPY NGUYÊN NHƯNG BỎ duration_minutes, headless, enable_threading, max_workers"""
        params = super().get_parameters()
        
        params["api_key_variable"] = self.api_key_var.get().strip()
        params["profile_ids"] = self.profile_ids_input.get("1.0", tk.END).strip()
        params["how_to_get"] = self.how_to_get_var.get()
        
        # Options
        params["refresh_fingerprint"] = self.refresh_fingerprint_var.get()
        
        # Proxy params
        params["proxy_mode_variable"] = self.proxy_mode_var.get().strip()
        params["proxy_host_variable"] = self.proxy_host_var.get().strip()
        params["proxy_port_variable"] = self.proxy_port_var.get().strip()
        params["proxy_username_variable"] = self.proxy_username_var.get().strip()
        params["proxy_password_variable"] = self.proxy_password_var.get().strip()
        
        return params
