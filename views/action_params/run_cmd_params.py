# views/action_params/run_cmd_params.py
import tkinter as tk
from tkinter import ttk, scrolledtext
import config as cfg
from views.action_params.base_params import BaseActionParams

class RunCmdParams(BaseActionParams):
    """UI for Run CMD action parameters."""
    
    def __init__(self, parent_frame, parameters=None):
        super().__init__(parent_frame, parameters)
    
    def create_params(self):
        """Create UI for run cmd parameters"""
        self.clear_frame()
        
        # ========== CMD COMMAND SECTION ==========
        self.create_cmd_section()
        
        # ========== COMMON PARAMETERS ==========
        self.create_common_params()
        
        # ========== BREAK CONDITIONS ==========
        self.create_break_conditions()
        
        # ========== PROGRAM SELECTOR ==========
        select_program_button = self.create_program_selector()
        
        return {
            'select_program_button': select_program_button
        }
    
    def create_cmd_section(self):
        """Create CMD command input section"""
        cmd_frame = tk.LabelFrame(
            self.parent_frame,
            text="CMD Command",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        cmd_frame.pack(fill=tk.X, pady=10)
        
        # Info label with examples
        info_text = (
            "Enter Windows Command Line command to execute.\n\n"
            "Examples:\n"
            "• shutdown /r /t 0  (Force restart computer immediately)\n"
            "• shutdown /s /t 0  (Shutdown computer immediately)\n"
            "• ipconfig  (Display network configuration)\n"
            "• tasklist  (List all running processes)\n"
            "• explorer C:\\  (Open C drive in Explorer)"
        )
        
        info_label = tk.Label(
            cmd_frame,
            text=info_text,
            bg=cfg.LIGHT_BG_COLOR,
            justify=tk.LEFT,
            font=("Segoe UI", 8),
            fg="gray"
        )
        info_label.pack(anchor=tk.W, pady=(0, 5))
        
        # CMD input
        tk.Label(
            cmd_frame,
            text="Command:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor=tk.W, pady=(5, 2))
        
        self.cmd_input = scrolledtext.ScrolledText(
            cmd_frame,
            height=4,
            width=60,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.cmd_input.pack(fill=tk.BOTH, expand=True, pady=5)
        
        if self.parameters:
            cmd_text = self.parameters.get("cmd_command", "")
            self.cmd_input.insert("1.0", cmd_text)
        
        # Warning label
        warning_label = tk.Label(
            cmd_frame,
            text="⚠️ Warning: Some commands require Administrator privileges!",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8, "bold"),
            fg="red"
        )
        warning_label.pack(anchor=tk.W, pady=(5, 0))
    
    def get_parameters(self):
        """Collect parameters"""
        params = super().get_parameters()
        
        # Get CMD command
        params["cmd_command"] = self.cmd_input.get("1.0", tk.END).strip()
        
        return params
