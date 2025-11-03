# controllers/actions/flow_auto/actions_auto/youtube_find_click_video_auto_action.py

import time
import random
import pyautogui
import os
from controllers.actions.mouse_move_action import MouseMoveAction
from controllers.actions.flow_auto.actions_auto.base_flow_auto_action import BaseFlowAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_random_move_scroll_auto_action import YouTubeRandomMoveScrollAutoAction

class YouTubeFindClickVideoAutoAction(BaseFlowAutoAction):
    """
    Find video by channel logo (retry with scroll) + Click video
    Support both main feed and sidebar areas
    """
    
    def __init__(self, profile_id, keywords, log_prefix="[YOUTUBE AUTO]", area="main", flow_type="search"):

        """
        Initialize find and click video action
        
        Args:
            profile_id: GoLogin profile ID
            keywords: Dict containing logo paths and area info
            area: 'main' or 'sidebar' - determines which area to search
            log_prefix: Log prefix
        """
        super().__init__(profile_id, log_prefix)
        self.keywords = keywords
        self.area = area.lower()
        self.flow_type = flow_type
        # ========== EXTRACT PARAMS BASED ON AREA ==========
        if self.area == "sidebar":
            # Sidebar params
            self.logo_path = keywords.get('youtube_sidebar_image_search_path', '').strip()
            area_x = int(keywords.get('youtube_sidebar_area_x', 0))
            area_y = int(keywords.get('youtube_sidebar_area_y', 0))
            area_width = int(keywords.get('youtube_sidebar_area_width', 400))
            area_height = int(keywords.get('youtube_sidebar_area_height', 1080))
        else:
            # Main feed params (default)
            self.logo_path = keywords.get('youtube_image_search_path', '').strip()
            area_x = int(keywords.get('youtube_area_x', 0))
            area_y = int(keywords.get('youtube_area_y', 0))
            area_width = int(keywords.get('youtube_area_width', 1920))
            area_height = int(keywords.get('youtube_area_height', 1080))
        
        # Define search region
        self.region = None
        if area_width > 0 and area_height > 0:
            self.region = (area_x, area_y, area_width, area_height)
        
        self.log(f"Initialized for area: {self.area.upper()}, region: {self.region}")
    
    def _execute_internal(self):
        """Execute find logo → calculate video position → click video"""
        try:
            # ========== FIND LOGO WITH RETRY & SCROLL ==========
            # Browse does not need search logo
            if self.flow_type == "browse":
                max_retries = 1
            else:
                max_retries = 5
                
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
                        click_type="single_click",
                        fast=False
                    )
                
                    # Wait for video to start
                    wait_time = random.uniform(4, 6)
                    self.log(f"Waiting {wait_time:.1f}s for video to start")
                    time.sleep(wait_time)
                
                    self.log("✓ Video clicked successfully")
                    return True
            
                # Not found: Scroll and retry
                if attempt < max_retries:                   
                    YouTubeRandomMoveScrollAutoAction(self.profile_id, 1, "main", self.log_prefix).execute()
                    time.sleep(random.uniform(1, 2))        
         
            # ========== FALLBACK: CLICK RANDOM HAND CURSOR ==========
            self.log(f"✗ Logo not found after {max_retries} attempts", "WARNING")
            
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
            accuracy=0.7,
            click_offset_x=0,  # Return center of logo
            click_offset_y=0
        )
    
        if not result or not result['found']:
            return None
    
        logo_x, logo_y = result['center']
    
        # ========== CALCULATE CLICK POSITION BASED ON AREA ==========
        if self.area == "sidebar":
            # Sidebar: Logo ở bên phải, video thumbnail ở bên TRÁI
            offset_x = random.randint(-280, -50)
            offset_y = random.randint(-60, 60)
        else:
            # Main feed: Logo ở bên phải, video thumbnail ở bên TRÁI
            offset_x = random.randint(-320, -50)
            offset_y = random.randint(-10, 80)
    
        video_x = logo_x + offset_x
        video_y = logo_y + offset_y
    
        self.log(f"Logo at ({logo_x}, {logo_y}), video click at ({video_x}, {video_y}), area: {self.area}")
        return (video_x, video_y)

    
    
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
                time.sleep(0.3)
            
                # Check if cursor is hand (clickable)
                if self._is_hand_cursor():
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
                if self._is_hand_cursor():
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
