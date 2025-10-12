# views/action_params/get_new_proxy_params.py

import tkinter as tk
from tkinter import ttk, scrolledtext
import config as cfg
from views.action_params.base_params import BaseActionParams

class GetNewProxyParams(BaseActionParams):
    """UI for Get New Proxy action"""
    
    def __init__(self, parent_frame, parameters=None):
        super().__init__(parent_frame, parameters)
    
    def create_params(self):
        """Create UI parameters"""
        self.clear_frame()
        
        # ========== PROXY PROVIDER SECTION ==========
        self.create_provider_section()
        
        # ========== API CONFIGURATION SECTION ==========
        self.create_api_section()
        
        # ========== EXTRA PARAMS SECTION ==========
        self.create_extra_params_section()
        
        # ========== COMMON PARAMETERS (NO MOUSE CONTROL) ==========
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
    
    def create_provider_section(self):
        """Proxy Provider selection"""
        provider_frame = tk.LabelFrame(
            self.parent_frame,
            text="Proxy Provider",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        provider_frame.pack(fill=tk.X, pady=10)
        
        provider_row = tk.Frame(provider_frame, bg=cfg.LIGHT_BG_COLOR)
        provider_row.pack(fill=tk.X, pady=5)
        
        tk.Label(
            provider_row,
            text="Provider:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10),
            width=15,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.variables["provider_var"] = tk.StringVar()
        if self.parameters:
            self.variables["provider_var"].set(self.parameters.get("provider", "TMPROXY"))
        else:
            self.variables["provider_var"].set("TMPROXY")
        
        provider_dropdown = ttk.Combobox(
            provider_row,
            textvariable=self.variables["provider_var"],
            values=["TMPROXY", "PROXYRACK"],
            state="readonly",
            width=30
        )
        provider_dropdown.pack(side=tk.LEFT)
        
        # Display label mapping
        provider_labels = {
            "TMPROXY": "TMProxy",
            "PROXYRACK": "ProxyRack"
        }
        
        display_label = tk.Label(
            provider_row,
            text=f"({provider_labels.get(self.variables['provider_var'].get(), '')})",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9),
            fg="#666666"
        )
        display_label.pack(side=tk.LEFT, padx=(10, 0))
        
        def on_provider_change(event):
            selected = self.variables["provider_var"].get()
            display_label.config(text=f"({provider_labels.get(selected, '')})")
        
        provider_dropdown.bind("<<ComboboxSelected>>", on_provider_change)
    
    def create_api_section(self):
        """API Configuration section"""
        api_frame = tk.LabelFrame(
            self.parent_frame,
            text="API Configuration",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        api_frame.pack(fill=tk.X, pady=10)        
       
        
        # API Token
        token_row = tk.Frame(api_frame, bg=cfg.LIGHT_BG_COLOR)
        token_row.pack(fill=tk.X, pady=5)
        
        tk.Label(
            token_row,
            text="API Token:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10),
            width=15,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.variables["api_token_var"] = tk.StringVar()
        if self.parameters:
            self.variables["api_token_var"].set(self.parameters.get("api_token", ""))
        else:
            self.variables["api_token_var"].set("")
        
        api_token_entry = ttk.Entry(token_row, textvariable=self.variables["api_token_var"], width=50, show="*")
        api_token_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def create_extra_params_section(self):
        """Extra Parameters section"""
        extra_frame = tk.LabelFrame(
            self.parent_frame,
            text="Extra Parameters (Optional)",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        extra_frame.pack(fill=tk.X, pady=10)
        
        extra_label_row = tk.Frame(extra_frame, bg=cfg.LIGHT_BG_COLOR)
        extra_label_row.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(
            extra_label_row,
            text="Format: key1=value1,key2=value2",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9),
            fg="#666666"
        ).pack(side=tk.LEFT)
        
        self.extra_params_text = scrolledtext.ScrolledText(
            extra_frame,
            height=4,
            width=60,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.extra_params_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        if self.parameters:
            self.extra_params_text.insert("1.0", self.parameters.get("extra_params", ""))
    
    def get_parameters(self):
        """Collect parameters"""
        params = super().get_parameters()
        params["provider"] = self.variables["provider_var"].get()
        params["api_token"] = self.variables["api_token_var"].get().strip()
        params["extra_params"] = self.extra_params_text.get("1.0", tk.END).strip()
        return params

