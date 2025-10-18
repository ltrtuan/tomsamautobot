# helpers/flow_google.py

import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class GoogleFlow:
    """Flow for Google search and browsing actions"""
    
    @staticmethod
    def execute(driver, keyword, profile_id, log_prefix="[GOOGLE]"):
        """
        Execute Google search flow
        
        Args:
            driver: Selenium WebDriver instance
            keyword: Search keyword
            profile_id: Profile ID for logging
            log_prefix: Log prefix
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"{log_prefix} [{profile_id}] Starting Google flow with keyword: '{keyword}'")
            
            # Navigate to Google
            url = "https://www.google.com"
            print(f"{log_prefix} [{profile_id}] Navigating to {url}...")
            driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            # Wait for page load
            driver.execute_script("return document.readyState")
            time.sleep(random.uniform(2, 3))
            
            # Find search box
            search_box = None
            selectors = ['textarea[name="q"]', 'input[name="q"]', 'input[title="Search"]']
            
            for selector in selectors:
                try:
                    search_box = driver.find_element(By.CSS_SELECTOR, selector)
                    if search_box:
                        break
                except:
                    continue
            
            if not search_box:
                print(f"{log_prefix} [{profile_id}] ✗ Search box not found")
                return False
            
            # Clear and type keyword with human-like delay
            search_box.clear()
            time.sleep(random.uniform(0.5, 1))
            
            for char in keyword:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            time.sleep(random.uniform(0.5, 1))
            
            # Submit search
            search_box.send_keys(Keys.RETURN)
            print(f"{log_prefix} [{profile_id}] ✓ Search submitted")
            
            # Wait for results
            time.sleep(random.uniform(3, 5))
            
            # Optional: Scroll and click random result
            try:
                # Scroll down
                driver.execute_script("window.scrollBy(0, 300);")
                time.sleep(random.uniform(1, 2))
                
                # Find search result links (skip ads)
                result_links = driver.find_elements(By.CSS_SELECTOR, 'div.g a[href]')
                if result_links and len(result_links) > 0:
                    # Click random result (skip first 2 to avoid ads)
                    clickable_results = [r for r in result_links[2:8] if r.is_displayed()]
                    if clickable_results:
                        random_result = random.choice(clickable_results)
                        random_result.click()
                        print(f"{log_prefix} [{profile_id}] ✓ Clicked random search result")
                        time.sleep(random.uniform(5, 8))
            except Exception as click_err:
                print(f"{log_prefix} [{profile_id}] ⚠ Could not click result: {click_err}")
            
            print(f"{log_prefix} [{profile_id}] ✓ Google flow completed")
            return True
            
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ✗ Error in Google flow: {e}")
            import traceback
            traceback.print_exc()
            return False
