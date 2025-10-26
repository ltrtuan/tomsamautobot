# helpers/actions/youtube_search_action.py

from helpers.actions.base_youtube_action import BaseYouTubeAction  # ← CHỈ CẦN IMPORT NÀY
from selenium.webdriver.common.by import By
from controllers.actions.mouse_move_action import MouseMoveAction
from controllers.actions.keyboard_action import KeyboardAction
import time
import random
import pyautogui


class YouTubeSearchAction(BaseYouTubeAction):  # ← CHỈ KẾ THỪA BaseYouTubeAction
    """Search for keyword on YouTube"""

    def __init__(self, driver, profile_id, keywords, log_prefix="[YOUTUBE]", debugger_address=None):
        super().__init__(driver, profile_id, log_prefix, debugger_address)
        self.keywords = keywords

    def execute(self):
        """Execute YouTube search"""
        try:
            import random
            keywords_youtube = self.keywords.get('keywords_youtube', [])
            keyword = random.choice(keywords_youtube)
            # Get suffix_prefix string từ keywords dict
            suffix_prefix_string = self.keywords.get('suffix_prefix', '')

            # Parse thành list
            from helpers.keyword_variation_helper import KeywordVariationHelper
            suffix_prefix_list = KeywordVariationHelper.parse_suffix_prefix_list(suffix_prefix_string)

            # Generate keyword variation
            keyword = KeywordVariationHelper.generate_keyword_variation(
                keyword, suffix_prefix_list
            )
            
            self.log(f"Searching for keyword: '{keyword}'", "INFO")
            
            # Exit fullscreen if needed (search box is hidden in fullscreen)
            if not self._exit_fullscreen_if_needed():
                self.log("Failed to exit fullscreen", "ERROR")
                return False
            
            # Find search box
            search_box = self._find_search_box()
            if not search_box:
                self.log("Search box not found", "ERROR")
                return False
            
            # ========== SỬ DỤNG VIEWPORT COORDINATES (từ BaseFlowAction) ==========
            viewport_coords = self.get_element_viewport_coordinates(search_box)
            if not viewport_coords:
                self.log("Failed to get viewport coordinates, using Selenium fallback", "WARNING")
                search_box.click()
                self.random_sleep(0.3, 0.7)
            else:
                # Lấy vị trí browser window trên màn hình
                viewport_offset_x = self.driver.execute_script(
                    "return window.screenX + (window.outerWidth - window.innerWidth) / 2;"
                )
                viewport_offset_y = self.driver.execute_script(
                    "return window.screenY + (window.outerHeight - window.innerHeight);"
                )
                
                # Calculate smart click position (method from BaseFlowAction)
                click_x, click_y = self.calculate_smart_click_position(
                    viewport_coords,
                    viewport_offset_x,
                    viewport_offset_y
                )
                
                if click_x is None or click_y is None:
                    self.log("Failed to calculate click position, using Selenium fallback", "WARNING")
                    search_box.click()
                    self.random_sleep(0.3, 0.7)
                else:
                    # Validate coordinates in screen bounds
                    screen_width, screen_height = pyautogui.size()
                    coords_valid = (
                        click_x >= 0 and
                        click_y >= 0 and
                        click_x <= screen_width and
                        click_y <= screen_height
                    )
                    
                    if coords_valid:
                        self.log(f"Clicking search box at smart position: ({click_x:.1f}, {click_y:.1f})", "INFO")
                        try:
                            MouseMoveAction.move_and_click_static(
                                click_x, click_y,
                                click_type="single_click",
                                fast=False
                            )
                            self.random_sleep(0.3, 0.7)
                        except Exception as pyautogui_err:
                            self.log(f"PyAutoGUI click failed: {pyautogui_err}, using Selenium fallback", "WARNING")
                            search_box.click()
                            self.random_sleep(0.3, 0.7)
                    else:
                        self.log(f"Invalid coords ({click_x:.1f}, {click_y:.1f}), using Selenium click", "WARNING")
                        search_box.click()
                        self.random_sleep(0.3, 0.7)
            
            # Clear search box
            KeyboardAction.press_key_static("Ctrl+a")
            time.sleep(0.1)
            KeyboardAction.press_key_static("Del")
            self.random_sleep(0.2, 0.5)
            
            # Type keyword with human-like typing
            self._type_human_like(keyword)
            
            # Submit search
            self.random_sleep(0.5, 1.5)
            KeyboardAction.press_key_static("Enter")
            self.log("Search submitted", "SUCCESS")
            
            # Wait for search results
            time.sleep(3)
            return True
            
        except Exception as e:
            self.log(f"Search error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False


    def _find_search_box(self):
        """Find YouTube search box"""
        selectors = [
            'input#search',
            'input[name="search_query"]',
            'input[placeholder*="Search"]',
            'input.ytd-searchbox'
        ]
        
        for selector in selectors:
            try:
                search_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                if search_box and search_box.is_displayed():
                    return search_box
            except:
                continue
        
        return None

    def _type_human_like(self, text):
        """Type text with human-like delays"""
        for char in text:
            pyautogui.write(char)
            if random.random() < 0.7:
                time.sleep(random.uniform(0.05, 0.15))
            else:
                time.sleep(random.uniform(0.15, 0.25))
