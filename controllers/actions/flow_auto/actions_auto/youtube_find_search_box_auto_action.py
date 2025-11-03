# controllers/actions/flow_auto/actions_auto/youtube_find_search_box_auto_action.py

import time
import random
import pyautogui
import os
from controllers.actions.mouse_move_action import MouseMoveAction
from controllers.actions.flow_auto.actions_auto.base_flow_auto_action import BaseFlowAutoAction


class YouTubeFindSearchBoxAutoAction(BaseFlowAutoAction):
    """
    Find search box (retry 3 times) → Click random position → Type keyword with mistakes → Enter
    """
    
    def __init__(self, profile_id, keywords, log_prefix="[YOUTUBE AUTO]"):
        """
        Initialize find search box action
        
        Args:
            profile_id: GoLogin profile ID
            keywords: Dict containing:
                - youtube_search_icon_path: Search icon image path
                - keywords_youtube: List of keywords
                - suffix_prefix: Suffix/prefix for variation
            log_prefix: Log prefix
        """
        super().__init__(profile_id, log_prefix)
        self.keywords = keywords
    
    def _execute_internal(self):
        """Execute find search box → click → type keyword → enter"""
        try:
            # ========== STEP 1: GENERATE KEYWORD ==========
            keyword = self._generate_keyword(self.keywords)
            if not keyword:
                self.log("No keywords available", "ERROR")
                return False
            
            self.log(f"Will search for keyword: '{keyword}'")
            
            # ========== STEP 2: FIND SEARCH BOX (RETRY 3 TIMES) ==========
            search_icon_path = self.keywords.get('youtube_search_icon_path', '').strip()
            
            icon_pos = None
            max_retries = 3
            
            
            for attempt in range(1, max_retries + 1):
                self.log(f"Attempt {attempt}/{max_retries}: Looking for search box")
    
                # Try image detection
                if search_icon_path and os.path.exists(search_icon_path):
                    icon_pos = self._find_by_image(search_icon_path)
        
                    if icon_pos:
                        self.log(f"✓ Found search icon on attempt {attempt}")
                        break
    
                # Wait before retry
                if attempt < max_retries:
                    self.log("Search icon not found, retrying...")
                    time.sleep(1)

            # ========== STEP 3: CALCULATE CLICK POSITION ==========
            if icon_pos:
                # Found icon: Calculate search box position (LEFT of icon)
                icon_x, icon_y = icon_pos
    
                # Search box ở bên TRÁI icon
                # YouTube UI: [___Search Box___] [🔍] [🎤]
                offset_x = random.randint(-300, -100)  # Click bên TRÁI icon (negative offset)
                offset_y = random.randint(-5, 5)       # Small vertical variation
    
                click_x = icon_x + offset_x
                click_y = icon_y + offset_y
    
                self.log(f"Clicking search box at ({click_x}, {click_y}) [icon at ({icon_x}, {icon_y}), offset: ({offset_x}, {offset_y})]")
            else:
                # Fallback: Use fixed position (center of screen, top area)
                self.log("Using fixed position (fallback)", "WARNING")
                screen_width, screen_height = pyautogui.size()
    
                # Fixed position: center of screen, top area
                search_x = screen_width // 2
                search_y = 100
    
                # Add small random offset
                offset_x = random.randint(-50, 50)
                offset_y = random.randint(-2, 2)
    
                click_x = search_x + offset_x
                click_y = search_y + offset_y
    
                self.log(f"Clicking search box at ({click_x}, {click_y}) [fixed position with random offset]")
            
            self.log(f"Clicking search box at ({click_x}, {click_y}) [icon at ({icon_x}, {icon_y}), offset: ({offset_x}, {offset_y})]")
            MouseMoveAction.move_and_click_static(click_x, click_y, click_type="single_click", fast=False)
            self._random_short_pause()
            
            # ========== STEP 4: TYPE KEYWORD WITH MISTAKES ==========
            self.log(f"Typing keyword: '{keyword}'")
            
            # 20% chance to make mistakes while typing (more realistic)
            if random.random() < 0.4:
                self._type_with_mistakes(keyword, mistake_rate=0.05)
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
    
    def _find_by_image(self, search_icon_path):
        """Find search icon using image detection"""
        try:          
        
            self.log(f"Searching for icon: {search_icon_path}")
        
            # Get screen size
            screen_width, screen_height = pyautogui.size()
        
            # Define search region: middle 1/3 of screen, height 300px
            region_width = screen_width // 3
            region_x = (screen_width - region_width) // 2  # Center horizontally
            region_y = 0  # Start from top
            region_height = 300
        
            search_region = (region_x, region_y, region_width, region_height)
            self.log(f"Search region (middle 1/3, h=300): {search_region}")
        
            # Use ImageSearcher directly
            from models.image_search import ImageSearcher
        
            # ImageSearcher expects INTEGER percentage (0-100)
            accuracy_percent = 70
            self.log(f"Creating ImageSearcher with accuracy: {accuracy_percent}%")
        
            # Create searcher instance
            searcher = ImageSearcher(
                image_path=search_icon_path,
                region=search_region,  # Use limited region
                accuracy=accuracy_percent
            )
        
            self.log("Calling ImageSearcher.search()...")
            success, result = searcher.search()
        
            self.log(f"Search result: success={success}, result={result}")
        
            if success and result:
                center_x, center_y, confidence = result
                self.log(f"✓ Icon found at ({center_x}, {center_y}), confidence: {confidence:.3f}")
                return (center_x, center_y)
            else:
                self.log("Icon not found by ImageSearcher")
                return None
        
        except Exception as e:
            self.log(f"Image search error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return None





