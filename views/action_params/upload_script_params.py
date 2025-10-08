# views/action_params/upload_script_params.py

import tkinter as tk
from tkinter import ttk, filedialog
import config as cfg
from views.action_params.base_params import BaseActionParams

class UploadScriptParams(BaseActionParams):
    """UI for Upload Script action"""
    
    def __init__(self, parent_frame, parameters=None):
        super().__init__(parent_frame, parameters)
    
    def create_params(self):
        """Create UI parameters"""
        self.clear_frame()
        
        # ========== SCRIPT PATH SELECTOR ==========
        script_frame = tk.LabelFrame(
            self.parent_frame,
            text="Script Source",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        script_frame.pack(fill=tk.X, pady=10)
        
        # Option 1: Browse file
        browse_label = tk.Label(
            script_frame,
            text="Option 1: Browse script file:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        browse_label.pack(anchor=tk.W, pady=(0, 5))
        
        browse_inner_frame = tk.Frame(script_frame, bg=cfg.LIGHT_BG_COLOR)
        browse_inner_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.script_path_var = tk.StringVar()
        if self.parameters:
            self.script_path_var.set(self.parameters.get("script_path", ""))
        
        self.variables["script_path_var"] = self.script_path_var
        
        script_entry = tk.Entry(
            browse_inner_frame,
            textvariable=self.script_path_var,
            font=("Segoe UI", 10),
            state="readonly"
        )
        script_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        def browse_script():
            filename = filedialog.askopenfilename(
                title="Select Script File",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                self.script_path_var.set(filename)
        
        browse_button = ttk.Button(
            browse_inner_frame,
            text="Browse",
            command=browse_script
        )
        browse_button.pack(side=tk.LEFT)
        
        # Option 2: Variable name
        var_label = tk.Label(
            script_frame,
            text="Option 2: Variable name containing script path:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        var_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.script_path_variable_var = tk.StringVar()
        if self.parameters:
            self.script_path_variable_var.set(self.parameters.get("script_path_variable", ""))
        
        self.variables["script_path_variable_var"] = self.script_path_variable_var
        
        var_entry = tk.Entry(
            script_frame,
            textvariable=self.script_path_variable_var,
            font=("Segoe UI", 10)
        )
        var_entry.pack(fill=tk.X, pady=(0, 5))
        
        # Hint
        hint = tk.Label(
            script_frame,
            text="💡 Script file must be valid JSON with action list format",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9),
            fg="#666666",
            justify=tk.LEFT
        )
        hint.pack(anchor=tk.W)
        
        # Note
        priority_note = tk.Label(
            script_frame,
            text="⚠️ Priority: Variable name will be used first if both are provided",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9, "italic"),
            fg="#FF6600",
            justify=tk.LEFT
        )
        priority_note.pack(anchor=tk.W, pady=(5, 0))
        
        # ========== COMMON PARAMS - CHỈ HIỂN THỊ NOTE ==========
        self.create_common_params(
            show_variable=False,      # Không cần
            show_random_time=False,   # Không cần
            show_repeat=False,        # Không cần
            show_random_skip=False    # Không cần
        )
        # Note sẽ được hiển thị tự động ở cuối
        
        return {}
