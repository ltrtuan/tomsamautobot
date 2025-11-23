# helpers/actions_headless/base_youtube_action_headless.py

"""
Base class for all headless YouTube actions

SIMPLIFIED VERSION:
- No pyautogui (physical mouse)
- No bring_to_front
- No health monitor
- Only Selenium direct interactions

Inherits from BaseFlowAction to reuse viewport helper methods
"""

from abc import ABC, abstractmethod
from helpers.actions.base_flow_action import BaseFlowAction
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random


class BaseYouTubeActionHeadless(BaseFlowAction, ABC):
    """
    Base class for headless YouTube actions
    
    Key differences from GUI version:
    - No pyautogui import
    - No MouseMoveAction
    - No GoLoginProfileHelper.bring_profile_to_front
    - Direct Selenium interactions only
    """
    
    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE HEADLESS]", debugger_address=None):
        """
        Initialize headless action
        
        Args:
            driver: Selenium WebDriver instance
            profile_id: GoLogin profile ID
            log_prefix: Prefix for log messages
            debugger_address: Chrome debugger address (optional)
        """
        BaseFlowAction.__init__(self, driver)
        self.driver = driver
        self.profile_id = profile_id
        self.log_prefix = log_prefix
        self.debugger_address = debugger_address
    
    # ========== ABSTRACT METHOD ==========
    
    @abstractmethod
    def execute(self):
        """Execute the action - must be implemented by subclasses"""
        pass
    
    # ========== HELPER METHODS ==========
    
    def _exit_fullscreen_if_needed(self):
        """
        Exit fullscreen mode if currently in fullscreen (Selenium only)
        
        Returns:
            bool: True if exited or not in fullscreen, False if error
        """
        try:
            # Check if in fullscreen
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
                
                # ===== HEADLESS: Use Selenium send_keys (NO pyautogui) =====
                # Send ESC key to body element
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ESCAPE)
                
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
        
        Returns:
            WebElement: Video element if found, None otherwise
        """
        selectors = [
            'video.html5-main-video',
            'video.video-stream',
            '#movie_player video',
            '.html5-video-player video'
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element and element.is_displayed():
                    return element
            except:
                continue
        
        return None
    
    def _scroll_element_into_view(self, element):
        """
        Scroll element into viewport using Selenium (center of viewport)
        
        Args:
            element: WebElement to scroll into view
            
        Returns:
            bool: True if success, False if error
        """
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                element
            )
            time.sleep(random.uniform(0.5, 1))
            return True
        except Exception as e:
            self.log(f"Scroll into view error: {e}", "ERROR")
            return False
    
    def _scroll_page_selenium(self, scroll_type="down", amount=300):
        """
        Scroll page using Selenium JavaScript (NO pyautogui)
        
        Args:
            scroll_type: "down" or "up"
            amount: Scroll amount in pixels (default 300)
            
        Returns:
            bool: True if success, False if error
        """
        try:
            if scroll_type == "down":
                scroll_amount = amount
            else:  # up
                scroll_amount = -amount
            
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.5, 1))
            return True
        except Exception as e:
            self.log(f"Scroll error: {e}", "ERROR")
            return False
    
    def _wait_for_element_visible(self, element, timeout=3):
        """
        Wait for element to be visible
        
        Args:
            element: WebElement to wait for
            timeout: Max wait time in seconds
            
        Returns:
            bool: True if visible, False if timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if element.is_displayed():
                    return True
            except:
                pass
            time.sleep(0.2)
        return False
    
    # ========== LOGGING & UTILITY ==========
    
    def log(self, message, level="INFO"):
        """
        Log message with consistent formatting
        
        Args:
            message: Message to log
            level: Log level (INFO, SUCCESS, WARNING, ERROR)
        """
        prefix_map = {
            "INFO": "ℹ",
            "SUCCESS": "✓",
            "WARNING": "⚠",
            "ERROR": "✗"
        }
        
        symbol = prefix_map.get(level, "•")
        print(f"{self.log_prefix}[{self.profile_id}] {symbol} {message}")
    
    def random_sleep(self, min_sec=1.0, max_sec=3.0):
        """
        Sleep for random duration
        
        Args:
            min_sec: Minimum sleep time
            max_sec: Maximum sleep time
            
        Returns:
            float: Actual sleep duration
        """
        duration = random.uniform(min_sec, max_sec)
        time.sleep(duration)
        return duration
