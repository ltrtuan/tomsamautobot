# views/action_params/write_csv_params.py

import tkinter as tk
from tkinter import ttk, filedialog
import config as cfg
from views.action_params.base_params import BaseActionParams

class WriteCsvParams(BaseActionParams):
    """UI for Write CSV File action parameters."""
    
    def __init__(self, parent_frame, parameters=None):
        super().__init__(parent_frame, parameters)
    
    def create_params(self):
        """Create UI for write csv file parameters"""
        self.clear_frame()
        
        # ========== FILE PATH VARIABLE SECTION ==========
        self.create_file_path_variable_section()
        
        # ========== FILE PATH SECTION ==========
        self.create_file_path_section()
        
        # ========== CONTENT TO WRITE SECTION ==========
        self.create_content_section()
        
        # ========== COMMON PARAMETERS ==========
        self.create_common_params()
        
        # ========== BREAK CONDITIONS ==========
        self.create_break_conditions()
        
        # ========== PROGRAM SELECTOR ==========
        select_program_button = self.create_program_selector()
        
        return {
            'browse_csv_button': self.browse_csv_button,
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
        
        self.browse_csv_button = ttk.Button(
            path_frame,
            text="Browse...",
            command=self.browse_file
        )
        self.browse_csv_button.pack(side=tk.RIGHT, padx=5)
    
    def create_content_section(self):
        """Create content to write section"""
        content_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        content_frame.pack(fill=tk.BOTH, pady=5, expand=True)
        
        label = tk.Label(
            content_frame,
            text="Content to Write (separate by ; - each becomes a column):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(anchor=tk.W, padx=(10, 5), pady=(5, 0))
        
        # Text widget for multi-line content
        text_frame = tk.Frame(content_frame, bg=cfg.LIGHT_BG_COLOR)
        text_frame.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        
        self.content_text = tk.Text(
            text_frame,
            height=5,
            width=50,
            font=("Segoe UI", 10)
        )
        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame, command=self.content_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.content_text.config(yscrollcommand=scrollbar.set)
        
        # Load existing content if editing
        if self.parameters:
            self.content_text.insert("1.0", self.parameters.get("content", ""))
    
    def browse_file(self):
        """Open file browser dialog to select CSV/Excel file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV/Excel File",
            filetypes=[
                ("CSV Files", "*.csv"),
                ("Excel Files", "*.xlsx"),
                ("Excel Files (old)", "*.xls"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self.variables["file_path_var"].set(file_path)
            print(f"[WRITE_CSV_PARAMS] Selected file: {file_path}")
    
    def get_parameters(self):
        """Collect parameters"""
        params = super().get_parameters()
        
        # Get file path variable (PRIORITY)
        params["file_path_variable"] = self.variables["file_path_variable_var"].get()
        
        # Get file path (FALLBACK)
        params["file_path"] = self.variables["file_path_var"].get()
        
        # Get content to write
        params["content"] = self.content_text.get("1.0", tk.END).strip()
        
        return params
