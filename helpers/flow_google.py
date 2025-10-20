# helpers/flow_google.py

import time
import random
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from helpers.action_chain_manager import ActionChainManager
from helpers.gologin_profile_helper import GoLoginProfileHelper
from controllers.actions.mouse_move_action import MouseMoveAction
from controllers.actions.keyboard_action import KeyboardAction

class GoogleFlow:
    """Google Flow Orchestrator"""
    
    @staticmethod
    def execute_main_flow(driver, keyword, profile_id, debugger_address, log_prefix="[GOOGLE]"):
        """MAIN FLOW: Search → Click result"""
        return ActionChainManager.execute_chain(
            profile_id,
            GoogleFlow._main_chain,
            driver, keyword, profile_id, debugger_address, log_prefix
        )
    
    @staticmethod
    def _main_chain(driver, keyword, profile_id, debugger_address, log_prefix):
        """Locked chain for Google search"""
        print(f"{log_prefix} [{profile_id}] ========== GOOGLE CHAIN START ==========")
        
        try:
            # Navigate
            GoogleFlow._navigate_to_google(driver, profile_id, debugger_address, log_prefix)
            
            # Pre-search actions
            GoogleFlow._random_actions(driver, profile_id, log_prefix, num_actions=2)
            
            # Search
            GoogleFlow._search_keyword(driver, keyword, profile_id, log_prefix)
            
            # Post-search actions
            GoogleFlow._random_actions(driver, profile_id, log_prefix, num_actions=2)
            
            # Click result
            GoogleFlow._click_search_result(driver, profile_id, log_prefix)
            
            print(f"{log_prefix} [{profile_id}] ========== GOOGLE CHAIN END ==========")
            return True
            
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ✗ Error: {e}")
            return False
    
    @staticmethod
    def _navigate_to_google(driver, profile_id, debugger_address, log_prefix):
        """Navigate to Google"""
        url = "https://www.google.com"
        print(f"{log_prefix} [{profile_id}] Navigating to {url}...")
        
        try:
            driver.get(url)
        except WebDriverException:
            if not GoLoginProfileHelper.check_and_fix_crashed_tabs(driver, debugger_address, log_prefix):
                raise Exception("Tab crashed and recovery failed")
            time.sleep(2)
            driver.get(url)
        
        time.sleep(random.uniform(3, 5))
    
    @staticmethod
    def _random_actions(driver, profile_id, log_prefix, num_actions=2):
        """Random scroll/mouse actions"""
        for i in range(num_actions):
            if random.random() < 0.5:
                scroll_amount = random.randint(100, 300)
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(1, 2))
    
    @staticmethod
    def _search_keyword(driver, keyword, profile_id, log_prefix):
        """Search keyword"""
        print(f"{log_prefix} [{profile_id}] Searching: '{keyword}'")
        
        # Find search box
        search_box = None
        for selector in ['textarea[name="q"]', 'input[name="q"]']:
            try:
                search_box = driver.find_element(By.CSS_SELECTOR, selector)
                if search_box.is_displayed():
                    break
            except:
                continue
        
        if not search_box:
            raise Exception("Search box not found")
        
        # Click search box
        location = search_box.location
        size = search_box.size
        viewport_offset_x = driver.execute_script("return window.screenX + (window.outerWidth - window.innerWidth);")
        viewport_offset_y = driver.execute_script("return window.screenY + (window.outerHeight - window.innerHeight);")
        
        random_x = location['x'] + size['width'] * random.uniform(0.3, 0.7)
        random_y = location['y'] + size['height'] * random.uniform(0.3, 0.7)
        screen_x = int(viewport_offset_x + random_x)
        screen_y = int(viewport_offset_y + random_y)
        
        MouseMoveAction.move_and_click_static(screen_x, screen_y, click_type="single_click", fast=False)
        time.sleep(random.uniform(0.3, 0.7))
        
        # Type keyword
        KeyboardAction.press_key_static("Ctrl+a")
        time.sleep(0.1)
        KeyboardAction.press_key_static("Del")
        time.sleep(0.2)
        
        import pyautogui
        for char in keyword:
            pyautogui.write(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        time.sleep(random.uniform(0.5, 1.5))
        KeyboardAction.press_key_static("Enter")
        time.sleep(random.uniform(3, 5))
    
    @staticmethod
    def _click_search_result(driver, profile_id, log_prefix):
        """Click search result"""
        try:
            driver.execute_script("window.scrollBy(0, 300);")
            time.sleep(1)
            
            result_links = driver.find_elements(By.CSS_SELECTOR, 'div.g a[href]')
            clickable = [r for r in result_links[2:8] if r.is_displayed()]
            
            if clickable:
                target = random.choice(clickable)
                location = target.location
                size = target.size
                viewport_offset_x = driver.execute_script("return window.screenX + (window.outerWidth - window.innerWidth);")
                viewport_offset_y = driver.execute_script("return window.screenY + (window.outerHeight - window.innerHeight);")
                
                random_x = location['x'] + size['width'] * random.uniform(0.3, 0.7)
                random_y = location['y'] + size['height'] * random.uniform(0.3, 0.7)
                screen_x = int(viewport_offset_x + random_x)
                screen_y = int(viewport_offset_y + random_y)
                
                MouseMoveAction.move_and_click_static(screen_x, screen_y, click_type="single_click", fast=False)
                time.sleep(random.uniform(5, 8))
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ⚠ Could not click result: {e}")
