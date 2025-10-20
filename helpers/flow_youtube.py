# helpers/flow_youtube.py

import time
import random
from selenium.webdriver.common.by import By
from helpers.action_chain_manager import ActionChainManager

# Import modular actions
from helpers.actions.youtube_navigate_action import YouTubeNavigateAction
from helpers.actions.youtube_search_action import YouTubeSearchAction
from helpers.actions.youtube_skip_ads_action import YouTubeSkipAdsAction
from helpers.actions.youtube_click_video_action import YouTubeClickVideoAction
from helpers.actions.youtube_scroll_action import YouTubeScrollAction
from helpers.actions.youtube_mouse_move_action import YouTubeMouseMoveAction

# Import TomSamAutobot actions
from controllers.actions.mouse_move_action import MouseMoveAction
from controllers.actions.keyboard_action import KeyboardAction
from helpers.gologin_profile_helper import GoLoginProfileHelper

class YouTubeFlow:
    """
    YouTube Flow Orchestrator - Natural interaction mode
    Profiles perform interactions whenever they get lock, organically
    """
    
    @staticmethod
    def execute_main_flow(driver, keyword, profile_id, debugger_address, log_prefix="[YOUTUBE]"):
        """
        MAIN FLOW - Natural mode:
        1. Search & Click video (LOCKED)
        2. Release lock
        3. Periodic interactions (LOCKED when active, compete with other profiles)
        4. Thread completes when interaction cycles done (video may still be playing - that's OK!)
        
        Returns:
            bool: True if successful
        """
     
        # ========== PHASE 1: SEARCH & START VIDEO (LOCKED) ==========
        chain_success = ActionChainManager.execute_chain(
            profile_id,
            YouTubeFlow._search_and_start_video_chain,
            driver, keyword, profile_id, debugger_address, log_prefix
        )
        
        if not chain_success:
            print(f"{log_prefix} [{profile_id}] ✗ Initial chain failed")
            return False
        
        # ========== PHASE 2: NATURAL INTERACTION CYCLES ==========
        print(f"{log_prefix} [{profile_id}] ========== VIDEO PLAYING, ENTERING NATURAL INTERACTION MODE ==========")
        
        # Random number of interaction cycles (3-6 times)
        num_interaction_cycles = random.randint(3, 6)
        print(f"{log_prefix} [{profile_id}] Will perform {num_interaction_cycles} interaction cycles")
        
        for cycle in range(num_interaction_cycles):
            # NO SLEEP HERE - Profile tries to acquire lock immediately
            # Other profiles may get lock first, that's natural!
            
            print(f"{log_prefix} [{profile_id}] [Cycle {cycle+1}/{num_interaction_cycles}] Competing for lock...")
            
            # Execute interaction cycle (LOCKED - will wait for lock if needed)
            interaction_success = ActionChainManager.execute_chain(
                profile_id,
                YouTubeFlow._video_interaction_chain,
                driver, profile_id, debugger_address, log_prefix, cycle + 1
            )
            
            if not interaction_success:
                print(f"{log_prefix} [{profile_id}] ⚠ Interaction cycle {cycle+1} failed, continuing...")
        
        print(f"{log_prefix} [{profile_id}] ✓ Finished all interaction cycles (video may still be playing - that's natural)")
        return True
    
    @staticmethod
    def _search_and_start_video_chain(driver, keyword, profile_id, debugger_address, log_prefix):
        """
        LOCKED CHAIN: Navigate → Search → Click video → Wait for playing
        Lock is released immediately after video starts playing
        """
        print(f"{log_prefix} [{profile_id}] ========== LOCKED CHAIN START: SEARCH & PLAY ==========")
        
        try:
            # THÊM ĐOẠN NÀY VÀO ĐẦU (TRONG LOCK)
            # Fix crashed tabs INSIDE lock to prevent window focus conflicts
            print(f"{log_prefix} [{profile_id}] Checking for crashed tabs...")
            if not GoLoginProfileHelper.check_and_fix_crashed_tabs(driver, debugger_address, log_prefix):
                print(f"{log_prefix} [{profile_id}] ⚠ Could not fix crashed tab, continuing anyway...")
                return False
        
            # Bring window to front AFTER fixing crashed tabs
            GoLoginProfileHelper.bring_profile_to_front(profile_id, driver=driver, log_prefix=log_prefix)
            time.sleep(2)
            
            # Step 1: Navigate to YouTube
            YouTubeFlow._navigate_to_youtube(driver, profile_id, debugger_address, log_prefix)
            
            # Step 2: Pre-search random actions
            # YouTubeFlow._random_actions(driver, profile_id, debugger_address, log_prefix, num_actions=2)
            
            
            # Step 3: Search keyword
            YouTubeSearchAction(driver, profile_id, keyword, log_prefix, debugger_address).execute()
            time.sleep(random.uniform(2, 4))
            
            # Step 4: Post-search scroll
            YouTubeScrollAction(driver, profile_id, log_prefix, debugger_address, direction="down", times=2).execute()
            time.sleep(random.uniform(1, 2))
            
            # Step 5: Skip ads if present
            YouTubeSkipAdsAction(driver, profile_id, log_prefix, debugger_address, wait_time=1).execute()
            
            # Step 6: Click video and WAIT FOR IT TO START PLAYING
            print(f"{log_prefix} [{profile_id}] Clicking video and waiting for playback...")
            video_action = YouTubeClickVideoAction(
                driver, profile_id, log_prefix, debugger_address,
                video_index_range=(1, 10)
            )
            
            if not video_action.execute():
                print(f"{log_prefix} [{profile_id}] ✗ Failed to start video playback")
                return False
            
            # VIDEO IS PLAYING - CHAIN COMPLETE
            print(f"{log_prefix} [{profile_id}] ========== LOCKED CHAIN END: VIDEO PLAYING ==========")
            return True
            
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ✗ Error in chain: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def _video_interaction_chain(driver, profile_id, debugger_address, log_prefix, cycle_number):
        """
        LOCKED CHAIN: Perform human-like interactions
        Random selection and random repetitions = organic watch time
        
        Possible actions:
        - Move mouse randomly
        - Click video timeline (seek)
        - Pause/Resume video
        - Fullscreen toggle
        - Click on ad (open new tab, scroll, close)
        - Scroll page
        - Volume control
        """
        print(f"{log_prefix} [{profile_id}] ========== INTERACTION CHAIN START: CYCLE {cycle_number} ==========")
        
        try:
            # Check if video ended or autoplayed to next video - that's OK!
            try:
                current_url = driver.current_url
                print(f"{log_prefix} [{profile_id}] Current URL: {current_url}")
            except:
                pass
            
            # Random number of interactions in this cycle (1-4)
            num_interactions_this_cycle = random.randint(1, 4)
            
            # Random selection of interaction types
            interaction_types = [
                'mouse_move',
                'seek_video',
                'pause_resume',
                'click_ad',
                'scroll_page'
            ]
            
            selected_interactions = random.sample(
                interaction_types, 
                min(num_interactions_this_cycle, len(interaction_types))
            )
            
            print(f"{log_prefix} [{profile_id}] Will perform {num_interactions_this_cycle} interactions: {selected_interactions}")
            
            for interaction in selected_interactions:
                if interaction == 'mouse_move':
                    YouTubeFlow._interaction_mouse_move(driver, profile_id, log_prefix)
                
                elif interaction == 'seek_video':
                    YouTubeFlow._interaction_seek_video(driver, profile_id, log_prefix)
                
                elif interaction == 'pause_resume':
                    YouTubeFlow._interaction_pause_resume(driver, profile_id, log_prefix)
                
                elif interaction == 'click_ad':
                    YouTubeFlow._interaction_click_ad(driver, profile_id, log_prefix)
                
                elif interaction == 'scroll_page':
                    YouTubeFlow._interaction_scroll_page(driver, profile_id, log_prefix)
                
                # Random wait between interactions (organic timing)
                wait_time = random.uniform(1, 5)
                print(f"{log_prefix} [{profile_id}] Waiting {wait_time:.1f}s before next interaction...")
                time.sleep(wait_time)
            
            print(f"{log_prefix} [{profile_id}] ========== INTERACTION CHAIN END: CYCLE {cycle_number} ==========")
            return True
            
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ✗ Error in interaction chain: {e}")
            return False
    
    # ========== INTERACTION METHODS (KEEP EXISTING) ==========
    
    @staticmethod
    def _interaction_mouse_move(driver, profile_id, log_prefix):
        """Move mouse randomly on video player area"""
        try:
            print(f"{log_prefix} [{profile_id}] 🖱️ Moving mouse randomly...")
            
            # Random number of mouse moves (1-3)
            num_moves = random.randint(1, 3)
            
            for i in range(num_moves):
                viewport_width = driver.execute_script("return window.innerWidth")
                viewport_height = driver.execute_script("return window.innerHeight")
                viewport_offset_x = driver.execute_script("return window.screenX + (window.outerWidth - window.innerWidth);")
                viewport_offset_y = driver.execute_script("return window.screenY + (window.outerHeight - window.innerHeight);")
                
                random_x = random.randint(int(viewport_width * 0.3), int(viewport_width * 0.7))
                random_y = random.randint(int(viewport_height * 0.3), int(viewport_height * 0.6))
                
                screen_x = int(viewport_offset_x + random_x)
                screen_y = int(viewport_offset_y + random_y)
                
                MouseMoveAction.move_and_click_static(screen_x, screen_y, click_type=None, fast=False)
                print(f"{log_prefix} [{profile_id}] ✓ Mouse moved to ({screen_x}, {screen_y})")
                
                if i < num_moves - 1:
                    time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ⚠ Mouse move error: {e}")
    
    @staticmethod
    def _interaction_seek_video(driver, profile_id, log_prefix):
        """Click on video timeline to seek to different position"""
        try:
            print(f"{log_prefix} [{profile_id}] ⏩ Seeking video position...")
            
            # Get current video time and duration
            current_time = driver.execute_script("return document.querySelector('video.html5-main-video') ? document.querySelector('video.html5-main-video').currentTime : null")
            duration = driver.execute_script("return document.querySelector('video.html5-main-video') ? document.querySelector('video.html5-main-video').duration : null")
            
            if current_time is not None and duration and duration > 30:
                # Seek to random position
                if random.random() < 0.7:
                    # Seek forward (70% chance)
                    new_time = current_time + random.uniform(5, 30)
                else:
                    # Seek backward (30% chance)
                    new_time = max(0, current_time - random.uniform(5, 15))
                
                new_time = min(new_time, duration - 5)
                
                driver.execute_script(f"document.querySelector('video.html5-main-video').currentTime = {new_time}")
                print(f"{log_prefix} [{profile_id}] ✓ Seeked from {current_time:.1f}s to {new_time:.1f}s")
                time.sleep(random.uniform(1, 2))
            else:
                print(f"{log_prefix} [{profile_id}] ℹ Video player not found or video too short to seek")
            
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ⚠ Seek error: {e}")
    
    @staticmethod
    def _interaction_pause_resume(driver, profile_id, log_prefix):
        """Pause video for a few seconds then resume"""
        try:
            print(f"{log_prefix} [{profile_id}] ⏸️ Pausing video...")
            
            viewport_width = driver.execute_script("return window.innerWidth")
            viewport_height = driver.execute_script("return window.innerHeight")
            viewport_offset_x = driver.execute_script("return window.screenX + (window.outerWidth - window.innerWidth);")
            viewport_offset_y = driver.execute_script("return window.screenY + (window.outerHeight - window.innerHeight);")
            
            center_x = int(viewport_offset_x + viewport_width / 2)
            center_y = int(viewport_offset_y + viewport_height / 2)
            
            # Click to pause
            MouseMoveAction.move_and_click_static(center_x, center_y, click_type="single_click", fast=False)
            print(f"{log_prefix} [{profile_id}] ✓ Video paused")
            
            # Wait 2-5 seconds
            pause_duration = random.uniform(2, 5)
            print(f"{log_prefix} [{profile_id}] Waiting {pause_duration:.1f}s...")
            time.sleep(pause_duration)
            
            # Click to resume
            MouseMoveAction.move_and_click_static(center_x, center_y, click_type="single_click", fast=False)
            print(f"{log_prefix} [{profile_id}] ▶️ Video resumed")
            
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ⚠ Pause/resume error: {e}")
    
    @staticmethod
    def _interaction_click_ad(driver, profile_id, log_prefix):
        """Click on ad (if present), open new tab, scroll, then close"""
        try:
            print(f"{log_prefix} [{profile_id}] 🎯 Looking for ads to click...")
            
            ad_selectors = [
                '.ytp-ad-overlay-image',
                '.ytp-ad-text-overlay',
                'div.ytp-ad-button',
                'a[href*="googleadservices"]',
                'div[class*="ad-container"] a'
            ]
            
            ad_clicked = False
            main_tab = driver.current_window_handle
            
            for selector in ad_selectors:
                try:
                    ad_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_ads = [ad for ad in ad_elements if ad.is_displayed()]
                    
                    if visible_ads:
                        target_ad = random.choice(visible_ads)
                        
                        location = target_ad.location
                        size = target_ad.size
                        viewport_offset_x = driver.execute_script("return window.screenX + (window.outerWidth - window.innerWidth);")
                        viewport_offset_y = driver.execute_script("return window.screenY + (window.outerHeight - window.innerHeight);")
                        
                        random_x = location['x'] + size['width'] * random.uniform(0.3, 0.7)
                        random_y = location['y'] + size['height'] * random.uniform(0.3, 0.7)
                        screen_x = int(viewport_offset_x + random_x)
                        screen_y = int(viewport_offset_y + random_y)
                        
                        MouseMoveAction.move_and_click_static(screen_x, screen_y, click_type="single_click", fast=False)
                        print(f"{log_prefix} [{profile_id}] ✓ Clicked ad")
                        ad_clicked = True
                        time.sleep(3)
                        break
                except:
                    continue
            
            if ad_clicked:
                if len(driver.window_handles) > 1:
                    new_tab = driver.window_handles[-1]
                    driver.switch_to.window(new_tab)
                    print(f"{log_prefix} [{profile_id}] ✓ Switched to ad tab")
                    
                    scroll_duration = random.uniform(10, 20)
                    print(f"{log_prefix} [{profile_id}] Scrolling ad page for {scroll_duration:.1f}s...")
                    
                    num_scrolls = random.randint(3, 6)
                    for i in range(num_scrolls):
                        scroll_amount = random.randint(200, 500)
                        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                        time.sleep(scroll_duration / num_scrolls)
                    
                    driver.close()
                    driver.switch_to.window(main_tab)
                    print(f"{log_prefix} [{profile_id}] ✓ Closed ad tab, back to YouTube")
                    
                    time.sleep(1)
                    is_paused = driver.execute_script("return document.querySelector('video.html5-main-video') ? document.querySelector('video.html5-main-video').paused : false")
                    if is_paused:
                        print(f"{log_prefix} [{profile_id}] Video paused, resuming...")
                        viewport_width = driver.execute_script("return window.innerWidth")
                        viewport_height = driver.execute_script("return window.innerHeight")
                        viewport_offset_x = driver.execute_script("return window.screenX + (window.outerWidth - window.innerWidth);")
                        viewport_offset_y = driver.execute_script("return window.screenY + (window.outerHeight - window.innerHeight);")
                        
                        center_x = int(viewport_offset_x + viewport_width / 2)
                        center_y = int(viewport_offset_y + viewport_height / 2)
                        
                        MouseMoveAction.move_and_click_static(center_x, center_y, click_type="single_click", fast=False)
                        print(f"{log_prefix} [{profile_id}] ✓ Video resumed")
            else:
                print(f"{log_prefix} [{profile_id}] ℹ No ads found to click")
                
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ⚠ Ad click error: {e}")
            try:
                driver.switch_to.window(driver.window_handles[0])
            except:
                pass
    
    @staticmethod
    def _interaction_scroll_page(driver, profile_id, log_prefix):
        """Scroll page up/down randomly multiple times"""
        try:
            print(f"{log_prefix} [{profile_id}] 📜 Scrolling page...")
            
            # Random number of scrolls (1-3)
            num_scrolls = random.randint(1, 3)
            
            for i in range(num_scrolls):
                scroll_amount = random.randint(200, 800)
                direction = random.choice([-1, 1])
                
                driver.execute_script(f"window.scrollBy(0, {scroll_amount * direction});")
                print(f"{log_prefix} [{profile_id}] ✓ Scrolled {'down' if direction > 0 else 'up'} {scroll_amount}px")
                
                if i < num_scrolls - 1:
                    time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ⚠ Scroll error: {e}")
    
    # ========== HELPER METHODS ==========
    
    @staticmethod
    def _navigate_to_youtube(driver, profile_id, debugger_address, log_prefix):
        """Navigate to YouTube homepage"""
        YouTubeNavigateAction(driver, profile_id, log_prefix, debugger_address).execute()
        time.sleep(random.uniform(2, 4))
    
    @staticmethod
    def _random_actions(driver, profile_id, debugger_address, log_prefix, num_actions=2):
        """Perform random scroll/mouse move actions"""
        print(f"{log_prefix} [{profile_id}] Performing {num_actions} random actions...")
        
        for i in range(num_actions):
            action_type = random.choice(['scroll', 'mouse_move'])
            
            if action_type == 'scroll':
                YouTubeScrollAction(driver, profile_id, log_prefix, debugger_address, direction="down").execute()
            else:
                YouTubeMouseMoveAction(driver, profile_id, log_prefix, debugger_address, click=False).execute()
            
            time.sleep(random.uniform(1, 2))
