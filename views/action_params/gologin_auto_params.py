# views/action_params/gologin_selenium_start_params.py

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import config as cfg
from views.action_params.base_params import BaseActionParams

class GoLoginAutoParams(BaseActionParams):
    """UI for GoLogin Selenium Start Profile action - Fast import cookies"""
    
    def __init__(self, parent_frame, parameters=None):
        super().__init__(parent_frame, parameters)
        self.youtube_option_frame = None  # Track Youtube Option frame
        self.youtube_select_area_button = None  # Track Select area button
        self.youtube_sidebar_select_area_button = None  # Track Sidebar Select area button
        self.youtube_ads_select_area_button = None
        self.youtube_skip_ads_select_area_button = None
        self.youtube_search_area_select_area_button = None  # Track Search Area select button

        # NEW: Multi-channel tracking
        self.youtube_channels = []  # List of channel configs
        self.youtube_channels_container = None  # Container frame for channels
    
    def create_params(self):
        """Create UI parameters"""
        self.clear_frame()
        
        # ========== API KEY VARIABLE SECTION ==========
        self.create_api_key_variable_section()
        
        # ========== ACTION TYPE SECTION ==========
        self.create_youtube_option_section()  # YOUTUBE OPTION SECTION
        
        self.create_action_type_section()

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
            'youtube_sidebar_select_area_button': self.youtube_sidebar_select_area_button,
            'youtube_ads_select_area_button': self.youtube_ads_select_area_button,
            'youtube_skip_ads_select_area_button': self.youtube_skip_ads_select_area_button
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
        """Youtube Option section - Multi-channel support (Channels at TOP)"""
    
        # Frame chính
        self.youtube_option_frame = tk.LabelFrame(
            self.parent_frame,
            text="Youtube Option",
            bg=cfg.LIGHT_BG_COLOR,
            pady=10,
            padx=10
        )
    
        # ========== BROWSE YOUTUBE CHECKBOX (GLOBAL) ==========
        self.browse_youtube_var = tk.BooleanVar()
        if self.parameters:
            self.browse_youtube_var.set(self.parameters.get("browse_youtube", False))
        else:
            self.browse_youtube_var.set(False)
    
        browse_cb = tk.Checkbutton(
            self.youtube_option_frame,
            text="Browse Youtube (warmup, collect cookie youtube)",
            variable=self.browse_youtube_var,
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        browse_cb.pack(anchor=tk.W, pady=(0, 10))
    
        # ========== SEPARATOR ==========
        separator_channels = ttk.Separator(self.youtube_option_frame, orient="horizontal")
        separator_channels.pack(fill=tk.X, pady=10)
    
        # ========== MULTI-CHANNEL SECTION (TOP) ==========
        # Add Channel button
        add_channel_button = ttk.Button(
            self.youtube_option_frame,
            text="➕ Add Channel",
            command=self.add_youtube_channel
        )
        add_channel_button.pack(anchor=tk.W, pady=(0, 10))
    
        # Channels container
        self.youtube_channels_container = tk.Frame(
            self.youtube_option_frame,
            bg=cfg.LIGHT_BG_COLOR
        )
        self.youtube_channels_container.pack(fill=tk.BOTH, expand=True)
    
        # ========== LOAD CHANNELS (Create/Edit mode) ==========
        if self.parameters and "youtube_channels" in self.parameters:
            # EDIT MODE: Load existing channels từ parameters
            channels_data = self.parameters["youtube_channels"]
            if channels_data:
                for channel_data in channels_data:
                    self._add_youtube_channel_from_data(channel_data)
                print(f"[UI] Loaded {len(channels_data)} channel(s) from parameters")
            else:
                # Empty youtube_channels array → Add default Channel 1
                self.add_youtube_channel()
        else:
            # CREATE MODE: Add empty Channel 1
            self.add_youtube_channel()

    
        # ========== SEPARATOR BEFORE GLOBAL PARAMS ==========
        separator_global = ttk.Separator(self.youtube_option_frame, orient="horizontal")
        separator_global.pack(fill=tk.X, pady=15)
    
        # ========== MAIN AREA YOUTUBE (GLOBAL) ==========
        main_area_label = tk.Label(
            self.youtube_option_frame,
            text="Main Area Youtube:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        main_area_label.pack(anchor=tk.W, pady=(5, 3))
    
        coords_frame = tk.Frame(self.youtube_option_frame, bg=cfg.LIGHT_BG_COLOR)
        coords_frame.pack(fill=tk.X, pady=(0, 10))
    
        # X
        tk.Label(coords_frame, text="X:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.youtube_main_area_x_var = tk.StringVar()
        if self.parameters:
            self.youtube_main_area_x_var.set(self.parameters.get("youtube_main_area_x", "0"))
        else:
            self.youtube_main_area_x_var.set("0")
        x_entry = ttk.Entry(coords_frame, textvariable=self.youtube_main_area_x_var, width=8)
        x_entry.pack(side=tk.LEFT, padx=5)
    
        # Y
        tk.Label(coords_frame, text="Y:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(15, 5))
        self.youtube_main_area_y_var = tk.StringVar()
        if self.parameters:
            self.youtube_main_area_y_var.set(self.parameters.get("youtube_main_area_y", "0"))
        else:
            self.youtube_main_area_y_var.set("0")
        y_entry = ttk.Entry(coords_frame, textvariable=self.youtube_main_area_y_var, width=8)
        y_entry.pack(side=tk.LEFT, padx=5)
    
        # Width
        tk.Label(coords_frame, text="Width:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(15, 5))
        self.youtube_main_area_width_var = tk.StringVar()
        if self.parameters:
            self.youtube_main_area_width_var.set(self.parameters.get("youtube_main_area_width", "1920"))
        else:
            self.youtube_main_area_width_var.set("1920")
        width_entry = ttk.Entry(coords_frame, textvariable=self.youtube_main_area_width_var, width=8)
        width_entry.pack(side=tk.LEFT, padx=5)
    
        # Height
        tk.Label(coords_frame, text="Height:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(15, 5))
        self.youtube_main_area_height_var = tk.StringVar()
        if self.parameters:
            self.youtube_main_area_height_var.set(self.parameters.get("youtube_main_area_height", "1080"))
        else:
            self.youtube_main_area_height_var.set("1080")
        height_entry = ttk.Entry(coords_frame, textvariable=self.youtube_main_area_height_var, width=8)
        height_entry.pack(side=tk.LEFT, padx=5)
    
        # Select area button
        self.youtube_select_area_button = ttk.Button(
            coords_frame,
            text="Select area",
            command=self.on_youtube_select_area_click
        )
        self.youtube_select_area_button.pack(side=tk.LEFT, padx=(15, 0))
        

        # ========== SEARCH AREA YOUTUBE (GLOBAL) ==========
        separator_search = ttk.Separator(self.youtube_option_frame, orient="horizontal")
        separator_search.pack(fill=tk.X, pady=10)

        search_area_label = tk.Label(
            self.youtube_option_frame,
            text="Search Area Youtube:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        search_area_label.pack(anchor=tk.W, pady=(5, 3))

        search_coords_frame = tk.Frame(self.youtube_option_frame, bg=cfg.LIGHT_BG_COLOR)
        search_coords_frame.pack(fill=tk.X, pady=(0, 10))

        # X
        tk.Label(search_coords_frame, text="X:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.youtube_search_area_x_var = tk.StringVar()
        if self.parameters:
            self.youtube_search_area_x_var.set(self.parameters.get("youtube_search_area_x", "0"))
        else:
            self.youtube_search_area_x_var.set("0")
        x_entry = ttk.Entry(search_coords_frame, textvariable=self.youtube_search_area_x_var, width=8)
        x_entry.pack(side=tk.LEFT, padx=5)

        # Y
        tk.Label(search_coords_frame, text="Y:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(15, 5))
        self.youtube_search_area_y_var = tk.StringVar()
        if self.parameters:
            self.youtube_search_area_y_var.set(self.parameters.get("youtube_search_area_y", "0"))
        else:
            self.youtube_search_area_y_var.set("0")
        y_entry = ttk.Entry(search_coords_frame, textvariable=self.youtube_search_area_y_var, width=8)
        y_entry.pack(side=tk.LEFT, padx=5)

        # Width
        tk.Label(search_coords_frame, text="Width:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(15, 5))
        self.youtube_search_area_width_var = tk.StringVar()
        if self.parameters:
            self.youtube_search_area_width_var.set(self.parameters.get("youtube_search_area_width", "800"))
        else:
            self.youtube_search_area_width_var.set("800")
        width_entry = ttk.Entry(search_coords_frame, textvariable=self.youtube_search_area_width_var, width=8)
        width_entry.pack(side=tk.LEFT, padx=5)

        # Height
        tk.Label(search_coords_frame, text="Height:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(15, 5))
        self.youtube_search_area_height_var = tk.StringVar()
        if self.parameters:
            self.youtube_search_area_height_var.set(self.parameters.get("youtube_search_area_height", "200"))
        else:
            self.youtube_search_area_height_var.set("200")
        height_entry = ttk.Entry(search_coords_frame, textvariable=self.youtube_search_area_height_var, width=8)
        height_entry.pack(side=tk.LEFT, padx=5)

        # Select area button
        self.youtube_search_area_select_area_button = ttk.Button(
            search_coords_frame,
            text="Select area",
            command=self.on_youtube_search_area_select_area_click
        )
        self.youtube_search_area_select_area_button.pack(side=tk.LEFT, padx=(15, 0))


    
        # ========== SEARCH ICON IMAGE (GLOBAL) ==========
        separator = ttk.Separator(self.youtube_option_frame, orient="horizontal")
        separator.pack(fill=tk.X, pady=10)
    
        search_icon_label = tk.Label(
            self.youtube_option_frame,
            text="Search Icon Image (for YouTube search box detection)",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        search_icon_label.pack(anchor=tk.W, pady=(5, 3))
    
        search_icon_browse_frame = tk.Frame(self.youtube_option_frame, bg=cfg.LIGHT_BG_COLOR)
        search_icon_browse_frame.pack(fill=tk.X, pady=(0, 5))
    
        tk.Label(search_icon_browse_frame, text="Đường dẫn hình ảnh:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=(0, 5))
    
        self.youtube_search_icon_path_var = tk.StringVar()
        if self.parameters:
            self.youtube_search_icon_path_var.set(self.parameters.get("youtube_search_icon_path", ""))
        else:
            self.youtube_search_icon_path_var.set("")
    
        search_icon_entry = ttk.Entry(search_icon_browse_frame, textvariable=self.youtube_search_icon_path_var, width=40)
        search_icon_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
    
        def browse_youtube_search_icon():
            filename = filedialog.askopenfilename(
                title="Chọn một hình ảnh",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
            )
            if filename:
                self.youtube_search_icon_path_var.set(filename)
    
        browse_search_icon_button = ttk.Button(search_icon_browse_frame, text="Duyệt...", command=browse_youtube_search_icon)
        browse_search_icon_button.pack(side=tk.RIGHT, padx=5)
        
        # ========== VIDEOS MENU CHANNEL IMAGE (GLOBAL) ==========
        separator_videos_menu = ttk.Separator(self.youtube_option_frame, orient="horizontal")
        separator_videos_menu.pack(fill=tk.X, pady=10)

        videos_menu_label = tk.Label(
            self.youtube_option_frame,
            text="Videos Menu Channel Image",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        videos_menu_label.pack(anchor=tk.W, pady=(5, 3))

        videos_menu_browse_frame = tk.Frame(self.youtube_option_frame, bg=cfg.LIGHT_BG_COLOR)
        videos_menu_browse_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(videos_menu_browse_frame, text="Đường dẫn hình ảnh:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=(0, 5))

        self.youtube_videos_menu_channel_path_var = tk.StringVar()
        if self.parameters:
            self.youtube_videos_menu_channel_path_var.set(self.parameters.get("youtube_videos_menu_channel_path", ""))
        else:
            self.youtube_videos_menu_channel_path_var.set("")

        videos_menu_entry = ttk.Entry(videos_menu_browse_frame, textvariable=self.youtube_videos_menu_channel_path_var, width=40)
        videos_menu_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)

        def browse_youtube_videos_menu_channel():
            filename = filedialog.askopenfilename(
                title="Chọn một hình ảnh",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
            )
            if filename:
                self.youtube_videos_menu_channel_path_var.set(filename)

        browse_videos_menu_button = ttk.Button(videos_menu_browse_frame, text="Duyệt...", command=browse_youtube_videos_menu_channel)
        browse_videos_menu_button.pack(side=tk.RIGHT, padx=5)

    
        # ========== SIDEBAR AREA YOUTUBE (GLOBAL) ==========
        separator2 = ttk.Separator(self.youtube_option_frame, orient="horizontal")
        separator2.pack(fill=tk.X, pady=10)
    
        sidebar_area_label = tk.Label(
            self.youtube_option_frame,
            text="Sidebar Area Youtube:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        sidebar_area_label.pack(anchor=tk.W, pady=(5, 3))
    
        sidebar_coords_frame = tk.Frame(self.youtube_option_frame, bg=cfg.LIGHT_BG_COLOR)
        sidebar_coords_frame.pack(fill=tk.X, pady=(0, 10))
    
        # X
        tk.Label(sidebar_coords_frame, text="X:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.youtube_sidebar_area_x_var = tk.StringVar()
        if self.parameters:
            self.youtube_sidebar_area_x_var.set(self.parameters.get("youtube_sidebar_area_x", "0"))
        else:
            self.youtube_sidebar_area_x_var.set("0")
        sidebar_x_entry = ttk.Entry(sidebar_coords_frame, textvariable=self.youtube_sidebar_area_x_var, width=8)
        sidebar_x_entry.pack(side=tk.LEFT, padx=5)
    
        # Y
        tk.Label(sidebar_coords_frame, text="Y:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(15, 5))
        self.youtube_sidebar_area_y_var = tk.StringVar()
        if self.parameters:
            self.youtube_sidebar_area_y_var.set(self.parameters.get("youtube_sidebar_area_y", "0"))
        else:
            self.youtube_sidebar_area_y_var.set("0")
        sidebar_y_entry = ttk.Entry(sidebar_coords_frame, textvariable=self.youtube_sidebar_area_y_var, width=8)
        sidebar_y_entry.pack(side=tk.LEFT, padx=5)
    
        # Width
        tk.Label(sidebar_coords_frame, text="Width:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(15, 5))
        self.youtube_sidebar_area_width_var = tk.StringVar()
        if self.parameters:
            self.youtube_sidebar_area_width_var.set(self.parameters.get("youtube_sidebar_area_width", "400"))
        else:
            self.youtube_sidebar_area_width_var.set("400")
        sidebar_width_entry = ttk.Entry(sidebar_coords_frame, textvariable=self.youtube_sidebar_area_width_var, width=8)
        sidebar_width_entry.pack(side=tk.LEFT, padx=5)
    
        # Height
        tk.Label(sidebar_coords_frame, text="Height:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(15, 5))
        self.youtube_sidebar_area_height_var = tk.StringVar()
        if self.parameters:
            self.youtube_sidebar_area_height_var.set(self.parameters.get("youtube_sidebar_area_height", "1080"))
        else:
            self.youtube_sidebar_area_height_var.set("1080")
        sidebar_height_entry = ttk.Entry(sidebar_coords_frame, textvariable=self.youtube_sidebar_area_height_var, width=8)
        sidebar_height_entry.pack(side=tk.LEFT, padx=5)
    
        # Select area button
        self.youtube_sidebar_select_area_button = ttk.Button(
            sidebar_coords_frame,
            text="Select area",
            command=self.on_youtube_sidebar_select_area_click
        )
        self.youtube_sidebar_select_area_button.pack(side=tk.LEFT, padx=(15, 0))
    
        # ========== ADS AREA (GLOBAL) ==========
        separator3 = ttk.Separator(self.youtube_option_frame, orient="horizontal")
        separator3.pack(fill=tk.X, pady=10)
    
        ads_area_label = tk.Label(
            self.youtube_option_frame,
            text="Ads Area Youtube (Skip Button Detection):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        ads_area_label.pack(anchor=tk.W, pady=(5, 3))
    
        ads_coords_frame = tk.Frame(self.youtube_option_frame, bg=cfg.LIGHT_BG_COLOR)
        ads_coords_frame.pack(fill=tk.X, pady=(0, 10))
    
        # X
        tk.Label(ads_coords_frame, text="X:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.youtube_ads_area_x_var = tk.StringVar()
        if self.parameters:
            self.youtube_ads_area_x_var.set(self.parameters.get("youtube_ads_area_x", "0"))
        else:
            self.youtube_ads_area_x_var.set("0")
        ads_x_entry = ttk.Entry(ads_coords_frame, textvariable=self.youtube_ads_area_x_var, width=8)
        ads_x_entry.pack(side=tk.LEFT, padx=5)
    
        # Y
        tk.Label(ads_coords_frame, text="Y:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(15, 5))
        self.youtube_ads_area_y_var = tk.StringVar()
        if self.parameters:
            self.youtube_ads_area_y_var.set(self.parameters.get("youtube_ads_area_y", "0"))
        else:
            self.youtube_ads_area_y_var.set("0")
        ads_y_entry = ttk.Entry(ads_coords_frame, textvariable=self.youtube_ads_area_y_var, width=8)
        ads_y_entry.pack(side=tk.LEFT, padx=5)
    
        # Width
        tk.Label(ads_coords_frame, text="Width:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(15, 5))
        self.youtube_ads_area_width_var = tk.StringVar()
        if self.parameters:
            self.youtube_ads_area_width_var.set(self.parameters.get("youtube_ads_area_width", "300"))
        else:
            self.youtube_ads_area_width_var.set("300")
        ads_width_entry = ttk.Entry(ads_coords_frame, textvariable=self.youtube_ads_area_width_var, width=8)
        ads_width_entry.pack(side=tk.LEFT, padx=5)
    
        # Height
        tk.Label(ads_coords_frame, text="Height:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(15, 5))
        self.youtube_ads_area_height_var = tk.StringVar()
        if self.parameters:
            self.youtube_ads_area_height_var.set(self.parameters.get("youtube_ads_area_height", "150"))
        else:
            self.youtube_ads_area_height_var.set("150")
        ads_height_entry = ttk.Entry(ads_coords_frame, textvariable=self.youtube_ads_area_height_var, width=8)
        ads_height_entry.pack(side=tk.LEFT, padx=5)
    
        # Select area button
        self.youtube_ads_select_area_button = ttk.Button(
            ads_coords_frame,
            text="Select area",
            command=self.on_youtube_ads_select_area_click
        )
        self.youtube_ads_select_area_button.pack(side=tk.LEFT, padx=(15, 0))
    
        # ========== SKIP ADS AREA (GLOBAL) ==========
        separator4 = ttk.Separator(self.youtube_option_frame, orient="horizontal")
        separator4.pack(fill=tk.X, pady=10)
    
        skip_ads_area_label = tk.Label(
            self.youtube_option_frame,
            text="Skip Ads Area Youtube (Skip Button Location):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        skip_ads_area_label.pack(anchor=tk.W, pady=(5, 3))
    
        skip_ads_coords_frame = tk.Frame(self.youtube_option_frame, bg=cfg.LIGHT_BG_COLOR)
        skip_ads_coords_frame.pack(fill=tk.X, pady=(0, 10))
    
        # X
        tk.Label(skip_ads_coords_frame, text="X:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 5))
        self.youtube_skip_ads_area_x_var = tk.StringVar()
        if self.parameters:
            self.youtube_skip_ads_area_x_var.set(self.parameters.get("youtube_skip_ads_area_x", "0"))
        else:
            self.youtube_skip_ads_area_x_var.set("0")
        skip_ads_x_entry = ttk.Entry(skip_ads_coords_frame, textvariable=self.youtube_skip_ads_area_x_var, width=8)
        skip_ads_x_entry.pack(side=tk.LEFT, padx=5)
    
        # Y
        tk.Label(skip_ads_coords_frame, text="Y:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(15, 5))
        self.youtube_skip_ads_area_y_var = tk.StringVar()
        if self.parameters:
            self.youtube_skip_ads_area_y_var.set(self.parameters.get("youtube_skip_ads_area_y", "0"))
        else:
            self.youtube_skip_ads_area_y_var.set("0")
        skip_ads_y_entry = ttk.Entry(skip_ads_coords_frame, textvariable=self.youtube_skip_ads_area_y_var, width=8)
        skip_ads_y_entry.pack(side=tk.LEFT, padx=5)
    
        # Width
        tk.Label(skip_ads_coords_frame, text="Width:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(15, 5))
        self.youtube_skip_ads_area_width_var = tk.StringVar()
        if self.parameters:
            self.youtube_skip_ads_area_width_var.set(self.parameters.get("youtube_skip_ads_area_width", "200"))
        else:
            self.youtube_skip_ads_area_width_var.set("200")
        skip_ads_width_entry = ttk.Entry(skip_ads_coords_frame, textvariable=self.youtube_skip_ads_area_width_var, width=8)
        skip_ads_width_entry.pack(side=tk.LEFT, padx=5)
    
        # Height
        tk.Label(skip_ads_coords_frame, text="Height:", bg=cfg.LIGHT_BG_COLOR, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(15, 5))
        self.youtube_skip_ads_area_height_var = tk.StringVar()
        if self.parameters:
            self.youtube_skip_ads_area_height_var.set(self.parameters.get("youtube_skip_ads_area_height", "100"))
        else:
            self.youtube_skip_ads_area_height_var.set("100")
        skip_ads_height_entry = ttk.Entry(skip_ads_coords_frame, textvariable=self.youtube_skip_ads_area_height_var, width=8)
        skip_ads_height_entry.pack(side=tk.LEFT, padx=5)
    
        # Select area button
        self.youtube_skip_ads_select_area_button = ttk.Button(
            skip_ads_coords_frame,
            text="Select area",
            command=self.on_youtube_skip_ads_select_area_click
        )
        self.youtube_skip_ads_select_area_button.pack(side=tk.LEFT, padx=(15, 0))
        


    def _add_youtube_channel_from_data(self, channel_data):
        """
        Add YouTube channel from existing data (EDIT MODE)
    
        Args:
            channel_data (dict): Channel data from parameters
                {
                    "channel_id": "ch_1",
                    "channel_index": 1,
                    "enabled": True,
                    "logo_path": "path/to/logo.png",
                    "main_image_search_path": "...",
                    "sidebar_image_search_path": "...",
                    "suffix_prefix": "watch; how to",
                    "keywords_file_path": "path/to/keywords.txt"
                }
        """
    
        channel_index = len(self.youtube_channels) + 1
        channel_id = f"ch_{channel_index}"
    
        # Create channel frame (LabelFrame)
        channel_frame = tk.LabelFrame(
            self.youtube_channels_container,
            text=f"Channel {channel_index}",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold"),
            pady=5,
            padx=5
        )
        channel_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
    
        # Header frame (toggle + delete buttons)
        header_frame = tk.Frame(channel_frame, bg=cfg.LIGHT_BG_COLOR)
        header_frame.pack(fill=tk.X, pady=(0, 5))
    
        # Toggle button (Collapse/Expand)
        toggle_btn = ttk.Button(
            header_frame,
            text="▼ Collapse",
            width=12,
            command=lambda: self.toggle_youtube_channel(channel_id)
        )
        toggle_btn.pack(side=tk.LEFT, padx=(0, 5))
    
        # Delete button (ONLY if not first channel)
        delete_btn = None
        if channel_index > 1:
            delete_btn = ttk.Button(
                header_frame,
                text="🗑️ Delete",
                width=12,
                command=lambda: self.delete_youtube_channel(channel_id)
            )
            delete_btn.pack(side=tk.LEFT)
    
        # Content frame (collapsible)
        content_frame = tk.Frame(channel_frame, bg=cfg.LIGHT_BG_COLOR)
        # DO NOT pack yet (collapsed by default)

        # Create widgets + INLINE LOAD from channel_data
        channel_vars = self._create_channel_params_widgets_with_data(content_frame, channel_id, channel_data)

        # Store channel config (DEFAULT: COLLAPSED)
        channel_config = {
            "channel_id": channel_id,
            "channel_index": channel_index,
            "frame": channel_frame,
            "header_frame": header_frame,
            "toggle_btn": toggle_btn,
            "delete_btn": delete_btn,
            "content_frame": content_frame,
            "is_collapsed": True,  # ← DEFAULT COLLAPSED
            "vars": channel_vars
        }

        self.youtube_channels.append(channel_config)

        # Update toggle button text (show "Expand" since collapsed)
        toggle_btn.config(text="▶ Expand")

        print(f"[UI] Channel {channel_index} loaded from data (ID: {channel_id}) - COLLAPSED")




    def _create_channel_params_widgets_with_data(self, parent_frame, channel_id, channel_data):
        """
        Create channel params widgets + INLINE LOAD from channel_data (EDIT MODE)
    
        Same as _create_channel_params_widgets() but with INLINE loading from channel_data
    
        Args:
            parent_frame: Parent frame
            channel_id: Channel ID
            channel_data (dict): Existing channel data
    
        Returns:
            dict: Tkinter variables
        """
    
        channel_vars = {}
    
        # ========== 1. CHECKBOX ENABLE (LOAD from data) ==========
        channel_vars["enabled"] = tk.BooleanVar(value=channel_data.get("enabled", True))
        enable_cb = tk.Checkbutton(
            parent_frame,
            text="Enable this channel",
            variable=channel_vars["enabled"],
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        enable_cb.pack(anchor=tk.W, pady=(0, 10))
    
        # ========== 2. LOGO CHANNEL (LOAD from data) ==========
        logo_label = tk.Label(
            parent_frame,
            text="Logo Channel (for channel detection):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        logo_label.pack(anchor=tk.W, pady=(5, 3))
    
        logo_browse_frame = tk.Frame(parent_frame, bg=cfg.LIGHT_BG_COLOR)
        logo_browse_frame.pack(fill=tk.X, pady=(0, 10))
    
        tk.Label(logo_browse_frame, text="Đường dẫn logo:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=(0, 5))
    
        channel_vars["logo_path"] = tk.StringVar(value=channel_data.get("logo_path", ""))
        logo_entry = ttk.Entry(logo_browse_frame, textvariable=channel_vars["logo_path"], width=40)
        logo_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
    
        def browse_logo():
            filename = filedialog.askopenfilename(
                title="Chọn logo channel",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
            )
            if filename:
                channel_vars["logo_path"].set(filename)
    
        logo_browse_btn = ttk.Button(logo_browse_frame, text="Duyệt...", command=browse_logo)
        logo_browse_btn.pack(side=tk.LEFT)
    
        # Separator
        separator1 = ttk.Separator(parent_frame, orient="horizontal")
        separator1.pack(fill=tk.X, pady=10)
    
        # ========== 3. IMAGE SEARCH MAIN AREA (LOAD from data) ==========
        main_image_label = tk.Label(
            parent_frame,
            text="Image Search Main Area:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        main_image_label.pack(anchor=tk.W, pady=(5, 3))
    
        main_image_browse_frame = tk.Frame(parent_frame, bg=cfg.LIGHT_BG_COLOR)
        main_image_browse_frame.pack(fill=tk.X, pady=(0, 10))
    
        tk.Label(main_image_browse_frame, text="Đường dẫn hình ảnh:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=(0, 5))
    
        channel_vars["main_image_search_path"] = tk.StringVar(value=channel_data.get("main_image_search_path", ""))
        main_image_entry = ttk.Entry(main_image_browse_frame, textvariable=channel_vars["main_image_search_path"], width=40)
        main_image_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
    
        def browse_main_image():
            filename = filedialog.askopenfilename(
                title="Chọn hình ảnh main area",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
            )
            if filename:
                channel_vars["main_image_search_path"].set(filename)
    
        main_image_browse_btn = ttk.Button(main_image_browse_frame, text="Duyệt...", command=browse_main_image)
        main_image_browse_btn.pack(side=tk.LEFT)
    
        # ========== 4. IMAGE SEARCH SIDEBAR AREA (LOAD from data) ==========
        sidebar_image_label = tk.Label(
            parent_frame,
            text="Image Search Sidebar Area:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        sidebar_image_label.pack(anchor=tk.W, pady=(5, 3))
    
        sidebar_image_browse_frame = tk.Frame(parent_frame, bg=cfg.LIGHT_BG_COLOR)
        sidebar_image_browse_frame.pack(fill=tk.X, pady=(0, 10))
    
        tk.Label(sidebar_image_browse_frame, text="Đường dẫn hình ảnh:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=(0, 5))
    
        channel_vars["sidebar_image_search_path"] = tk.StringVar(value=channel_data.get("sidebar_image_search_path", ""))
        sidebar_image_entry = ttk.Entry(sidebar_image_browse_frame, textvariable=channel_vars["sidebar_image_search_path"], width=40)
        sidebar_image_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
    
        def browse_sidebar_image():
            filename = filedialog.askopenfilename(
                title="Chọn hình ảnh sidebar area",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
            )
            if filename:
                channel_vars["sidebar_image_search_path"].set(filename)
    
        sidebar_image_browse_btn = ttk.Button(sidebar_image_browse_frame, text="Duyệt...", command=browse_sidebar_image)
        sidebar_image_browse_btn.pack(side=tk.LEFT)
    
        # Separator
        separator2 = ttk.Separator(parent_frame, orient="horizontal")
        separator2.pack(fill=tk.X, pady=10)
    
        # ========== 5. KEYWORD SUFFIX/PREFIX (LOAD from data) ==========
        suffix_label = tk.Label(
            parent_frame,
            text="Keyword Suffix/Prefix (Nhiều giá trị, cách nhau bởi dấu ;):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        suffix_label.pack(anchor=tk.W, pady=(5, 3))
    
        suffix_frame = tk.Frame(parent_frame, bg=cfg.LIGHT_BG_COLOR)
        suffix_frame.pack(fill=tk.X, pady=(0, 10))
    
        channel_vars["suffix_prefix"] = tk.StringVar(value=channel_data.get("suffix_prefix", ""))
        suffix_entry = ttk.Entry(suffix_frame, textvariable=channel_vars["suffix_prefix"], width=50)
        suffix_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
        # ========== 6. KEYWORDS FILE (LOAD from data) ==========
        keywords_label = tk.Label(
            parent_frame,
            text="Search Keywords YouTube (File):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        keywords_label.pack(anchor=tk.W, pady=(5, 3))
    
        keywords_file_frame = tk.Frame(parent_frame, bg=cfg.LIGHT_BG_COLOR)
        keywords_file_frame.pack(fill=tk.X, pady=(0, 5))
    
        tk.Label(keywords_file_frame, text="Chọn file keywords:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=(0, 5))
    
        channel_vars["keywords_file_path"] = tk.StringVar(value=channel_data.get("keywords_file_path", ""))
        keywords_file_entry = ttk.Entry(keywords_file_frame, textvariable=channel_vars["keywords_file_path"], width=40)
        keywords_file_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
    
        def browse_keywords_file():
            filename = filedialog.askopenfilename(
                title="Chọn file keywords",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                channel_vars["keywords_file_path"].set(filename)
    
        keywords_browse_btn = ttk.Button(keywords_file_frame, text="Duyệt...", command=browse_keywords_file)
        keywords_browse_btn.pack(side=tk.LEFT)
    
        return channel_vars




    def add_youtube_channel(self):
        """Add new YouTube channel frame (collapsible)"""
    
        channel_index = len(self.youtube_channels) + 1
        channel_id = f"ch_{channel_index}"
    
        # Create channel frame (LabelFrame)
        channel_frame = tk.LabelFrame(
            self.youtube_channels_container,
            text=f"Channel {channel_index}",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold"),
            pady=5,
            padx=5
        )
        channel_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
    
        # Header frame (toggle + delete buttons)
        header_frame = tk.Frame(channel_frame, bg=cfg.LIGHT_BG_COLOR)
        header_frame.pack(fill=tk.X, pady=(0, 5))
    
        # Toggle button (Collapse/Expand)
        toggle_btn = ttk.Button(
            header_frame,
            text="▼ Collapse",
            width=12,
            command=lambda: self.toggle_youtube_channel(channel_id)
        )
        toggle_btn.pack(side=tk.LEFT, padx=(0, 5))
    
        # Delete button (ONLY if not first channel)
        delete_btn = None
        if channel_index > 1:
            delete_btn = ttk.Button(
                header_frame,
                text="🗑️ Delete",
                width=12,
                command=lambda: self.delete_youtube_channel(channel_id)
            )
            delete_btn.pack(side=tk.LEFT)
    
        # Content frame (collapsible - contains all params)
        content_frame = tk.Frame(channel_frame, bg=cfg.LIGHT_BG_COLOR)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
    
        # Create all channel params widgets
        channel_vars = self._create_channel_params_widgets(content_frame, channel_id)
    
        # Store channel config
        channel_config = {
            "channel_id": channel_id,
            "channel_index": channel_index,
            "frame": channel_frame,
            "header_frame": header_frame,
            "toggle_btn": toggle_btn,
            "delete_btn": delete_btn,
            "content_frame": content_frame,
            "is_collapsed": False,
            "vars": channel_vars
        }
    
        self.youtube_channels.append(channel_config)
    
        print(f"[UI] Channel {channel_index} added (ID: {channel_id})")

    def _create_channel_params_widgets(self, parent_frame, channel_id):
        """
        Create channel-specific params widgets (UPDATED: Remove textarea, update suffix label)
    
        ONLY these params:
        1. Checkbox Enable (NEW)
        2. Logo channel (NEW - browse image)
        3. Image Search Main area (EXISTING - moved from global)
        4. Image Search Sidebar area (EXISTING - moved from global)
        5. Keyword suffix/prefix (EXISTING - UPDATED label + width)
        6. Keywords file ONLY (EXISTING - REMOVED textarea)
    
        Args:
            parent_frame: Parent frame (content_frame of channel)
            channel_id: Unique channel ID
    
        Returns:
            dict: All Tkinter variables for this channel
        """
    
        channel_vars = {}
    
        # ========== 1. CHECKBOX ENABLE (NEW) ==========
        channel_vars["enabled"] = tk.BooleanVar(value=True)
        enable_cb = tk.Checkbutton(
            parent_frame,
            text="Enable this channel",
            variable=channel_vars["enabled"],
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10)
        )
        enable_cb.pack(anchor=tk.W, pady=(0, 10))
    
        # ========== 2. LOGO CHANNEL (NEW - Browse image) ==========
        logo_label = tk.Label(
            parent_frame,
            text="Logo Channel (for channel detection):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        logo_label.pack(anchor=tk.W, pady=(5, 3))
    
        logo_browse_frame = tk.Frame(parent_frame, bg=cfg.LIGHT_BG_COLOR)
        logo_browse_frame.pack(fill=tk.X, pady=(0, 10))
    
        tk.Label(logo_browse_frame, text="Đường dẫn logo:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=(0, 5))
    
        channel_vars["logo_path"] = tk.StringVar(value="")
        logo_entry = ttk.Entry(logo_browse_frame, textvariable=channel_vars["logo_path"], width=40)
        logo_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
    
        def browse_logo():
            filename = filedialog.askopenfilename(
                title="Chọn logo channel",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
            )
            if filename:
                channel_vars["logo_path"].set(filename)
                print(f"[CHANNEL {channel_id}] Logo set: {filename}")
    
        logo_browse_btn = ttk.Button(logo_browse_frame, text="Duyệt...", command=browse_logo)
        logo_browse_btn.pack(side=tk.LEFT)
    
        # Separator
        separator1 = ttk.Separator(parent_frame, orient="horizontal")
        separator1.pack(fill=tk.X, pady=10)
    
        # ========== 3. IMAGE SEARCH MAIN AREA (EXISTING - Moved from global) ==========
        main_image_label = tk.Label(
            parent_frame,
            text="Image Search Main Area:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        main_image_label.pack(anchor=tk.W, pady=(5, 3))
    
        main_image_browse_frame = tk.Frame(parent_frame, bg=cfg.LIGHT_BG_COLOR)
        main_image_browse_frame.pack(fill=tk.X, pady=(0, 10))
    
        tk.Label(main_image_browse_frame, text="Đường dẫn hình ảnh:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=(0, 5))
    
        channel_vars["main_image_search_path"] = tk.StringVar(value="")
        main_image_entry = ttk.Entry(main_image_browse_frame, textvariable=channel_vars["main_image_search_path"], width=40)
        main_image_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
    
        def browse_main_image():
            filename = filedialog.askopenfilename(
                title="Chọn hình ảnh main area",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
            )
            if filename:
                channel_vars["main_image_search_path"].set(filename)
                print(f"[CHANNEL {channel_id}] Main image set: {filename}")
    
        main_image_browse_btn = ttk.Button(main_image_browse_frame, text="Duyệt...", command=browse_main_image)
        main_image_browse_btn.pack(side=tk.LEFT)
    
        # ========== 4. IMAGE SEARCH SIDEBAR AREA (EXISTING - Moved from global) ==========
        sidebar_image_label = tk.Label(
            parent_frame,
            text="Image Search Sidebar Area:",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        sidebar_image_label.pack(anchor=tk.W, pady=(5, 3))
    
        sidebar_image_browse_frame = tk.Frame(parent_frame, bg=cfg.LIGHT_BG_COLOR)
        sidebar_image_browse_frame.pack(fill=tk.X, pady=(0, 10))
    
        tk.Label(sidebar_image_browse_frame, text="Đường dẫn hình ảnh:", bg=cfg.LIGHT_BG_COLOR).pack(side=tk.LEFT, padx=(0, 5))
    
        channel_vars["sidebar_image_search_path"] = tk.StringVar(value="")
        sidebar_image_entry = ttk.Entry(sidebar_image_browse_frame, textvariable=channel_vars["sidebar_image_search_path"], width=40)
        sidebar_image_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
    
        def browse_sidebar_image():
            filename = filedialog.askopenfilename(
                title="Chọn hình ảnh sidebar area",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
            )
            if filename:
                channel_vars["sidebar_image_search_path"].set(filename)
                print(f"[CHANNEL {channel_id}] Sidebar image set: {filename}")
    
        sidebar_image_browse_btn = ttk.Button(sidebar_image_browse_frame, text="Duyệt...", command=browse_sidebar_image)
        sidebar_image_browse_btn.pack(side=tk.LEFT)
    
        # Separator
        separator2 = ttk.Separator(parent_frame, orient="horizontal")
        separator2.pack(fill=tk.X, pady=10)
    
        # ========== 5. KEYWORD SUFFIX/PREFIX (UPDATED LABEL + WIDTH) ==========
        suffix_label = tk.Label(
            parent_frame,
            text="Keyword Suffix/Prefix (Nhiều giá trị, cách nhau bởi dấu ;):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        suffix_label.pack(anchor=tk.W, pady=(5, 3))
    
        suffix_frame = tk.Frame(parent_frame, bg=cfg.LIGHT_BG_COLOR)
        suffix_frame.pack(fill=tk.X, pady=(0, 10))
    
        channel_vars["suffix_prefix"] = tk.StringVar(value="")
        suffix_entry = ttk.Entry(suffix_frame, textvariable=channel_vars["suffix_prefix"], width=50)
        suffix_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
        # ========== 6. KEYWORDS FILE ONLY (REMOVED TEXTAREA) ==========
        keywords_label = tk.Label(
            parent_frame,
            text="Search Keywords YouTube (File):",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        keywords_label.pack(anchor=tk.W, pady=(5, 3))
    
        keywords_file_frame = tk.Frame(parent_frame, bg=cfg.LIGHT_BG_COLOR)
        keywords_file_frame.pack(fill=tk.X, pady=(0, 5))
    
        tk.Label(
            keywords_file_frame,
            text="Chọn file keywords:",
            bg=cfg.LIGHT_BG_COLOR
        ).pack(side=tk.LEFT, padx=(0, 5))
    
        channel_vars["keywords_file_path"] = tk.StringVar(value="")
        keywords_file_entry = ttk.Entry(
            keywords_file_frame,
            textvariable=channel_vars["keywords_file_path"],
            width=40
        )
        keywords_file_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
    
        def browse_keywords_file():
            filename = filedialog.askopenfilename(
                title="Chọn file keywords",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                channel_vars["keywords_file_path"].set(filename)
                print(f"[CHANNEL {channel_id}] Keywords file set: {filename}")
    
        keywords_browse_btn = ttk.Button(keywords_file_frame, text="Duyệt...", command=browse_keywords_file)
        keywords_browse_btn.pack(side=tk.LEFT)
    
        return channel_vars






    def toggle_youtube_channel(self, channel_id):
        """Toggle channel frame (Collapse/Expand)"""
        channel = next((ch for ch in self.youtube_channels if ch["channel_id"] == channel_id), None)
        if not channel:
            return
    
        if channel["is_collapsed"]:
            # Expand
            channel["content_frame"].pack(fill=tk.BOTH, expand=True, pady=5)
            channel["toggle_btn"].config(text="▼ Collapse")
            channel["is_collapsed"] = False
            print(f"[UI] Channel {channel['channel_index']} expanded")
        else:
            # Collapse
            channel["content_frame"].pack_forget()
            channel["toggle_btn"].config(text="▶ Expand")
            channel["is_collapsed"] = True
            print(f"[UI] Channel {channel['channel_index']} collapsed")

    def delete_youtube_channel(self, channel_id):
        """Delete channel frame (NOT allowed for Channel 1)"""
        channel = next((ch for ch in self.youtube_channels if ch["channel_id"] == channel_id), None)
        if not channel:
            return
    
        if channel["channel_index"] == 1:
            print("[UI] Cannot delete Channel 1")
            return
    
        # Destroy channel frame
        channel["frame"].destroy()
    
        # Remove from list
        self.youtube_channels.remove(channel)
    
        # Renumber remaining channels
        for idx, ch in enumerate(self.youtube_channels):
            ch["channel_index"] = idx + 1
            ch["frame"].config(text=f"Channel {idx + 1}")
    
        print(f"[UI] Channel {channel['channel_index']} deleted. Remaining: {len(self.youtube_channels)}")


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
        
    def on_youtube_search_area_select_area_click(self):
        """Handler for Search Area select button"""
        from views.screen_area_selector import ScreenAreaSelector
    
        def update_coords(x, y, width, height):
            self.youtube_search_area_x_var.set(str(x))
            self.youtube_search_area_y_var.set(str(y))
            self.youtube_search_area_width_var.set(str(width))
            self.youtube_search_area_height_var.set(str(height))
            print(f"[SEARCH_AREA] Updated: x={x}, y={y}, w={width}, h={height}")
    
        dialog = self.parent_frame.winfo_toplevel()
        selector = ScreenAreaSelector(parent_dialog=dialog, callback=update_coords)
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

    def on_youtube_ads_select_area_click(self):
        """Handler khi click button Select area của Ads Youtube Option"""
        from views.screen_area_selector import ScreenAreaSelector
    
        # Callback để update các textboxes
        def update_coords(x, y, width, height):
            self.youtube_ads_area_x_var.set(str(x))
            self.youtube_ads_area_y_var.set(str(y))
            self.youtube_ads_area_width_var.set(str(width))
            self.youtube_ads_area_height_var.set(str(height))
            print(f"[YOUTUBE_ADS_SELECT_AREA] Updated: x={x}, y={y}, w={width}, h={height}")
    
        # Tìm dialog cha (ActionDialogView)
        dialog = self.parent_frame.winfo_toplevel()
    
        # Tạo và show selector
        selector = ScreenAreaSelector(
            parent_dialog=dialog,
            callback=update_coords
        )
        selector.show()

    def on_youtube_skip_ads_select_area_click(self):
        """Handler khi click button Select area của Skip Ads Youtube Option"""
        from views.screen_area_selector import ScreenAreaSelector
    
        def update_coords(x, y, width, height):
            self.youtube_skip_ads_area_x_var.set(str(x))
            self.youtube_skip_ads_area_y_var.set(str(y))
            self.youtube_skip_ads_area_width_var.set(str(width))
            self.youtube_skip_ads_area_height_var.set(str(height))
            print(f"[YOUTUBE_SKIP_ADS_SELECT_AREA] Updated: x={x}, y={y}, w={width}, h={height}")
    
        dialog = self.parent_frame.winfo_toplevel()
        selector = ScreenAreaSelector(parent_dialog=dialog, callback=update_coords)
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
        
        
        # ========== PROXY FILE SECTION ==========
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

        proxyfile_label = tk.Label(
            options_frame,
            text="Proxy File (Optional) - TXT format: type;api_key per line",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 10, "bold")
        )
        proxyfile_label.pack(anchor=tk.W, pady=(5, 2))

        proxybrowseframe = tk.Frame(options_frame, bg=cfg.LIGHT_BG_COLOR)
        proxybrowseframe.pack(fill=tk.X, pady=(0, 10))

        self.proxy_file_var = tk.StringVar()
        if self.parameters:
            self.proxy_file_var.set(self.parameters.get("proxy_file", ""))
        proxyentry = tk.Entry(proxybrowseframe, textvariable=self.proxy_file_var, font=("Segoe UI", 10))
        proxyentry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        def browse_proxy_file():
            filename = filedialog.askopenfilename(
                title="Select Proxy TXT File",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                self.proxy_file_var.set(filename)

        browse_proxy_button = ttk.Button(proxybrowseframe, text="Browse", command=browse_proxy_file)
        browse_proxy_button.pack(side=tk.LEFT)

        proxyfile_hint = tk.Label(
            options_frame,
            text="File format example:\nhttp;your_api_key_1\nsocks5;your_api_key_2\nProxies will be assigned to profiles sequentially or randomly.",
            bg=cfg.LIGHT_BG_COLOR,
            font=("Segoe UI", 8),
            fg="#666666",
            wraplength=500,
            justify=tk.LEFT
        )
        proxyfile_hint.pack(anchor=tk.W)

        
        
        

        # ========== THÊM MULTI-THREADING SECTION ==========
        separator = ttk.Separator(options_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)

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
        """
        Collect all parameters from UI (UPDATED: Multi-channel support)
    
        Returns:
            dict: Complete parameters including youtube_channels array
        """
        # Get base params from parent class
        params = super().get_parameters()
    
        # ========== API KEY ==========
        params["api_key_variable"] = self.api_key_var.get().strip()
    
        # ========== PROFILE IDS & RANGE ==========
        params["profile_ids"] = self.profile_ids_input.get("1.0", tk.END).strip()
        params["profile_count"] = self.profile_count_var.get().strip()
        params["profile_start_index"] = self.profile_start_index_var.get().strip()
        params["how_to_get"] = self.how_to_get_var.get()
    
        # ========== ACTION TYPE ==========
        params["action_type"] = self.action_type_var.get()
    
        # ========== KEYWORDS (YouTube & Google) - GLOBAL ==========     
        params["keywords_google_file"] = self.keywords_google_file_var.get().strip()
        params["keywords_google_variable"] = self.keywords_google_variable_var.get().strip()
    
        # ========== OPTIONS ==========
        params["refresh_fingerprint"] = self.refresh_fingerprint_var.get()
        params["remove_proxy"] = self.remove_proxy_var.get()
        params["proxy_file"] = self.proxy_file_var.get().strip()
        params["enable_threading"] = self.enable_threading_var.get()
        params["max_workers"] = self.max_workers_var.get().strip()
    
        # ========== BROWSE YOUTUBE (GLOBAL) ==========
        params["browse_youtube"] = self.browse_youtube_var.get()
    
        # ========== YOUTUBE GLOBAL PARAMS (Main/Search Icon/Sidebar/Ads/Skip Ads) ==========
        params["youtube_main_area_x"] = self.youtube_main_area_x_var.get()
        params["youtube_main_area_y"] = self.youtube_main_area_y_var.get()
        params["youtube_main_area_width"] = self.youtube_main_area_width_var.get()
        params["youtube_main_area_height"] = self.youtube_main_area_height_var.get()
        
        # Search Area Youtube
        params['youtube_search_area_x'] = self.youtube_search_area_x_var.get()
        params['youtube_search_area_y'] = self.youtube_search_area_y_var.get()
        params['youtube_search_area_width'] = self.youtube_search_area_width_var.get()
        params['youtube_search_area_height'] = self.youtube_search_area_height_var.get()

    
        params["youtube_search_icon_path"] = self.youtube_search_icon_path_var.get()
        params["youtube_videos_menu_channel_path"] = self.youtube_videos_menu_channel_path_var.get()

    
        params["youtube_sidebar_area_x"] = self.youtube_sidebar_area_x_var.get()
        params["youtube_sidebar_area_y"] = self.youtube_sidebar_area_y_var.get()
        params["youtube_sidebar_area_width"] = self.youtube_sidebar_area_width_var.get()
        params["youtube_sidebar_area_height"] = self.youtube_sidebar_area_height_var.get()
    
        params["youtube_ads_area_x"] = self.youtube_ads_area_x_var.get()
        params["youtube_ads_area_y"] = self.youtube_ads_area_y_var.get()
        params["youtube_ads_area_width"] = self.youtube_ads_area_width_var.get()
        params["youtube_ads_area_height"] = self.youtube_ads_area_height_var.get()
    
        params["youtube_skip_ads_area_x"] = self.youtube_skip_ads_area_x_var.get()
        params["youtube_skip_ads_area_y"] = self.youtube_skip_ads_area_y_var.get()
        params["youtube_skip_ads_area_width"] = self.youtube_skip_ads_area_width_var.get()
        params["youtube_skip_ads_area_height"] = self.youtube_skip_ads_area_height_var.get()
    
        # ========== YOUTUBE CHANNELS (Multi-channel) ==========
        youtube_channels = []

        for channel in self.youtube_channels:
            channel_vars = channel["vars"]   
    
            # Build channel data
            channel_data = {
                "channel_id": channel["channel_id"],
                "channel_index": channel["channel_index"],
                "enabled": channel_vars["enabled"].get(),
                "logo_path": channel_vars["logo_path"].get(),
                "main_image_search_path": channel_vars["main_image_search_path"].get(),
                "sidebar_image_search_path": channel_vars["sidebar_image_search_path"].get(),
                "suffix_prefix": channel_vars["suffix_prefix"].get(),
                "keywords_file_path": channel_vars["keywords_file_path"].get().strip()
            }
    
            youtube_channels.append(channel_data)

        # Add channels array to params
        params["youtube_channels"] = youtube_channels

        print(f"[PARAMS] Collected {len(youtube_channels)} channel(s)")

        return params

