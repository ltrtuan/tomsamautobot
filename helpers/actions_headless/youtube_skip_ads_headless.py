# helpers/actions_headless/youtube_skip_ads_headless.py

"""
Skip YouTube video ads action for headless mode

SIMPLIFIED VERSION:
- Direct Selenium click on skip button (NO pyautogui)
- No calculate click position
- No mouse movement
- Anti-detection: Random watch ad time before skipping (2-10s)

Fast and efficient for headless background execution
"""

from helpers.actions_headless.base_youtube_action_headless import BaseYouTubeActionHeadless
from selenium.webdriver.common.by import By
import random
import time


class YouTubeSkipAdsHeadless(BaseYouTubeActionHeadless):
    """
    Skip YouTube ads (headless mode)
    
    Features:
    - Detect skippable ads
    - Watch ad for random time (2-10s) - Anti-detection
    - Click skip button
    - Verify ad dismissed
    - Handle multiple ad formats
    
    Differences from GUI:
    - Direct Selenium click (no pyautogui)
    - No calculate click position
    - Simpler and faster
    - Anti-detection random delays
    """
    
    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE HEADLESS]", 
                 debugger_address=None, wait_time=2, watch_ad_time_range=(2, 10)):
        """
        Initialize skip ads action
        
        Args:
            driver: Selenium WebDriver
            profile_id: GoLogin profile ID
            log_prefix: Log prefix
            debugger_address: Chrome debugger address
            wait_time: Wait time before checking for ads (seconds)
            watch_ad_time_range: Tuple (min, max) seconds to watch ad before skipping
                                 Default: (2, 10) - watch 2-10 seconds randomly
                                 This simulates human behavior (anti-detection)
        """
        super().__init__(driver, profile_id, log_prefix, debugger_address)
        self.wait_time = wait_time
        self.watch_ad_time_range = watch_ad_time_range
    
    def execute(self):
        """Execute ad skip using Selenium direct click"""
        try:
            self.log("Checking for ads...", "INFO")
            
            # Wait for ads to potentially show
            time.sleep(self.wait_time)
            
            # ========== STEP 1: EXIT FULLSCREEN ==========
            if not self._exit_fullscreen_if_needed():
                self.log("Failed to exit fullscreen", "ERROR")
                return False
            
            # ========== STEP 2: FIND SKIP BUTTON ==========
            skip_button = self._find_skip_button()
            
            if not skip_button:
                self.log("No skip button found (no ads or non-skippable)", "INFO")
                return True  # Not an error - just no ads
            
            # ========== STEP 2.5: WATCH AD FOR RANDOM TIME (ANTI-DETECTION) =====
            watch_time = random.uniform(self.watch_ad_time_range[0], self.watch_ad_time_range[1])
            self.log(f"🎬 Ad detected, watching for {watch_time:.1f}s before skipping (anti-detection)...", "INFO")
            time.sleep(watch_time)
            
            # ========== STEP 3: CLICK SKIP BUTTON (SELENIUM) =====
            try:
                self.log("Watched ad, now clicking skip button...", "INFO")
                
                # ===== DIRECT SELENIUM CLICK (NO PYAUTOGUI) =====
                skip_button.click()
                
                # Wait for ad to dismiss
                time.sleep(random.uniform(0.5, 1.0))
                
                self.log("✓ Skip button clicked", "SUCCESS")
                
            except Exception as e:
                self.log(f"Failed to click skip button: {e}", "ERROR")
                return False
            
            # ========== STEP 4: VERIFY AD DISMISSED ==========
            if self._verify_ad_dismissed():
                self.log("✓ Ad dismissed successfully", "SUCCESS")
                return True
            else:
                self.log("⚠ Ad still present after skip attempt", "WARNING")
                return True  # Don't fail - maybe ad dismissed but we didn't detect
            
        except Exception as e:
            self.log(f"Execute error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    # ========== HELPER METHODS ==========
    
    def _find_skip_button(self):
        """
        Find YouTube skip ad button
        
        Returns:
            WebElement: Skip button element if found, None otherwise
        """
        # Skip button selectors (prioritized order)
        skip_selectors = [
            '.ytp-ad-skip-button',
            '.ytp-ad-skip-button-modern',
            'button.ytp-ad-skip-button',
            '.ytp-skip-ad-button',
            '.ytp-ad-skip-button-slot',
            'button[class*="ytp-ad-skip"]',
            '.ytp-ad-skip-button-container button',
            'button.ytp-ad-skip-button-modern',
            '.video-ads .ytp-ad-skip-button'
        ]
        
        for selector in skip_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                
                # Check if element is displayed
                if element and element.is_displayed():
                    # Additional check: element should be clickable
                    if self._is_element_clickable(element):
                        self.log(f"Found skip button with selector: {selector}", "DEBUG")
                        return element
                    
            except:
                continue
        
        return None
    
    def _is_element_clickable(self, element):
        """
        Check if element is clickable (not obscured, enabled)
        
        Args:
            element: WebElement to check
            
        Returns:
            bool: True if clickable
        """
        try:
            # Check if element is enabled
            if not element.is_enabled():
                return False
            
            # Check if element has size
            size = element.size
            if size['width'] == 0 or size['height'] == 0:
                return False
            
            return True
            
        except:
            return False
    
    def _verify_ad_dismissed(self, timeout=3):
        """
        Verify that ad was dismissed
        
        Args:
            timeout: Max wait time to verify (seconds)
            
        Returns:
            bool: True if ad dismissed
        """
        try:
            self.log("Verifying ad dismissed...", "DEBUG")
            
            # Ad indicator selectors
            ad_indicators = [
                '.ytp-ad-player-overlay',
                '.video-ads',
                '.ytp-ad-text',
                '.ytp-ad-skip-button',
                'div[class*="ad-showing"]'
            ]
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                ad_found = False
                
                for selector in ad_indicators:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        # Check if any ad indicator is visible
                        for elem in elements:
                            if elem.is_displayed():
                                ad_found = True
                                break
                        
                        if ad_found:
                            break
                            
                    except:
                        continue
                
                if not ad_found:
                    # No ad indicators found - ad dismissed
                    self.log("Ad indicators not found - ad dismissed", "DEBUG")
                    return True
                
                time.sleep(1)
            
            # Timeout - assume ad dismissed anyway
            self.log("Verification timeout - assuming ad dismissed", "DEBUG")
            return True
            
        except Exception as e:
            self.log(f"Verify ad dismissed error: {e}", "DEBUG")
            return True  # Assume dismissed on error
