# controllers/actions/flow_auto/actions_auto/youtube_find_click_video_auto_action.py

from pydoc import pager
import time
import random
from cv2.gapi import video
import pyautogui
import os
from models.global_variables import GlobalVariables
from controllers.actions.mouse_move_action import MouseMoveAction
from controllers.actions.flow_auto.actions_auto.base_flow_auto_action import BaseFlowAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_random_move_scroll_auto_action import YouTubeRandomMoveScrollAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_mouse_move_auto_action import YouTubeMouseMoveAutoAction

from helpers.app_helpers import is_hand_cursor

class YouTubeFindClickVideoAutoAction(BaseFlowAutoAction):
    """
    Find video by channel logo (retry with scroll) + Click video
    Support both main feed and sidebar areas
    """
    
    def __init__(self, profile_id, parameters, log_prefix="[YOUTUBE AUTO]", area="search", flow_type="search"):
        """
        Initialize find and click video action
    
        Args:
            profile_id: GoLogin profile ID
            parameters: Full parameters dict containing:
                - youtube_image_search_path: Main area logo path (channel-specific)
                - youtube_sidebar_image_search_path: Sidebar logo path (channel-specific)
                - youtube_area_x/y/width/height: Main area coords
                - youtube_sidebar_area_x/y/width/height: Sidebar area coords
                - ... (other params)
            area: 'main', 'sidebar', 'channel', 'video_channel' , 'menu_videos_channel'  - determines which area to search
            log_prefix: Log prefix
            flow_type: 'search' or 'browse'
            search_and_click : True / False : for search logo channel in current video, found logo -> return true, viewing the Channel, not return False
        """
        super().__init__(profile_id, log_prefix)
        self.profile_id = profile_id
        self.parameters = parameters
        self.area = area.lower()
        self.flow_type = flow_type
        
        # ========== EXTRACT PARAMS BASED ON AREA ==========
        if self.area == "sidebar":
            self.logo_path = parameters.get('youtube_sidebar_image_search_path', '').strip()
            area_x = int(parameters.get('youtube_sidebar_area_x', 0))
            area_y = int(parameters.get('youtube_sidebar_area_y', 0))
            area_width = int(parameters.get('youtube_sidebar_area_width', 400))
            area_height = int(parameters.get('youtube_sidebar_area_height', 1080))
            
        elif self.area == "main" or self.area == "channel":
            self.logo_path = parameters.get('youtube_channel_logo_path', '').strip()
            area_x = int(parameters.get('youtube_main_area_x', 0))
            area_y = int(parameters.get('youtube_main_area_y', 0))
            area_width = int(parameters.get('youtube_main_area_width', 400))
            area_height = int(parameters.get('youtube_main_area_height', 1080))
            
        elif self.area == "menu_videos_channel":
            self.logo_path = parameters.get('youtube_videos_menu_channel_path', '').strip()
            area_x = int(parameters.get('youtube_main_area_x', 0))
            area_y = int(parameters.get('youtube_main_area_y', 0))
            area_width = int(parameters.get('youtube_main_area_width', 400))
            area_height = int(parameters.get('youtube_main_area_height', 1080))
            
        else:
            self.logo_path = parameters.get('youtube_image_search_path', '').strip()
            area_x = int(parameters.get('youtube_search_area_x', 0))
            area_y = int(parameters.get('youtube_search_area_y', 0))
            area_width = int(parameters.get('youtube_search_area_width', 1920))
            area_height = int(parameters.get('youtube_search_area_height', 1080))

        
        # Define search region
        self.region = None
        if area_width > 0 and area_height > 0:
            self.region = (area_x, area_y, area_width, area_height)
        
        self.log(f"Initialized for area: {self.area.upper()}, region: {self.region}")
    
    def _execute_internal(self):
        """Execute find logo → calculate video position → click video"""
        ###################################################################
        # Logic fake view Youtube:
        # - 1/ 35% search video home page
        # - 2/ If 1 True -> Do not need search video
        # - 3/ If 1 False -> Search video area = search
        self._close_extra_tabs_keep_first()
        try:
            # If find logo channel when view a video , just try once
            if self.area == "channel":
                # Find logo and calculate video click position
                video_position = self._find_and_calculate_click_position()
            
                if video_position:
                    self.log(f"✓ Found logo Channellllllllllllllllll")                   
                    # ========== CLICK VIDEO DIRECTLY ==========
                    click_x, click_y = video_position
                
                    # Click using human-like movement
                    MouseMoveAction.move_and_click_static(
                        click_x, click_y,
                        click_type="single_click",
                        fast=False
                    )
                   
                    # Wait for video to start
                    wait_time = random.uniform(2, 4)
                    self.log(f"Waiting {wait_time:.1f}s for video to start")
                    time.sleep(wait_time)
                    GlobalVariables().set(f'found_logo_channel_{self.profile_id}', True)
                    return True
                
                return False
            
            # Just move mouse on menu Videos of The Channel and click to show all videos of the channel
            if self.area == "menu_videos_channel":
                found_logo_channel = GlobalVariables().get(f'found_logo_channel_{self.profile_id}', False)
                if found_logo_channel:
                    YouTubeMouseMoveAutoAction(
                        profile_id=self.profile_id,
                        click=False,
                        log_prefix=self.log_prefix,
                    )
                    for attempt in range(1, 2):
                        menu_position = self._find_and_calculate_click_position()
                        if menu_position:
                            # ========== CLICK VIDEO DIRECTLY ==========
                            click_x, click_y = menu_position
                            self.log(f"✓ Found Menu Videos Channellllllllllllllll")
                
                            # Click using human-like movement
                            MouseMoveAction.move_and_click_static(
                                click_x, click_y,
                                click_type="single_click",
                                fast=False
                            )
                            
                            # Wait for video to start
                            wait_time = random.uniform(1, 2)
                            time.sleep(wait_time)
                            GlobalVariables().set(f'found_menu_videos_channel_{self.profile_id}', True)
                            return True
                return False
            
            # Just move mouse on channel page -> Cursor hand -> click
            if self.area == "video_channel":
                found_menu_videos_channel = GlobalVariables().get(f'found_menu_videos_channel_{self.profile_id}', False)
                if found_menu_videos_channel:
                    # Scroll to list videos
                    YouTubeRandomMoveScrollAutoAction(self.profile_id, random.randint(1, 4), "main", self.log_prefix).execute()
                    time.sleep(random.randint(2, 4))
                    for attempt in range(1, 5):                        
                        _is_hand_cursor_video_page = self._hover_and_check_hand_cursor()
                        if _is_hand_cursor_video_page:
                            time.sleep(random.uniform(0.5, 2))
                            pyautogui.click()
                            wait_time = random.uniform(4, 7)
                            time.sleep(wait_time)
                            self.log(f"✓ Found Videos Channellllllllllllllllllll")
                            GlobalVariables().set(f'found_menu_videos_channel_{self.profile_id}', False)
                            GlobalVariables().set(f'found_logo_channel_{self.profile_id}', False)
                            GlobalVariables().set(f'found_clicked_video_{self.profile_id}', True)
                            GlobalVariables().set(f'clicked_second_video_{self.profile_id}', True)
                            return True
                return False

            # ========== FIND LOGO WITH RETRY & SCROLL ==========
            # Browse does not need search logo
            if self.flow_type == "browse":
                max_retries = 1
            else:
                # if search home, do not need scroll to much
                if self.area == "main":
                    max_retries = random.randint(1, 3)
                else:
                    max_retries = random.randint(4, 7)
                
            for attempt in range(1, max_retries + 1):
                self.log(f"Attempt {attempt}/{max_retries}: Looking for logo in {self.area} area")
            
                # Find logo and calculate video click position
                video_position = self._find_and_calculate_click_position()
            
                if video_position:
                    self.log(f"✓ Found video position on attempt {attempt}")
                
                    # ========== CLICK VIDEO DIRECTLY ==========
                    click_x, click_y = video_position
                    self.log(f"Clicking video at ({click_x}, {click_y})")
                
                    # Click using human-like movement
                    MouseMoveAction.move_and_click_static(
                        click_x, click_y,
                        click_type=None,
                        fast=False
                    )                    
                    if is_hand_cursor():
                        time.sleep(random.uniform(0.5, 2))
                        pyautogui.click()
                    else:
                        continue
                    # Wait for video to start
                    wait_time = random.uniform(4, 7)
                    self.log(f"Waiting {wait_time:.1f}s for video to start")
                    time.sleep(wait_time)
                
                    self.log("✓ Video clicked successfully")
                    
                    GlobalVariables().set(f'found_clicked_video_{self.profile_id}', True)
                    #If click video in home page youtube
                    if self.area == "main":                        
                        GlobalVariables().set(f'found_video_home_{self.profile_id}', True)
                    elif self.area == "sidebar":
                        GlobalVariables().set(f'clicked_second_video_{self.profile_id}', True)
                        
                    return True
            
                # Not found: Scroll and retry
                if attempt < max_retries:                   
                    YouTubeRandomMoveScrollAutoAction(self.profile_id, 1, "main", self.log_prefix).execute()
                    time.sleep(random.uniform(2, 3))        
         
            # ========== FALLBACK: CLICK RANDOM HAND CURSOR ==========
            self.log(f"✗ Logo not found after {max_retries} attempts", "WARNING")
            # return False
            if self.flow_type == "browse":
                return self._fallback_click_for_cookies_only_browse()
            else:                
                return self._fallback_click_for_cookies()
                
        
        except Exception as e:
            self.log(f"✗ Find and click video error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False

    
    
    def _find_and_calculate_click_position(self):
        """
        Find logo and calculate video click position based on area
    
        Returns:
            tuple: (x, y) position to click video, or None if not found
        """
        # Use defined region or full screen
        search_region = self.region
    
        if not search_region:
            # Fallback to full screen if no region defined
            screen_width, screen_height = pyautogui.size()
            search_region = (0, 0, screen_width, screen_height)
            self.log("No region defined, using full screen", "WARNING")
    
        # Use base class to find logo
        result = self._find_image_on_screen(
            image_path=self.logo_path,
            region=search_region,  # ← FIX: Always pass valid region
            accuracy=0.85,
            click_offset_x=0,  # Return center of logo
            click_offset_y=0
        )
    
        if not result or not result['found']:
            return None
    
        logo_x, logo_y = result['center']
    
        # ========== CALCULATE CLICK POSITION BASED ON AREA ==========
        if self.area == "sidebar":
            rand_choice_sidebar = random.choice([1, 2])
            if rand_choice_sidebar == 1:
                # Sidebar: Logo ở bên phải, video thumbnail ở bên TRÁI
                offset_x = random.randint(-140, -60)
                offset_y = random.randint(-20, 20)
            else:
                # CLICK VÀO TITLE & DESCRIPTION
                offset_x = random.randint(-5, 150)
                offset_y = random.randint(-10, 20)
        elif self.area == "main":
            rand_choice_main = random.choice([1, 2])
            if rand_choice_main == 1:
                # Home: Logo ở dưới, video thumbnail ở trên
                offset_x = random.randint(10, 250)
                offset_y = random.randint(-30, -150)
            else:
                # Click title
                offset_x = random.randint(100, 250)
                offset_y = random.randint(5, 30)
        elif self.area == "channel" or self.area == "menu_videos_channel":
            # Cần click vào logo channel khi xem video -> vào channel page
            offset_x = random.randint(-3, 3)
            offset_y = random.randint(-2, 2)
        else:
            # Search feed: Logo ở bên phải, video thumbnail ở bên TRÁI
            rand_choice = random.choice([1, 2, 3])
            if rand_choice == 1:
                # CLICK VÀO THUMBNAIL                
                offset_x = random.randint(-320, -70)
                offset_y = random.randint(-10, 120)
            elif rand_choice == 2:
                # CLICK VÀO TITLE
                offset_x = random.randint(10, 220)
                offset_y = random.randint(-20, -10)
            else:
                # CLICK VÀO DESCRIPTION
                offset_x = random.randint(10, 220)
                offset_y = random.randint(50, 120)
    
        video_x = logo_x + offset_x
        video_y = logo_y + offset_y
    
        self.log(f"Logo at ({logo_x}, {logo_y}), video click at ({video_x}, {video_y}), area: {self.area}")
        return (video_x, video_y)

    def _hover_and_check_hand_cursor(self):
        """
        Hover mouse and check hand cursor
        
        Returns:
            bool: True if cursor = hand (clickable), False otherwise
        """
        if not self.region:          
            return False
        
        region_x, region_y, region_width, region_height = self.region
        
        # Random position in ads area
        random_x = region_x + random.randint(0, region_width)
        random_y = region_y + random.randint(0, region_height)
        
        self.log(f"Hovering on CHANNEL PAGE")
        
        # Move mouse (NO CLICK)
        MouseMoveAction.move_and_click_static(
            random_x, random_y,
            click_type=None,  # No click, just hover
            fast=False
        )
        
        time.sleep(0.5)  # Wait for cursor to update
        
        # Check if cursor = hand
        is_hand = self._is_hand_cursor()
        
        if is_hand:
            self.log("✓ Cursor = HAND (ads clickable)")
        else:
            self.log("Cursor NOT hand (no clickable ads)")
        
        return is_hand
    
    def _fallback_click_for_cookies(self):
        """
        Fallback: Move mouse to random positions, check hand cursor, click
    
        Returns:
            bool: True if clicked successfully
        """
        try:
            self.log("Using fallback: move mouse to find clickable element")        
        
            # Try multiple random positions
            max_attempts = 5
        
            for attempt in range(1, max_attempts + 1):                
                YouTubeRandomMoveScrollAutoAction(self.profile_id, 1, "main", self.log_prefix).execute()
                # Random position within area
                random_x = 500 + random.randint(0, 300)
                random_y = 400 + random.randint(0, 200)
            
                self.log(f"Fallback attempt {attempt}/{max_attempts}: Moving to ({random_x}, {random_y})")
            
                # Move mouse using pyautogui (for cursor check)
                MouseMoveAction.move_and_click_static(
                        random_x, random_y,
                        click_type=None,
                        fast=False
                    )              
            
                # Check if cursor is hand (clickable)
                if is_hand_cursor():
                    time.sleep(random.uniform(0.5, 2))
                    self.log(f"✓ Found clickable element at ({random_x}, {random_y})")
                
                    # Click using MouseMoveAction for consistency
                    pyautogui.click()
                
                    self.log("Clicked for cookie collection")
                
                    # Wait for page load
                    wait_time = random.uniform(3, 5)
                    time.sleep(wait_time)
                
                    return True
        
            # If no clickable found, click last position anyway
            self.log(f"No clickable found, clicking last position anyway", "WARNING")
        
            # Get last random position
            random_x = 500 + random.randint(0, 300)
            random_y = 400 + random.randint(0, 200)
        
            MouseMoveAction.move_and_click_static(
                random_x, random_y,
                click_type="single_click",
                fast=False
            )
        
            time.sleep(random.uniform(3, 5))
            return True
        
        except Exception as e:
            self.log(f"Fallback click error: {e}", "ERROR")
            return False


    def _fallback_click_for_cookies_only_browse(self):
        """
        Fallback: Move mouse to random positions, check hand cursor, click
    
        Returns:
            bool: True if clicked successfully
        """
        try:
            self.log("Using fallback: move mouse to find clickable element")        
        
            # Try multiple random positions
            max_attempts = 15
        
            for attempt in range(1, max_attempts + 1):
                if attempt % 4 == 1:
                    YouTubeRandomMoveScrollAutoAction(self.profile_id, 4, "main", self.log_prefix).execute()
                # Random position within area
                random_x = 500 + random.randint(0, 300)
                random_y = 400 + random.randint(0, 200)
            
                self.log(f"Fallback attempt {attempt}/{max_attempts}: Moving to ({random_x}, {random_y})")
            
                # Move mouse using pyautogui (for cursor check)
                MouseMoveAction.move_and_click_static(
                        random_x, random_y,
                        click_type=None,
                        fast=False
                    )
                time.sleep(0.3)
            
                # Check if cursor is hand (clickable)
                if is_hand_cursor():
                    time.sleep(random.uniform(0.5, 2))
                    self.log(f"✓ Found clickable element at ({random_x}, {random_y})")
                
                    # Click using MouseMoveAction for consistency
                    pyautogui.click()
                
                    self.log("Clicked for cookie collection")
                
                    # Wait for page load
                    wait_time = random.uniform(3, 5)
                    time.sleep(wait_time)
                
                    return True
        
            # If no clickable found, click last position anyway
            self.log(f"No clickable found, clicking last position anyway", "WARNING")
        
            # Get last random position
            random_x = 500 + random.randint(0, 300)
            random_y = 400 + random.randint(0, 200)
        
            MouseMoveAction.move_and_click_static(
                random_x, random_y,
                click_type="single_click",
                fast=False
            )
        
            time.sleep(random.uniform(3, 5))
            return True
        
        except Exception as e:
            self.log(f"Fallback click error: {e}", "ERROR")
            return False
