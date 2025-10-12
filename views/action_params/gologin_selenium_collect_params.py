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
        
        # ========== OUTPUT FOLDER SECTION ==========
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
            "<variable_name> to use variable value\n"
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
        
        # Delete cookies checkbox
        self.delete_cookies_var = tk.BooleanVar()
        if self.parameters:
            self.delete_cookies_var.set(self.parameters.get("delete_cookies", False))
        else:
            self.delete_cookies_var.set(False)
        
        delete_cb = tk.Checkbutton(
            options_frame,
            text="Delete cookies before warming up",
            variable=self.delete_cookies_var,
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        delete_cb.pack(anchor=tk.W, pady=2)
        

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
        
        # ========== COOKIES IMPORT SECTION ==========
        cookies_label = tk.Label(
            options_frame,
            text="Import Cookies (if not Delete cookies):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        cookies_label.pack(anchor=tk.W, pady=(10, 5))
        
        # Option 1: Browse cookies folder
        browse_cookies_label = tk.Label(
            options_frame,
            text="Option 1: Cookies Folder Path (will random pick 1 JSON file):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        )
        browse_cookies_label.pack(anchor=tk.W, pady=(0, 3))
        
        cookies_browse_frame = tk.Frame(options_frame, bg=cfg.LIGHT_BG_COLOR)
        cookies_browse_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.cookies_folder_var = tk.StringVar()
        if self.parameters:
            self.cookies_folder_var.set(self.parameters.get("cookies_folder", ""))
        
        cookies_entry = tk.Entry(
            cookies_browse_frame,
            textvariable=self.cookies_folder_var,
            font=("Segoe UI", 10)
        )
        cookies_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        def browse_cookies_folder():
            folder = filedialog.askdirectory(title="Select Cookies Folder")
            if folder:
                self.cookies_folder_var.set(folder)
        
        browse_cookies_button = ttk.Button(
            cookies_browse_frame,
            text="Browse",
            command=browse_cookies_folder
        )
        browse_cookies_button.pack(side=tk.LEFT)
        
        # Option 2: Variable name
        var_cookies_label = tk.Label(
            options_frame,
            text="Option 2: Variable name containing cookies folder path:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        )
        var_cookies_label.pack(anchor=tk.W, pady=(0, 3))
        
        self.cookies_folder_variable_var = tk.StringVar()
        if self.parameters:
            self.cookies_folder_variable_var.set(self.parameters.get("cookies_folder_variable", ""))
        
        cookies_var_entry = tk.Entry(
            options_frame,
            textvariable=self.cookies_folder_variable_var,
            font=("Segoe UI", 10)
        )
        cookies_var_entry.pack(fill=tk.X, pady=(0, 5))
        
        # Hint
        cookies_hint = tk.Label(
            options_frame,
            text="💡 Will random pick 1 JSON file from folder. Priority: Variable > Direct path",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666"
        )
        cookies_hint.pack(anchor=tk.W)
        
        
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
    
    def create_output_folder_section(self):
        """Output folder section - giống GoLogin Get Cookies"""
        folder_frame = tk.LabelFrame(
            self.parent_frame,
            text="Output Folder for Cookies",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        folder_frame.pack(fill=tk.X, pady=10)
        
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
            text="💡 File format: cookies_DD_MM_YYYY_HH_MM_SS.json. Priority: Variable > Direct path",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666"
        )
        hint.pack(anchor=tk.W)
    
    def get_parameters(self):
        """Collect parameters"""
        params = super().get_parameters()
        
        params["api_key_variable"] = self.api_key_var.get().strip()
        params["profile_ids"] = self.profile_ids_input.get("1.0", tk.END).strip()
        params["how_to_get"] = self.how_to_get_var.get()
        
        # Options
        params["refresh_fingerprint"] = self.refresh_fingerprint_var.get()
        params["delete_cookies"] = self.delete_cookies_var.get()
        params["cookies_folder"] = self.cookies_folder_var.get().strip()
        params["cookies_folder_variable"] = self.cookies_folder_variable_var.get().strip()
        
        # Websites params
        params["websites_file"] = self.websites_file_var.get().strip()
        params["websites_variable"] = self.websites_variable_var.get().strip()
        params["how_to_get_websites"] = self.how_to_get_websites_var.get()
        params["duration_minutes"] = self.duration_var.get().strip()
        
        # Output folder (for saving cookies only)
        params["folder_path"] = self.folder_path_var.get().strip()
        params["folder_variable"] = self.folder_variable_var.get().strip()
        params["headless"] = self.headless_var.get()
        
        params["enable_threading"] = self.enable_threading_var.get()  # ← THÊM
        params["max_workers"] = self.max_workers_var.get().strip()    # ← THÊM
        
        params["keywords_file"] = self.keywords_file_var.get().strip()
        params["keywords_variable"] = self.keywords_variable_var.get().strip()
        
        # Proxy params - THÊM 5 DÒNG NÀY
        params["proxy_mode_variable"] = self.proxy_mode_var.get().strip()
        params["proxy_host_variable"] = self.proxy_host_var.get().strip()
        params["proxy_port_variable"] = self.proxy_port_var.get().strip()
        params["proxy_username_variable"] = self.proxy_username_var.get().strip()
        params["proxy_password_variable"] = self.proxy_password_var.get().strip()
        
        return params
