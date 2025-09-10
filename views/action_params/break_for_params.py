from views.action_params.base_params import BaseActionParams
import tkinter as tk
import config as cfg

class BreakForParams(BaseActionParams):
    def __init__(self, parent_frame, parameters=None):
        """
        Create UI for Break For parameters
        Args:
            parent_frame: The parent frame to place UI elements
            parameters: Dictionary containing parameters (if editing an action)
        """
        super().__init__(parent_frame, parameters)

    def create_params(self):
        """Create UI for Break For parameters"""
        # Clear any existing widgets
        self.clear_frame()

        # Tạo label thông báo
        info_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        info_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            info_frame,
            text="Break For loop sẽ thoát khỏi vòng lặp For hiện tại ngay lập tức và chuyển đến action sau End For loop.\nNếu không có điều kiện, sẽ thực thi ngay lập tức.",
            bg=cfg.LIGHT_BG_COLOR,
            justify=tk.LEFT,
            padx=10,
            pady=10
        ).pack(fill=tk.X)

        # ========== PHẦN ĐIỀU KIỆN THỰC THI ==========
        self.create_break_conditions()

        return {}
