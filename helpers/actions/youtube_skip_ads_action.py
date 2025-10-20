# helpers/actions/youtube_skip_ads_action.py

from helpers.actions.base_youtube_action import BaseYouTubeAction
from selenium.webdriver.common.by import By
from controllers.actions.mouse_move_action import MouseMoveAction
import time

class YouTubeSkipAdsAction(BaseYouTubeAction):
    """Skip YouTube ads if present"""
    
    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE]", debugger_address=None, wait_time=2):
        super().__init__(driver, profile_id, log_prefix, debugger_address)
        self.wait_time = wait_time
    
    def execute(self):
        """Execute ad skip"""
        try:
            self.log("Checking for ads...", "INFO")
            
            # Wait for ad to potentially show
            time.sleep(self.wait_time)
            
            # Look for skip button
            skip_selectors = [
                '.ytp-ad-skip-button',
                '.ytp-ad-skip-button-modern',
                'button.ytp-ad-skip-button',
                '.ytp-skip-ad-button'
            ]
            
            for selector in skip_selectors:
                try:
                    skip_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if skip_button and skip_button.is_displayed():
                        # Use base class method for click position
                        screen_x, screen_y = self.get_random_click_position(skip_button)
                        
                        # Click skip button
                        MouseMoveAction.move_and_click_static(screen_x, screen_y, click_type="single_click", fast=False)
                        self.log("Skipped ad", "SUCCESS")
                        time.sleep(2)
                        return True
                except:
                    continue
            
            self.log("No ads detected or skip button not available yet", "INFO")
            return False
            
        except Exception as e:
            self.log(f"Ad skip error: {e}", "WARNING")
            return False
