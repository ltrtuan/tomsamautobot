# views/action_params/gologin_selenium_collect_params.py

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import config as cfg
from views.action_params.base_params import BaseActionParams

class GoLoginSeleniumCollectParams(BaseActionParams):
    """UI for GoLogin Selenium Collect Profiles action"""
    
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
        
        # ========== WEBSITES LIST SECTION ==========
        self.create_websites_section()
        
        # ========== HOW TO GET WEBSITES SECTION ==========
        self.create_how_to_get_websites_section()
        
        # ========== DURATION SECTION ==========
        self.create_duration_section()
        
        # ========== SAVE OPTIONS SECTION ==========
        self.create_save_options_section()
        
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
            "Example: 68e485dd;<profile_id>;68e486ab"
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
    
    def create_save_options_section(self):
        """Save options checkboxes"""
        options_frame = tk.LabelFrame(
            self.parent_frame,
            text="Save Options",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        options_frame.pack(fill=tk.X, pady=10)
        
        # Save IndexDB
        self.save_indexdb_var = tk.BooleanVar()
        if self.parameters:
            self.save_indexdb_var.set(self.parameters.get("save_indexdb", False))
        else:
            self.save_indexdb_var.set(False)
        
        indexdb_cb = tk.Checkbutton(
            options_frame,
            text="Save IndexDB",
            variable=self.save_indexdb_var,
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        indexdb_cb.pack(anchor=tk.W, pady=2)
        
        # Save Cookies
        self.save_cookies_var = tk.BooleanVar()
        if self.parameters:
            self.save_cookies_var.set(self.parameters.get("save_cookies", True))
        else:
            self.save_cookies_var.set(True)
        
        cookies_cb = tk.Checkbutton(
            options_frame,
            text="Save Cookies",
            variable=self.save_cookies_var,
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        cookies_cb.pack(anchor=tk.W, pady=2)
        
        # Save localStorage
        self.save_localstorage_var = tk.BooleanVar()
        if self.parameters:
            self.save_localstorage_var.set(self.parameters.get("save_localstorage", False))
        else:
            self.save_localstorage_var.set(False)
        
        localstorage_cb = tk.Checkbutton(
            options_frame,
            text="Save localStorage",
            variable=self.save_localstorage_var,
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        localstorage_cb.pack(anchor=tk.W, pady=2)
        
        
        # Save Fingerprint Profile (CSV)
        self.save_fingerprint_var = tk.BooleanVar()
        if self.parameters:
            self.save_fingerprint_var.set(self.parameters.get("save_fingerprint", False))
        else:
            self.save_fingerprint_var.set(False)
        
        fingerprint_cb = tk.Checkbutton(
            options_frame,
            text="Save Fingerprint Profile (Export CSV via API)",
            variable=self.save_fingerprint_var,
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        fingerprint_cb.pack(anchor=tk.W, pady=2)
    
    def create_output_folder_section(self):
        """Output folder section with browse and variable options"""
        folder_frame = tk.LabelFrame(
            self.parent_frame,
            text="Output Folder",
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
            text="💡 Structure: FOLDER_PATH/DD_MM_YYYY/PROFILENAME_DD_MM_YYYY_HH_MM_SS/files. Priority: Variable > Direct path",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666",
            wraplength=500,
            justify=tk.LEFT
        )
        hint.pack(anchor=tk.W)
    
    def get_parameters(self):
        """Collect parameters"""
        params = super().get_parameters()
        
        params["api_key_variable"] = self.api_key_var.get().strip()
        params["profile_ids"] = self.profile_ids_input.get("1.0", tk.END).strip()
        params["how_to_get"] = self.how_to_get_var.get()
        
        # Websites params
        params["websites_file"] = self.websites_file_var.get().strip()
        params["websites_variable"] = self.websites_variable_var.get().strip()
        params["how_to_get_websites"] = self.how_to_get_websites_var.get()
        
        params["duration_minutes"] = self.duration_var.get().strip()
        
        # Save options
        params["save_indexdb"] = self.save_indexdb_var.get()
        params["save_cookies"] = self.save_cookies_var.get()
        params["save_localstorage"] = self.save_localstorage_var.get()
        params["save_fingerprint"] = self.save_fingerprint_var.get()
        
        # Output folder
        params["folder_path"] = self.folder_path_var.get().strip()
        params["folder_variable"] = self.folder_variable_var.get().strip()
        
        return params
