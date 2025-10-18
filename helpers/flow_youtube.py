# helpers/flow_youtube.py

import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
# Import TomSamAutobot's human-like actions
from controllers.actions.mouse_move_action import MouseMoveAction
from controllers.actions.keyboard_action import KeyboardAction

class YouTubeFlow:
    """Flow for YouTube search and browsing actions with human-like behavior"""
    
    # ========== THÊM METHOD NÀY ==========
    @staticmethod
    def _is_tab_crashed(exception):
        """Check if exception is a tab crash error"""
        if isinstance(exception, WebDriverException):
            error_msg = str(exception).lower()
            return "tab crashed" in error_msg or "target closed" in error_msg
        return False
    
    @staticmethod
    def _handle_crashed_tab(driver, profile_id, log_prefix):
        """Handle crashed tab during flow execution"""
        try:
            print(f"{log_prefix} [{profile_id}] ⚠ Tab crashed during flow, opening new tab...")
        
            # Open new tab
            driver.execute_script("window.open('about:blank', '_blank');")
            import time
            time.sleep(1)
        
            # Switch to new tab
            handles = driver.window_handles
            if len(handles) > 1:
                driver.switch_to.window(handles[-1])
                print(f"{log_prefix} [{profile_id}] ✓ Switched to new tab")
                return True
            else:
                print(f"{log_prefix} [{profile_id}] ✗ Could not open new tab")
                return False
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ✗ Recovery failed: {e}")
            return False

    # =====================================
    
    @staticmethod
    def execute(driver, keyword, profile_id, log_prefix="[YOUTUBE]"):
        """
        Execute YouTube search flow with advanced human-like actions
        Includes retry logic for tab crashes
        """
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"{log_prefix} [{profile_id}] Retry attempt {attempt+1}/{max_retries}")
                
                print(f"{log_prefix} [{profile_id}] Starting YouTube flow with keyword: '{keyword}'")
                
                # Navigate to YouTube
                url = "https://www.youtube.com"
                print(f"{log_prefix} [{profile_id}] Navigating to {url}...")
                
                try:
                    driver.get(url)
                except WebDriverException as e:
                    if YouTubeFlow._is_tab_crashed(e):
                        print(f"{log_prefix} [{profile_id}] ✗ TAB CRASHED during navigation")
                        
                        # Try to recover
                        if YouTubeFlow._handle_crashed_tab(driver, profile_id, log_prefix):
                            # Retry navigation
                            time.sleep(2)
                            driver.get(url)
                        else:
                            # Cannot recover, try next attempt
                            if attempt < max_retries - 1:
                                time.sleep(3)
                                continue
                            else:
                                raise
                    else:
                        raise
                
                # Wait for page to fully load
                if not YouTubeFlow._wait_for_page_load(driver, profile_id, log_prefix):
                    if attempt < max_retries - 1:
                        print(f"{log_prefix} [{profile_id}] ⚠ Page load failed, retrying...")
                        time.sleep(3)
                        continue
                    return False
                
                # Random initial sleep (1-5s) after page load
                initial_sleep = random.uniform(1, 5)
                print(f"{log_prefix} [{profile_id}] Page loaded, waiting {initial_sleep:.1f}s...")
                time.sleep(initial_sleep)
                
                # ========== RANDOM PRE-SEARCH ACTIONS ==========
                print(f"{log_prefix} [{profile_id}] Performing pre-search random actions...")
                YouTubeFlow._perform_random_actions_loop(driver, profile_id, log_prefix)
                
                # ========== SEARCH FOR KEYWORD ==========
                if not YouTubeFlow._search_keyword(driver, keyword, profile_id, log_prefix):
                    if attempt < max_retries - 1:
                        print(f"{log_prefix} [{profile_id}] ⚠ Search failed, retrying...")
                        time.sleep(3)
                        continue
                    return False
                
                # Wait for search results
                if not YouTubeFlow._wait_for_page_load(driver, profile_id, log_prefix):
                    if attempt < max_retries - 1:
                        print(f"{log_prefix} [{profile_id}] ⚠ Search results load failed, retrying...")
                        time.sleep(3)
                        continue
                    return False
                
                result_sleep = random.uniform(2, 4)
                print(f"{log_prefix} [{profile_id}] Search results loaded, waiting {result_sleep:.1f}s...")
                time.sleep(result_sleep)
                
                # ========== RANDOM POST-SEARCH ACTIONS ==========
                print(f"{log_prefix} [{profile_id}] Performing post-search random actions...")
                YouTubeFlow._perform_random_actions_loop(driver, profile_id, log_prefix)
                
                # ========== OPTIONAL: CLICK RANDOM VIDEO ==========
                if random.random() < 0.7:  # 70% chance to click video
                    YouTubeFlow._click_random_video(driver, profile_id, log_prefix)
                
                print(f"{log_prefix} [{profile_id}] ✓ YouTube flow completed")
                return True
                
            except WebDriverException as e:
                if YouTubeFlow._is_tab_crashed(e):
                    print(f"{log_prefix} [{profile_id}] ✗ TAB CRASHED: {str(e)[:100]}")
                    if attempt < max_retries - 1:
                        print(f"{log_prefix} [{profile_id}] ⚠ Will retry after 5 seconds...")
                        time.sleep(5)
                        continue
                    else:
                        print(f"{log_prefix} [{profile_id}] ✗ Max retries reached, giving up")
                        return False
                else:
                    raise
            
            except Exception as e:
                print(f"{log_prefix} [{profile_id}] ✗ Error in YouTube flow: {e}")
                import traceback
                traceback.print_exc()
                
                if attempt < max_retries - 1:
                    print(f"{log_prefix} [{profile_id}] ⚠ Will retry after 3 seconds...")
                    time.sleep(3)
                    continue
                return False
        
        # If all retries failed
        print(f"{log_prefix} [{profile_id}] ✗ All retry attempts failed")
        return False
    
    @staticmethod
    def _wait_for_page_load(driver, profile_id, log_prefix, timeout=20):
        """Wait for page to fully load using Selenium"""
        try:
            print(f"{log_prefix} [{profile_id}] Waiting for page to load...")
        
            # Check if tab is crashed first
            try:
                current_url = driver.current_url
            except WebDriverException as e:
                if YouTubeFlow._is_tab_crashed(e):
                    print(f"{log_prefix} [{profile_id}] ✗ Tab is crashed")
                    return False
                raise
        
            # Wait for document.readyState == 'complete'
            wait = WebDriverWait(driver, timeout)
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        
            # Additional check: wait for body element
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
            print(f"{log_prefix} [{profile_id}] ✓ Page fully loaded")
            return True
        except WebDriverException as e:
            if YouTubeFlow._is_tab_crashed(e):
                print(f"{log_prefix} [{profile_id}] ✗ Tab crashed during page load check")
            else:
                print(f"{log_prefix} [{profile_id}] ⚠ Page load timeout: {e}")
            return False
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ⚠ Page load error: {e}")
            return False

    
    @staticmethod
    def _get_random_click_position(element, driver):
        """
        Get random click position within element bounds
        Shrink clickable area by 5px on each side to avoid clicking edges
        
        Args:
            element: Selenium WebElement
            driver: WebDriver instance
            
        Returns:
            tuple: (screen_x, screen_y) coordinates for clicking
        """
        # Get element position and size
        location = element.location  # {'x': 100, 'y': 200}
        size = element.size  # {'width': 300, 'height': 50}
        
        # Get browser window position
        window_x = driver.execute_script("return window.screenX")
        window_y = driver.execute_script("return window.screenY")
        
        # Calculate element bounds (shrink by 5px on each side)
        margin = 5
        safe_width = size['width'] - (margin * 2)
        safe_height = size['height'] - (margin * 2)
        
        # Ensure safe dimensions are positive
        if safe_width <= 0:
            safe_width = size['width'] * 0.6  # Use 60% of width if too small
            margin = (size['width'] - safe_width) / 2
        
        if safe_height <= 0:
            safe_height = size['height'] * 0.6  # Use 60% of height if too small
            margin_y = (size['height'] - safe_height) / 2
        else:
            margin_y = margin
        
        # Random position within safe area (local coordinates)
        local_x = location['x'] + margin + random.uniform(0, safe_width)
        local_y = location['y'] + margin_y + random.uniform(0, safe_height)
        
        # Convert to screen coordinates
        screen_x = int(window_x + local_x)
        screen_y = int(window_y + local_y + 100)  # +100 for browser chrome/toolbar
        
        return screen_x, screen_y
    
    @staticmethod
    def _perform_random_actions_loop(driver, profile_id, log_prefix):
        """
        Perform random actions in a loop with random repetitions
        Each action is executed 1-4 times with random sleep between
        """
        # List of available actions
        available_actions = [
            YouTubeFlow._action_move_mouse_random,
            YouTubeFlow._action_scroll_page,
            YouTubeFlow._action_move_to_element,
        ]
        
        # Random number of different actions to perform (2-4 actions)
        num_actions = random.randint(2, 4)
        print(f"{log_prefix} [{profile_id}] Will perform {num_actions} different action types")
        
        # Shuffle actions to randomize order
        random.shuffle(available_actions)
        
        for i in range(num_actions):
            action_func = available_actions[i % len(available_actions)]
            
            # Random repetitions for this action (1-4 times)
            repetitions = random.randint(1, 4)
            print(f"{log_prefix} [{profile_id}] Action {i+1}: {action_func.__name__} x{repetitions} times")
            
            for rep in range(repetitions):
                try:
                    # Execute action
                    action_func(driver, profile_id, log_prefix)
                    
                    # Random sleep after each repetition (0.5-2s)
                    sleep_time = random.uniform(0.5, 2.0)
                    time.sleep(sleep_time)
                except Exception as e:
                    print(f"{log_prefix} [{profile_id}] ⚠ Action error: {e}")
                    continue
    
    @staticmethod
    def _action_move_mouse_random(driver, profile_id, log_prefix):
        """
        Move mouse to random position using pyautogui (physical mouse movement)
        Optionally click (30% chance)
        """
        try:
            import pyautogui
            
            # Get viewport size from Selenium
            viewport_width = driver.execute_script("return window.innerWidth")
            viewport_height = driver.execute_script("return window.innerHeight")
            
            # Get browser window position
            window_x = driver.execute_script("return window.screenX")
            window_y = driver.execute_script("return window.screenY")
            
            # Random position within browser viewport (avoid edges by 100px)
            local_x = random.randint(100, viewport_width - 100)
            local_y = random.randint(100, viewport_height - 100)
            
            # Convert to screen coordinates
            screen_x = window_x + local_x
            screen_y = window_y + local_y + 100  # +100 for browser chrome/toolbar
            
            # Use TomSamAutobot's human-like mouse movement
            click_type = "single_click" if random.random() < 0.3 else None
            MouseMoveAction.move_and_click_static(screen_x, screen_y, click_type=click_type, fast=False)
            
            if click_type:
                print(f"{log_prefix} [{profile_id}] ✓ Moved mouse to ({screen_x}, {screen_y}) and clicked")
            else:
                print(f"{log_prefix} [{profile_id}] ✓ Moved mouse to ({screen_x}, {screen_y})")
            
            return True
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ⚠ Mouse move error: {e}")
            return False
    
    @staticmethod
    def _action_scroll_page(driver, profile_id, log_prefix):
        """
        Scroll page using pyautogui keyboard (physical keyboard input)
        Random method: Page Down/Up or Arrow keys
        Random speed and distance
        """
        try:
            # Random scroll method: 50% Page keys, 50% Arrow keys
            use_page_keys = random.random() < 0.5
            
            # Random direction: 80% down, 20% up
            direction_down = random.random() < 0.8
            
            if use_page_keys:
                # Page Down/Up
                key = "Down" if direction_down else "Up"
                times = random.randint(1, 3)
                
                # Use TomSamAutobot's keyboard action (multiple presses with delay)
                key_sequence = ";".join([key] * times)  # "Down;Down;Down"
                KeyboardAction.press_key_static(key_sequence)
                
                print(f"{log_prefix} [{profile_id}] ✓ Scrolled with Page {key} x{times}")
            else:
                # Arrow keys (smaller scroll)
                key = "Down" if direction_down else "Up"
                times = random.randint(3, 8)
                
                # Use TomSamAutobot's keyboard action
                key_sequence = ";".join([key] * times)
                KeyboardAction.press_key_static(key_sequence)
                
                print(f"{log_prefix} [{profile_id}] ✓ Scrolled with Arrow {key} x{times}")
            
            return True
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ⚠ Scroll error: {e}")
            return False
    
    @staticmethod
    def _action_move_to_element(driver, profile_id, log_prefix):
        """
        Use Selenium to find element coordinates, then use pyautogui to move mouse to RANDOM position within element
        """
        try:
            # Find random visible element (prefer video thumbnails, buttons)
            selectors = [
                'a#video-title',
                'ytd-thumbnail',
                'button',
                'a[href]',
            ]
            
            random.shuffle(selectors)
            
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_elements = [el for el in elements if el.is_displayed()]
                    
                    if visible_elements:
                        # Pick random element
                        target = random.choice(visible_elements[:10])  # Limit to first 10
                        
                        # Get RANDOM click position within element (shrunk by 5px)
                        screen_x, screen_y = YouTubeFlow._get_random_click_position(target, driver)
                        
                        # Use TomSamAutobot's human-like mouse movement (no click, just hover)
                        MouseMoveAction.move_and_click_static(screen_x, screen_y, click_type=None, fast=False)
                        
                        print(f"{log_prefix} [{profile_id}] ✓ Moved mouse to random position in element: {selector}")
                        return True
                except:
                    continue
            
            print(f"{log_prefix} [{profile_id}] ⚠ No hoverable elements found")
            return False
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ⚠ Move to element error: {e}")
            return False
    
    @staticmethod
    def _search_keyword(driver, keyword, profile_id, log_prefix):
        """
        Search for keyword on YouTube using physical keyboard input
        Click on RANDOM position within search box (not center)
        """
        try:
            # Find search box using Selenium
            search_box = None
            selectors = ['input#search', 'input[name="search_query"]', 'input[placeholder*="Search"]']
            
            for selector in selectors:
                try:
                    search_box = driver.find_element(By.CSS_SELECTOR, selector)
                    if search_box and search_box.is_displayed():
                        break
                except:
                    continue
            
            if not search_box:
                print(f"{log_prefix} [{profile_id}] ✗ Search box not found")
                return False
            
            # Get RANDOM click position within search box (shrunk by 5px to avoid edges)
            screen_x, screen_y = YouTubeFlow._get_random_click_position(search_box, driver)
            
            # Move mouse to search box and click using pyautogui
            print(f"{log_prefix} [{profile_id}] Moving to search box (random position: {screen_x}, {screen_y})...")
            MouseMoveAction.move_and_click_static(screen_x, screen_y, click_type="single_click", fast=False)
            time.sleep(random.uniform(0.3, 0.7))
            
            # Clear search box first (Ctrl+A then Delete)
            KeyboardAction.press_key_static("Ctrl+a")
            time.sleep(0.1)
            KeyboardAction.press_key_static("Del")
            time.sleep(random.uniform(0.2, 0.5))
            
            # Type keyword with human-like delay using pyautogui
            print(f"{log_prefix} [{profile_id}] Typing keyword: '{keyword}'")
            import pyautogui
            for char in keyword:
                pyautogui.write(char)
                # Random typing speed: 70% fast, 30% slow
                if random.random() < 0.7:
                    time.sleep(random.uniform(0.05, 0.1))  # Fast typing
                else:
                    time.sleep(random.uniform(0.1, 0.2))  # Slow typing
            
            # Random pause before submit (0.5-1.5s)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Press Enter using TomSamAutobot's keyboard action
            KeyboardAction.press_key_static("Enter")
            print(f"{log_prefix} [{profile_id}] ✓ Search submitted")
            
            return True
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ✗ Search error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def _click_random_video(driver, profile_id, log_prefix):
        """
        Click a random video from search results using physical mouse click
        Click on RANDOM position within video thumbnail (not center)
        """
        try:
            print(f"{log_prefix} [{profile_id}] Looking for videos to click...")
            
            # Wait a bit for videos to load
            time.sleep(random.uniform(1, 2))
            
            # Find video links using Selenium
            video_links = driver.find_elements(By.CSS_SELECTOR, 'a#video-title')
            
            if not video_links or len(video_links) == 0:
                print(f"{log_prefix} [{profile_id}] ⚠ No videos found")
                return False
            
            # Filter visible videos (skip first one to avoid ads)
            clickable_videos = [v for v in video_links[1:10] if v.is_displayed()]
            
            if not clickable_videos:
                print(f"{log_prefix} [{profile_id}] ⚠ No clickable videos found")
                return False
            
            # Pick random video
            target_video = random.choice(clickable_videos)
            
            # Scroll video into view using Selenium
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target_video)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Get RANDOM click position within video element (shrunk by 5px)
            hover_x, hover_y = YouTubeFlow._get_random_click_position(target_video, driver)
            
            # Move mouse to video (hover first at random position)
            MouseMoveAction.move_and_click_static(hover_x, hover_y, click_type=None, fast=False)
            time.sleep(random.uniform(0.3, 0.8))
            
            # Get another RANDOM position for clicking (more natural)
            click_x, click_y = YouTubeFlow._get_random_click_position(target_video, driver)
            
            # Click video at random position
            MouseMoveAction.move_and_click_static(click_x, click_y, click_type="single_click", fast=False)
            print(f"{log_prefix} [{profile_id}] ✓ Clicked random video at position ({click_x}, {click_y})")
            
            # Wait for video to load
            time.sleep(random.uniform(3, 6))
            
            # Random actions on video page
            YouTubeFlow._perform_random_actions_loop(driver, profile_id, log_prefix)
            
            return True
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ⚠ Video click error: {e}")
            return False
