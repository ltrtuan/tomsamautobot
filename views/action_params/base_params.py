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
        """Abstract method, must be overridden by subclasses"""
        return {}
    
    def clear_frame(self):
        """Clear all widgets from the parent frame"""
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
    
    def create_region_inputs(self, parent_frame, title="Khu vực", include_select_button=True):
        """
        Create a common UI for region selection with X, Y, Width, Height
        Args:
            parent_frame: The frame to add the region section to
            title: The title for the region frame
            include_select_button: Whether to include a button to select the region
        Returns:
            dict: The region frame and the select area button (if created)
        """
        region_frame = tk.LabelFrame(parent_frame, text=title, bg=cfg.LIGHT_BG_COLOR, pady=10, padx=10)
        region_frame.pack(fill=tk.X, pady=10)
        
        # Fullscreen checkbox
        fullscreen_frame = tk.Frame(region_frame, bg=cfg.LIGHT_BG_COLOR)
        fullscreen_frame.pack(fill=tk.X, pady=5)
        self.variables["fullscreen_var"] = tk.BooleanVar(value=self.parameters.get("fullscreen", False))
        fullscreen_checkbox = ttk.Checkbutton(
            fullscreen_frame,
            text="Fullscreen",
            variable=self.variables["fullscreen_var"]
        )
        fullscreen_checkbox.pack(side=tk.LEFT, padx=5)
        
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
        if include_select_button:
            select_area_button = ttk.Button(region_frame, text="Chọn khu vực màn hình")
            select_area_button.pack(pady=10)
        
        return {
            'region_frame': region_frame,
            'select_area_button': select_area_button
        }
    
    def create_common_params(self,
                            show_variable=True,
                            show_random_time=True,
                            show_repeat=True,
                            show_random_skip=True,
                            show_result_action=False):
        """Create UI for common parameters shared by all actions - NOTE ALWAYS SHOWN AT END"""
        common_frame = tk.LabelFrame(
            self.parent_frame,
            text="Tham số chung",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        common_frame.pack(fill=tk.X, pady=10)
        
        # Variable
        if show_variable:
            variable_frame = tk.Frame(common_frame, bg=cfg.LIGHT_BG_COLOR)
            variable_frame.pack(fill=tk.X, pady=5)
            tk.Label(variable_frame, text="Variable(s):", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
            self.variables["variable_var"] = tk.StringVar(value=self.parameters.get("variable", ""))
            ttk.Entry(variable_frame, textvariable=self.variables["variable_var"], width=30).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            tk.Label(variable_frame, text="(For multi-column: VAR1;VAR2;VAR3)", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 8), fg="gray").pack(side=tk.LEFT, padx=5)
        
        # Random Time
        if show_random_time:
            random_time_frame = tk.Frame(common_frame, bg=cfg.LIGHT_BG_COLOR)
            random_time_frame.pack(fill=tk.X, pady=5)
            tk.Label(random_time_frame, text="Random Time:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
            self.variables["random_time_var"] = tk.StringVar(value=self.parameters.get("random_time", "0"))
            ttk.Entry(random_time_frame, textvariable=self.variables["random_time_var"], width=10, validate="key", validatecommand=self.validate_int_cmd).pack(side=tk.LEFT, padx=5)
            tk.Label(random_time_frame, text="(Giây chờ ngẫu nhiên trước khi thực thi)", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 8), fg="gray").pack(side=tk.LEFT, padx=5)
        
        # Repeat
        if show_repeat:
            repeat_frame = tk.Frame(common_frame, bg=cfg.LIGHT_BG_COLOR)
            repeat_frame.pack(fill=tk.X, pady=5)
            tk.Label(repeat_frame, text="Repeat:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
            tk.Label(repeat_frame, text="Fixed:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=(10, 5))
            self.variables["repeat_fixed_var"] = tk.StringVar(value=self.parameters.get("repeat_fixed", "0"))
            ttk.Entry(repeat_frame, textvariable=self.variables["repeat_fixed_var"], width=6, validate="key", validatecommand=self.validate_int_cmd).pack(side=tk.LEFT, padx=5)
            tk.Label(repeat_frame, text="+", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
            tk.Label(repeat_frame, text="Random (0-X):", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
            self.variables["repeat_random_var"] = tk.StringVar(value=self.parameters.get("repeat_random", "0"))
            ttk.Entry(repeat_frame, textvariable=self.variables["repeat_random_var"], width=6, validate="key", validatecommand=self.validate_int_cmd).pack(side=tk.LEFT, padx=5)
            tk.Label(repeat_frame, text="(Total = Fixed + Random(0-X))", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 8, "italic"), fg="#555555").pack(side=tk.LEFT, padx=5)       
      
        
        # Random Skip
        if show_random_skip:
            random_skip_frame = tk.Frame(common_frame, bg=cfg.LIGHT_BG_COLOR)
            random_skip_frame.pack(fill=tk.X, pady=5)
            tk.Label(random_skip_frame, text="Random Skip Action:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
            self.variables["random_skip_var"] = tk.StringVar(value=self.parameters.get("random_skip", "0"))
            ttk.Entry(random_skip_frame, textvariable=self.variables["random_skip_var"], width=10, validate="key", validatecommand=self.validate_int_cmd).pack(side=tk.LEFT, padx=5)
            tk.Label(random_skip_frame, text="(0 = skip, >0 = run)", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 8), fg="gray").pack(side=tk.LEFT, padx=5)
        
        # Result Action
        if show_result_action:
            result_frame = tk.Frame(common_frame, bg=cfg.LIGHT_BG_COLOR)
            result_frame.pack(fill=tk.X, pady=5)
            tk.Label(result_frame, text="Result Action:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
            self.variables["result_action_var"] = tk.StringVar(value=self.parameters.get("result_action", "next_action"))
            tk.Radiobutton(result_frame, text="Next Action", variable=self.variables["result_action_var"], value="next_action", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
            tk.Radiobutton(result_frame, text="Skip Next Action", variable=self.variables["result_action_var"], value="skip_next_action", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
        
        # Note (always at end)
        self.create_note()
        
        return common_frame
    
    def create_note(self):
        """Create note field"""
        note_frame = tk.LabelFrame(self.parent_frame, text="Note", bg=cfg.LIGHT_BG_COLOR, pady=5, padx=10)
        note_frame.pack(fill=tk.X, pady=10)
        tk.Label(note_frame, text="Description:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(anchor=tk.W, padx=5, pady=(0, 2))
        self.variables["note_var"] = tk.Text(note_frame, height=3, wrap=tk.WORD, font=("Segoe UI", 9))
        self.variables["note_var"].pack(fill=tk.X, padx=5, pady=5)
        if self.parameters:
            existing_note = self.parameters.get("note", "")
            if existing_note:
                self.variables["note_var"].insert("1.0", existing_note)
        return note_frame
    
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
        self.conditions_container = tk.Frame(break_frame, bg=cfg.LIGHT_BG_COLOR)
        self.conditions_container.pack(fill=tk.X)
        
        if "break_conditions" in self.parameters and self.parameters["break_conditions"]:
            for condition in self.parameters["break_conditions"]:
                self.add_break_condition(self.conditions_container, condition)
        else:
            self.add_break_condition(self.conditions_container)
        
        self.add_condition_button = ttk.Button(break_frame, text="Add Condition", command=lambda: self.add_break_condition(self.conditions_container))
        self.add_condition_button.pack(pady=5)
        return break_frame
    
    def add_break_condition(self, parent_frame, condition=None):
        """Add a break condition row"""
        condition_frame = tk.Frame(parent_frame, bg=cfg.LIGHT_BG_COLOR)
        condition_frame.pack(fill=tk.X, pady=5)
        is_first_row = len(self.break_conditions) == 0
        
        # Variable
        var_frame = tk.Frame(condition_frame, bg=cfg.LIGHT_BG_COLOR)
        var_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        tk.Label(var_frame, text="Variable:", bg=cfg.LIGHT_BG_COLOR, width=8, anchor="w").pack(side=tk.LEFT)
        variable_var = tk.StringVar(value=condition.get("variable", "") if condition else "")
        ttk.Entry(var_frame, textvariable=variable_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Value
        val_frame = tk.Frame(condition_frame, bg=cfg.LIGHT_BG_COLOR)
        val_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        tk.Label(val_frame, text="Value:", bg=cfg.LIGHT_BG_COLOR, width=6, anchor="w").pack(side=tk.LEFT)
        value_var = tk.StringVar(value=condition.get("value", "") if condition else "")
        ttk.Entry(val_frame, textvariable=value_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Logical operator
        logical_op_var = tk.StringVar(value=condition.get("logical_op", "AND") if condition else "AND")
        logical_op_combo = None
        if not is_first_row:
            logical_op_combo = ttk.Combobox(condition_frame, values=["AND", "OR"], textvariable=logical_op_var, width=5)
            logical_op_combo.pack(side=tk.RIGHT, padx=5)
        else:
            spacer = tk.Label(condition_frame, width=5, bg=cfg.LIGHT_BG_COLOR)
            spacer.pack(side=tk.RIGHT, padx=5)
        
        # Remove button
        remove_button = None
        if not is_first_row:
            condition_dict = {
                "frame": condition_frame,
                "logical_op_var": logical_op_var,
                "logical_op_combo": logical_op_combo,
                "variable_var": variable_var,
                "value_var": value_var,
                "remove_button": None
            }
            remove_button = ttk.Button(condition_frame, text="X", command=lambda: self.remove_break_condition(condition_frame, condition_dict))
            remove_button.pack(side=tk.RIGHT, padx=5)
            condition_dict["remove_button"] = remove_button
        else:
            condition_dict = {
                "frame": condition_frame,
                "logical_op_var": logical_op_var,
                "logical_op_combo": logical_op_combo,
                "variable_var": variable_var,
                "value_var": value_var,
                "remove_button": remove_button
            }
        
        self.break_conditions.append(condition_dict)
        return condition_dict
    
    def remove_break_condition(self, frame, condition_dict):
        """Remove a break condition"""
        if len(self.break_conditions) > 1:
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
        
        # Get values from all StringVar/BooleanVar
        for key, var in self.variables.items():
            if key == "note_var":
                continue
            if isinstance(var, tk.Variable):
                param_key = key.replace("_var", "")
                params[param_key] = var.get()
        
        # Collect note from Text widget
        if "note_var" in self.variables:
            note_widget = self.variables["note_var"]
            note_text = note_widget.get("1.0", tk.END).strip()
            params["note"] = note_text
        
        # Collect break conditions
        break_conditions = []
        for condition in self.break_conditions:
            var_value = condition["variable_var"].get()
            if var_value and var_value.strip() != '':
                break_conditions.append({
                    "logical_op": condition["logical_op_var"].get(),
                    "variable": var_value,
                    "value": condition["value_var"].get()
                })
        params["break_conditions"] = break_conditions
        
        return params
