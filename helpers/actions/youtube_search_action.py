# helpers/actions/youtube_search_action.py

from helpers.actions.base_youtube_action import BaseYouTubeAction
from selenium.webdriver.common.by import By
from controllers.actions.mouse_move_action import MouseMoveAction
from controllers.actions.keyboard_action import KeyboardAction
import time
import random

class YouTubeSearchAction(BaseYouTubeAction):
    """Search for keyword on YouTube"""
    
    def __init__(self, driver, profile_id, keyword, log_prefix="[YOUTUBE]", debugger_address=None):
        super().__init__(driver, profile_id, log_prefix, debugger_address)
        self.keyword = keyword
    
    def execute(self):
        """Execute YouTube search"""
        try:
            self.log(f"ℹ Searching for keyword: '{self.keyword}'", "INFO")
            
            # Find search box
            search_box = self._find_search_box()
            if not search_box:
                self.log("✗ Search box not found", "ERROR")
                return False
            
            # ========== FIX: VALIDATE COORDS BEFORE PYAUTOGUI ==========
            # Get screen coordinates
            screen_x, screen_y = self.get_random_click_position(search_box)
            
            # Validate coordinates
            import pyautogui
            screen_width, screen_height = pyautogui.size()
            
            coords_valid = (
                screen_x >= 0 and 
                screen_y >= 0 and 
                screen_x <= screen_width and 
                screen_y <= screen_height
            )
            
            if coords_valid:
                # Use PyAutoGUI click (natural human behavior)
                self.log(f"ℹ Clicking search box at ({screen_x}, {screen_y})", "INFO")
                try:
                    MouseMoveAction.move_and_click_static(screen_x, screen_y, click_type="single_click", fast=False)
                    self.random_sleep(0.3, 0.7)
                except Exception as pyautogui_err:
                    self.log(f"⚠ PyAutoGUI click failed: {pyautogui_err}, using Selenium fallback", "WARNING")
                    search_box.click()
                    self.random_sleep(0.3, 0.7)
            else:
                # Invalid coords → Use Selenium click directly
                self.log(f"⚠ Invalid coords ({screen_x}, {screen_y}), using Selenium click", "WARNING")
                search_box.click()
                self.random_sleep(0.3, 0.7)
            # ===========================================================
            
            # Clear search box
            KeyboardAction.press_key_static("Ctrl+a")
            time.sleep(0.1)
            KeyboardAction.press_key_static("Del")
            self.random_sleep(0.2, 0.5)
            
            # Type keyword with human-like typing
            self._type_human_like(self.keyword)
            
            # Submit search
            self.random_sleep(0.5, 1.5)
            KeyboardAction.press_key_static("Enter")
            self.log("✓ Search submitted", "SUCCESS")
            
            # Wait for search results
            time.sleep(3)
            return True
            
        except Exception as e:
            self.log(f"✗ Search error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    def _find_search_box(self):
        """Find YouTube search box"""
        selectors = [
            'input.yt-searchbox-input',
            'input[name="search_query"]',
            'input[placeholder*="Search"]'
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
        import pyautogui
        for char in text:
            pyautogui.write(char)
            if random.random() < 0.7:
                time.sleep(random.uniform(0.05, 0.1))
            else:
                time.sleep(random.uniform(0.1, 0.2))
