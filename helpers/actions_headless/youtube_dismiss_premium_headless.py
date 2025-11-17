# helpers/actions_headless/youtube_dismiss_premium_headless.py

"""
Dismiss YouTube Premium popup action for headless mode

Handles the "YouTube Premium" popup that appears with:
- Title: "YouTube Premium"
- Text: "Dùng YouTube không có quảng cáo"
- Buttons: "Không, cảm ơn" (dismiss) | "Miễn phí 1 tháng" (subscribe)

SIMPLIFIED VERSION:
- JavaScript-based click (NO pyautogui)
- No mouse movement
- Fast and efficient for headless background execution
"""

from helpers.actions_headless.base_youtube_action_headless import BaseYouTubeActionHeadless
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class YouTubeDismissPremiumHeadless(BaseYouTubeActionHeadless):
    """
    Dismiss YouTube Premium popup using JavaScript (headless mode)
    
    Features:
    - Detect and dismiss premium popup
    - Multiple selector strategies
    - Timeout if popup not found
    
    Differences from GUI:
    - JavaScript click (no physical mouse)
    - No mouse movement
    - Simpler and faster
    """
    
    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE HEADLESS]",
                 debugger_address=None, wait_time=3):
        """
        Initialize dismiss premium popup action
        
        Args:
            driver: Selenium WebDriver
            profile_id: GoLogin profile ID
            log_prefix: Log prefix for messages
            debugger_address: Chrome debugger address
            wait_time: Max seconds to wait for popup (default: 3)
        """
        super().__init__(driver, profile_id, log_prefix, debugger_address)
        self.wait_time = wait_time
    
    def execute(self):
        """
        Main execution: Dismiss YouTube Premium popup if present
        
        Returns:
            bool: True if popup dismissed or not found, False on error
        """
        try:
            self.log(f"Checking for YouTube Premium popup...", "INFO")
            
            # Try to find and dismiss popup
            dismissed = self._dismiss_premium_popup()
            
            if dismissed:
                self.log("✓ YouTube Premium popup dismissed", "SUCCESS")
                return True
            else:
                self.log("No YouTube Premium popup found (OK)", "INFO")
                return True  # Not an error if popup doesn't exist
                
        except Exception as e:
            self.log(f"Dismiss premium popup error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    def _dismiss_premium_popup(self):
        """
        Find and dismiss YouTube Premium popup
        
        Returns:
            bool: True if dismissed, False if not found
        """
        try:
            # Wait briefly for popup to appear
            wait = WebDriverWait(self.driver, self.wait_time)
            
            # ===== STRATEGY 1: Button with text "Không, cảm ơn" =====
            try:
                self.log("Strategy 1: Looking for 'Không, cảm ơn' button...", "DEBUG")
                
                # XPath for button containing text
                dismiss_button = wait.until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//button[contains(., 'Không') or contains(., 'No thanks') or contains(., 'cảm ơn')]"
                    ))
                )
                
                if dismiss_button and dismiss_button.is_displayed():
                    self.log("Found dismiss button, clicking...", "DEBUG")
                    
                    # JavaScript click
                    self.driver.execute_script("arguments[0].click();", dismiss_button)
                    
                    time.sleep(0.5)
                    self.log("✓ Clicked dismiss button", "SUCCESS")
                    return True
                    
            except Exception as e:
                self.log(f"Strategy 1 failed: {e}", "DEBUG")
            
            # ===== STRATEGY 2: ytd-button-renderer dismiss button =====
            try:
                self.log("Strategy 2: Looking for ytd-button-renderer...", "DEBUG")
                
                # Find all buttons in popup
                buttons = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "ytd-button-renderer button, tp-yt-paper-button"
                )
                
                for button in buttons:
                    button_text = button.text.strip().lower()
                    
                    # Check if it's the dismiss button (not subscribe)
                    if any(keyword in button_text for keyword in ['không', 'no thanks', 'cảm ơn', 'dismiss']):
                        if button.is_displayed():
                            self.log(f"Found dismiss button with text: '{button.text}'", "DEBUG")
                            
                            # JavaScript click
                            self.driver.execute_script("arguments[0].click();", button)
                            
                            time.sleep(0.5)
                            self.log("✓ Clicked dismiss button", "SUCCESS")
                            return True
                            
            except Exception as e:
                self.log(f"Strategy 2 failed: {e}", "DEBUG")
            
            # ===== STRATEGY 3: Close popup by X button =====
            try:
                self.log("Strategy 3: Looking for close (X) button...", "DEBUG")
                
                close_button = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "ytd-popup-container button[aria-label*='Close'], " +
                    "tp-yt-iron-dropdown button[aria-label*='Close']"
                )
                
                if close_button and close_button.is_displayed():
                    self.log("Found close (X) button", "DEBUG")
                    
                    # JavaScript click
                    self.driver.execute_script("arguments[0].click();", close_button)
                    
                    time.sleep(0.5)
                    self.log("✓ Clicked close button", "SUCCESS")
                    return True
                    
            except Exception as e:
                self.log(f"Strategy 3 failed: {e}", "DEBUG")
            
            # ===== STRATEGY 4: Press ESC key =====
            try:
                self.log("Strategy 4: Pressing ESC key...", "DEBUG")
                
                # JavaScript to trigger ESC keypress
                self.driver.execute_script("""
                    var event = new KeyboardEvent('keydown', {
                        key: 'Escape',
                        code: 'Escape',
                        keyCode: 27,
                        which: 27,
                        bubbles: true
                    });
                    document.dispatchEvent(event);
                """)
                
                time.sleep(0.5)
                self.log("✓ Pressed ESC key", "SUCCESS")
                return True
                
            except Exception as e:
                self.log(f"Strategy 4 failed: {e}", "DEBUG")
            
            # No popup found
            return False
            
        except Exception as e:
            self.log(f"Dismiss popup error: {e}", "DEBUG")
            return False
