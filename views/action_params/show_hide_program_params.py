# views/action_params/show_hide_program_params.py
import tkinter as tk
from tkinter import ttk, scrolledtext
import config as cfg
from views.action_params.base_params import BaseActionParams

class ShowHideProgramParams(BaseActionParams):
    """UI for Show Hide Program action parameters."""
    
    def __init__(self, parent_frame, parameters=None):
        """
        Create UI for show hide program parameters
        
        Args:
            parent_frame: The parent frame to place UI elements
            parameters: Dictionary containing parameters (if editing an action)
        """
        super().__init__(parent_frame, parameters)
    
    def create_params(self):
        """Create UI for show hide program parameters"""
        # Clear any existing widgets
        self.clear_frame()
        
        # ========== PROGRAM PATH SECTION ========== ← THÊM MỚI
        self.create_program_path_section()
        
        # ========== PROGRAM ACTION SECTION ==========
        self.create_program_action_section()
        
        # ========== TITLE PROGRAM SECTION ==========
        self.create_title_program_section()
        
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
    
    def create_program_path_section(self):
        """Create program path browse section"""
        path_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        path_frame.pack(fill=tk.X, pady=5)
    
        # Label
        label = tk.Label(
            path_frame,
            text="Program path:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(10, 5))
    
        # StringVar for program path
        self.variables["program_path_var"] = tk.StringVar()
    
        # Load existing value if editing
        if self.parameters:
            self.variables["program_path_var"].set(
                self.parameters.get("program_path", "")
            )
    
        # Entry for program path
        path_entry = ttk.Entry(
            path_frame,
            textvariable=self.variables["program_path_var"],
            width=40
        )
        path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
        # Browse button
        browse_button = ttk.Button(
            path_frame,
            text="Browse .exe",
            command=self.browse_program
        )
        browse_button.pack(side=tk.RIGHT, padx=5)

    def browse_program(self):
        """Open file browser dialog to select EXE file"""
        from tkinter import filedialog
    
        file_path = filedialog.askopenfilename(
            title="Chọn file thực thi",
            filetypes=[
                ("Executable Files", "*.exe"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.variables["program_path_var"].set(file_path)
            print(f"[SHOW_HIDE_PROGRAM_PARAMS] Selected program: {file_path}")
    
        
    def create_program_action_section(self):
        """Create program action selectbox section"""
        action_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        action_frame.pack(fill=tk.X, pady=5)
        
        label = tk.Label(
            action_frame,
            text="Program action:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(10, 5))
        
        # StringVar for combobox
        self.variables["program_action_var"] = tk.StringVar()
        
        # Load existing value or default
        if self.parameters:
            self.variables["program_action_var"].set(
                self.parameters.get("program_action", "Check exist")
            )
        else:
            self.variables["program_action_var"].set("Check exist")
        
        # Combobox with all actions
        combo = ttk.Combobox(
            action_frame,
            textvariable=self.variables["program_action_var"],
            values=[
                "Check exist",
                "Show",
                "Hide",
                "Minimize",
                "Maximize",
                "Open",
                "Close"
            ],
            state="readonly",
            width=20
        )
        combo.pack(side=tk.LEFT, padx=5)
    
    def create_title_program_section(self):
        """Create title program textarea section with pattern support"""
        text_frame = tk.LabelFrame(
            self.parent_frame,
            text="Title Program",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Label with instructions
        label_text = (
            "Multiple titles separated by ';'. Special formats:\n"
            "<VAR_NAME>, [1-10:CN] random 1-10 chars/numbers/both, "
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
        self.title_program_input = scrolledtext.ScrolledText(
            text_frame,
            height=6,
            width=50,
            wrap=tk.WORD,
            font=("Segoe UI", 10)
        )
        self.title_program_input.pack(fill=tk.BOTH, expand=True)
        
        # Load existing data if editing
        if self.parameters:
            title_program = self.parameters.get("title_program", "")
            self.title_program_input.insert("1.0", title_program)
    
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
        self.variables["how_to_get_var"] = tk.StringVar()
        
        # Load existing value or default
        if self.parameters:
            self.variables["how_to_get_var"].set(
                self.parameters.get("how_to_get", "Random")
            )
        else:
            self.variables["how_to_get_var"].set("Random")
        
        # Combobox
        combo = ttk.Combobox(
            get_frame,
            textvariable=self.variables["how_to_get_var"],
            values=["Random", "Sequential by loop"],
            state="readonly",
            width=20
        )
        combo.pack(side=tk.LEFT, padx=5)
    
    def get_parameters(self):
        """Collect parameters"""
        params = super().get_parameters()
        
        params["program_path"] = self.variables["program_path_var"].get()
        
        # Get program action
        params["program_action"] = self.variables["program_action_var"].get()
        
        # Get title program text
        params["title_program"] = self.title_program_input.get("1.0", tk.END).strip()
        
        # Get how_to_get selection
        params["how_to_get"] = self.variables["how_to_get_var"].get()
        
        return params
