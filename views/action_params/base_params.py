# views/action_params/base_params.py
import tkinter as tk
from tkinter import ttk, messagebox
import config as cfg

class BaseActionParams:
    def __init__(self, parent_frame, parameters=None):
        """
        Base class for all action parameters UI
        
        Args:
            parent_frame: The parent frame to place UI elements
            parameters: Dictionary containing parameters (if editing an action)
        """
        self.parent_frame = parent_frame
        self.parameters = parameters or {}
        self.widgets = {}
        self.variables = {}
        self.break_conditions = []
        
    def create_params(self):
        """Phương thức trừu tượng, cần được override bởi lớp con"""
        return {}
    
    def create_region_inputs(self, parent_frame, title="Khu vực", include_select_button=True):
        """
        Create a common UI for region selection with X, Y, Width, Height
    
        Args:
            parent_frame: The frame to add the region section to
            title: The title for the region frame
            include_select_button: Whether to include a button to select the region
        
        Returns:
            tuple: The region frame and the select area button (if created)
        """
        region_frame = tk.LabelFrame(parent_frame, text=title, bg=cfg.LIGHT_BG_COLOR, pady=10, padx=10)
        region_frame.pack(fill=tk.X, pady=10)

        # Coordinates inputs
        coords_frame = tk.Frame(region_frame, bg=cfg.LIGHT_BG_COLOR)
        coords_frame.pack(fill=tk.X, pady=5)

        # X coordinate
        tk.Label(coords_frame, text="X:", bg=cfg.LIGHT_BG_COLOR).grid(row=0, column=0, padx=5, pady=2)
        x_var = tk.StringVar(value=self.parameters.get("x", "0"))
        self.variables["x_var"] = x_var
        ttk.Entry(
            coords_frame,
            textvariable=x_var,
            width=6,
            validate="key",
            validatecommand=self.validate_int_cmd
        ).grid(row=0, column=1, padx=5, pady=2)

        # Y coordinate
        tk.Label(coords_frame, text="Y:", bg=cfg.LIGHT_BG_COLOR).grid(row=0, column=2, padx=5, pady=2)
        y_var = tk.StringVar(value=self.parameters.get("y", "0"))
        self.variables["y_var"] = y_var
        ttk.Entry(
            coords_frame,
            textvariable=y_var,
            width=6,
            validate="key",
            validatecommand=self.validate_int_cmd
        ).grid(row=0, column=3, padx=5, pady=2)

        # Width
        tk.Label(coords_frame, text="Width:", bg=cfg.LIGHT_BG_COLOR).grid(row=1, column=0, padx=5, pady=2)
        width_var = tk.StringVar(value=self.parameters.get("width", "0"))
        self.variables["width_var"] = width_var
        ttk.Entry(
            coords_frame,
            textvariable=width_var,
            width=6,
            validate="key",
            validatecommand=self.validate_int_cmd
        ).grid(row=1, column=1, padx=5, pady=2)

        # Height
        tk.Label(coords_frame, text="Height:", bg=cfg.LIGHT_BG_COLOR).grid(row=1, column=2, padx=5, pady=2)
        height_var = tk.StringVar(value=self.parameters.get("height", "0"))
        self.variables["height_var"] = height_var
        ttk.Entry(
            coords_frame,
            textvariable=height_var,
            width=6,
            validate="key",
            validatecommand=self.validate_int_cmd
        ).grid(row=1, column=3, padx=5, pady=2)

        select_area_button = None
        # Nút chọn khu vực màn hình (optional)
        if include_select_button:
            select_area_button = ttk.Button(region_frame, text="Chọn khu vực màn hình")
            select_area_button.pack(pady=10)

        return {
            'region_frame': region_frame,
            'select_area_button': select_area_button
        }
    
    def create_common_params(self):
        """Create UI for common parameters shared by all actions"""
        # ========== PHẦN THAM SỐ CHUNG ==========
        common_frame = tk.LabelFrame(self.parent_frame, text="Tham số chung", bg=cfg.LIGHT_BG_COLOR, pady=10, padx=10)
        common_frame.pack(fill=tk.X, pady=10)

        # Random Time
        random_time_frame = tk.Frame(common_frame, bg=cfg.LIGHT_BG_COLOR)
        random_time_frame.pack(fill=tk.X, pady=5)

        tk.Label(random_time_frame, text="Random Time:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
        self.variables["random_time_var"] = tk.StringVar(value=self.parameters.get("random_time", "0"))
        ttk.Entry(
            random_time_frame, 
            textvariable=self.variables["random_time_var"], 
            width=6,
            validate="key",
            validatecommand=self.validate_int_cmd
        ).pack(side=tk.LEFT, padx=5)

        # Double Click
        click_frame = tk.Frame(common_frame, bg=cfg.LIGHT_BG_COLOR)
        click_frame.pack(fill=tk.X, pady=5)

        self.variables["double_click_var"] = tk.BooleanVar(value=self.parameters.get("double_click", False))
        ttk.Checkbutton(
            click_frame, 
            text="Double Click", 
            variable=self.variables["double_click_var"]
        ).pack(side=tk.LEFT, padx=5)

        # Random Skip Action
        skip_frame = tk.Frame(common_frame, bg=cfg.LIGHT_BG_COLOR)
        skip_frame.pack(fill=tk.X, pady=5)

        tk.Label(skip_frame, text="Random Skip Action:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
        self.variables["random_skip_var"] = tk.StringVar(value=self.parameters.get("random_skip", "0"))
        ttk.Entry(
            skip_frame, 
            textvariable=self.variables["random_skip_var"], 
            width=6,
            validate="key",
            validatecommand=self.validate_int_cmd
        ).pack(side=tk.LEFT, padx=5)

        # Variable
        variable_frame = tk.Frame(common_frame, bg=cfg.LIGHT_BG_COLOR)
        variable_frame.pack(fill=tk.X, pady=5)

        tk.Label(variable_frame, text="Variable:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
        self.variables["variable_var"] = tk.StringVar(value=self.parameters.get("variable", ""))
        ttk.Entry(variable_frame, textvariable=self.variables["variable_var"], width=15).pack(side=tk.LEFT, padx=5)

        return common_frame
    
    def create_program_selector(self):
        """Create UI for program selection"""
        program_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        program_frame.pack(fill=tk.X, pady=10)

        tk.Label(program_frame, text="Select Program to Action:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)

        self.variables["program_var"] = tk.StringVar(value=self.parameters.get("program", ""))
        program_entry = ttk.Entry(program_frame, textvariable=self.variables["program_var"], width=30)
        program_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        select_program_button = ttk.Button(program_frame, text="Browse...")
        select_program_button.pack(side=tk.RIGHT, padx=5)
        
        return select_program_button
    
    def create_break_conditions(self):
        """Create UI for break conditions"""
        break_frame = tk.LabelFrame(self.parent_frame, text="Break action If", bg=cfg.LIGHT_BG_COLOR, pady=10, padx=10)
        break_frame.pack(fill=tk.X, pady=10)
        
        self.break_conditions = []
        
        # Load existing conditions or add a default empty one
        if "break_conditions" in self.parameters and self.parameters["break_conditions"]:
            for condition in self.parameters["break_conditions"]:
                self.add_break_condition(break_frame, condition)
        else:
            self.add_break_condition(break_frame)
        
        # Button to add more conditions
        add_condition_button = ttk.Button(
            break_frame, 
            text="Add Condition", 
            command=lambda: self.add_break_condition(break_frame)
        )
        add_condition_button.pack(pady=5)
        
        return break_frame
    
    def add_break_condition(self, parent_frame, condition=None):
        """Add a break condition row to the UI"""
        condition_frame = tk.Frame(parent_frame, bg=cfg.LIGHT_BG_COLOR)
        condition_frame.pack(fill=tk.X, pady=5)
        
        # Logical operator
        logical_op_var = tk.StringVar(value=condition.get("logical_op", "AND") if condition else "AND")
        logical_op_combo = ttk.Combobox(condition_frame, values=["AND", "OR"], textvariable=logical_op_var, width=5)
        logical_op_combo.pack(side=tk.LEFT, padx=5)
        
        # Variable
        var_frame = tk.Frame(condition_frame, bg=cfg.LIGHT_BG_COLOR)
        var_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        tk.Label(var_frame, text="Variable:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT)
        variable_var = tk.StringVar(value=condition.get("variable", "") if condition else "")
        ttk.Entry(var_frame, textvariable=variable_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Value
        val_frame = tk.Frame(condition_frame, bg=cfg.LIGHT_BG_COLOR)
        val_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        tk.Label(val_frame, text="Value:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT)
        value_var = tk.StringVar(value=condition.get("value", "") if condition else "")
        ttk.Entry(val_frame, textvariable=value_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Remove button
        remove_button = ttk.Button(
            condition_frame, 
            text="X", 
            command=lambda: self.remove_break_condition(condition_frame, condition_dict)
        )
        remove_button.pack(side=tk.RIGHT, padx=5)
        
        # Store condition variables in a dictionary
        condition_dict = {
            "frame": condition_frame,
            "logical_op_var": logical_op_var,
            "variable_var": variable_var,
            "value_var": value_var
        }
        
        self.break_conditions.append(condition_dict)
        return condition_dict
    
    def remove_break_condition(self, frame, condition_dict):
        """Remove a break condition from the UI"""
        if len(self.break_conditions) > 1:  # Keep at least one condition
            frame.destroy()
            self.break_conditions.remove(condition_dict)
    
    @property
    def validate_float_cmd(self):
        """Validation command for floating-point numbers"""
        return (self.parent_frame.register(self.validate_number), '%P')
    
    @property
    def validate_int_cmd(self):
        """Validation command for integer numbers"""
        return (self.parent_frame.register(self.validate_integer), '%P')
    
    @staticmethod
    def validate_number(P):
        """Validate if input is a number"""
        if P == "":
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_integer(P):
        """Validate if input is an integer"""
        if P == "":
            return True
        try:
            int(P)
            return True
        except ValueError:
            return False
    
    def get_parameters(self):
        """Get all parameters as a dictionary"""
        params = {}
        
        # Get values from all variables
        for key, var in self.variables.items():
            # Convert StringVar/BooleanVar to values
            if isinstance(var, tk.Variable):
                param_key = key.replace("_var", "")
                params[param_key] = var.get()
        
        # Collect break conditions
        break_conditions = []
        for condition in self.break_conditions:
            var_value = condition["variable_var"].get()
            if var_value:  # Only add if variable is specified
                break_conditions.append({
                    "logical_op": condition["logical_op_var"].get(),
                    "variable": var_value,
                    "value": condition["value_var"].get()
                })
        
        params["break_conditions"] = break_conditions
        
        return params
    
    def clear_frame(self):
        """Clear all widgets from the parent frame"""
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
