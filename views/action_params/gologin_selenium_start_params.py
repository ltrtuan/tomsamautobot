# views/action_params/gologin_selenium_start_params.py

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import config as cfg
from views.action_params.base_params import BaseActionParams

class GoLoginSeleniumStartParams(BaseActionParams):
    """UI for GoLogin Selenium Start Profile action - Fast import cookies"""
    
    def __init__(self, parent_frame, parameters=None):
        super().__init__(parent_frame, parameters)
        self.youtube_option_frame = None  # Track Youtube Option frame
        self.youtube_select_area_button = None  # Track Select area button
        self.youtube_sidebar_select_area_button = None  # Track Sidebar Select area button


    
    def create_params(self):
        """Create UI parameters"""
        self.clear_frame()
        
        # ========== API KEY VARIABLE SECTION ==========
        self.create_api_key_variable_section()
        
        # ========== ACTION TYPE SECTION ==========
        self.create_youtube_option_section()  # YOUTUBE OPTION SECTION
        
        self.create_action_type_section()
        
        
        self.create_suffix_prefix_section()
        
        # ========== KEYWORDS YOUTUBE SECTION ==========
        self.create_keywords_youtube_section()

        # ========== KEYWORDS GOOGLE SECTION ==========
        self.create_keywords_google_section()
        
        # ========== PROFILE IDs SECTION ==========
        self.create_profile_ids_section()
        
        # ========== HOW TO GET PROFILE SECTION ==========
        self.create_how_to_get_profile_section()
        
        # ========== OPTIONS SECTION (BỎ HEADLESS VÀ MULTI-THREADING) ==========
        self.create_options_section()
       
        
        # ========== COMMON PARAMETERS ==========
        self.create_common_params(
            show_variable=True,
            show_random_time=True,
            show_repeat=True,
            show_random_skip=True
        )
        
        # ========== BREAK CONDITIONS ==========
        self.create_break_conditions()
        
        # ========== PROGRAM SELECTOR ==========
        select_program_button = self.create_program_selector()
        
        return {
            'select_program_button': select_program_button,
            'youtube_select_area_button': self.youtube_select_area_button,
            'youtube_sidebar_select_area_button': self.youtube_sidebar_select_area_button
        }
    
    def create_api_key_variable_section(self):
        """API Key Variable name input"""
        api_frame = tk.LabelFrame(
            self.parent_frame,
            text="GoLogin API Key Variable",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        api_frame.pack(fill=tk.X, pady=10)
        
        label = tk.Label(
            api_frame,
            text="Variable name containing API token:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(anchor=tk.W, pady=(0, 5))
        
        self.api_key_var = tk.StringVar()
        if self.parameters:
            self.api_key_var.set(self.parameters.get("api_key_variable", "GOLOGIN_API_KEY"))
        else:
            self.api_key_var.set("GOLOGIN_API_KEY")
        
        entry = ttk.Entry(
            api_frame,
            textvariable=self.api_key_var,
            width=30
        )
        entry.pack(anchor=tk.W, padx=5)
    
    def create_youtube_option_section(self):
        """Youtube Option section - only show when Action Type is Youtube"""
        # Frame chính - KHÔNG PACK NGAY
        self.youtube_option_frame = tk.LabelFrame(
            self.parent_frame,
            text="Youtube Option",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
    
        # ========== MAIN AREA YOUTUBE SECTION ==========
        main_area_label = tk.Label(
            self.youtube_option_frame,
            text="Main Area Youtube:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        main_area_label.pack(anchor=tk.W, pady=(5, 3))
    
        # Frame chứa 4 inputs + Select area button
        coords_frame = tk.Frame(self.youtube_option_frame, bg=cfg.LIGHT_BG_COLOR)
        coords_frame.pack(fill=tk.X, pady=(0, 10))
    
        # X coordinate
        tk.Label(
            coords_frame,
            text="X:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=(0, 5))
    
        self.youtube_main_area_x_var = tk.StringVar()
        if self.parameters:
            self.youtube_main_area_x_var.set(self.parameters.get("youtube_main_area_x", "0"))
        else:
            self.youtube_main_area_x_var.set("0")
    
        x_entry = ttk.Entry(coords_frame, textvariable=self.youtube_main_area_x_var, width=8)
        x_entry.pack(side=tk.LEFT, padx=5)
    
        # Y coordinate
        tk.Label(
            coords_frame,
            text="Y:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=(15, 5))
    
        self.youtube_main_area_y_var = tk.StringVar()
        if self.parameters:
            self.youtube_main_area_y_var.set(self.parameters.get("youtube_main_area_y", "0"))
        else:
            self.youtube_main_area_y_var.set("0")
    
        y_entry = ttk.Entry(coords_frame, textvariable=self.youtube_main_area_y_var, width=8)
        y_entry.pack(side=tk.LEFT, padx=5)
    
        # Width
        tk.Label(
            coords_frame,
            text="Width:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=(15, 5))
    
        self.youtube_main_area_width_var = tk.StringVar()
        if self.parameters:
            self.youtube_main_area_width_var.set(self.parameters.get("youtube_main_area_width", "1920"))
        else:
            self.youtube_main_area_width_var.set("1920")
    
        width_entry = ttk.Entry(coords_frame, textvariable=self.youtube_main_area_width_var, width=8)
        width_entry.pack(side=tk.LEFT, padx=5)
    
        # Height
        tk.Label(
            coords_frame,
            text="Height:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=(15, 5))
    
        self.youtube_main_area_height_var = tk.StringVar()
        if self.parameters:
            self.youtube_main_area_height_var.set(self.parameters.get("youtube_main_area_height", "1080"))
        else:
            self.youtube_main_area_height_var.set("1080")
    
        height_entry = ttk.Entry(coords_frame, textvariable=self.youtube_main_area_height_var, width=8)
        height_entry.pack(side=tk.LEFT, padx=5)
    
        # Button "Select area" - KHÔNG GÁN command
        self.youtube_select_area_button = ttk.Button(
            coords_frame,
            text="Select area",
            command=self.on_youtube_select_area_click
        )
        self.youtube_select_area_button.pack(side=tk.LEFT, padx=(15, 0))
    
        # ========== IMAGE SEARCH MAIN AREA SECTION ==========
        separator = ttk.Separator(self.youtube_option_frame, orient="horizontal")
        separator.pack(fill=tk.X, pady=10)
    
        image_label = tk.Label(
            self.youtube_option_frame,
            text="Image Search Main Area:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        image_label.pack(anchor=tk.W, pady=(5, 3))
    
        # Frame browse image
        image_browse_frame = tk.Frame(self.youtube_option_frame, bg=cfg.LIGHT_BG_COLOR)
        image_browse_frame.pack(fill=tk.X, pady=(0, 5))
    
        tk.Label(
            image_browse_frame,
            text="Đường dẫn hình ảnh:",
            bg=cfg.LIGHT_BG_COLOR
        ).pack(side=tk.LEFT, padx=(0, 5))
    
        self.youtube_image_search_path_var = tk.StringVar()
        if self.parameters:
            self.youtube_image_search_path_var.set(self.parameters.get("youtube_image_search_path", ""))
        else:
            self.youtube_image_search_path_var.set("")
    
        image_entry = ttk.Entry(
            image_browse_frame,
            textvariable=self.youtube_image_search_path_var,
            width=40
        )
        image_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
    
        # Browse button
        def browse_youtube_image():
            filename = filedialog.askopenfilename(
                title="Chọn một hình ảnh",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                    ("All files", "*.*")
                ]
            )
            if filename:
                self.youtube_image_search_path_var.set(filename)
                print(f"[YOUTUBE_OPTION] Selected image: {filename}")
    
        browse_button = ttk.Button(
            image_browse_frame,
            text="Duyệt...",
            command=browse_youtube_image
        )
        browse_button.pack(side=tk.RIGHT, padx=5)
        
        # ========== SIDEBAR AREA YOUTUBE SECTION ==========
        separator2 = ttk.Separator(self.youtube_option_frame, orient="horizontal")
        separator2.pack(fill=tk.X, pady=10)

        sidebar_area_label = tk.Label(
            self.youtube_option_frame,
            text="Sidebar Area Youtube:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        sidebar_area_label.pack(anchor=tk.W, pady=(5, 3))

        # Frame chứa 4 inputs + Select area button cho Sidebar
        sidebar_coords_frame = tk.Frame(self.youtube_option_frame, bg=cfg.LIGHT_BG_COLOR)
        sidebar_coords_frame.pack(fill=tk.X, pady=(0, 10))

        # X coordinate
        tk.Label(
            sidebar_coords_frame,
            text="X:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.youtube_sidebar_area_x_var = tk.StringVar()
        if self.parameters:
            self.youtube_sidebar_area_x_var.set(self.parameters.get("youtube_sidebar_area_x", "0"))
        else:
            self.youtube_sidebar_area_x_var.set("0")

        sidebar_x_entry = ttk.Entry(sidebar_coords_frame, textvariable=self.youtube_sidebar_area_x_var, width=8)
        sidebar_x_entry.pack(side=tk.LEFT, padx=5)

        # Y coordinate
        tk.Label(
            sidebar_coords_frame,
            text="Y:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=(15, 5))

        self.youtube_sidebar_area_y_var = tk.StringVar()
        if self.parameters:
            self.youtube_sidebar_area_y_var.set(self.parameters.get("youtube_sidebar_area_y", "0"))
        else:
            self.youtube_sidebar_area_y_var.set("0")

        sidebar_y_entry = ttk.Entry(sidebar_coords_frame, textvariable=self.youtube_sidebar_area_y_var, width=8)
        sidebar_y_entry.pack(side=tk.LEFT, padx=5)

        # Width
        tk.Label(
            sidebar_coords_frame,
            text="Width:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=(15, 5))

        self.youtube_sidebar_area_width_var = tk.StringVar()
        if self.parameters:
            self.youtube_sidebar_area_width_var.set(self.parameters.get("youtube_sidebar_area_width", "400"))
        else:
            self.youtube_sidebar_area_width_var.set("400")

        sidebar_width_entry = ttk.Entry(sidebar_coords_frame, textvariable=self.youtube_sidebar_area_width_var, width=8)
        sidebar_width_entry.pack(side=tk.LEFT, padx=5)

        # Height
        tk.Label(
            sidebar_coords_frame,
            text="Height:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=(15, 5))

        self.youtube_sidebar_area_height_var = tk.StringVar()
        if self.parameters:
            self.youtube_sidebar_area_height_var.set(self.parameters.get("youtube_sidebar_area_height", "1080"))
        else:
            self.youtube_sidebar_area_height_var.set("1080")

        sidebar_height_entry = ttk.Entry(sidebar_coords_frame, textvariable=self.youtube_sidebar_area_height_var, width=8)
        sidebar_height_entry.pack(side=tk.LEFT, padx=5)

        # Button "Select area" cho Sidebar - Bind command
        self.youtube_sidebar_select_area_button = ttk.Button(
            sidebar_coords_frame,
            text="Select area",
            command=self.on_youtube_sidebar_select_area_click
        )
        self.youtube_sidebar_select_area_button.pack(side=tk.LEFT, padx=(15, 0))

        # ========== IMAGE SEARCH SIDEBAR AREA SECTION ==========
        separator3 = ttk.Separator(self.youtube_option_frame, orient="horizontal")
        separator3.pack(fill=tk.X, pady=10)

        sidebar_image_label = tk.Label(
            self.youtube_option_frame,
            text="Image Search Sidebar Area:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        sidebar_image_label.pack(anchor=tk.W, pady=(5, 3))

        # Frame browse image cho Sidebar
        sidebar_image_browse_frame = tk.Frame(self.youtube_option_frame, bg=cfg.LIGHT_BG_COLOR)
        sidebar_image_browse_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(
            sidebar_image_browse_frame,
            text="Đường dẫn hình ảnh:",
            bg=cfg.LIGHT_BG_COLOR
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.youtube_sidebar_image_search_path_var = tk.StringVar()
        if self.parameters:
            self.youtube_sidebar_image_search_path_var.set(self.parameters.get("youtube_sidebar_image_search_path", ""))
        else:
            self.youtube_sidebar_image_search_path_var.set("")

        sidebar_image_entry = ttk.Entry(
            sidebar_image_browse_frame,
            textvariable=self.youtube_sidebar_image_search_path_var,
            width=40
        )
        sidebar_image_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)

        # Browse button cho Sidebar
        def browse_youtube_sidebar_image():
            filename = filedialog.askopenfilename(
                title="Chọn một hình ảnh",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                    ("All files", "*.*")
                ]
            )
            if filename:
                self.youtube_sidebar_image_search_path_var.set(filename)
                print(f"[YOUTUBE_OPTION_SIDEBAR] Selected image: {filename}")

        browse_sidebar_button = ttk.Button(
            sidebar_image_browse_frame,
            text="Duyệt...",
            command=browse_youtube_sidebar_image
        )
        browse_sidebar_button.pack(side=tk.RIGHT, padx=5)


    def on_youtube_select_area_click(self):
        """Handler khi click button Select area của Youtube Option"""
        from views.screen_area_selector import ScreenAreaSelector
    
        # Callback để update các textboxes
        def update_coords(x, y, width, height):
            self.youtube_main_area_x_var.set(str(x))
            self.youtube_main_area_y_var.set(str(y))
            self.youtube_main_area_width_var.set(str(width))
            self.youtube_main_area_height_var.set(str(height))
            print(f"[YOUTUBE_SELECT_AREA] Updated: x={x}, y={y}, w={width}, h={height}")
    
        # Tìm dialog cha (ActionDialogView)
        dialog = self.parent_frame.winfo_toplevel()
    
        # Tạo và show selector
        selector = ScreenAreaSelector(
            parent_dialog=dialog,
            callback=update_coords
        )
        selector.show()

    def on_youtube_sidebar_select_area_click(self):
        """Handler khi click button Select area của Sidebar Youtube Option"""
        from views.screen_area_selector import ScreenAreaSelector
    
        # Callback để update các textboxes
        def update_coords(x, y, width, height):
            self.youtube_sidebar_area_x_var.set(str(x))
            self.youtube_sidebar_area_y_var.set(str(y))
            self.youtube_sidebar_area_width_var.set(str(width))
            self.youtube_sidebar_area_height_var.set(str(height))
            print(f"[YOUTUBE_SIDEBAR_SELECT_AREA] Updated: x={x}, y={y}, w={width}, h={height}")
    
        # Tìm dialog cha (ActionDialogView)
        dialog = self.parent_frame.winfo_toplevel()
    
        # Tạo và show selector
        selector = ScreenAreaSelector(
            parent_dialog=dialog,
            callback=update_coords
        )
        selector.show()


    def create_how_to_get_profile_section(self):
        """How to get profile selection"""
        get_frame = tk.Frame(self.parent_frame, bg=cfg.LIGHT_BG_COLOR)
        get_frame.pack(fill=tk.X, pady=5, padx=10)
        
        label = tk.Label(
            get_frame,
            text="How to get Profile:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.how_to_get_var = tk.StringVar()
        if self.parameters:
            self.how_to_get_var.set(self.parameters.get("how_to_get", "Random"))
        else:
            self.how_to_get_var.set("Random")
        
        combo = ttk.Combobox(
            get_frame,
            textvariable=self.how_to_get_var,
            values=["Random", "Sequential by loop"],
            state="readonly",
            width=20
        )
        combo.pack(side=tk.LEFT, padx=5)
        
    def create_keywords_youtube_section(self):
        """Keywords Youtube file browse section"""
        keywords_frame = tk.LabelFrame(
            self.parent_frame,
            text="Search Keywords Youtube",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        keywords_frame.pack(fill=tk.X, pady=10)
    
        # Option 1: Browse keywords TXT file
        keywords_browse_label = tk.Label(
            keywords_frame,
            text="Option 1: Keywords TXT file (one keyword per line):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        )
        keywords_browse_label.pack(anchor=tk.W, pady=(0, 3))
    
        keywords_browse_frame = tk.Frame(keywords_frame, bg=cfg.LIGHT_BG_COLOR)
        keywords_browse_frame.pack(fill=tk.X, pady=(0, 10))
    
        self.keywords_file_var = tk.StringVar()
        if self.parameters:
            self.keywords_file_var.set(self.parameters.get("keywords_file", ""))
    
        keywords_entry = tk.Entry(
            keywords_browse_frame,
            textvariable=self.keywords_file_var,
            font=("Segoe UI", 10)
        )
        keywords_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    
        def browse_keywords_file():
            filename = filedialog.askopenfilename(
                title="Select Keywords TXT File",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                self.keywords_file_var.set(filename)
    
        browse_keywords_button = ttk.Button(
            keywords_browse_frame,
            text="Browse",
            command=browse_keywords_file
        )
        browse_keywords_button.pack(side=tk.LEFT)
    
        # Option 2: Variable name
        keywords_var_label = tk.Label(
            keywords_frame,
            text="Option 2: Variable name containing keywords TXT file path:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        )
        keywords_var_label.pack(anchor=tk.W, pady=(0, 3))
    
        self.keywords_variable_var = tk.StringVar()
        if self.parameters:
            self.keywords_variable_var.set(self.parameters.get("keywords_variable", ""))
    
        keywords_var_entry = tk.Entry(
            keywords_frame,
            textvariable=self.keywords_variable_var,
            font=("Segoe UI", 10)
        )
        keywords_var_entry.pack(fill=tk.X, pady=(0, 5))
    
        # Hint
        keywords_hint = tk.Label(
            keywords_frame,
            text="💡 Keywords will be used when Action Type is YouTube. Random keyword per search.",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666",
            wraplength=500,
            justify=tk.LEFT
        )
        keywords_hint.pack(anchor=tk.W)


    def create_keywords_google_section(self):
        """Keywords Google file browse section"""
        keywords_google_frame = tk.LabelFrame(
            self.parent_frame,
            text="Search Keywords Google",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        keywords_google_frame.pack(fill=tk.X, pady=10)
    
        # Option 1: Browse keywords TXT file
        keywords_google_browse_label = tk.Label(
            keywords_google_frame,
            text="Option 1: Keywords TXT file (one keyword per line):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        )
        keywords_google_browse_label.pack(anchor=tk.W, pady=(0, 3))
    
        keywords_google_browse_frame = tk.Frame(keywords_google_frame, bg=cfg.LIGHT_BG_COLOR)
        keywords_google_browse_frame.pack(fill=tk.X, pady=(0, 10))
    
        self.keywords_google_file_var = tk.StringVar()
        if self.parameters:
            self.keywords_google_file_var.set(self.parameters.get("keywords_google_file", ""))
    
        keywords_google_entry = tk.Entry(
            keywords_google_browse_frame,
            textvariable=self.keywords_google_file_var,
            font=("Segoe UI", 10)
        )
        keywords_google_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    
        def browse_keywords_google_file():
            filename = filedialog.askopenfilename(
                title="Select Keywords TXT File",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                self.keywords_google_file_var.set(filename)
    
        browse_keywords_google_button = ttk.Button(
            keywords_google_browse_frame,
            text="Browse",
            command=browse_keywords_google_file
        )
        browse_keywords_google_button.pack(side=tk.LEFT)
    
        # Option 2: Variable name
        keywords_google_var_label = tk.Label(
            keywords_google_frame,
            text="Option 2: Variable name containing keywords TXT file path:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        )
        keywords_google_var_label.pack(anchor=tk.W, pady=(0, 3))
    
        self.keywords_google_variable_var = tk.StringVar()
        if self.parameters:
            self.keywords_google_variable_var.set(self.parameters.get("keywords_google_variable", ""))
    
        keywords_google_var_entry = tk.Entry(
            keywords_google_frame,
            textvariable=self.keywords_google_variable_var,
            font=("Segoe UI", 10)
        )
        keywords_google_var_entry.pack(fill=tk.X, pady=(0, 5))
    
        # Hint
        keywords_google_hint = tk.Label(
            keywords_google_frame,
            text="💡 Keywords will be used when Action Type is Google. Random keyword per search.",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666",
            wraplength=500,
            justify=tk.LEFT
        )
        keywords_google_hint.pack(anchor=tk.W)

    
    def create_options_section(self):
        """Options checkboxes and cookies import - BỎ HEADLESS VÀ MULTI-THREADING"""
        options_frame = tk.LabelFrame(
            self.parent_frame,
            text="Profile Options",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        options_frame.pack(fill=tk.X, pady=10)
        
        # Refresh fingerprint checkbox
        self.refresh_fingerprint_var = tk.BooleanVar()
        if self.parameters:
            self.refresh_fingerprint_var.set(self.parameters.get("refresh_fingerprint", False))
        else:
            self.refresh_fingerprint_var.set(False)
        
        refresh_cb = tk.Checkbutton(
            options_frame,
            text="Refresh fingerprint before warming up",
            variable=self.refresh_fingerprint_var,
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        refresh_cb.pack(anchor=tk.W, pady=2)      
        
        
        
        # ========== PROXY CONFIGURATION SECTION ==========
        separator_proxy = ttk.Separator(options_frame, orient='horizontal')
        separator_proxy.pack(fill=tk.X, pady=10)

        self.remove_proxy_var = tk.BooleanVar()
        if self.parameters:
            self.remove_proxy_var.set(self.parameters.get("remove_proxy", False))
        else:
            self.remove_proxy_var.set(False)

        remove_proxy_cb = tk.Checkbutton(
            options_frame,
            text="Remove proxy of profile before warming up",
            variable=self.remove_proxy_var,
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        remove_proxy_cb.pack(anchor=tk.W, pady=2)

        proxy_file_label = tk.Label(
            options_frame,
            text="Proxy File (Optional - TXT format type://host:port:user:pass per line):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        proxy_file_label.pack(anchor=tk.W, pady=(5, 2))

        proxy_browse_frame = tk.Frame(options_frame, bg=cfg.LIGHT_BG_COLOR)
        proxy_browse_frame.pack(fill=tk.X, pady=(0, 10))

        self.proxy_file_var = tk.StringVar()
        if self.parameters:
            self.proxy_file_var.set(self.parameters.get("proxy_file", ""))

        proxy_entry = tk.Entry(proxy_browse_frame, textvariable=self.proxy_file_var, font=("Segoe UI", 10))
        proxy_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        def browse_proxy_file():
            filename = filedialog.askopenfilename(
                title="Select Proxy TXT File",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                self.proxy_file_var.set(filename)

        browse_proxy_button = ttk.Button(proxy_browse_frame, text="Browse...", command=browse_proxy_file)
        browse_proxy_button.pack(side=tk.LEFT)

        proxy_file_hint = tk.Label(
            options_frame,
            text="File format example:\nhttp://1.2.3.4:8080:user:pass\nsocks5://5.6.7.8:1080:youruser:yourpass\nProxies will be assigned to profiles sequentially or randomly.",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666",
            wraplength=500,
            justify=tk.LEFT
        )
        proxy_file_hint.pack(anchor=tk.W)

        # ========== THÊM MULTI-THREADING SECTION ==========
    
        separator = ttk.Separator(options_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)
        
        # ========== THÊM HEADLESS CHECKBOX ==========
        self.headless_var = tk.BooleanVar()
        if self.parameters:
            self.headless_var.set(self.parameters.get("headless", False))
        else:
            self.headless_var.set(False)
    
        headless_cb = tk.Checkbutton(
            options_frame,
            text="Run in Headless mode (no browser UI, faster but harder to debug)",
            variable=self.headless_var,
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        headless_cb.pack(anchor=tk.W, pady=2)

        threading_label = tk.Label(
            options_frame,
            text="Multi-Threading (Parallel Start):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        threading_label.pack(anchor=tk.W, pady=(5, 2))

        # Enable multi-threading checkbox
        self.enable_threading_var = tk.BooleanVar()
        if self.parameters:
            self.enable_threading_var.set(self.parameters.get("enable_threading", False))
        else:
            self.enable_threading_var.set(False)

        threading_cb = tk.Checkbutton(
            options_frame,
            text="Enable Multi-Threading (start multiple profiles simultaneously)",
            variable=self.enable_threading_var,
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        threading_cb.pack(anchor=tk.W, pady=2)

        # Max workers input
        workers_frame = tk.Frame(options_frame, bg=cfg.LIGHT_BG_COLOR)
        workers_frame.pack(fill=tk.X, pady=5)

        workers_label = tk.Label(
            workers_frame,
            text="Max parallel profiles:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        )
        workers_label.pack(side=tk.LEFT, padx=(20, 5))

        self.max_workers_var = tk.StringVar()
        if self.parameters:
            self.max_workers_var.set(self.parameters.get("max_workers", "3"))
        else:
            self.max_workers_var.set("3")

        workers_entry = ttk.Entry(
            workers_frame,
            textvariable=self.max_workers_var,
            width=5
        )
        workers_entry.pack(side=tk.LEFT, padx=5)

        workers_hint = tk.Label(
            workers_frame,
            text="(Recommended: 3-5 for normal PC)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666"
        )
        workers_hint.pack(side=tk.LEFT, padx=5)

        
    def create_action_type_section(self):
        """Action type selection: None, Youtube, Google"""
        action_frame = tk.LabelFrame(
            self.parent_frame,
            text="Action Type",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        action_frame.pack(fill=tk.X, pady=10)
    
        self.action_type_var = tk.StringVar()
        if self.parameters:
            self.action_type_var.set(self.parameters.get("action_type", "None"))
        else:
            self.action_type_var.set("None")
    
        radio_frame = tk.Frame(action_frame, bg=cfg.LIGHT_BG_COLOR)
        radio_frame.pack(anchor=tk.W)
    
        tk.Radiobutton(
            radio_frame,
            text="None (just start profile)",
            variable=self.action_type_var,
            value="None",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=10)
    
        tk.Radiobutton(
            radio_frame,
            text="YouTube Search",
            variable=self.action_type_var,
            value="Youtube",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=10)
    
        tk.Radiobutton(
            radio_frame,
            text="Google Search",
            variable=self.action_type_var,
            value="Google",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=10)

        # Callback để show/hide Youtube Option frame
        def on_action_type_change(*args):
            if self.action_type_var.get() == "Youtube":
                # Pack Youtube Option frame SAU action_frame
                self.youtube_option_frame.pack(fill=tk.X, pady=10, after=action_frame)
            else:
                self.youtube_option_frame.pack_forget()

        # Bind callback
        self.action_type_var.trace_add("write", on_action_type_change)

        # Trigger initial state
        on_action_type_change()



    def create_profile_ids_section(self):
        """Profile IDs textarea with range selection"""
        text_frame = tk.LabelFrame(
            self.parent_frame,
            text="Profile IDs",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # ========== THAY THẾ: 2 TEXTBOX INTEGER RANGE ==========
        range_frame = tk.Frame(text_frame, bg=cfg.LIGHT_BG_COLOR)
        range_frame.pack(fill=tk.X, pady=(0, 10))

        # How many profiles
        tk.Label(
            range_frame,
            text="How many profiles to use:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.profile_count_var = tk.StringVar()
        if self.parameters:
            self.profile_count_var.set(self.parameters.get("profile_count", "30"))
        else:
            self.profile_count_var.set("30")

        count_entry = ttk.Entry(
            range_frame,
            textvariable=self.profile_count_var,
            width=10
        )
        count_entry.pack(side=tk.LEFT, padx=5)

        # From profile index
        tk.Label(
            range_frame,
            text="From profile index:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=(15, 5))

        self.profile_start_index_var = tk.StringVar()
        if self.parameters:
            self.profile_start_index_var.set(self.parameters.get("profile_start_index", "0"))
        else:
            self.profile_start_index_var.set("0")

        start_entry = ttk.Entry(
            range_frame,
            textvariable=self.profile_start_index_var,
            width=10
        )
        start_entry.pack(side=tk.LEFT, padx=5)

        # Hint
        hint_label = tk.Label(
            text_frame,
            text="💡 Example: Count=30, Start=10 → Use profiles from index 10 to 39 (30 profiles total)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666",
            wraplength=500,
            justify=tk.LEFT
        )
        hint_label.pack(anchor=tk.W, pady=(0, 10))

        # ========== PROFILE IDS TEXTAREA (EXISTING) ==========
        label_text = (
            "OR manually enter Profile IDs separated by ';'. Special formats:\n"
            " <variable_name> to use variable value\n"
            "Example: 68e485dd;<profile_var>;68e486ab\n"
            "(Leave empty to use range above)"
        )
        label = tk.Label(
            text_frame,
            text=label_text,
            bg=cfg.LIGHT_BG_COLOR,
            justify=tk.LEFT,
            wraplength=500
        )
        label.pack(anchor=tk.W, pady=(0, 5))

        self.profile_ids_input = scrolledtext.ScrolledText(
            text_frame,
            height=4,
            width=50,
            wrap=tk.WORD,
            font=("Segoe UI", 10)
        )
        self.profile_ids_input.pack(fill=tk.BOTH, expand=True)

        if self.parameters:
            profile_ids = self.parameters.get("profile_ids", "")
            self.profile_ids_input.insert("1.0", profile_ids)

    
    def create_suffix_prefix_section(self):
        """Suffix & Prefix for keyword variations - SINGLE INPUT"""
        suffix_prefix_frame = tk.LabelFrame(
            self.parent_frame,
            text="Keyword Suffix & Prefix (Optional)",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
        suffix_prefix_frame.pack(fill=tk.X, pady=10)
    
        # Hint - UPDATED
        hint_label = tk.Label(
            suffix_prefix_frame,
            text="💡 30% keywords will use suffix/prefix variations. Enter multiple values separated by semicolon (;).",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666",
            wraplength=500,
            justify=tk.LEFT
        )
        hint_label.pack(anchor=tk.W, pady=(0, 10))
    
        # Label - UPDATED
        label = tk.Label(
            suffix_prefix_frame,
            text="Suffix & Prefix (semicolon-separated):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 9)
        )
        label.pack(anchor=tk.W, pady=(0, 3))
    
        # Single input
        self.keywords_suffix_prefix_var = tk.StringVar()
        if self.parameters:
            self.keywords_suffix_prefix_var.set(self.parameters.get("keywords_suffix_prefix", ""))
    
        entry = tk.Entry(
            suffix_prefix_frame,
            textvariable=self.keywords_suffix_prefix_var,
            font=("Segoe UI", 10)
        )
        entry.pack(fill=tk.X, pady=(0, 5))
    
        # Example - UPDATED
        example_label = tk.Label(
            suffix_prefix_frame,
            text="Example: 'watch; how to; video; tutorial' → random pick one per keyword",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8, "italic"),
            fg="#999999"
        )
        example_label.pack(anchor=tk.W)


    def get_parameters(self):
        """Collect parameters - COPY NGUYÊN NHƯNG BỎ duration_minutes, headless, enable_threading, max_workers"""
        params = super().get_parameters()
        
        params["api_key_variable"] = self.api_key_var.get().strip()
        params["profile_ids"] = self.profile_ids_input.get("1.0", tk.END).strip()
        params["how_to_get"] = self.how_to_get_var.get()
        
        # Options
        params["refresh_fingerprint"] = self.refresh_fingerprint_var.get()
        
        # Proxy params
        params["proxy_file"] = self.proxy_file_var.get().strip()
        params["remove_proxy"] = self.remove_proxy_var.get()
        
        params["profile_count"] = self.profile_count_var.get().strip()
        params["profile_start_index"] = self.profile_start_index_var.get().strip()
        params["action_type"] = self.action_type_var.get()
        
        params["keywords_file"] = self.keywords_file_var.get().strip()
        params["keywords_variable"] = self.keywords_variable_var.get().strip()
        # NEW - Google keywords
        params["keywords_google_file"] = self.keywords_google_file_var.get().strip()
        params["keywords_google_variable"] = self.keywords_google_variable_var.get().strip()
        # Suffix & Prefix param (SINGLE FIELD)
        params["keywords_suffix_prefix"] = self.keywords_suffix_prefix_var.get().strip()
        
        params["headless"] = self.headless_var.get()
        params["enable_threading"] = self.enable_threading_var.get()
        params["max_workers"] = self.max_workers_var.get().strip()
        
        # Youtube Option params
        params["youtube_main_area_x"] = self.youtube_main_area_x_var.get().strip()
        params["youtube_main_area_y"] = self.youtube_main_area_y_var.get().strip()
        params["youtube_main_area_width"] = self.youtube_main_area_width_var.get().strip()
        params["youtube_main_area_height"] = self.youtube_main_area_height_var.get().strip()
        params["youtube_image_search_path"] = self.youtube_image_search_path_var.get().strip()

        # Youtube Sidebar Option params
        params["youtube_sidebar_area_x"] = self.youtube_sidebar_area_x_var.get().strip()
        params["youtube_sidebar_area_y"] = self.youtube_sidebar_area_y_var.get().strip()
        params["youtube_sidebar_area_width"] = self.youtube_sidebar_area_width_var.get().strip()
        params["youtube_sidebar_area_height"] = self.youtube_sidebar_area_height_var.get().strip()
        params["youtube_sidebar_image_search_path"] = self.youtube_sidebar_image_search_path_var.get().strip()

        

        return params
