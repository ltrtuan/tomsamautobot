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
        
        # ========== ACTION TYPE SECTION ==========
        self.create_action_type_section()
        
        # ========== KEYWORDS SECTION ==========
        self.create_keywords_section()
        
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
        
    def create_keywords_section(self):
        """Keywords file browse section"""
        keywords_frame = tk.LabelFrame(
            self.parent_frame,
            text="Search Keywords (for YouTube/Google)",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        keywords_frame.pack(fill=tk.X, pady=10)

        # Option 1: Browse keywords TXT file
        keywords_browse_label = tk.Label(
            keywords_frame,
            text="Option 1: Keywords TXT file (one keyword per line):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        )
        keywords_browse_label.pack(anchor=tk.W, pady=(0, 3))

        keywords_browse_frame = tk.Frame(keywords_frame, bg=cfg.LIGHT_BG_COLOR)
        keywords_browse_frame.pack(fill=tk.X, pady=(0, 10))

        self.keywords_file_var = tk.StringVar()
        if self.parameters:
            self.keywords_file_var.set(self.parameters.get("keywords_file", ""))

        keywords_entry = tk.Entry(
            keywords_browse_frame,
            textvariable=self.keywords_file_var,
            font=("Segoe UI", 10)
        )
        keywords_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        def browse_keywords_file():
            filename = filedialog.askopenfilename(
                title="Select Keywords TXT File",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                self.keywords_file_var.set(filename)

        browse_keywords_button = ttk.Button(
            keywords_browse_frame,
            text="Browse",
            command=browse_keywords_file
        )
        browse_keywords_button.pack(side=tk.LEFT)

        # Option 2: Variable name
        keywords_var_label = tk.Label(
            keywords_frame,
            text="Option 2: Variable name containing keywords TXT file path:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        )
        keywords_var_label.pack(anchor=tk.W, pady=(0, 3))

        self.keywords_variable_var = tk.StringVar()
        if self.parameters:
            self.keywords_variable_var.set(self.parameters.get("keywords_variable", ""))

        keywords_var_entry = tk.Entry(
            keywords_frame,
            textvariable=self.keywords_variable_var,
            font=("Segoe UI", 10)
        )
        keywords_var_entry.pack(fill=tk.X, pady=(0, 5))

        # Hint
        keywords_hint = tk.Label(
            keywords_frame,
            text="💡 Keywords will be used when Action Type is YouTube or Google. Random keyword per search.",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666",
            wraplength=500,
            justify=tk.LEFT
        )
        keywords_hint.pack(anchor=tk.W)

    
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
        

        # ========== THÊM MULTI-THREADING SECTION ==========
        separator = ttk.Separator(options_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)

        threading_label = tk.Label(
            options_frame,
            text="Multi-Threading (Parallel Start):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        threading_label.pack(anchor=tk.W, pady=(5, 2))

        # Enable multi-threading checkbox
        self.enable_threading_var = tk.BooleanVar()
        if self.parameters:
            self.enable_threading_var.set(self.parameters.get("enable_threading", False))
        else:
            self.enable_threading_var.set(False)

        threading_cb = tk.Checkbutton(
            options_frame,
            text="Enable Multi-Threading (start multiple profiles simultaneously)",
            variable=self.enable_threading_var,
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        threading_cb.pack(anchor=tk.W, pady=2)

        # Max workers input
        workers_frame = tk.Frame(options_frame, bg=cfg.LIGHT_BG_COLOR)
        workers_frame.pack(fill=tk.X, pady=5)

        workers_label = tk.Label(
            workers_frame,
            text="Max parallel profiles:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        )
        workers_label.pack(side=tk.LEFT, padx=(20, 5))

        self.max_workers_var = tk.StringVar()
        if self.parameters:
            self.max_workers_var.set(self.parameters.get("max_workers", "3"))
        else:
            self.max_workers_var.set("3")

        workers_entry = ttk.Entry(
            workers_frame,
            textvariable=self.max_workers_var,
            width=5
        )
        workers_entry.pack(side=tk.LEFT, padx=5)

        workers_hint = tk.Label(
            workers_frame,
            text="(Recommended: 3-5 for normal PC)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666"
        )
        workers_hint.pack(side=tk.LEFT, padx=5)

        
    def create_action_type_section(self):
        """Action type selection: None, Youtube, Google"""
        action_frame = tk.LabelFrame(
            self.parent_frame,
            text="Action Type",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        action_frame.pack(fill=tk.X, pady=10)
    
        self.action_type_var = tk.StringVar()
        if self.parameters:
            self.action_type_var.set(self.parameters.get("action_type", "None"))
        else:
            self.action_type_var.set("None")
    
        radio_frame = tk.Frame(action_frame, bg=cfg.LIGHT_BG_COLOR)
        radio_frame.pack(anchor=tk.W)
    
        tk.Radiobutton(
            radio_frame,
            text="None (just start profile)",
            variable=self.action_type_var,
            value="None",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=10)
    
        tk.Radiobutton(
            radio_frame,
            text="YouTube Search",
            variable=self.action_type_var,
            value="Youtube",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=10)
    
        tk.Radiobutton(
            radio_frame,
            text="Google Search",
            variable=self.action_type_var,
            value="Google",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=10)


    def create_profile_ids_section(self):
        """Profile IDs textarea with range selection"""
        text_frame = tk.LabelFrame(
            self.parent_frame,
            text="Profile IDs",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # ========== THAY THẾ: 2 TEXTBOX INTEGER RANGE ==========
        range_frame = tk.Frame(text_frame, bg=cfg.LIGHT_BG_COLOR)
        range_frame.pack(fill=tk.X, pady=(0, 10))

        # How many profiles
        tk.Label(
            range_frame,
            text="How many profiles to use:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.profile_count_var = tk.StringVar()
        if self.parameters:
            self.profile_count_var.set(self.parameters.get("profile_count", "30"))
        else:
            self.profile_count_var.set("30")

        count_entry = ttk.Entry(
            range_frame,
            textvariable=self.profile_count_var,
            width=10
        )
        count_entry.pack(side=tk.LEFT, padx=5)

        # From profile index
        tk.Label(
            range_frame,
            text="From profile index:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=(15, 5))

        self.profile_start_index_var = tk.StringVar()
        if self.parameters:
            self.profile_start_index_var.set(self.parameters.get("profile_start_index", "0"))
        else:
            self.profile_start_index_var.set("0")

        start_entry = ttk.Entry(
            range_frame,
            textvariable=self.profile_start_index_var,
            width=10
        )
        start_entry.pack(side=tk.LEFT, padx=5)

        # Hint
        hint_label = tk.Label(
            text_frame,
            text="💡 Example: Count=30, Start=10 → Use profiles from index 10 to 39 (30 profiles total)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666",
            wraplength=500,
            justify=tk.LEFT
        )
        hint_label.pack(anchor=tk.W, pady=(0, 10))

        # ========== PROFILE IDS TEXTAREA (EXISTING) ==========
        label_text = (
            "OR manually enter Profile IDs separated by ';'. Special formats:\n"
            " <variable_name> to use variable value\n"
            "Example: 68e485dd;<profile_var>;68e486ab\n"
            "(Leave empty to use range above)"
        )
        label = tk.Label(
            text_frame,
            text=label_text,
            bg=cfg.LIGHT_BG_COLOR,
            justify=tk.LEFT,
            wraplength=500
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
        
        params["profile_count"] = self.profile_count_var.get().strip()
        params["profile_start_index"] = self.profile_start_index_var.get().strip()
        params["action_type"] = self.action_type_var.get()
        params["keywords_file"] = self.keywords_file_var.get().strip()
        params["keywords_variable"] = self.keywords_variable_var.get().strip()
        params["enable_threading"] = self.enable_threading_var.get()
        params["max_workers"] = self.max_workers_var.get().strip()
        
        return params
