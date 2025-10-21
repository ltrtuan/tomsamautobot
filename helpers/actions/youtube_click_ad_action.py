# helpers/actions/youtube_click_ad_action.py

from helpers.actions.base_youtube_action import BaseYouTubeAction
from selenium.webdriver.common.by import By
from controllers.actions.mouse_move_action import MouseMoveAction

# Import các action để reuse
from helpers.actions.youtube_mouse_move_action import YouTubeMouseMoveAction
from helpers.actions.youtube_scroll_action import YouTubeScrollAction

import random
import time
import pyautogui
from selenium.common.exceptions import TimeoutException, WebDriverException


class YouTubeClickAdAction(BaseYouTubeAction):
    """Click on YouTube ad, interact with ad page, then close and return to video"""
    
    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE]", debugger_address=None):
        super().__init__(driver, profile_id, log_prefix, debugger_address)
    
    def execute(self):
        """Execute ad click with full interaction flow"""
        try:
            self.log("Looking for ads to click...", "INFO")
            if not self._exit_fullscreen_if_needed():
                self.log("Failed to exit fullscreen", "ERROR")
                return False
            # Store main window handle
            main_tab = self.driver.current_window_handle
            
            # Try to find and click ads
            ad_location = self._find_and_click_ad()
            
            if not ad_location:
                self.log("No clickable ads found", "INFO")
                return False
            
            self.log(f"Ad clicked at location: {ad_location}", "SUCCESS")
            
            # Wait for new tab to open
            time.sleep(random.uniform(2, 4))
            
            # Check if new tab opened
            all_tabs = self.driver.window_handles
            if len(all_tabs) > 1:
                # Switch to ad tab (last opened tab)
                ad_tab = [tab for tab in all_tabs if tab != main_tab][0]
                self.driver.switch_to.window(ad_tab)
                self.log("Switched to ad tab", "INFO")
                
                # Interact with ad page
                self._interact_with_ad_page()
                
                # Close ad tab
                try:
                    self.driver.close()
                    self.log("Ad tab closed", "SUCCESS")
                except (TimeoutException, WebDriverException) as e:
                    self.log(f"Error closing ad tab (timeout?), forcing switch to main tab: {e}", "WARNING")
                except Exception as e:
                    self.log(f"Error closing ad tab: {e}", "WARNING")

                # Switch back to main YouTube tab
                try:
                    self.driver.switch_to.window(main_tab)
                    self.log("Switched back to YouTube tab", "INFO")
                except Exception as e:
                    self.log(f"Error switching back to main tab: {e}", "ERROR")
                    return False
                
                # ========== ALWAYS RESUME VIDEO AFTER AD CLICK ==========
                # Click ad (any location) will pause video, so always resume
                time.sleep(random.uniform(1, 2))
                self._resume_video_if_paused()
                
                return True
            else:
                self.log("Ad didn't open new tab", "INFO")
                return False
                
        except Exception as e:
            self.log(f"Ad click error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            
            # Try to return to main tab if something goes wrong
            try:
                self.driver.switch_to.window(main_tab)
            except:
                pass
            
            return False
    
    def _find_and_click_ad(self):
        """
        Find and click ad with random position
        Returns: 'video' if clicked video ad, 'sidebar' if clicked sidebar ad, None if no ad found
        """
        # Try video ads first (overlay ads on video player)
        video_ad_selectors = [
            '.ytp-ad-overlay-image',
            '.ytp-ad-text-overlay', 
            'div.ytp-ad-button',
            '.video-ads.ytp-ad-module a'
        ]
        
        for selector in video_ad_selectors:
            try:
                ad_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                visible_ads = [ad for ad in ad_elements if ad.is_displayed()]
                
                if visible_ads:
                    target_ad = random.choice(visible_ads)
                    
                    # Get viewport coordinates
                    viewport_coords = self.get_element_viewport_coordinates(target_ad)
                    if not viewport_coords:
                        continue
                
                    # Get viewport offset
                    viewport_offset_x = self.driver.execute_script(
                        "return window.screenX + (window.outerWidth - window.innerWidth) / 2;"
                    )
                    viewport_offset_y = self.driver.execute_script(
                        "return window.screenY + (window.outerHeight - window.innerHeight);"
                    )
                
                    # Calculate smart click position (method from BaseFlowAction)
                    click_x, click_y = self.calculate_smart_click_position(
                        viewport_coords,
                        viewport_offset_x,
                        viewport_offset_y
                    )
                
                    if click_x is None or click_y is None:
                        continue
                
                    # Validate coordinates
                    if not self._validate_coordinates(click_x, click_y):
                        continue

                    
                    self.log(f"Clicking video ad at ({click_x:.1f}, {click_y:.1f})", "INFO")
                    
                    # Click ad
                    MouseMoveAction.move_and_click_static(
                        int(click_x), int(click_y),
                        click_type="single_click",
                        fast=False
                    )
                    
                    return "video"
                    
            except Exception as e:
                self.log(f"Error with video ad selector {selector}: {e}", "DEBUG")
                continue
        
        # Try sidebar ads (companion ads)
        sidebar_ad_selectors = [
            '#player-ads a',
            '.ytp-ad-player-overlay-instream-info a',
            'a[href*="googleadservices"]',
            'div[class*="ad-container"] a'
        ]
        
        for selector in sidebar_ad_selectors:
            try:
                ad_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                visible_ads = [ad for ad in ad_elements if ad.is_displayed()]
                
                if visible_ads:
                    target_ad = random.choice(visible_ads)
                    
                    # Get viewport coordinates
                    viewport_coords = self.get_element_viewport_coordinates(target_ad)
                    if not viewport_coords:
                        continue
                
                    # Get viewport offset
                    viewport_offset_x = self.driver.execute_script(
                        "return window.screenX + (window.outerWidth - window.innerWidth) / 2;"
                    )
                    viewport_offset_y = self.driver.execute_script(
                        "return window.screenY + (window.outerHeight - window.innerHeight);"
                    )
                
                    # Calculate smart click position (method from BaseFlowAction)
                    click_x, click_y = self.calculate_smart_click_position(
                        viewport_coords,
                        viewport_offset_x,
                        viewport_offset_y
                    )
                
                    if click_x is None or click_y is None:
                        continue
                
                    # Validate coordinates
                    if not self._validate_coordinates(click_x, click_y):
                        continue

                    
                    self.log(f"Clicking sidebar ad at ({click_x:.1f}, {click_y:.1f})", "INFO")
                    
                    # Click ad
                    MouseMoveAction.move_and_click_static(
                        int(click_x), int(click_y),
                        click_type="single_click",
                        fast=False
                    )
                    
                    return "sidebar"
                    
            except Exception as e:
                self.log(f"Error with sidebar ad selector {selector}: {e}", "DEBUG")
                continue
        
        return None    
    
    def _validate_coordinates(self, click_x, click_y):
        """Validate click coordinates are within screen bounds"""
        screen_width, screen_height = pyautogui.size()
        return (0 <= click_x <= screen_width and 0 <= click_y <= screen_height)
    
    def _interact_with_ad_page(self):
        """
        Interact with ad page: random mouse moves and scrolls
        Reuse logic from YouTubeMouseMoveAction and YouTubeScrollAction
        """
        try:
            
            # ===== CODE MỚI: SET TIMEOUT 30 GIÂY =====
            original_page_load_timeout = self.driver.timeouts.page_load
            original_script_timeout = self.driver.timeouts.script
        
            self.driver.set_page_load_timeout(30)
            self.driver.set_script_timeout(30)
            self.log("Set timeout 30s for ad page interaction", "INFO")
            # ===== KẾT THÚC CODE MỚI =====
        
            self.log("Interacting with ad page...", "INFO")
        
            # Random number of mouse moves (1-3)
            mouse_move_count = random.randint(1, 3)
            self.log(f"Performing {mouse_move_count} mouse moves", "INFO")
        
            for i in range(mouse_move_count):
                try:
                    mouse_action = YouTubeMouseMoveAction(
                        driver=self.driver,
                        profile_id=self.profile_id,
                        debugger_address=self.debugger_address,
                        click=False  # Just move, no click
                    )
                    mouse_action.execute()
                    time.sleep(random.uniform(0.5, 1.5))
                except (TimeoutException, WebDriverException) as e:
                    if "Timed out receiving message from renderer" in str(e):
                        self.log(f"Renderer timeout during mouse move {i+1}, aborting ad interaction", "WARNING")
                        # Restore original timeouts before returning
                        try:
                            self.driver.set_page_load_timeout(original_page_load_timeout)
                            self.driver.set_script_timeout(original_script_timeout)
                        except:
                            pass
                        return  # Exit and let caller close the tab
                    raise
        
            # Random number of scrolls (1-3)
            scroll_count = random.randint(1, 3)
            self.log(f"Performing {scroll_count} scrolls", "INFO")
        
            for i in range(scroll_count):
                try:
                    scroll_action = YouTubeScrollAction(
                        driver=self.driver,
                        profile_id=self.profile_id,
                        debugger_address=self.debugger_address,
                        direction="random",  # Random up/down
                        times=None  # Random times per scroll action
                    )
                    scroll_action.execute()
                    time.sleep(random.uniform(0.8, 2))
                except (TimeoutException, WebDriverException) as e:
                    if "Timed out receiving message from renderer" in str(e):
                        self.log(f"Renderer timeout during scroll {i+1}, aborting ad interaction", "WARNING")
                        # Restore original timeouts before returning
                        try:
                            self.driver.set_page_load_timeout(original_page_load_timeout)
                            self.driver.set_script_timeout(original_script_timeout)
                        except:
                            pass
                        return  # Exit and let caller close the tab
                    raise
        
            # Wait a bit before closing (simulate reading)
            wait_time = random.uniform(2, 5)
            self.log(f"Waiting {wait_time:.1f}s before closing ad tab", "INFO")
            time.sleep(wait_time)
        
            # ===== CODE MỚI: RESTORE TIMEOUT =====
            try:
                self.driver.set_page_load_timeout(original_page_load_timeout)
                self.driver.set_script_timeout(original_script_timeout)
            except:
                pass
            # ===== KẾT THÚC CODE MỚI =====
        
        except Exception as e:
            self.log(f"Error interacting with ad page: {e}", "WARNING")

    
    def _resume_video_if_paused(self):
        """
        Check if video is paused and resume by clicking video player
        Always execute after returning from ad tab (any ad click pauses video)
        """
        try:
            self.log("Checking video state and resuming if needed...", "INFO")
            
            # Check if video is paused
            is_paused = self.driver.execute_script(
                "return document.querySelector('video.html5-main-video') ? "
                "document.querySelector('video.html5-main-video').paused : null"
            )
            
            if is_paused is None:
                self.log("Video element not found", "WARNING")
                return False
            
            if not is_paused:
                self.log("Video is already playing, no action needed", "INFO")
                return True
            
            self.log("Video is paused, clicking to resume...", "INFO")
            
            # Find video element
            video_element = self._find_video_element()
            if not video_element:
                self.log("Video element not found for resume", "ERROR")
                return False
            
            # Get viewport coordinates
            viewport_coords = self.get_element_viewport_coordinates(video_element)
            if not viewport_coords:
                self.log("Failed to get video viewport coordinates", "ERROR")
                return False
            
            # Get viewport offset
            viewport_offset_x = self.driver.execute_script(
                "return window.screenX + (window.outerWidth - window.innerWidth) / 2;"
            )
            viewport_offset_y = self.driver.execute_script(
                "return window.screenY + (window.outerHeight - window.innerHeight);"
            )
            
            # Calculate smart click position (method from BaseFlowAction)
            click_x, click_y = self.calculate_smart_click_position(
                viewport_coords,
                viewport_offset_x,
                viewport_offset_y
            )
            
            if click_x is None or click_y is None:
                self.log("Failed to calculate click position for resume", "ERROR")
                return False
            
            # Validate coordinates
            if not self._validate_coordinates(click_x, click_y):
                self.log("Invalid coordinates for resume click", "ERROR")
                return False

            
            self.log(f"Clicking video to resume at ({click_x:.1f}, {click_y:.1f})", "INFO")
            
            # Click to resume
            MouseMoveAction.move_and_click_static(
                int(click_x), int(click_y),
                click_type="single_click",
                fast=False
            )
            
            time.sleep(random.uniform(0.5, 1))
            
            # Verify video resumed
            is_playing = self.driver.execute_script(
                "return document.querySelector('video.html5-main-video') ? "
                "!document.querySelector('video.html5-main-video').paused : false"
            )
            
            if is_playing:
                self.log("Video resumed successfully", "SUCCESS")
                return True
            else:
                self.log("Video still paused after click", "WARNING")
                return False
            
        except Exception as e:
            self.log(f"Resume video error: {e}", "ERROR")
            return False
    
    def _find_video_element(self):
        """
        Find YouTube video player element
        Reuse from YouTubePauseResumeAction
        """
        selectors = [
            'video.html5-main-video',
            'video.video-stream',
            '#movie_player video',
            '.html5-video-player video'
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return element
            except:
                continue
        
        return None
