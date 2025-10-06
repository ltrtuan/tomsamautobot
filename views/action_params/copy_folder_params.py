# views/action_params/copy_folder_params.py
import tkinter as tk
from tkinter import ttk, filedialog
import config as cfg
from views.action_params.base_params import BaseActionParams

class CopyFolderParams(BaseActionParams):
    """UI for Copy File/Folder action parameters."""
    
    def __init__(self, parent_frame, parameters=None):
        super().__init__(parent_frame, parameters)
        self.zip_checkbox = None
        self.extract_checkbox = None
    
    def create_params(self):
        """Create UI for copy file/folder parameters"""
        self.clear_frame()
        
        # ========== TYPE SELECTION ==========
        self.create_type_section()
        
        # ========== SOURCE SECTIONS ==========
        self.create_source_variable_section()
        self.create_source_browse_section()
        
        # ========== DESTINATION SECTIONS ==========
        self.create_dest_variable_section()
        self.create_dest_browse_section()
        
        # ========== RENAME SECTION ==========
        self.create_rename_section()
        
        # ========== OPTIONS SECTION ==========
        self.create_options_section()
        
        # ========== COMMON PARAMETERS ==========
        self.create_common_params()
        
        # ========== BREAK CONDITIONS ==========
        self.create_break_conditions()
        
        # ========== PROGRAM SELECTOR ==========
        select_program_button = self.create_program_selector()
        
        # Initial UI update
        self.on_type_changed()
        
        return {
            'browse_source_button': self.browse_source_button,
            'browse_dest_button': self.browse_dest_button,
            'select_program_button': select_program_button
        }
    
    def create_type_section(self):
        """Create type selection (Folder/File)"""
        type_frame = tk.LabelFrame(
            self.parent_frame,
            text="Type",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        type_frame.pack(fill=tk.X, pady=10)
        
        self.variables["type_var"] = tk.StringVar()
        
        if self.parameters:
            self.variables["type_var"].set(
                self.parameters.get("copy_type", "Folder")
            )
        else:
            self.variables["type_var"].set("Folder")
        
        # Radio buttons
        folder_radio = ttk.Radiobutton(
            type_frame,
            text="Folder",
            variable=self.variables["type_var"],
            value="Folder",
            command=self.on_type_changed
        )
        folder_radio.pack(side=tk.LEFT, padx=10)
        
        file_radio = ttk.Radiobutton(
            type_frame,
            text="File",
            variable=self.variables["type_var"],
            value="File",
            command=self.on_type_changed
        )
        file_radio.pack(side=tk.LEFT, padx=10)
    
    def create_source_variable_section(self):
        """Create source variable input"""
        var_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        var_frame.pack(fill=tk.X, pady=5)
        
        label = tk.Label(
            var_frame,
            text="Source Variable:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(10, 5))
        
        self.variables["source_variable_var"] = tk.StringVar()
        
        if self.parameters:
            self.variables["source_variable_var"].set(
                self.parameters.get("source_variable", "")
            )
        
        var_entry = ttk.Entry(
            var_frame,
            textvariable=self.variables["source_variable_var"],
            width=30
        )
        var_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        help_label = tk.Label(
            var_frame,
            text="(Priority over Browse)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="gray"
        )
        help_label.pack(side=tk.LEFT, padx=5)
    
    def create_source_browse_section(self):
        """Create source browse section"""
        browse_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        browse_frame.pack(fill=tk.X, pady=5)
        
        label = tk.Label(
            browse_frame,
            text="Source (Browse):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(10, 5))
        
        self.variables["source_browse_var"] = tk.StringVar()
        
        if self.parameters:
            self.variables["source_browse_var"].set(
                self.parameters.get("source_browse", "")
            )
        
        path_entry = ttk.Entry(
            browse_frame,
            textvariable=self.variables["source_browse_var"],
            width=40
        )
        path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.browse_source_button = ttk.Button(
            browse_frame,
            text="Browse...",
            command=self.browse_source
        )
        self.browse_source_button.pack(side=tk.RIGHT, padx=5)
    
    def create_dest_variable_section(self):
        """Create destination variable input"""
        var_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        var_frame.pack(fill=tk.X, pady=5)
        
        label = tk.Label(
            var_frame,
            text="Destination Variable:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(10, 5))
        
        self.variables["dest_variable_var"] = tk.StringVar()
        
        if self.parameters:
            self.variables["dest_variable_var"].set(
                self.parameters.get("dest_variable", "")
            )
        
        var_entry = ttk.Entry(
            var_frame,
            textvariable=self.variables["dest_variable_var"],
            width=30
        )
        var_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        help_label = tk.Label(
            var_frame,
            text="(Empty = same location)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="gray"
        )
        help_label.pack(side=tk.LEFT, padx=5)
    
    def create_dest_browse_section(self):
        """Create destination browse section"""
        browse_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        browse_frame.pack(fill=tk.X, pady=5)
        
        label = tk.Label(
            browse_frame,
            text="Destination (Browse):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(10, 5))
        
        self.variables["dest_browse_var"] = tk.StringVar()
        
        if self.parameters:
            self.variables["dest_browse_var"].set(
                self.parameters.get("dest_browse", "")
            )
        
        path_entry = ttk.Entry(
            browse_frame,
            textvariable=self.variables["dest_browse_var"],
            width=40
        )
        path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.browse_dest_button = ttk.Button(
            browse_frame,
            text="Browse...",
            command=self.browse_dest
        )
        self.browse_dest_button.pack(side=tk.RIGHT, padx=5)
    
    def create_rename_section(self):
        """Create rename input section"""
        rename_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        rename_frame.pack(fill=tk.X, pady=5)
        
        label = tk.Label(
            rename_frame,
            text="Rename (Optional):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(10, 5))
        
        self.variables["rename_var"] = tk.StringVar()
        
        if self.parameters:
            self.variables["rename_var"].set(
                self.parameters.get("rename_name", "")
            )
        
        rename_entry = ttk.Entry(
            rename_frame,
            textvariable=self.variables["rename_var"],
            width=30
        )
        rename_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        help_label = tk.Label(
            rename_frame,
            text="(Leave empty to keep original name)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="gray"
        )
        help_label.pack(side=tk.LEFT, padx=5)
    
    def create_options_section(self):
        """Create options checkboxes section"""
        options_frame = tk.LabelFrame(
            self.parent_frame,
            text="Options",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        options_frame.pack(fill=tk.X, pady=10)
        
        # Zip Folder checkbox (only for Folder)
        self.variables["zip_folder_var"] = tk.BooleanVar()
        
        if self.parameters:
            self.variables["zip_folder_var"].set(
                self.parameters.get("zip_folder", False)
            )
        
        self.zip_checkbox = ttk.Checkbutton(
            options_frame,
            text="Zip Folder (compress to .zip before copy)",
            variable=self.variables["zip_folder_var"]
        )
        self.zip_checkbox.pack(anchor=tk.W, pady=5)
        
        # Extract File checkbox (only for File)
        self.variables["extract_file_var"] = tk.BooleanVar()
        
        if self.parameters:
            self.variables["extract_file_var"].set(
                self.parameters.get("extract_file", False)
            )
        
        self.extract_checkbox = ttk.Checkbutton(
            options_frame,
            text="Extract File (unzip .zip file after copy)",
            variable=self.variables["extract_file_var"]
        )
        self.extract_checkbox.pack(anchor=tk.W, pady=5)
        
        # Delete Source checkbox (always visible)
        self.variables["delete_source_var"] = tk.BooleanVar()
        
        if self.parameters:
            self.variables["delete_source_var"].set(
                self.parameters.get("delete_source", False)
            )
        
        delete_check = ttk.Checkbutton(
            options_frame,
            text="Delete Source (after copy completed)",
            variable=self.variables["delete_source_var"]
        )
        delete_check.pack(anchor=tk.W, pady=5)
        
        # Warning label
        warning_label = tk.Label(
            options_frame,
            text="⚠️ Warning: Delete operation cannot be undone!",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8, "bold"),
            fg="red"
        )
        warning_label.pack(anchor=tk.W, pady=(5, 0))
    
    def on_type_changed(self):
        """Handle type radio button change - show/hide options"""
        copy_type = self.variables["type_var"].get()
        
        if copy_type == "Folder":
            # Show Zip, hide Extract
            if self.zip_checkbox:
                self.zip_checkbox.pack(anchor=tk.W, pady=5)
            if self.extract_checkbox:
                self.extract_checkbox.pack_forget()
        else:  # File
            # Hide Zip, show Extract
            if self.zip_checkbox:
                self.zip_checkbox.pack_forget()
            if self.extract_checkbox:
                self.extract_checkbox.pack(anchor=tk.W, pady=5)
    
    def browse_source(self):
        """Browse source file or folder"""
        copy_type = self.variables["type_var"].get()
        
        if copy_type == "Folder":
            path = filedialog.askdirectory(title="Select Source Folder")
        else:
            path = filedialog.askopenfilename(title="Select Source File")
        
        if path:
            self.variables["source_browse_var"].set(path)
            print(f"[COPY_PARAMS] Selected source: {path}")
    
    def browse_dest(self):
        """Browse destination folder"""
        path = filedialog.askdirectory(title="Select Destination Folder")
        if path:
            self.variables["dest_browse_var"].set(path)
            print(f"[COPY_PARAMS] Selected destination: {path}")
    
    def get_parameters(self):
        """Collect parameters"""
        params = super().get_parameters()
        
        params["copy_type"] = self.variables["type_var"].get()
        params["source_variable"] = self.variables["source_variable_var"].get().strip()
        params["source_browse"] = self.variables["source_browse_var"].get().strip()
        params["dest_variable"] = self.variables["dest_variable_var"].get().strip()
        params["dest_browse"] = self.variables["dest_browse_var"].get().strip()
        params["rename_name"] = self.variables["rename_var"].get().strip()
        params["zip_folder"] = self.variables["zip_folder_var"].get()
        params["extract_file"] = self.variables["extract_file_var"].get()
        params["delete_source"] = self.variables["delete_source_var"].get()
        
        return params
