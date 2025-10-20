# helpers/actions/base_youtube_action.py

from abc import ABC, abstractmethod
import time
import random
from selenium.common.exceptions import WebDriverException
from helpers.gologin_profile_helper import GoLoginProfileHelper

class BaseYouTubeAction(ABC):
    """
    Base class for all YouTube actions
    Each action is a modular, reusable component
    """
    
    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE]", debugger_address=None):
        self.driver = driver
        self.profile_id = profile_id
        self.log_prefix = log_prefix
        self.debugger_address = debugger_address
    
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
    
    # ========== USE GOLOGIN_PROFILE_HELPER METHODS ==========
    
    def check_and_recover_crashed_tab(self):
        """
        Check if tab crashed and attempt recovery using GoLoginProfileHelper
        Returns:
            bool: True if tab is healthy or recovered, False if unrecoverable
        """
        if not self.debugger_address:
            self.log("No debugger address available for crash recovery", "WARNING")
            return True
        
        return GoLoginProfileHelper.check_and_fix_crashed_tabs(
            self.driver, 
            self.debugger_address,
            self.log_prefix
        )
    
    def bring_to_front(self):
        """Bring browser window to front using GoLoginProfileHelper"""
        return GoLoginProfileHelper.bring_profile_to_front(
            self.profile_id,
            self.driver,
            self.log_prefix
        )
    
    def cleanup_tabs(self):
        """Close all tabs except first one using GoLoginProfileHelper"""
        return GoLoginProfileHelper.cleanup_browser_tabs(
            self.driver,
            self.log_prefix
        )
    
    # ========== CENTRALIZED get_random_click_position ==========
    
    def get_random_click_position(self, element):
        """
        Calculate random click position within element
        Converts element position to absolute screen coordinates
        
        Args:
            element: Selenium WebElement
            
        Returns:
            tuple: (screen_x, screen_y) absolute screen coordinates
        """
        try:
            location = element.location
            size = element.size
            
            # Get window position on screen
            viewport_offset_x = self.driver.execute_script(
                "return window.screenX + (window.outerWidth - window.innerWidth);"
            )
            viewport_offset_y = self.driver.execute_script(
                "return window.screenY + (window.outerHeight - window.innerHeight);"
            )
            
            # Random position within element (30-70% range for natural click)
            random_x = location['x'] + size['width'] * random.uniform(0.3, 0.7)
            random_y = location['y'] + size['height'] * random.uniform(0.3, 0.7)
            
            # Convert to screen coordinates
            screen_x = int(viewport_offset_x + random_x)
            screen_y = int(viewport_offset_y + random_y)
            
            return screen_x, screen_y
            
        except Exception as e:
            self.log(f"Position calculation error: {e}", "WARNING")
            # Return default safe position
            return 500, 300
