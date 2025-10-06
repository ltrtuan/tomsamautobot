# views/action_params/text_search_params.py
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import config as cfg
from views.action_params.base_params import BaseActionParams

class TextSearchParams(BaseActionParams):
    """UI for Text Search action parameters."""
    
    def __init__(self, parent_frame, parameters=None):
        super().__init__(parent_frame, parameters)
        self.select_area_button = None
    
    def create_params(self):
        """Create UI for text search parameters"""
        self.clear_frame()
        
        # ========== FILE PATH SECTION ==========
        self.create_file_path_section()
        
        # ========== TEXT CONTENT SECTION ==========
        self.create_text_content_section()
        
        # ========== HOW TO GET SECTION ==========
        self.create_how_to_get_section()
        
        # ========== SEARCH REGION SECTION ==========
        self.create_region_section()
        
        # ========== MOUSE CONTROL ==========
        self.create_mouse_control()
        
        # ========== COMMON PARAMETERS ==========
        self.create_common_params()
        
        # ========== BREAK CONDITIONS ==========
        self.create_break_conditions()
        
        # ========== PROGRAM SELECTOR ==========
        select_program_button = self.create_program_selector()
        
        return {
            'select_area_button': self.select_area_button,
            'select_program_button': select_program_button
        }
    
    def create_file_path_section(self):
        """Create file path selection section"""
        path_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        path_frame.pack(fill=tk.X, pady=5)
        
        # Label
        label = tk.Label(
            path_frame,
            text="Đường dẫn file txt:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(10, 5))
        
        # StringVar for file path
        self.variables["text_file_path_var"] = tk.StringVar()
        
        # Load existing value if editing
        if self.parameters:
            self.variables["text_file_path_var"].set(
                self.parameters.get("text_file_path", "")
            )
        
        # Entry for file path
        path_entry = ttk.Entry(
            path_frame,
            textvariable=self.variables["text_file_path_var"],
            width=40
        )
        path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Browse button
        browse_button = ttk.Button(
            path_frame,
            text="Duyệt...",
            command=self.browse_file
        )
        browse_button.pack(side=tk.RIGHT, padx=5)
    
    def create_text_content_section(self):
        """Create text content textarea section"""
        text_frame = tk.LabelFrame(
            self.parent_frame,
            text="Text cần search (ưu tiên file txt nếu có)",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Label with instructions
        label_text = (
            "Multiple texts separated by ';'. Special formats:\n"
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
        self.text_content_widget = scrolledtext.ScrolledText(
            text_frame,
            height=6,
            width=50,
            wrap=tk.WORD,
            font=("Segoe UI", 10)
        )
        self.text_content_widget.pack(fill=tk.BOTH, expand=True)
        
        # Load existing data if editing
        if self.parameters:
            text_content = self.parameters.get("text_content", "")
            self.text_content_widget.insert("1.0", text_content)
    
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
                self.parameters.get("how_to_get", "All")
            )
        else:
            self.variables["how_to_get_var"].set("All")
        
        # Combobox
        combo = ttk.Combobox(
            get_frame,
            textvariable=self.variables["how_to_get_var"],
            values=["All", "Random", "Sequential by loop"],
            state="readonly",
            width=20
        )
        combo.pack(side=tk.LEFT, padx=5)
    
    def create_region_section(self):
        """Create search region input section"""
        region_result = self.create_region_inputs(
            self.parent_frame,
            title="Khu vực tìm kiếm",
            include_select_button=True
        )
        self.select_area_button = region_result.get('select_area_button')
    
    def browse_file(self):
        """Open file browser dialog to select TXT file"""
        file_path = filedialog.askopenfilename(
            title="Chọn file text",
            filetypes=[
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.variables["text_file_path_var"].set(file_path)
            print(f"[TEXT_SEARCH_PARAMS] Selected file: {file_path}")
    
    def get_parameters(self):
        """Collect parameters"""
        params = super().get_parameters()
        
        # Get file path
        params["text_file_path"] = self.variables["text_file_path_var"].get()
        
        # Get text content from ScrolledText widget
        params["text_content"] = self.text_content_widget.get("1.0", tk.END).strip()
        
        # Get how_to_get selection
        params["how_to_get"] = self.variables["how_to_get_var"].get()
        
        return params
