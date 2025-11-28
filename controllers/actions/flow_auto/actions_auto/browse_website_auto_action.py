# controllers/actions/flow_auto/actions_auto/browse_website_auto_action.py

import time
import random
import pyautogui
import pyperclip
from helpers.gologin_profile_helper import GoLoginProfileHelper
from controllers.actions.flow_auto.actions_auto.base_flow_auto_action import BaseFlowAutoAction
from helpers.app_helpers import perform_random_movements_with_click_detection

# Import YouTube sub-actions for Choice 2
from controllers.actions.flow_auto.actions_auto.youtube_find_search_box_auto_action import YouTubeFindSearchBoxAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_random_move_scroll_auto_action import YouTubeRandomMoveScrollAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_skip_ads_auto_action import YouTubeSkipAdsAutoAction

class BrowseWebsiteAutoAction(BaseFlowAutoAction):
    """
    Browse to a website URL and perform random mouse movements with click detection
    
    Two random behaviors:
    - Choice 1 (50%): Navigate to random URL → Random click
    - Choice 2 (50%): If on YouTube → Search → Click video (skip navigation)
    """
    
    def __init__(self, profile_id, parameters, area = "search", choice = "youtube", log_prefix="[BROWSE WEBSITE]"):
        """
        Initialize browse website action
        
        Args:
            profile_id: GoLogin profile ID
            parameters: Dict containing 'list_warmup_url' and 'keywords_google'
            log_prefix: Prefix for log messages
        """
        super().__init__(profile_id, log_prefix)
        self.parameters = parameters
        self.area = area.lower()
        self.choice = choice
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
    
    def _execute_internal(self):
        """Execute browse website action with 2 random choices"""
        try:
            # ========== RANDOM CHOICE: 1 or 2 ==========
            # choice = random.choice([1, 2])
            # self.log(f"🎲 Random choice: {choice}")
            
            if self.choice == "web":
                return self._execute_choice_1_navigate_and_click()
            else:
                return self._execute_choice_2_youtube_search()
        
        except Exception as e:
            self.log(f"✗ Browse website error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    def _execute_choice_1_navigate_and_click(self , random_click = False):
        """
        Choice 1: Navigate to random URL and perform random clicks
        
        Flow:
        1. Bring browser to front
        2. Focus address bar (Ctrl+L)
        3. Enter random URL from list_warmup_url
        4. Press Enter
        5. Random mouse movements with click detection (5 attempts)
        """
        self.log("📍 Choice 1: Navigate to URL and click")
        
        # Get keywords list from parameters
        list_warmup_url = self.parameters.get('list_warmup_url', [])
        
        if not list_warmup_url:
            self.log("No warmup URLs available", "WARNING")
            return False
        
        # Random choice ONE URL from list
        warmup_url = random.choice(list_warmup_url)
        
        # ========== STEP 1: BRING BROWSER TO FRONT ==========
        result_bring = GoLoginProfileHelper.bring_profile_to_front(self.profile_id, driver=None)
        if result_bring:
            time.sleep(0.5)
        
            # ========== STEP 2: FOCUS ADDRESS BAR (Ctrl+L) ==========
            self.log("Focusing address bar (Ctrl+L)")
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.3)
        
            # ========== STEP 3: ENTER URL ==========
            self.log(f"Entering URL: {warmup_url}")
        
            # Use pyperclip for reliability (handles special characters)
            pyperclip.copy(warmup_url)
            pyautogui.hotkey('ctrl', 'v')  # Paste
        
            # Wait 1-2 seconds before Enter
            wait_before_enter = random.uniform(1, 2)
            self.log(f"Waiting {wait_before_enter:.1f}s before Enter")
            time.sleep(wait_before_enter)
        
            # ========== STEP 4: PRESS ENTER ==========
            self.log("Pressing Enter to navigate")
            pyautogui.press('enter')
        
            # Wait for page load
            page_load_wait = random.uniform(3, 5)
            self.log(f"Waiting {page_load_wait:.1f}s for page load")
            time.sleep(page_load_wait)
           
            if random_click:
                # ========== STEP 5: RANDOM MOUSE MOVEMENTS WITH CLICK DETECTION ==========
                self.log("Starting random mouse movements (3 attempts)")
        
                # Use helper function from app_helpers
                clicked, position = perform_random_movements_with_click_detection(
                    max_attempts=2,
                    type_action=self.parameters.get('keyword_type')
                )
        
                if clicked:
                    self.log(f"✓ Successfully clicked at {position}")
                else:
                    self.log("No clickable elements found after 5 attempts", "WARNING")
        
            self.log("✓ Choice 1 completed")
            return True
        
        return False
    
    def _execute_choice_2_youtube_search(self):
        """
        Choice 2: YouTube search and click video (100% YouTube)
    
        Flow:
        1. Bring browser to front
        2. Get current URL
        3. If NOT on YouTube:
           - Navigate to youtube.com (Ctrl+L → youtube.com → Enter)
        4. If already on YouTube:
           - Skip navigation step
        5. Find search box → Enter keyword → Enter
        6. Click random video
        """
        self.log("🎥 Choice 2: YouTube search and click video")
    
        # ========== STEP 1: BRING BROWSER TO FRONT ==========
        result_bring = GoLoginProfileHelper.bring_profile_to_front(self.profile_id, driver=None)
        if result_bring:
            time.sleep(1)
            self._close_extra_tabs_keep_first()
            time.sleep(1)
            # # ========== STEP 2: GET CURRENT URL ==========
            # current_url = self._get_current_url()
    
            # if current_url:
            #     self.log(f"Current URL: {current_url}")
    
            # # ========== STEP 3: CHECK IF NEED TO NAVIGATE TO YOUTUBE ==========
            # if not current_url or "youtube.com" not in current_url.lower():
            #     self.log("Not on YouTube, navigating to youtube.com")

            # If clicked to Short video back to home
            
                
            for attempt in range(1, 6):
                current_url = self._get_current_url()
                if "youtube.com/watch" not in current_url.lower():
                    self._navigate_youtube()
                    time.sleep(random.uniform(2, 3))
                    
                if self.area == "main" or self.area == "search":
                    # self._navigate_youtube()
                    # ========== STEP 4: FIND SEARCH BOX AND ENTER KEYWORD: RANDOM SEARCH VIDEO AND CLICK RANDOM VIDEO SEARCH OR CLICK RANDOM VIDEO HOME ==========
                    choice = random.choice([1, 2])
                    if choice == 1:
                        self.log("Finding search box and entering keyword")
    
                        search_action = YouTubeFindSearchBoxAutoAction(
                            profile_id=self.profile_id,
                            parameters=self.parameters,  # Contains keywords_google
                            log_prefix=self.log_prefix,
                            search_type="browse"
                        )
    
                        search_action.execute()
    
           
                        # Wait for search results
                        time.sleep(random.uniform(2, 3))
                    else:                                   
                        num_random_actions = random.randint(1, 3)
                        YouTubeRandomMoveScrollAutoAction(self.profile_id, num_random_actions, "main", self.log_prefix).execute()
    
            
                # ========== STEP 5: CLICK RANDOM VIDEO ==========
                self.log("Clicking random video from search results")
    
                # Use helper function from app_helpers
                clicked, position = perform_random_movements_with_click_detection(
                    max_attempts=5, type_action="youtube" , region = self.region
                )
        
                if clicked:
                    self.log(f"✓ Successfully clicked at {position}")               
                    time.sleep(random.uniform(2, 3))
                    current_url = self._get_current_url()
                    if "youtube.com/shorts" not in current_url.lower() and "youtube.com/watch" in current_url.lower():
                        YouTubeSkipAdsAutoAction(
                                profile_id=self.profile_id,
                                parameters=self.parameters,  # Pass keywords dict for ads area params
                                log_prefix=self.log_prefix
                        ).execute()
                    return True
                else:
                    self.log("No clickable elements found after 5 attempts", "WARNING")
              
                if attempt < 5:
                    continue
        
        return False
    
    def _navigate_youtube(self):
        # Navigate to YouTube (same as Choice 1)
        # Focus address bar
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.3)
        
        # Enter youtube.com
        pyperclip.copy("youtube.com")
        pyautogui.hotkey('ctrl', 'v')
        
        # Wait before Enter
        wait_before_enter = random.uniform(1, 2)
        time.sleep(wait_before_enter)
        
        # Press Enter
        self.log("Pressing Enter to navigate to YouTube")
        pyautogui.press('enter')
        
        # Wait for page load
        page_load_wait = random.uniform(3, 5)
        self.log(f"Waiting {page_load_wait:.1f}s for YouTube to load")
        time.sleep(page_load_wait)
    
    
