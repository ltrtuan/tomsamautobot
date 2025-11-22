# controllers/actions/flow_auto/actions_auto/youtube_find_search_box_auto_action.py

import time
import random
import pyautogui
import os
from controllers.actions.mouse_move_action import MouseMoveAction
from controllers.actions.flow_auto.actions_auto.base_flow_auto_action import BaseFlowAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_navigate_auto_action import YouTubeNavigateAutoAction
import logging
logger = logging.getLogger('TomSamAutobot')
from helpers.gologin_profile_helper import GoLoginProfileHelper

class YouTubeFindSearchBoxAutoAction(BaseFlowAutoAction):
    """
    Find search box (retry 3 times) → Click random position → Type keyword with mistakes → Enter
    """
    
    def __init__(self, profile_id, parameters, log_prefix="[YOUTUBE AUTO]", search_type="channel"):
        """
        Initialize find search box action
    
        Args:
            profile_id: GoLogin profile ID
            parameters: Full parameters dict containing:
                - youtube_search_icon_path: Search icon image path
                - keywords_youtube: List of keywords (cached from channel)
                - suffix_prefix: Suffix/prefix for variation (cached from channel)
                - youtube_area_x/y/width/height: Search area coords
                - ... (other params)
            log_prefix: Log prefix
        """
        super().__init__(profile_id, log_prefix)
        self.profile_id = profile_id
        self.log_prefix = log_prefix
        self.parameters = parameters
        self.search_type = search_type

    
    def _execute_internal(self):
        """Execute find search box → click → type keyword → enter"""
        result_bring = GoLoginProfileHelper.bring_profile_to_front(self.profile_id, driver=None)
        if result_bring:
            self._close_extra_tabs_keep_first()
            try:
                # ========== STEP 1: GENERATE KEYWORD ==========
                # Build minimal dict for _generate_keyword()
                keyword = ""
                if self.search_type == "channel":
                    keywords_dict = {
                        'keywords_youtube': self.parameters.get('keywords_youtube', []),
                        'suffix_prefix': self.parameters.get('suffix_prefix', '')
                    }
        
                    keyword = self._generate_keyword(keywords_dict)
                else:
                    keywords_google_file = self.parameters.get("keywords_google_file", "").strip()
                    if keywords_google_file and os.path.exists(keywords_google_file):                    
                        try:                    
                            with open(keywords_google_file, 'r', encoding='utf-8') as f:
                                keywords = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                        except Exception as e:
                            logger.error(f"[MIXED KEYWORDS] Failed to read keywords Google file: {e}")
                     
                        if keywords:
                            keyword = random.choice(keywords)
            
                if not keyword:
                    self.log("No keywords available", "ERROR")
                    return False
        
                self.log(f"Will search for keyword: '{keyword}'")
        
                # ========== STEP 2: FIND SEARCH BOX (RETRY 3 TIMES) ==========
                search_icon_path = self.parameters.get('youtube_search_icon_path', '').strip()
                search_result = None
                max_retries = 5
        
                for attempt in range(1, max_retries + 1):
                    self.log(f"Attempt {attempt}/{max_retries}: Looking for search box")
            
                    # Try image detection
                    if search_icon_path and os.path.exists(search_icon_path):
                        # Calculate search region (middle 1/3 of screen, height 300px)
                        screen_width, screen_height = pyautogui.size()
                        region_width = screen_width // 3
                        region_x = (screen_width - region_width) // 2
                        region_y = 0
                        region_height = 300
                        search_region = (region_x, region_y, region_width, region_height)
                
                        # ========== REUSE BASE CLASS METHOD ==========
                        search_result = self._find_image_on_screen(
                            image_path=search_icon_path,
                            region=search_region,
                            accuracy=0.7  # 0-1 scale
                        )
                
                        if search_result and search_result['found']:
                            self.log(f"✓ Found search icon on attempt {attempt}")
                            break
            
                    # Wait before retry
                    if attempt < max_retries:
                        self.log("Search icon not found, retrying...")
                        YouTubeNavigateAutoAction(self.profile_id,self.log_prefix).execute()
        
                # ========== STEP 3: CALCULATE CLICK POSITION ==========
                if search_result and search_result['found']:
                    # Found icon: Calculate search box position (LEFT of icon)
                    icon_x, icon_y = search_result['center']
                    confidence = search_result['confidence']
            
                    # Search box ở bên TRÁI icon
                    # YouTube UI: [___Search Box___] [🔍] [🎤]
                    offset_x = random.randint(-300, -100)  # Click LEFT of icon
                    offset_y = random.randint(-5, 5)       # Small vertical variation
            
                    click_x = icon_x + offset_x
                    click_y = icon_y + offset_y
            
                    self.log(f"Clicking search box at ({click_x}, {click_y}) "
                            f"[icon at ({icon_x}, {icon_y}), offset: ({offset_x}, {offset_y}), "
                            f"confidence: {confidence:.3f}]")
                else:
                    # Fallback: Use fixed position (center of screen, top area)
                    self.log("Using fixed position (fallback)", "WARNING")
                    screen_width, screen_height = pyautogui.size()
            
                    search_x = screen_width // 2
                    search_y = 100
            
                    # Add small random offset
                    offset_x = random.randint(-50, 50)
                    offset_y = random.randint(-2, 2)
            
                    click_x = search_x + offset_x
                    click_y = search_y + offset_y
            
                    self.log(f"Clicking search box at ({click_x}, {click_y}) [fixed position with random offset]")
        
                # Click search box
                MouseMoveAction.move_and_click_static(click_x, click_y, click_type="single_click", fast=False)
                self._random_short_pause()
                # Ctrl+L to focus address bar
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.3)
                if random.random() < 0.5:
                    pyautogui.press('backspace')
                # ========== STEP 4: TYPE KEYWORD WITH MISTAKES ==========
                self.log(f"Typing keyword: '{keyword}'")
        
                # 40% chance to make mistakes while typing (more realistic)
                if random.random() < 0.35:
                    self._type_with_mistakes(keyword, mistake_rate=0.1)
                else:
                    self._type_human_like(keyword)
        
                self._random_short_pause()
        
                # ========== STEP 5: PRESS ENTER ==========
                pyautogui.press('enter')
                self.log("Pressed Enter to search")
        
                # ========== STEP 6: WAIT FOR RESULTS ==========
                wait_time = random.uniform(4, 8)
                self.log(f"Waiting {wait_time:.1f}s for search results")
                time.sleep(wait_time)
        
                self.log("✓ Search completed")
                return True            
            except Exception as e:
                self.log(f"✗ Find search box failed: {e}", "ERROR")
                import traceback
                traceback.print_exc()
                return False
        return False
