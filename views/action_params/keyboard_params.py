import tkinter as tk
from tkinter import ttk
import config as cfg
from views.action_params.base_params import BaseActionParams

KEY_OPTIONS = [
    # modifiers + empty
    "", "Ctrl", "Shift", "Alt", "Window",
    # function keys
    *[f"F{i}" for i in range(1, 13)],
    # arrows
    "Up", "Down", "Left", "Right", 
    # specials
    "Enter", "Esc", "Del", "BackSpace", "Space",
    # numbers
    *[str(i) for i in range(0, 10)],
    # letters
    *[chr(c) for c in range(ord('A'), ord('Z') + 1)],
]

class KeyboardParams(BaseActionParams):
    """UI cho action Bàn phím theo flow ImageSearch."""
    
    def __init__(self, parent_frame, parameters=None):
        """
        Create UI for keyboard parameters
        Args:
            parent_frame: The parent frame to place UI elements
            parameters: Dictionary containing parameters (if editing an action)
        """
        super().__init__(parent_frame, parameters)
        
    def create_params(self):
        """Create UI for keyboard parameters"""
        # Clear any existing widgets
        self.clear_frame()
        
        # ========== PHẦN CẤU HÌNH PHÍM ==========
        self.create_keyboard_section()
        
        # ========== PHẦN THAM SỐ CHUNG ==========
        self.create_common_params()
        
        # ========== PHẦN BREAK ACTION IF ==========
        self.create_break_conditions()
        
        # ========== PHẦN CHỌN CHƯƠNG TRÌNH ==========
        select_program_button = self.create_program_selector()
        
        return {
            'select_program_button': select_program_button
        }
        
    def create_keyboard_section(self):
        """Create UI for keyboard key configuration"""
        # ---- khu vực phím ----
        key_frame = tk.LabelFrame(
            self.parent_frame, text="Các phím cần nhấn",
            bg=cfg.LIGHT_BG_COLOR, pady=10, padx=10)
        key_frame.pack(fill=tk.X, pady=10)

        # Container cho rows (trước nút Add)
        self.rows_container = tk.Frame(key_frame, bg=cfg.LIGHT_BG_COLOR)
        self.rows_container.pack(fill=tk.X)
        
        self.key_rows = []
        
        # Load dữ liệu cũ nếu edit (theo cách ImageSearch dùng self.parameters)
        self._load_existing_keyboard_data()
        
        # Nếu không có data cũ, tạo 1 row mặc định
        if not self.key_rows:
            self._add_key_row(self.rows_container)

        # Nút Add ở dưới cùng  
        add_btn = ttk.Button(
            key_frame, text="Add Row",
            command=lambda: self._add_key_row(self.rows_container))
        add_btn.pack(pady=5)
        
    def _load_existing_keyboard_data(self):
        """Load dữ liệu từ key_sequence đã lưu khi edit (theo pattern ImageSearch)."""
        if not self.parameters:
            return
            
        key_sequence = self.parameters.get("key_sequence", "")
        if not key_sequence:
            return
        
        # Tách thành các rows bằng dấu ;
        rows = [row.strip() for row in key_sequence.split(";") if row.strip()]
        
        for row_str in rows:
            # Tách thành các keys bằng dấu +
            keys = [key.strip() for key in row_str.split("+") if key.strip()]
            
            # Pad với empty strings nếu không đủ 3 keys
            while len(keys) < 3:
                keys.append("")
                
            # Chỉ lấy 3 keys đầu tiên
            keys = keys[:3]
            
            # Tạo row với data
            self._add_key_row(self.rows_container, row_data=keys)

    def _add_key_row(self, container, row_data=None):
        """Thêm row keyboard với data (theo pattern ImageSearch load data)"""
        row_frm = tk.Frame(container, bg=cfg.LIGHT_BG_COLOR)
        row_frm.pack(fill=tk.X, pady=3)

        vars_in_row = []
        for i in range(3):
            # Load giá trị từ row_data (giống ImageSearch load từ self.parameters)
            value = ""
            if row_data and i < len(row_data):
                value = row_data[i]
                
            var = tk.StringVar(value=value)
            combo = ttk.Combobox(
                row_frm, width=8, values=KEY_OPTIONS,
                textvariable=var, state="readonly")
            combo.pack(side=tk.LEFT, padx=3)
            vars_in_row.append(var)

        # nút xoá (trừ hàng đầu)
        if len(self.key_rows) > 0:
            ttk.Button(
                row_frm, text="X",
                command=lambda: self._remove_key_row(row_frm)
            ).pack(side=tk.RIGHT, padx=3)

        self.key_rows.append({"frame": row_frm, "vars": vars_in_row})

    def _remove_key_row(self, frame):
        """Xóa row keyboard"""
        for r in self.key_rows:
            if r["frame"] is frame:
                r["frame"].destroy()
                self.key_rows.remove(r)
                break

    def get_parameters(self):
        """Thu thập tham số (theo pattern ImageSearch)"""
        params = super().get_parameters()
        
        # Lấy key sequences từ UI
        key_sequences = []
        for row in self.key_rows:
            keys = [v.get() for v in row["vars"] if v.get()]
            if keys:
                key_sequences.append(" + ".join(keys))
                
        params["key_sequence"] = " ; ".join(key_sequences)
        return params
