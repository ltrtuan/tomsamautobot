# helpers/actions/youtube_navigate_action.py

from helpers.actions.base_youtube_action import BaseYouTubeAction
from selenium.common.exceptions import WebDriverException
import time

class YouTubeNavigateAction(BaseYouTubeAction):
    """Navigate to YouTube homepage"""
    
    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE]", debugger_address=None, url="https://www.youtube.com"):
        super().__init__(driver, profile_id, log_prefix, debugger_address)
        self.url = url
    
    def execute(self):
        """Execute navigation to YouTube"""
        try:
            self.log(f"Navigating to {self.url}...", "INFO")
            
            try:
                self.driver.get(self.url)
            except WebDriverException as e:
                # ========== SỬ DỤNG HELPER ==========
                self.log("Navigation error, checking for tab crash...", "WARNING")
                if not self.check_and_recover_crashed_tab():
                    self.log("Tab crashed and recovery failed", "ERROR")
                    return False
                
                # After recovery, retry navigation
                self.log("Tab recovered, retrying navigation...", "INFO")
                time.sleep(2)
                self.driver.get(self.url)
                # ===================================
            
            # Wait for page load
            time.sleep(2)
            
            # Verify page loaded
            if "youtube.com" in self.driver.current_url.lower():
                self.log("Successfully navigated to YouTube", "SUCCESS")
                return True
            else:
                self.log(f"Unexpected URL: {self.driver.current_url}", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"Navigation error: {e}", "ERROR")
            return False
