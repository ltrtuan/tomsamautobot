# views/action_params/gologin_selenium_collect_params.py

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import config as cfg
from views.action_params.base_params import BaseActionParams

class GoLoginSeleniumCollectParams(BaseActionParams):
    """UI for GoLogin Selenium Warm Up action"""
    
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
        
        # ========== OPTIONS SECTION ==========
        self.create_options_section()
        
        # ========== WEBSITES LIST SECTION ==========
        self.create_websites_section()
        
        # ========== HOW TO GET WEBSITES SECTION ==========
        self.create_how_to_get_websites_section()
        
        # ========== DURATION SECTION ==========
        self.create_duration_section()     
        
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
            " <var_name> to use variable value\n"
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
        """Options checkboxes and cookies import"""
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
        

        # ========== THÊM HEADLESS CHECKBOX ==========
        self.headless_var = tk.BooleanVar()
        if self.parameters:
            self.headless_var.set(self.parameters.get("headless", False))
        else:
            self.headless_var.set(False)
    
        headless_cb = tk.Checkbutton(
            options_frame,
            text="Run in Headless mode (no browser UI, faster but harder to debug)",
            variable=self.headless_var,
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        headless_cb.pack(anchor=tk.W, pady=2)
        
        # ========== THÊM MULTI-THREADING SECTION ==========
        separator = ttk.Separator(options_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)

        threading_label = tk.Label(
            options_frame,
            text="Multi-Threading (Parallel Warm Up):",
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
            text="Enable Multi-Threading (warm up multiple profiles simultaneously)",
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
            text="(Recommended: 3-5 for normal PC, 10+ for high-end PC with headless mode)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666"
        )
        workers_hint.pack(side=tk.LEFT, padx=5)       
        
        
        # ========== PROXY CONFIGURATION SECTION ==========
        separator_proxy = ttk.Separator(options_frame, orient='horizontal')
        separator_proxy.pack(fill=tk.X, pady=10)

        self.remove_proxy_var = tk.BooleanVar()
        if self.parameters:
            self.remove_proxy_var.set(self.parameters.get("remove_proxy", False))
        else:
            self.remove_proxy_var.set(False)

        remove_proxy_cb = tk.Checkbutton(
            options_frame,
            text="Remove proxy of profile before warming up",
            variable=self.remove_proxy_var,
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        remove_proxy_cb.pack(anchor=tk.W, pady=2)

        proxy_file_label = tk.Label(
            options_frame,
            text="Proxy File (Optional - TXT format type://host:port:user:pass per line):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        proxy_file_label.pack(anchor=tk.W, pady=(5, 2))

        proxy_browse_frame = tk.Frame(options_frame, bg=cfg.LIGHT_BG_COLOR)
        proxy_browse_frame.pack(fill=tk.X, pady=(0, 10))

        self.proxy_file_var = tk.StringVar()
        if self.parameters:
            self.proxy_file_var.set(self.parameters.get("proxy_file", ""))

        proxy_entry = tk.Entry(proxy_browse_frame, textvariable=self.proxy_file_var, font=("Segoe UI", 10))
        proxy_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        def browse_proxy_file():
            filename = filedialog.askopenfilename(
                title="Select Proxy TXT File",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                self.proxy_file_var.set(filename)

        browse_proxy_button = ttk.Button(proxy_browse_frame, text="Browse...", command=browse_proxy_file)
        browse_proxy_button.pack(side=tk.LEFT)

        proxy_file_hint = tk.Label(
            options_frame,
            text="File format example:\nhttp://1.2.3.4:8080:user:pass\nsocks5://5.6.7.8:1080:youruser:yourpass\nProxies will be assigned to profiles sequentially or randomly.",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666",
            wraplength=500,
            justify=tk.LEFT
        )
        proxy_file_hint.pack(anchor=tk.W)

    
    def create_websites_section(self):
        """Websites file browse and variable"""
        websites_frame = tk.LabelFrame(
            self.parent_frame,
            text="Websites List (TXT File)",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        websites_frame.pack(fill=tk.X, pady=10)
        
        # Option 1: Browse TXT file
        browse_label = tk.Label(
            websites_frame,
            text="Option 1: Browse TXT file (one URL per line):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        )
        browse_label.pack(anchor=tk.W, pady=(0, 3))
        
        browse_frame = tk.Frame(websites_frame, bg=cfg.LIGHT_BG_COLOR)
        browse_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.websites_file_var = tk.StringVar()
        if self.parameters:
            self.websites_file_var.set(self.parameters.get("websites_file", ""))
        
        file_entry = tk.Entry(
            browse_frame,
            textvariable=self.websites_file_var,
            font=("Segoe UI", 10)
        )
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        def browse_file():
            filename = filedialog.askopenfilename(
                title="Select Websites TXT File",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                self.websites_file_var.set(filename)
        
        browse_button = ttk.Button(
            browse_frame,
            text="Browse",
            command=browse_file
        )
        browse_button.pack(side=tk.LEFT)
        
        # Option 2: Variable name
        var_label = tk.Label(
            websites_frame,
            text="Option 2: Variable name containing TXT file path:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        )
        var_label.pack(anchor=tk.W, pady=(0, 3))
        
        self.websites_variable_var = tk.StringVar()
        if self.parameters:
            self.websites_variable_var.set(self.parameters.get("websites_variable", ""))
        
        var_entry = tk.Entry(
            websites_frame,
            textvariable=self.websites_variable_var,
            font=("Segoe UI", 10)
        )
        var_entry.pack(fill=tk.X, pady=(0, 5))
        
        # Hint
        hint = tk.Label(
            websites_frame,
            text="💡 TXT file format: one URL per line. Lines starting with # are comments. Priority: Variable > Direct path",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666",
            wraplength=500,
            justify=tk.LEFT
        )
        hint.pack(anchor=tk.W)
        
        # ========== THÊM KEYWORDS SECTION ==========
        separator = ttk.Separator(websites_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)
    
        keywords_label = tk.Label(
            websites_frame,
            text="Search Keywords for Google/YouTube:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        keywords_label.pack(anchor=tk.W, pady=(5, 5))
    
        # Option 1: Browse keywords TXT file
        keywords_browse_label = tk.Label(
            websites_frame,
            text="Option 1: Keywords TXT file (one keyword per line):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        )
        keywords_browse_label.pack(anchor=tk.W, pady=(0, 3))
    
        keywords_browse_frame = tk.Frame(websites_frame, bg=cfg.LIGHT_BG_COLOR)
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
            websites_frame,
            text="Option 2: Variable name containing keywords TXT file path:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        )
        keywords_var_label.pack(anchor=tk.W, pady=(0, 3))
    
        self.keywords_variable_var = tk.StringVar()
        if self.parameters:
            self.keywords_variable_var.set(self.parameters.get("keywords_variable", ""))
    
        keywords_var_entry = tk.Entry(
            websites_frame,
            textvariable=self.keywords_variable_var,
            font=("Segoe UI", 10)
        )
        keywords_var_entry.pack(fill=tk.X, pady=(0, 5))
    
        # Hint
        keywords_hint = tk.Label(
            websites_frame,
            text="💡 Keywords will be used when visiting google.com or youtube.com. Random keyword per visit. Priority: Variable > Direct path",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666",
            wraplength=500,
            justify=tk.LEFT
        )
        keywords_hint.pack(anchor=tk.W)
    
    def create_how_to_get_websites_section(self):
        """How to get websites selection"""
        get_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        get_frame.pack(fill=tk.X, pady=5, padx=10)
        
        label = tk.Label(
            get_frame,
            text="How to browse Websites:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.how_to_get_websites_var = tk.StringVar()
        if self.parameters:
            self.how_to_get_websites_var.set(self.parameters.get("how_to_get_websites", "Random"))
        else:
            self.how_to_get_websites_var.set("Random")
        
        combo = ttk.Combobox(
            get_frame,
            textvariable=self.how_to_get_websites_var,
            values=["Random", "Sequential by loop"],
            state="readonly",
            width=20
        )
        combo.pack(side=tk.LEFT, padx=5)
        
        hint = tk.Label(
            get_frame,
            text="(Random = pick random URL each time, Sequential = go through list in order)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666"
        )
        hint.pack(side=tk.LEFT, padx=5)
    
    def create_duration_section(self):
        """Duration in minutes"""
        duration_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        duration_frame.pack(fill=tk.X, pady=5, padx=10)
        
        label = tk.Label(
            duration_frame,
            text="Duration (minutes):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.duration_var = tk.StringVar()
        if self.parameters:
            self.duration_var.set(self.parameters.get("duration_minutes", "5"))
        else:
            self.duration_var.set("5")
        
        entry = ttk.Entry(
            duration_frame,
            textvariable=self.duration_var,
            width=10
        )
        entry.pack(side=tk.LEFT, padx=5)
        
        hint = tk.Label(
            duration_frame,
            text="(Total time to browse websites and warm up profile)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666"
        )
        hint.pack(side=tk.LEFT, padx=5)
    
       
    def get_parameters(self):
        """Collect parameters"""
        params = super().get_parameters()
        
        params["api_key_variable"] = self.api_key_var.get().strip()
        params["profile_ids"] = self.profile_ids_input.get("1.0", tk.END).strip()
        params["how_to_get"] = self.how_to_get_var.get()
        
        params["profile_count"] = self.profile_count_var.get().strip()
        params["profile_start_index"] = self.profile_start_index_var.get().strip()
        
        # Options
        params["refresh_fingerprint"] = self.refresh_fingerprint_var.get()       
        
        # Websites params
        params["websites_file"] = self.websites_file_var.get().strip()
        params["websites_variable"] = self.websites_variable_var.get().strip()
        params["how_to_get_websites"] = self.how_to_get_websites_var.get()
        params["duration_minutes"] = self.duration_var.get().strip()    
     
        params["headless"] = self.headless_var.get()
        
        params["enable_threading"] = self.enable_threading_var.get()  # ← THÊM
        params["max_workers"] = self.max_workers_var.get().strip()    # ← THÊM
        
        params["keywords_file"] = self.keywords_file_var.get().strip()
        params["keywords_variable"] = self.keywords_variable_var.get().strip()
        
        # Proxy file
        params["proxy_file"] = self.proxy_file_var.get().strip()
        params["remove_proxy"] = self.remove_proxy_var.get()
        
        return params
