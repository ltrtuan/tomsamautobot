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
        
        # ========== PROFILE IDs SECTION ==========
        self.create_profile_ids_section()
        
        # ========== OPTIONS SECTION ==========  # ← THÊM DÒNG NÀY
        self.create_options_section()           # ← THÊM DÒNG NÀY
        
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

    def create_options_section(self):
        """Options checkboxes"""
        options_frame = tk.LabelFrame(
            self.parent_frame,
            text="Options",
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
            text="Refresh fingerprint before starting profile",
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
            text="Delete cookies before starting profile",
            variable=self.delete_cookies_var,
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        delete_cb.pack(anchor=tk.W, pady=2)
        
        # ========== COOKIES SECTION ==========
        cookies_label = tk.Label(
            options_frame,
            text="Cookies (nếu có giá trị và không check Delete cookies):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        cookies_label.pack(anchor=tk.W, pady=(10, 5))

        # Option 1: Browse cookies file
        from tkinter import filedialog

        browse_cookies_label = tk.Label(
            options_frame,
            text="Option 1: Cookies Folder Path (will random pick 1 file):",
            bg=cfg.LIGHT_BG_COLOR,
            font=(("Segoe UI", 9))
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
            folder = filedialog.askdirectory(
                title="Select Cookies Folder"
            )
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
            font=(("Segoe UI", 9))
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
            font=(("Segoe UI", 8)),
            fg="#666666"
        )
        cookies_hint.pack(anchor=tk.W)


    
    def get_parameters(self):
        """Collect parameters"""
        params = super().get_parameters()
        
        params["api_key_variable"] = self.api_key_var.get().strip()
        params["profile_ids"] = self.profile_ids_input.get("1.0", tk.END).strip()
        params["how_to_get"] = self.how_to_get_var.get()
        params["refresh_fingerprint"] = self.refresh_fingerprint_var.get()  # ← THÊM DÒNG NÀY
        params["delete_cookies"] = self.delete_cookies_var.get()            # ← THÊM DÒNG NÀY
        params["cookies_folder"] = self.cookies_folder_var.get().strip()
        params["cookies_folder_variable"] = self.cookies_folder_variable_var.get().strip()
        return params
