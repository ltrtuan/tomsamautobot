# views/action_params/gologin_create_launch_params.py
import tkinter as tk
from tkinter import ttk
import config as cfg
from views.action_params.base_params import BaseActionParams

class GoLoginCreateLaunchParams(BaseActionParams):
    """UI for GoLogin Create and Launch Profile action"""
    
    def __init__(self, parent_frame, parameters=None):
        super().__init__(parent_frame, parameters)
    
    def create_params(self):
        """Create UI for GoLogin create and launch profile parameters"""
        self.clear_frame()
        
        # ========== API KEY SECTION ==========
        self.create_api_key_section()
        
        # ========== PROFILE SETTINGS ==========
        self.create_profile_settings_section()
        
        # ========== PROXY SETTINGS ==========
        self.create_proxy_section()
        
        # ========== OPTIONS ==========
        self.create_options_section()
        
        # ========== COMMON PARAMETERS (NO Mouse Control) ==========
        self.create_common_params(
            show_variable=True,
            show_random_time=True,
            show_repeat=True,
            show_random_skip=True,
            show_result_action=False
        )
        
        # ========== BREAK CONDITIONS ==========
        self.create_break_conditions()
        
        # ========== PROGRAM SELECTOR ==========
        select_program_button = self.create_program_selector()
        
        return {
            'select_program_button': select_program_button
        }
    
    def create_api_key_section(self):
        """Create API Key input section"""
        api_frame = tk.LabelFrame(
            self.parent_frame,
            text="GoLogin API Key",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        api_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            api_frame,
            text="API Token:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=5)
        
        self.variables["api_token_var"] = tk.StringVar(
            value=self.parameters.get("api_token", "")
        )
        
        api_entry = ttk.Entry(
            api_frame,
            textvariable=self.variables["api_token_var"],
            width=50,
            show="*"  # Hide API key
        )
        api_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        tk.Label(
            api_frame,
            text="(Get from Settings -> API in GoLogin dashboard)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="gray"
        ).pack(side=tk.LEFT, padx=5)
    
    def create_profile_settings_section(self):
        """Create profile settings section"""
        profile_frame = tk.LabelFrame(
            self.parent_frame,
            text="Profile Settings",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        profile_frame.pack(fill=tk.X, pady=10)
        
        # Profile Name
        name_frame = tk.Frame(profile_frame, bg=cfg.LIGHT_BG_COLOR)
        name_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            name_frame,
            text="Profile Name:",
            bg=cfg.LIGHT_BG_COLOR,
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5)
        
        self.variables["profile_name_var"] = tk.StringVar(
            value=self.parameters.get("profile_name", "Auto Profile")
        )
        
        ttk.Entry(
            name_frame,
            textvariable=self.variables["profile_name_var"],
            width=40
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # OS Selection
        os_frame = tk.Frame(profile_frame, bg=cfg.LIGHT_BG_COLOR)
        os_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            os_frame,
            text="Operating System:",
            bg=cfg.LIGHT_BG_COLOR,
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5)
        
        self.variables["os_var"] = tk.StringVar(
            value=self.parameters.get("os", "win")
        )
        
        os_combo = ttk.Combobox(
            os_frame,
            textvariable=self.variables["os_var"],
            values=["win", "mac", "lin"],
            state="readonly",
            width=15
        )
        os_combo.pack(side=tk.LEFT, padx=5)
        
        # Language
        lang_frame = tk.Frame(profile_frame, bg=cfg.LIGHT_BG_COLOR)
        lang_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            lang_frame,
            text="Language:",
            bg=cfg.LIGHT_BG_COLOR,
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5)
        
        self.variables["language_var"] = tk.StringVar(
            value=self.parameters.get("language", "en-US")
        )
        
        ttk.Entry(
            lang_frame,
            textvariable=self.variables["language_var"],
            width=15
        ).pack(side=tk.LEFT, padx=5)
    
    def create_proxy_section(self):
        """Create proxy settings section"""
        proxy_frame = tk.LabelFrame(
            self.parent_frame,
            text="Proxy Settings",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        proxy_frame.pack(fill=tk.X, pady=10)
        
        # Enable Proxy Checkbox
        enable_frame = tk.Frame(proxy_frame, bg=cfg.LIGHT_BG_COLOR)
        enable_frame.pack(fill=tk.X, pady=5)
        
        self.variables["enable_proxy_var"] = tk.BooleanVar(
            value=self.parameters.get("enable_proxy", True)
        )
        
        ttk.Checkbutton(
            enable_frame,
            text="Enable GoLogin Proxy",
            variable=self.variables["enable_proxy_var"]
        ).pack(side=tk.LEFT, padx=5)
        
        # Country Code
        country_frame = tk.Frame(proxy_frame, bg=cfg.LIGHT_BG_COLOR)
        country_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            country_frame,
            text="Country Code:",
            bg=cfg.LIGHT_BG_COLOR,
            width=15,
            anchor="w"
        ).pack(side=tk.LEFT, padx=5)
        
        self.variables["country_code_var"] = tk.StringVar(
            value=self.parameters.get("country_code", "US")
        )
        
        ttk.Entry(
            country_frame,
            textvariable=self.variables["country_code_var"],
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            country_frame,
            text="(US, UK, DE, FR, etc.)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="gray"
        ).pack(side=tk.LEFT, padx=5)
    
    def create_options_section(self):
        """Create additional options"""
        options_frame = tk.LabelFrame(
            self.parent_frame,
            text="Options",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        options_frame.pack(fill=tk.X, pady=10)
        
        # Auto Delete Profile
        self.variables["auto_delete_var"] = tk.BooleanVar(
            value=self.parameters.get("auto_delete", False)
        )
        
        ttk.Checkbutton(
            options_frame,
            text="Auto Delete Profile After Use",
            variable=self.variables["auto_delete_var"]
        ).pack(anchor=tk.W, pady=5)
        
        # Store Profile ID Variable
        store_frame = tk.Frame(options_frame, bg=cfg.LIGHT_BG_COLOR)
        store_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            store_frame,
            text="Store Profile ID in Variable:",
            bg=cfg.LIGHT_BG_COLOR
        ).pack(side=tk.LEFT, padx=5)
        
        self.variables["profile_id_var_name"] = tk.StringVar(
            value=self.parameters.get("profile_id_var_name", "gologin_profile_id")
        )
        
        ttk.Entry(
            store_frame,
            textvariable=self.variables["profile_id_var_name"],
            width=30
        ).pack(side=tk.LEFT, padx=5)
