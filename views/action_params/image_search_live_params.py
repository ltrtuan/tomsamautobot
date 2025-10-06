# views/action_params/image_search_live_params.py
import tkinter as tk
from tkinter import ttk
import config as cfg
from views.action_params.base_params import BaseActionParams

class ImageSearchLiveParams(BaseActionParams):
    """UI for Image Search Live action parameters."""
    
    def __init__(self, parent_frame, parameters=None):
        super().__init__(parent_frame, parameters)
        self.select_area_button = None
        self.dialog = None
    
    def set_dialog(self, dialog):
        """Set dialog reference for screenshot feature"""
        self.dialog = dialog
    
    def create_params(self):
        """Create UI for image search live parameters"""
        self.clear_frame()
        
        # ========== INFO LABEL ==========
        self.create_info_section()
        
        # ========== DELAY SECTION ==========
        self.create_delay_section()
        
        # ========== SIMILARITY THRESHOLD SECTION ==========
        self.create_similarity_section()
        
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
    
    def create_info_section(self):
        """Create info label explaining the action"""
        info_frame = tk.LabelFrame(
            self.parent_frame,
            text="Action Information",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        info_frame.pack(fill=tk.X, pady=10)
        
        info_text = (
            "So sánh 2 screenshots của cùng 1 vùng để phát hiện thay đổi.\n\n"
            "Use case: Phát hiện video đang play (thay đổi) hay pause (giống nhau)\n\n"
            "• Screenshot 1 → Delay X giây → Screenshot 2 → So sánh\n"
            "• True: Hai ảnh GIỐNG NHAU (video pause)\n"
            "• False: Hai ảnh KHÁC NHAU (video đang play)\n\n"
            "Lưu kết quả vào Variable."
        )
        
        label = tk.Label(
            info_frame,
            text=info_text,
            bg=cfg.LIGHT_BG_COLOR,
            justify=tk.LEFT,
            wraplength=500,
            font=("Segoe UI", 9)
        )
        label.pack(anchor=tk.W, padx=5, pady=5)
    
    def create_delay_section(self):
        """Create delay input section"""
        delay_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        delay_frame.pack(fill=tk.X, pady=5)
        
        label = tk.Label(
            delay_frame,
            text="Delay giữa 3 screenshots (giây):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(10, 5))
        
        self.variables["compare_delay_var"] = tk.StringVar()
        
        if self.parameters:
            self.variables["compare_delay_var"].set(
                self.parameters.get("compare_delay", "3")
            )
        else:
            self.variables["compare_delay_var"].set("3")
        
        delay_entry = ttk.Entry(
            delay_frame,
            textvariable=self.variables["compare_delay_var"],
            width=10
        )
        delay_entry.pack(side=tk.LEFT, padx=5)
        
        hint_label = tk.Label(
            delay_frame,
            text="(Khuyến nghị: 1-3 giây)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="gray"
        )
        hint_label.pack(side=tk.LEFT, padx=5)
    
    def create_similarity_section(self):
        """Create similarity threshold slider section"""
        similarity_frame = tk.LabelFrame(
            self.parent_frame,
            text="Ngưỡng giống nhau (%)",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        similarity_frame.pack(fill=tk.X, pady=10)
        
        info_label = tk.Label(
            similarity_frame,
            text="Nếu độ tương đồng >= ngưỡng này → Coi là GIỐNG NHAU (pause)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="gray"
        )
        info_label.pack(anchor=tk.W, pady=(0, 5))
        
        slider_frame = tk.Frame(similarity_frame, bg=cfg.LIGHT_BG_COLOR)
        slider_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            slider_frame,
            text="Ngưỡng (%):",
            bg=cfg.LIGHT_BG_COLOR
        ).pack(side=tk.LEFT, padx=5)
        
        self.variables["similarity_threshold_var"] = tk.StringVar(
            value=self.parameters.get("similarity_threshold", "98") if self.parameters else "98"
        )
        
        similarity_scale = ttk.Scale(
            slider_frame,
            from_=50,
            to=100,
            orient=tk.HORIZONTAL,
            command=lambda v: self.variables["similarity_threshold_var"].set(str(int(float(v))))
        )
        similarity_scale.set(int(self.variables["similarity_threshold_var"].get()))
        similarity_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        similarity_value = ttk.Entry(
            slider_frame,
            textvariable=self.variables["similarity_threshold_var"],
            width=5
        )
        similarity_value.pack(side=tk.LEFT, padx=5)
        
        # Sync scale with textbox
        def update_scale(*args):
            try:
                value = int(self.variables["similarity_threshold_var"].get())
                if 50 <= value <= 100:
                    similarity_scale.set(value)
            except ValueError:
                pass
        
        self.variables["similarity_threshold_var"].trace_add("write", update_scale)
    
    def create_region_section(self):
        """Create search region input section"""
        region_result = self.create_region_inputs(
            self.parent_frame,
            title="Vùng so sánh (để trống = toàn màn hình)",
            include_select_button=True
        )
        self.select_area_button = region_result.get('select_area_button')
    
    def get_parameters(self):
        """Collect parameters"""
        params = super().get_parameters()
        
        # Get delay
        params["compare_delay"] = self.variables["compare_delay_var"].get()
        
        # Get similarity threshold
        params["similarity_threshold"] = self.variables["similarity_threshold_var"].get()
        
        return params
