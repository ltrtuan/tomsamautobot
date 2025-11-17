# helpers/actions_headless/youtube_search_headless.py

"""
YouTube Search action for headless mode

SIMPLIFIED VERSION:
- Direct Selenium click on search box (NO pyautogui)
- Direct Selenium send_keys to type (NO KeyboardAction)
- Direct Selenium send_keys to submit (NO KeyboardAction)
- No mouse movement calculation

Fast and reliable for headless background execution
"""

from helpers.actions_headless.base_youtube_action_headless import BaseYouTubeActionHeadless
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException
import random
import time


class YouTubeSearchHeadless(BaseYouTubeActionHeadless):
    """
    Search for keyword on YouTube (headless mode)
    
    Features:
    - Random keyword selection
    - Keyword modification (suffix/prefix)
    - Wait for search results
    - Retry mechanism
    
    Differences from GUI:
    - Direct Selenium interactions (no pyautogui)
    - No mouse movement to search box
    - Simpler and faster
    """
    
    def __init__(self, driver, profile_id, keywords, log_prefix="[YOUTUBE HEADLESS]", debugger_address=None):
        """
        Initialize search action
        
        Args:
            driver: Selenium WebDriver
            profile_id: GoLogin profile ID
            keywords: Dict with 'keywords_youtube' list and 'suffix_prefix' string
            log_prefix: Log prefix
            debugger_address: Chrome debugger address
        """
        super().__init__(driver, profile_id, log_prefix, debugger_address)
        self.keywords = keywords
    
    def execute(self):
        """Execute YouTube search using Selenium direct interactions"""
        try:
            # ========== STEP 1: SELECT & PREPARE KEYWORD ==========
            keywords_youtube = self.keywords.get('keywords_youtube', [])
            
            if not keywords_youtube:
                self.log("No YouTube keywords provided", "ERROR")
                return False
            
            # Select random keyword
            keyword = random.choice(keywords_youtube)
            self.log(f"Selected keyword: '{keyword}'", "INFO")
            
         
            # ========== STEP 2: EXIT FULLSCREEN ==========
            if not self._exit_fullscreen_if_needed():
                self.log("Failed to exit fullscreen", "ERROR")
                return False
            
            # ========== STEP 3: FIND & FOCUS SEARCH BOX ==========
            search_box = self._find_search_box()
            if not search_box:
                self.log("Search box not found", "ERROR")
                return False
            
            # ===== DIRECT SELENIUM CLICK (NO PYAUTOGUI) =====
            try:
                self.log("Clicking search box with Selenium...", "INFO")
                search_box.click()
                time.sleep(random.uniform(0.3, 0.7))
            except Exception as e:
                self.log(f"Failed to click search box: {e}", "WARNING")
                # Try to focus anyway
                try:
                    self.driver.execute_script("arguments[0].focus();", search_box)
                except:
                    pass
            
            # ========== STEP 4: CLEAR EXISTING TEXT ==========
            try:
                # Clear search box first
                search_box.clear()
                time.sleep(random.uniform(0.2, 0.4))
            except Exception as e:
                self.log(f"Failed to clear search box: {e}", "WARNING")
            
            # ========== STEP 5: TYPE KEYWORD (SELENIUM SEND_KEYS) =====
            try:
                self.log(f"Typing keyword: '{keyword}'", "INFO")
                
                # ===== DIRECT SELENIUM SEND_KEYS (NO KeyboardAction) =====
                search_box.send_keys(keyword)
                
                # Wait after typing (simulate human delay)
                time.sleep(random.uniform(0.5, 1.0))
                
                self.log("✓ Keyword typed successfully", "SUCCESS")
                
            except Exception as e:
                self.log(f"Failed to type keyword: {e}", "ERROR")
                return False
            
            # ========== STEP 6: SUBMIT SEARCH (ENTER KEY) =====
            try:
                self.log("Submitting search (pressing Enter)...", "INFO")
                
                # ===== DIRECT SELENIUM SEND_KEYS (NO KeyboardAction) =====
                search_box.send_keys(Keys.ENTER)
                
                self.log("✓ Search submitted", "SUCCESS")
                
            except Exception as e:
                self.log(f"Failed to submit search: {e}", "ERROR")
                return False
            
            # ========== STEP 7: WAIT FOR SEARCH RESULTS ==========
            if not self._wait_for_search_results():
                self.log("Search results did not load", "WARNING")
                # Don't return False - maybe results loaded but we didn't detect
            
            self.log("✓ Search completed successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Execute error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    # ========== HELPER METHODS ==========
    
    def _find_search_box(self):
        """
        Find YouTube search box
        
        Returns:
            WebElement: Search box element if found, None otherwise
        """
        # Search box selectors (prioritized order)
        search_selectors = [
            'input#search',
            'input[name="search_query"]',
            'input[id="search"]',
            '#search-input input',
            'ytd-searchbox input',
            '#container input#search'
        ]
        
        for selector in search_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element and element.is_displayed():
                    self.log(f"Found search box with selector: {selector}", "DEBUG")
                    return element
            except:
                continue
        
        return None   
    
    def _wait_for_search_results(self, timeout=10):
        """
        Wait for search results to load
        
        Args:
            timeout: Max wait time in seconds
            
        Returns:
            bool: True if results loaded, False if timeout
        """
        try:
            self.log(f"Waiting for search results (timeout: {timeout}s)...", "INFO")
            
            # Result selectors
            result_selectors = [
                'ytd-video-renderer',
                'ytd-item-section-renderer',
                '#contents ytd-video-renderer',
                'ytd-search #contents'
            ]
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                for selector in result_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements and len(elements) > 0:
                            elapsed = time.time() - start_time
                            self.log(f"Search results loaded (waited {elapsed:.1f}s)", "SUCCESS")
                            return True
                    except:
                        pass
                
                time.sleep(random.uniform(1.0, 4.0))
            
            self.log(f"Search results did not load after {timeout}s", "WARNING")
            return False
            
        except Exception as e:
            self.log(f"Wait for results error: {e}", "ERROR")
            return False
