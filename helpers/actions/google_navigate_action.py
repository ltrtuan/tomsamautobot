# helpers/actions/google_navigate_action.py

from helpers.actions.base_youtube_action import BaseYouTubeAction
from controllers.actions.keyboard_action import KeyboardAction
from selenium.common.exceptions import WebDriverException
import time
import random
import pyautogui

class GoogleNavigateAction(BaseYouTubeAction):
    """Navigate to Google search by typing keyword directly in address bar"""
    
    def __init__(self, driver, profile_id, keywords, log_prefix="[GOOGLE]", debugger_address=None):
        """
        Initialize Google Navigate Action
        
        Args:
            driver: Selenium WebDriver instance
            profile_id: Profile ID
            keywords: List of keywords to search
            log_prefix: Prefix for log messages
            debugger_address: Chrome debugger address (optional)
        """
        super().__init__(driver, profile_id, log_prefix, debugger_address)
        self.keywords = keywords
    
    def execute(self):
        """
        Execute Google search by typing keyword in address bar
        Chrome will auto-redirect to Google search results
        """
        try:
            # Select random keyword
            keywords_google = self.keywords.get('keywords_google', [])
            keyword = random.choice(keywords_google)
            
            # Get suffix_prefix string từ keywords dict
            suffix_prefix_string = self.keywords.get('suffix_prefix', '')

            # Parse thành list
            from helpers.keyword_variation_helper import KeywordVariationHelper
            suffix_prefix_list = KeywordVariationHelper.parse_suffix_prefix_list(suffix_prefix_string)

            # Generate keyword variation
            keyword = KeywordVariationHelper.generate_keyword_variation(
                keyword, suffix_prefix_list
            )

            self.log(f"Searching Google for keyword: '{keyword}'", "INFO")
            
            # Click address bar (Ctrl+L to focus)
            self.log("Focusing address bar...", "DEBUG")
            KeyboardAction.press_key_static("Ctrl+l")
            time.sleep(random.uniform(0.5, 1.0))
            
            # Clear address bar (in case there's existing content)
            KeyboardAction.press_key_static("Ctrl+a")
            time.sleep(0.1)
            KeyboardAction.press_key_static("Del")
            time.sleep(random.uniform(0.3, 0.5))
            
            # Type keyword with human-like typing
            self.log(f"Typing keyword: '{keyword}'", "DEBUG")
            self._type_human_like(keyword)
            
            # Press Enter to search
            self.random_sleep(0.5, 1.5)
            KeyboardAction.press_key_static("Enter")
            self.log("Search submitted via address bar", "SUCCESS")
            
            # Wait for Google search results to load
            time.sleep(3)
            
            # Verify we're on Google search results page
            current_url = self.driver.current_url.lower()
            if "google.com/search" in current_url or "google.com.vn/search" in current_url:
                self.log(f"✓ Successfully navigated to Google search: {current_url}", "SUCCESS")
                return True
            else:
                self.log(f"⚠ Unexpected URL after search: {current_url}", "WARNING")
                # Still return True as search was executed, just maybe different redirect
                return True
            
        except WebDriverException as e:
            # Handle tab crash
            self.log("Navigation error, checking for tab crash...", "WARNING")
            if not self.check_and_recover_crashed_tab():
                self.log("Tab crashed and recovery failed", "ERROR")
                return False
            
            # Retry after recovery
            self.log("Tab recovered, retrying search...", "INFO")
            time.sleep(2)
            return self.execute()  # Recursive retry
            
        except Exception as e:
            self.log(f"Google search error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    def _type_human_like(self, text):
        """
        Type text with human-like delays between characters
        
        Args:
            text: Text to type
        """
        for char in text:
            pyautogui.write(char)
            # 70% chance of short delay, 30% chance of longer delay
            if random.random() < 0.7:
                time.sleep(random.uniform(0.05, 0.15))
            else:
                time.sleep(random.uniform(0.15, 0.25))
