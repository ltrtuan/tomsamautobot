# helpers/actions/base_youtube_action.py

from abc import ABC, abstractmethod
import time
import random
from selenium.common.exceptions import WebDriverException
from helpers.gologin_profile_helper import GoLoginProfileHelper
from helpers.actions.base_flow_action import BaseFlowAction  # ← THÊM IMPORT
from controllers.actions.mouse_move_action import MouseMoveAction
import pyautogui

class BaseYouTubeAction(BaseFlowAction, ABC):  # ← THÊM BaseFlowAction
    """
    Base class for all YouTube actions
    Each action is a modular, reusable component
    Inherits viewport coordinate methods from BaseFlowAction
    """
    
    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE]", debugger_address=None):
        BaseFlowAction.__init__(self, driver)  # ← THÊM: khởi tạo BaseFlowAction
        self.driver = driver
        self.profile_id = profile_id
        self.log_prefix = log_prefix
        self.debugger_address = debugger_address
        

    def _exit_fullscreen_if_needed(self):
        """
        Exit fullscreen mode if currently in fullscreen
        Returns: True if exited fullscreen or not in fullscreen, False if error
        """
        try:
            # Check if in fullscreen using same logic as YouTubeFullscreenAction
            is_fullscreen = self.driver.execute_script("""
                // Check if document is in fullscreen
                if (document.fullscreenElement || 
                    document.webkitFullscreenElement || 
                    document.mozFullScreenElement || 
                    document.msFullscreenElement) {
                    return true;
                }
                
                // Check YouTube player fullscreen state
                var player = document.querySelector('.html5-video-player');
                if (player && player.classList.contains('ytp-fullscreen')) {
                    return true;
                }
                
                return false;
            """)
            
            if is_fullscreen:
                self.log("Currently in fullscreen, exiting...", "INFO")
                # Import here to avoid circular import
                from controllers.actions.keyboard_action import KeyboardAction
                KeyboardAction.press_key_static("Escape")  # Use ESC instead of F11 for safer exit
                import time
                time.sleep(1)  # Wait for fullscreen exit animation
                self.log("Exited fullscreen mode", "SUCCESS")
                return True
            else:
                # Not in fullscreen, no action needed
                return True
                
        except Exception as e:
            self.log(f"Exit fullscreen error: {e}", "ERROR")
            return False

    def _find_video_element(self):
        """
        Find YouTube video player element
        Returns: Video element if found, None otherwise
        """
        selectors = [
            'video.html5-main-video',
            'video.video-stream',
            '#movie_player video',
            '.html5-video-player video'
        ]
    
        for selector in selectors:
            try:
                from selenium.webdriver.common.by import By
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return element
            except:
                continue
    
        return None

    def _random_scroll_pyautogui(self, area_type="main"):
        """
        Random scroll page using pyautogui (giả lập chuột vật lý, tránh bot detection)
        
        Args:
            area_type: "main" or "sidebar" (for different scroll amounts)
        """
        try:
            # Different scroll amounts based on area
            if area_type == "main":
                # Main area: Scroll more (300-600px equivalent)
                # pyautogui scroll units: negative = down, positive = up
                # Each unit ≈ 100px on most systems
                scroll_amount = random.randint(-700, -500)  # -3 to -6 units = 300-600px down
            else:  # sidebar
                # Sidebar: Scroll less (200-400px equivalent)
                scroll_amount = random.randint(-400, -200)  # -2 to -4 units = 200-400px down
            
            self.log(f"Scrolling {abs(scroll_amount) * 100}px (pyautogui)...", "INFO")           
            screen_width, screen_height = pyautogui.size()
            # Move to right-center (safe area, no UI elements)
            # Move to right edge, random Y (avoid top/bottom 100px)
            safe_x = screen_width - random.randint(5,30)  # 10px từ mép phải
            safe_y = random.randint(100, screen_height - 100)  # Random từ 100px đến (height-100)px

            MouseMoveAction.move_and_click_static(safe_x, safe_y, "single_click", fast=False)
            # Use pyautogui scroll (simulates physical mouse wheel)
            pyautogui.scroll(scroll_amount)
            
            # Add small random delay after scroll (human-like behavior)
            time.sleep(random.uniform(0.3, 0.6))
        
        except Exception as e:
            self.log(f"Error scrolling with pyautogui: {e}", "ERROR")

    @abstractmethod
    def execute(self):
        """Execute the action - must be implemented by subclasses"""
        pass

    def log(self, message, level="INFO"):
        """Log message with consistent formatting"""
        prefix_map = {
            "INFO": "ℹ",
            "SUCCESS": "✓",
            "WARNING": "⚠",
            "ERROR": "✗"
        }
        symbol = prefix_map.get(level, "•")
        print(f"{self.log_prefix} [{self.profile_id}] {symbol} {message}")

    def random_sleep(self, min_sec=1.0, max_sec=3.0):
        """Sleep for random duration"""
        duration = random.uniform(min_sec, max_sec)
        time.sleep(duration)
        return duration
    
