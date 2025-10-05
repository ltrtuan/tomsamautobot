# views/action_params/read_txt_params.py

import tkinter as tk
from tkinter import ttk, filedialog
import config as cfg
from views.action_params.base_params import BaseActionParams

class ReadTxtParams(BaseActionParams):
    """UI for Read TXT File action parameters."""
    
    def __init__(self, parent_frame, parameters=None):
        super().__init__(parent_frame, parameters)
    
    def create_params(self):
        """Create UI for read txt file parameters"""
        self.clear_frame()
        
        # ========== FILE PATH VARIABLE SECTION (NEW!) ==========
        self.create_file_path_variable_section()
        
        # ========== FILE PATH SECTION ==========
        self.create_file_path_section()
        
        # ========== HOW TO GET SECTION ==========
        self.create_how_to_get_section()
        
        # ========== HOW TO INPUT SECTION ==========
        self.create_how_to_input_section()
        
        # ========== COMMON PARAMETERS ==========
        self.create_common_params()
        
        # ========== BREAK CONDITIONS ==========
        self.create_break_conditions()
        
        # ========== PROGRAM SELECTOR ==========
        select_program_button = self.create_program_selector()
        
        return {
            'browse_txt_button': self.browse_txt_button,
            'select_program_button': select_program_button
        }
    
    def create_file_path_variable_section(self):
        """Create file path variable input section (PRIORITY)"""
        var_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        var_frame.pack(fill=tk.X, pady=5)
        
        # Label
        label = tk.Label(
            var_frame,
            text="File Path Variable:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(10, 5))
        
        # StringVar for file path variable
        self.variables["file_path_variable_var"] = tk.StringVar()
        
        # Load existing value if editing
        if self.parameters:
            self.variables["file_path_variable_var"].set(
                self.parameters.get("file_path_variable", "")
            )
        
        # Entry for variable name
        var_entry = ttk.Entry(
            var_frame,
            textvariable=self.variables["file_path_variable_var"],
            width=30
        )
        var_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Help label
        help_label = tk.Label(
            var_frame,
            text="(e.g., FILE_PATH - has priority over Browse)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="gray"
        )
        help_label.pack(side=tk.LEFT, padx=5)
    
    def create_file_path_section(self):
        """Create file path selection section (FALLBACK)"""
        path_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        path_frame.pack(fill=tk.X, pady=5)
        
        # Label
        label = tk.Label(
            path_frame,
            text="TXT File (Browse):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(10, 5))
        
        # StringVar for file path
        self.variables["file_path_var"] = tk.StringVar()
        
        # Load existing value if editing
        if self.parameters:
            self.variables["file_path_var"].set(self.parameters.get("file_path", ""))
        
        # Entry for file path
        path_entry = ttk.Entry(
            path_frame,
            textvariable=self.variables["file_path_var"],
            width=40
        )
        path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Browse button
        self.browse_txt_button = ttk.Button(
            path_frame,
            text="Browse...",
            command=self.browse_file
        )
        self.browse_txt_button.pack(side=tk.RIGHT, padx=5)
    
    def create_how_to_get_section(self):
        """Create 'How to get' selection section"""
        get_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        get_frame.pack(fill=tk.X, pady=5)
        
        label = tk.Label(
            get_frame,
            text="How to get:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(10, 5))
        
        self.variables["how_to_get_var"] = tk.StringVar()
        
        if self.parameters:
            self.variables["how_to_get_var"].set(
                self.parameters.get("how_to_get", "Random")
            )
        else:
            self.variables["how_to_get_var"].set("Random")
        
        combo = ttk.Combobox(
            get_frame,
            textvariable=self.variables["how_to_get_var"],
            values=["Random", "Sequential by loop"],
            state="readonly",
            width=20
        )
        combo.pack(side=tk.LEFT, padx=5)
    
    def create_how_to_input_section(self):
        """Create 'How to input' selection section"""
        input_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        input_frame.pack(fill=tk.X, pady=5)
        
        label = tk.Label(
            input_frame,
            text="How to input:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(10, 5))
        
        self.variables["how_to_input_var"] = tk.StringVar()
        
        if self.parameters:
            self.variables["how_to_input_var"].set(
                self.parameters.get("how_to_input", "Random")
            )
        else:
            self.variables["how_to_input_var"].set("Random")
        
        combo = ttk.Combobox(
            input_frame,
            textvariable=self.variables["how_to_input_var"],
            values=["Random", "Copy & Paste", "Press Keyboard"],
            state="readonly",
            width=20
        )
        combo.pack(side=tk.LEFT, padx=5)
    
    def browse_file(self):
        """Open file browser dialog to select TXT file"""
        file_path = filedialog.askopenfilename(
            title="Select TXT File",
            filetypes=[
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self.variables["file_path_var"].set(file_path)
            print(f"[READ_TXT_PARAMS] Selected file: {file_path}")
    
    def get_parameters(self):
        """Collect parameters"""
        params = super().get_parameters()
        
        # Get file path variable (PRIORITY)
        params["file_path_variable"] = self.variables["file_path_variable_var"].get()
        
        # Get file path (FALLBACK)
        params["file_path"] = self.variables["file_path_var"].get()
        
        # Get how_to_get selection
        params["how_to_get"] = self.variables["how_to_get_var"].get()
        
        # Get how_to_input selection
        params["how_to_input"] = self.variables["how_to_input_var"].get()
        
        return params
