# views/action_params/read_csv_params.py

import tkinter as tk
from tkinter import ttk, filedialog
import config as cfg
from views.action_params.base_params import BaseActionParams

class ReadCsvParams(BaseActionParams):
    """UI for Read CSV/Excel File action parameters."""
    
    def __init__(self, parent_frame, parameters=None):
        super().__init__(parent_frame, parameters)
    
    def create_params(self):
        """Create UI for read CSV/Excel parameters"""
        self.clear_frame()
        
        # ========== FILE PATH VARIABLE SECTION (NEW!) ==========
        self.create_file_path_variable_section()
        
        # ========== FILE PATH SECTION ==========
        self.create_file_path_section()
        
        # ========== SKIP HEADER CHECKBOX ==========
        self.create_skip_header_section()
        
        # ========== HOW TO GET SECTION ==========
        self.create_how_to_get_section()
        
        # ========== COMMON PARAMETERS ==========
        self.create_common_params()
        
        # ========== BREAK CONDITIONS ==========
        self.create_break_conditions()
        
        # ========== PROGRAM SELECTOR ==========
        select_program_button = self.create_program_selector()
        
        return {
            'select_program_button': select_program_button
        }
    
    def create_file_path_variable_section(self):
        """Create file path variable input section (PRIORITY)"""
        var_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        var_frame.pack(fill=tk.X, pady=5)
        
        label = tk.Label(
            var_frame,
            text="File Path Variable:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(10, 5))
        
        self.variables["file_path_variable_var"] = tk.StringVar()
        
        if self.parameters:
            self.variables["file_path_variable_var"].set(
                self.parameters.get("file_path_variable", "")
            )
        
        var_entry = ttk.Entry(
            var_frame,
            textvariable=self.variables["file_path_variable_var"],
            width=30
        )
        var_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        help_label = tk.Label(
            var_frame,
            text="(e.g., CSV_FILE - has priority over Browse)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="gray"
        )
        help_label.pack(side=tk.LEFT, padx=5)
    
    def create_file_path_section(self):
        """Create file path selection section (FALLBACK)"""
        path_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        path_frame.pack(fill=tk.X, pady=5)
        
        label = tk.Label(
            path_frame,
            text="CSV/Excel File (Browse):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(10, 5))
        
        self.variables["file_path_var"] = tk.StringVar()
        if self.parameters:
            self.variables["file_path_var"].set(self.parameters.get("file_path", ""))
        
        path_entry = ttk.Entry(
            path_frame,
            textvariable=self.variables["file_path_var"],
            width=40
        )
        path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        browse_button = ttk.Button(
            path_frame,
            text="Browse...",
            command=self.browse_file
        )
        browse_button.pack(side=tk.RIGHT, padx=5)
    
    def create_skip_header_section(self):
        """Create skip header checkbox section"""
        header_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        header_frame.pack(fill=tk.X, pady=5)
        
        self.variables["skip_header_var"] = tk.BooleanVar()
        if self.parameters:
            self.variables["skip_header_var"].set(
                self.parameters.get("skip_header", False)
            )
        
        skip_header_cb = tk.Checkbutton(
            header_frame,
            text="Skip Header Row (Bỏ qua dòng tiêu đề)",
            variable=self.variables["skip_header_var"],
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        skip_header_cb.pack(side=tk.LEFT, padx=(10, 5))
    
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
    
    def browse_file(self):
        """Open file browser dialog to select CSV/Excel file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV or Excel File",
            filetypes=[
                ("CSV Files", "*.csv"),
                ("Excel Files", "*.xlsx *.xls"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self.variables["file_path_var"].set(file_path)
            print(f"[READ_CSV_PARAMS] Selected file: {file_path}")
    
    def get_parameters(self):
        """Collect parameters"""
        params = super().get_parameters()
        
        # Get file path variable (PRIORITY)
        params["file_path_variable"] = self.variables["file_path_variable_var"].get()
        
        # Get file path (FALLBACK)
        params["file_path"] = self.variables["file_path_var"].get()
        
        # Get skip_header checkbox
        params["skip_header"] = self.variables["skip_header_var"].get()
        
        # Get how_to_get selection
        params["how_to_get"] = self.variables["how_to_get_var"].get()
        
        return params
