import tkinter as tk
from tkinter import ttk, scrolledtext
import config as cfg
from views.action_params.base_params import BaseActionParams

class InputTextParams(BaseActionParams):
    """UI for Input Text action parameters."""
    
    def __init__(self, parent_frame, parameters=None):
        """
        Create UI for input text parameters
        Args:
            parent_frame: The parent frame to place UI elements
            parameters: Dictionary containing parameters (if editing an action)
        """
        super().__init__(parent_frame, parameters)
    
    def create_params(self):
        """Create UI for input text parameters"""
        # Clear any existing widgets
        self.clear_frame()
        
        # ========== TEXT INPUT SECTION ==========
        self.create_text_input_section()
        
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
            'select_program_button': select_program_button
        }
    
    def create_text_input_section(self):
        """Create text input textarea section"""
        text_frame = tk.LabelFrame(
            self.parent_frame,
            text="Text Input",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Label with instructions
        label_text = (
            "Multiple texts separated by ';'. Special formats:\n"
            "<VARIABLE_NAME>, [1-10:CN] random 1-10 chars/numbers/both, "
            "[1-10] random number 1-10"
        )
        label = tk.Label(
            text_frame,
            text=label_text,
            bg=cfg.LIGHT_BG_COLOR,            
            justify=tk.LEFT,
            wraplength=400
        )
        label.pack(anchor=tk.W, pady=(0, 5))
        
        # ScrolledText widget for multi-line input
        self.text_input = scrolledtext.ScrolledText(
            text_frame,
            height=6,
            width=50,
            wrap=tk.WORD,
            font=("Segoe UI", 10)
        )
        self.text_input.pack(fill=tk.BOTH, expand=True)
        
        # Load existing data if editing
        if self.parameters:
            text_list = self.parameters.get("text_list", "")
            self.text_input.insert("1.0", text_list)
    
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
        
        # StringVar for combobox
        self.how_to_get_var = tk.StringVar()
        
        # Load existing value or default
        if self.parameters:
            self.how_to_get_var.set(self.parameters.get("how_to_get", "Random"))
        else:
            self.how_to_get_var.set("Random")
        
        # Combobox
        combo = ttk.Combobox(
            get_frame,
            textvariable=self.how_to_get_var,
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
        
        # StringVar for combobox
        self.how_to_input_var = tk.StringVar()
        
        # Load existing value or default
        if self.parameters:
            self.how_to_input_var.set(self.parameters.get("how_to_input", "Random"))
        else:
            self.how_to_input_var.set("Random")
        
        # Combobox
        combo = ttk.Combobox(
            input_frame,
            textvariable=self.how_to_input_var,
            values=["Random", "Copy & Paste", "Press Keyboard"],
            state="readonly",
            width=20
        )
        combo.pack(side=tk.LEFT, padx=5)
    
    def get_parameters(self):
        """Collect parameters (follows ImageSearch pattern)"""
        params = super().get_parameters()
        
        # Get text input
        params["text_list"] = self.text_input.get("1.0", tk.END).strip()
        
        # Get how_to_get selection
        params["how_to_get"] = self.how_to_get_var.get()
        
        # Get how_to_input selection
        params["how_to_input"] = self.how_to_input_var.get()
        
        return params
