# helpers/actions_headless/youtube_scroll_headless.py

"""
Scroll page action for headless mode

SIMPLIFIED VERSION:
- JavaScript scrollBy() (NO pyautogui keyboard)
- No mouse movement to safe area
- Random scroll amounts and times

Fast and efficient for headless background execution
"""

from helpers.actions_headless.base_youtube_action_headless import BaseYouTubeActionHeadless
from selenium.webdriver.common.by import By
import random
import time


class YouTubeScrollHeadless(BaseYouTubeActionHeadless):
    """
    Scroll page using JavaScript (headless mode)
    
    Features:
    - Random scroll direction (up/down)
    - Random scroll amount
    - Multiple scroll iterations
    - Natural delays between scrolls
    
    Differences from GUI:
    - JavaScript scrollBy() (no keyboard arrow keys)
    - No mouse movement to safe area
    - Simpler and faster
    """
    
    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE HEADLESS]",
                 debugger_address=None, direction="random", times=None):
        """
        Initialize scroll action
        
        Args:
            driver: Selenium WebDriver
            profile_id: GoLogin profile ID
            log_prefix: Log prefix
            debugger_address: Chrome debugger address
            direction: "up", "down", or "random" (default: "random")
            times: Number of scroll iterations (None = random 2-5)
        """
        super().__init__(driver, profile_id, log_prefix, debugger_address)
        self.direction = direction
        self.times = times
    
    def execute(self):
        """Execute scroll action using JavaScript"""
        try:
            # ========== STEP 1: EXIT FULLSCREEN ==========
            if not self._exit_fullscreen_if_needed():
                self.log("Failed to exit fullscreen", "ERROR")
                return False
            
            # ========== STEP 2: DETERMINE SCROLL TIMES ==========
            if self.times is None:
                scroll_times = random.randint(2, 5)
            else:
                scroll_times = self.times
            
            self.log(f"Starting scroll ({scroll_times} iterations, direction: {self.direction})...", "INFO")
            
            # ========== STEP 3: SCROLL MULTIPLE TIMES ==========
            for i in range(scroll_times):
                # Determine direction for this iteration
                if self.direction == "random":
                    current_direction = random.choice(["down", "up"])
                else:
                    current_direction = self.direction
                
                # Random scroll amount (200-500 pixels)
                scroll_amount = random.randint(500, 900)
                
                # Execute scroll
                success = self._scroll_page_js(current_direction, scroll_amount)
                
                if success:
                    self.log(f"Scroll {i+1}/{scroll_times}: {current_direction} {scroll_amount}px", "INFO")
                else:
                    self.log(f"Scroll {i+1}/{scroll_times}: Failed", "WARNING")
                
                # Random delay between scrolls (0.5-2s) - Anti-detection
                if i < scroll_times - 1:  # Don't delay after last scroll
                    delay = random.uniform(0.5, 2.0)
                    time.sleep(delay)
            
            self.log(f"✓ Completed {scroll_times} scroll iterations", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Execute error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    # ========== HELPER METHODS ==========
    
    def _scroll_page_js(self, direction, amount):
        """
        Scroll page using JavaScript
        
        Args:
            direction: "up" or "down"
            amount: Scroll amount in pixels
            
        Returns:
            bool: True if success
        """
        try:
            # Calculate scroll delta
            if direction == "down":
                scroll_delta = amount
            else:  # up
                scroll_delta = -amount
            
            # ===== JAVASCRIPT SCROLL (NO PYAUTOGUI KEYBOARD) =====
            self.driver.execute_script(f"window.scrollBy(0, {scroll_delta});")
            
            # Small delay for scroll animation
            time.sleep(random.uniform(0.3, 0.7))
            
            return True
            
        except Exception as e:
            self.log(f"JavaScript scroll error: {e}", "ERROR")
            return False
