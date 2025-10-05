# views/action_params/image_search_params.py

import tkinter as tk
from tkinter import ttk, filedialog
import config as cfg
import time
import os
import pyautogui
from views.action_params.base_params import BaseActionParams

class ImageSearchParams(BaseActionParams):
    def __init__(self, parent_frame, parameters=None):
        super().__init__(parent_frame, parameters)
        self.dialog = None
        self.select_area_button = None  # ➊ Track for controller binding
    
    def set_dialog(self, dialog):
        """Set dialog reference for screenshot feature"""
        self.dialog = dialog
    
    def create_params(self):
        """Create UI for image search parameters"""
        self.clear_frame()
        
        # ========== IMAGE PATH SECTION ==========
        path_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        path_frame.pack(fill=tk.X, pady=(5, 5))
        
        tk.Label(path_frame, text="Đường dẫn hình ảnh:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=(0, 5))
        self.variables["image_path_var"] = tk.StringVar(value=self.parameters.get("image_path", ""))
        path_entry = ttk.Entry(path_frame, textvariable=self.variables["image_path_var"], width=40)
        path_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        # ➊ Browse button - SELF-CONTAINED
        browse_button = ttk.Button(
            path_frame,
            text="Duyệt...",
            command=self.browse_image  # Local method
        )
        browse_button.pack(side=tk.RIGHT, padx=5)
        
        # Screenshot section
        screenshot_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        screenshot_frame.pack(fill=tk.X, pady=(0, 10))
        
        # ➋ Screenshot button - SELF-CONTAINED
        screenshot_button = ttk.Button(
            screenshot_frame,
            text="Chụp Màn Hình",
            command=self.capture_screen_area  # Local method
        )
        screenshot_button.pack(side=tk.LEFT, padx=5)
        
        # ========== SEARCH REGION SECTION ==========
        self.create_region_section()
        
        # ========== ACCURACY SECTION ==========
        self.create_accuracy_section()
        
        # ========== COMMON PARAMETERS ==========
        self.create_common_params()
        
        # ========== BREAK CONDITIONS ==========
        self.create_break_conditions()
        
        # ========== PROGRAM SELECTOR ==========
        select_program_button = self.create_program_selector()
        
        # ➌ Return SHARED buttons (select_area_button + select_program_button)
        return {
            'select_area_button': self.select_area_button,  # SHARED: handled by controller
            'select_program_button': select_program_button  # SHARED: handled by controller
        }
    
    def browse_image(self):
        """Browse and select image file - SELF-CONTAINED"""
        filename = filedialog.askopenfilename(
            title="Chọn một hình ảnh",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            self.variables["image_path_var"].set(filename)
            print(f"[IMAGE_SEARCH_PARAMS] Selected image: {filename}")
    
    def capture_screen_area(self):
        """Capture screen area and save - SELF-CONTAINED"""
        if not self.dialog:
            print("[IMAGE_SEARCH_PARAMS] Error: Dialog not set!")
            return
        
        from views.screen_area_selector import ScreenAreaSelector
        
        def update_textboxes(x, y, width, height):
            """Update coordinate textboxes"""
            try:
                self.variables["x_var"].set(str(int(x)))
                self.variables["y_var"].set(str(int(y)))
                self.variables["width_var"].set(str(int(width)))
                self.variables["height_var"].set(str(int(height)))
            except Exception as e:
                print(f"[IMAGE_SEARCH_PARAMS] Error updating textboxes: {e}")
        
        def take_screenshot_after_close(x, y, width, height):
            """Take screenshot after selector closes"""
            try:
                # Get save path
                save_path = self.get_save_path()
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
                full_path = os.path.join(save_path, filename)
                
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Take screenshot
                screenshot = pyautogui.screenshot(region=(x, y, width, height))
                screenshot.save(full_path)
                
                # Update path
                self.variables["image_path_var"].set(full_path)
                print(f"[IMAGE_SEARCH_PARAMS] Screenshot saved: {full_path}")
            except Exception as e:
                print(f"[IMAGE_SEARCH_PARAMS] Error taking screenshot: {e}")
        
        # Show selector with post-close callback
        try:
            selector = ScreenAreaSelector(
                self.dialog,
                callback=update_textboxes,
                post_close_callback=take_screenshot_after_close
            )
            selector.show()
        except Exception as e:
            print(f"[IMAGE_SEARCH_PARAMS] Error showing selector: {e}")
            self.dialog.deiconify()
    
    def get_save_path(self):
        """Get save path from config"""
        try:
            from config import get_config
            config = get_config()
            path = config.get("FILE_PATH", "")
            if path and os.path.exists(os.path.dirname(path)):
                return os.path.dirname(path)
        except Exception as e:
            print(f"[IMAGE_SEARCH_PARAMS] Cannot get config path: {e}")
        
        # Default path
        default_path = "C:\\tomsamautobot"
        os.makedirs(default_path, exist_ok=True)
        return default_path
    
    def create_region_section(self):
        """Create search region input section"""
        region_result = self.create_region_inputs(
            self.parent_frame,
            title="Khu vực tìm kiếm",
            include_select_button=True
        )
        
        # ➊ Store button reference for controller binding (NO local command!)
        self.select_area_button = region_result.get('select_area_button')
    
    def create_accuracy_section(self):
        """Create accuracy slider section"""
        accuracy_frame = tk.LabelFrame(
            self.parent_frame,
            text="Độ chính xác",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        accuracy_frame.pack(fill=tk.X, pady=10)
        
        slider_frame = tk.Frame(accuracy_frame, bg=cfg.LIGHT_BG_COLOR)
        slider_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(slider_frame, text="Độ chính xác (%):", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=5)
        self.variables["accuracy_var"] = tk.StringVar(value=self.parameters.get("accuracy", "80"))
        
        accuracy_scale = ttk.Scale(
            slider_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=lambda v: self.variables["accuracy_var"].set(str(int(float(v))))
        )
        accuracy_scale.set(int(self.variables["accuracy_var"].get()))
        accuracy_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        accuracy_value = ttk.Entry(
            slider_frame,
            textvariable=self.variables["accuracy_var"],
            width=5,
            validate="key",
            validatecommand=self.validate_int_cmd
        )
        accuracy_value.pack(side=tk.LEFT, padx=5)
        
        # Sync scale with textbox
        def update_scale(*args):
            try:
                value = int(self.variables["accuracy_var"].get())
                if 0 <= value <= 100:
                    accuracy_scale.set(value)
            except ValueError:
                pass
        
        self.variables["accuracy_var"].trace_add("write", update_scale)
    
    def get_parameters(self):
        """Collect all parameters"""
        params = super().get_parameters()
        
        # Image-specific params
        params["image_path"] = self.variables["image_path_var"].get()
        params["accuracy"] = self.variables["accuracy_var"].get()
        
        return params
