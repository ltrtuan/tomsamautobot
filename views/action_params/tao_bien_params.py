# views/action_params/tao_bien_params.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import config as cfg
from views.action_params.base_params import BaseActionParams

class TaoBienParams(BaseActionParams):
    """UI for Create Variable action parameters (multi-row support)."""
    
    def __init__(self, parent_frame, parameters=None):
        super().__init__(parent_frame, parameters)
        self.variable_rows = []
    
    def create_params(self):
        """Create UI for create variable parameters"""
        self.create_variables_section()
        
        # ✅ Common params with ALL fields hidden except Note
        self.create_common_params(
            show_variable=False,
            show_random_time=False,
            show_repeat=False,          
            show_random_skip=False,
            show_result_action=False
        )
        return {}
    
    def create_variables_section(self):
        """Create multi-row variable input section"""
        # Container frame
        container = tk.LabelFrame(
            self.parent_frame,
            text="Variables",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        container.pack(fill=tk.BOTH, expand=True, pady=10)
    
        # ========== HEADER ==========
        header_frame = tk.Frame(container, bg=cfg.LIGHT_BG_COLOR)
        header_frame.pack(fill=tk.X, pady=(0, 5))

        # Variable Name Label
        tk.Label(
            header_frame,
            text="Variable Name",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9, "bold"),
            anchor='w'
        ).grid(row=0, column=0, padx=2, sticky='ew')  # ✅ Same padx as rows!
       
        # Value Label
        tk.Label(
            header_frame,
            text="Value",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9, "bold"),
            anchor='w'
        ).grid(row=0, column=1, padx=2, sticky='ew')

        # File Path Label
        tk.Label(
            header_frame,
            text="File Path (Priority)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9, "bold"),
            anchor='w'
        ).grid(row=0, column=2, padx=2, sticky='ew')

        # Browse Label (spacer)
        tk.Label(
            header_frame,
            text="",
            bg=cfg.LIGHT_BG_COLOR,
            width=8  # ✅ Match Browse button width
        ).grid(row=0, column=3, padx=2)

        # Delete Label (spacer)
        tk.Label(
            header_frame,
            text="",
            bg=cfg.LIGHT_BG_COLOR,
            width=3  # ✅ Match X button width
        ).grid(row=0, column=4, padx=2)

        # ✅ Configure column weights - Variable Name smaller
        header_frame.grid_columnconfigure(0, weight=1, minsize=80)   # Variable Name: smaller (was weight=1)
        header_frame.grid_columnconfigure(1, weight=2, minsize=100)  # Value: medium
        header_frame.grid_columnconfigure(2, weight=4, minsize=200)  # File Path: larger (more space)
        header_frame.grid_columnconfigure(3, weight=0)               # Browse: fixed
        header_frame.grid_columnconfigure(4, weight=0)               # Delete: fixed
    
        # ========== SCROLLABLE CANVAS ==========
        canvas_container = tk.Frame(container, bg=cfg.LIGHT_BG_COLOR)
        canvas_container.pack(fill=tk.BOTH, expand=True)
    
        self.canvas = tk.Canvas(canvas_container, bg=cfg.LIGHT_BG_COLOR, height=200)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
        self.rows_frame = tk.Frame(self.canvas, bg=cfg.LIGHT_BG_COLOR)
    
        # ✅ Bind scrollregion update
        self.rows_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
    
        # ✅ Create window and store window ID
        self.canvas_window = self.canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
    
        # ✅ CRITICAL: Bind canvas width to rows_frame width
        def _configure_canvas_width(event):
            # Set rows_frame width to match canvas width (minus scrollbar)
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
        self.canvas.bind("<Configure>", _configure_canvas_width)
    
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        # ========== LOAD EXISTING OR CREATE DEFAULT ==========
        existing_variables = self.parameters.get("variables", [])
        if existing_variables:
            for var_data in existing_variables:
                self.add_variable_row(
                    var_name=var_data.get("name", ""),
                    var_value=var_data.get("value", ""),
                    var_file=var_data.get("file_path", "")
                )
        else:
            self.add_variable_row()
    
        # ========== ADD BUTTON (OUTSIDE CANVAS) ==========
        button_frame = tk.Frame(container, bg=cfg.LIGHT_BG_COLOR)
        button_frame.pack(fill=tk.X, pady=(10, 0))
    
        ttk.Button(
            button_frame,
            text="+ Add Variable",
            command=self.add_variable_row
        ).pack(side=tk.LEFT, padx=5)

        
    
    def add_variable_row(self, var_name="", var_value="", var_file=""):
        """Add a new variable row"""
        row_frame = tk.Frame(self.rows_frame, bg=cfg.LIGHT_BG_COLOR)
        row_frame.pack(fill=tk.X, pady=2, expand=True)
    
        is_first_row = len(self.variable_rows) == 0
    
        # Variable Name
        name_var = tk.StringVar(value=var_name)
        name_entry = ttk.Entry(row_frame, textvariable=name_var)
        name_entry.grid(row=0, column=0, padx=2, sticky='ew')  # ✅ Same padx!
    
        # Value
        value_var = tk.StringVar(value=var_value)
        value_entry = ttk.Entry(row_frame, textvariable=value_var)
        value_entry.grid(row=0, column=1, padx=2, sticky='ew')
    
        # File Path (Priority)
        file_var = tk.StringVar(value=var_file)
        file_entry = ttk.Entry(row_frame, textvariable=file_var)
        file_entry.grid(row=0, column=2, padx=2, sticky='ew')
    
        # Browse Button (fixed width)
        browse_btn = ttk.Button(
            row_frame,
            text="Browse",
            command=lambda: self.browse_file(file_var),
            width=8  # ✅ Match header spacer
        )
        browse_btn.grid(row=0, column=3, padx=2)
    
        # Store row data BEFORE using it in lambda
        row_data = {
            'frame': row_frame,
            'name_var': name_var,
            'value_var': value_var,
            'file_var': file_var
        }
    
        # Delete Button (only for rows 2+)
        if not is_first_row:
            delete_btn = ttk.Button(
                row_frame,
                text="✕",
                command=lambda rd=row_data: self.delete_variable_row(rd['frame'], rd),
                width=3  # ✅ Match header spacer
            )
            delete_btn.grid(row=0, column=4, padx=2)
        else:
            # Spacer
            spacer = tk.Label(row_frame, width=3, bg=cfg.LIGHT_BG_COLOR, text="")
            spacer.grid(row=0, column=4, padx=2)
    
        # ✅ SAME column weights as header
        row_frame.grid_columnconfigure(0, weight=1, minsize=80)   # Variable Name: smaller
        row_frame.grid_columnconfigure(1, weight=2, minsize=100)  # Value: medium
        row_frame.grid_columnconfigure(2, weight=4, minsize=200)  # File Path: larger
        row_frame.grid_columnconfigure(3, weight=0)               # Browse: fixed
        row_frame.grid_columnconfigure(4, weight=0)               # Delete: fixed
    
        self.variable_rows.append(row_data)


    
    def delete_variable_row(self, row_frame, row_data):
        """Delete a variable row"""
        if len(self.variable_rows) <= 1:
            messagebox.showwarning("Warning", "Must keep at least one variable row!")
            return
        
        row_frame.destroy()
        self.variable_rows.remove(row_data)
    
    def browse_file(self, file_var):
        """Browse for file"""
        file_path = filedialog.askopenfilename(
            title="Select File",
            filetypes=[("All Files", "*.*")]
        )
        
        if file_path:
            file_var.set(file_path)
            print(f"[TAO_BIEN_PARAMS] Selected file: {file_path}")
    
    def get_parameters(self):
        """Collect parameters"""
        params = {}
        
        variables = []
        for row in self.variable_rows:
            var_name = row['name_var'].get().strip()
            var_value = row['value_var'].get()
            var_file = row['file_var'].get().strip()
            
            if var_name:
                variables.append({
                    'name': var_name,
                    'value': var_value,
                    'file_path': var_file
                })
        
        params["variables"] = variables
        
        # ✅ Get note from base_params
        if "note_var" in self.variables:
            note_widget = self.variables["note_var"]
            note_text = note_widget.get("1.0", tk.END).strip()
            params["note"] = note_text
        return params
