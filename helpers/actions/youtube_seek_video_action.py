# helpers/actions/youtube_seek_video_action.py

from helpers.actions.base_youtube_action import BaseYouTubeAction
from selenium.webdriver.common.by import By
from controllers.actions.mouse_move_action import MouseMoveAction
import random
import time

class YouTubeSeekVideoAction(BaseYouTubeAction):
    """Seek video to random position using physical mouse click"""
    
    def execute(self):
        try:
            self.log("Seeking video position...", "INFO")
            """Execute video seek by clicking on timeline"""
            
            if not self._exit_fullscreen_if_needed():
                self.log("Failed to exit fullscreen", "ERROR")
                return False
            
            # Get current time and duration
            current_time = self.driver.execute_script(
                "return document.querySelector('video.html5-main-video') ? "
                "document.querySelector('video.html5-main-video').currentTime : null"
            )
            
            duration = self.driver.execute_script(
                "return document.querySelector('video.html5-main-video') ? "
                "document.querySelector('video.html5-main-video').duration : null"
            )
            
            if current_time is None or not duration or duration < 30:
                self.log("Video player not found or too short", "INFO")
                return False
            
            # ===== STEP 1: MOVE MOUSE TO VIDEO AREA TO SHOW TIMELINE =====
            self.log("Moving mouse to video area to show timeline...", "INFO")
            video_element = self._find_video_element()
            
            if not video_element:
                self.log("Video element not found for hover", "WARNING")
                return False
            
            # Get video viewport coordinates
            video_coords = self.get_element_viewport_coordinates(video_element)
            if not video_coords:
                self.log("Failed to get video coordinates", "WARNING")
                return False
            
            # Get viewport offset
            try:
                viewport_offset_x = self.driver.execute_script(
                    "return window.screenX + (window.outerWidth - window.innerWidth) / 2;"
                )
                viewport_offset_y = self.driver.execute_script(
                    "return window.screenY + (window.outerHeight - window.innerHeight);"
                )
                
                if viewport_offset_x is None or viewport_offset_y is None:
                    self.log("Failed to get viewport offset", "WARNING")
                    return False
            except Exception as e:
                self.log(f"Failed to get viewport offset: {e}", "WARNING")
                return False
            
            # Calculate random position in video area
            video_hover_x, video_hover_y = self.calculate_smart_click_position(
                video_coords,
                viewport_offset_x,
                viewport_offset_y
            )
            
            if not video_hover_x or not video_hover_y:
                self.log("Failed to calculate hover position", "WARNING")
                return False
            
            self.log(f"Hovering at video area ({video_hover_x:.1f}, {video_hover_y:.1f})", "INFO")
            
            # Just move, don't click - use MouseMoveAction with click_type=None
            MouseMoveAction.move_and_click_static(
                int(video_hover_x),
                int(video_hover_y),
                click_type=None,  # No click, just move
                fast=False
            )
            time.sleep(random.uniform(0.3, 0.5))  # Wait for timeline to appear
            
            self.log("Timeline should now be visible", "INFO")
            # ===== END HOVER =====
            
            # Find progress bar element (should be visible now)
            progress_bar = self._find_progress_bar()
            
            if not progress_bar:
                self.log("Progress bar not found", "ERROR")
                return False
            
            # ========== USE VIEWPORT COORDINATES (from BaseFlowAction) ==========
            viewport_coords = self.get_element_viewport_coordinates(progress_bar)
            if not viewport_coords:
                self.log("Failed to get progress bar viewport coordinates", "ERROR")
                return False
            
            # Calculate target position (30-70% of video)
            target_percent = random.uniform(0.3, 0.7)
            target_time = duration * target_percent
            
            # Skip if too close to current time
            if abs(target_time - current_time) < 5:
                self.log(f"Target time {target_time:.1f}s too close to current {current_time:.1f}s", "INFO")
                return True
            
            self.log(f"Seeking from {current_time:.1f}s to {target_time:.1f}s ({target_percent*100:.1f}%)", "INFO")
            
            # Get viewport offset for click calculation
            try:
                viewport_offset_x = self.driver.execute_script(
                    "return window.screenX + (window.outerWidth - window.innerWidth) / 2;"
                )
                viewport_offset_y = self.driver.execute_script(
                    "return window.screenY + (window.outerHeight - window.innerHeight);"
                )
            except Exception as e:
                self.log(f"Failed to get viewport offset: {e}", "ERROR")
                return False
            
            if viewport_offset_x is None or viewport_offset_y is None:
                self.log("Failed to get viewport offset", "ERROR")
                return False
            
            # Calculate physical click position
            click_x = viewport_offset_x + viewport_coords['x'] + (viewport_coords['width'] * target_percent)
            click_y = viewport_offset_y + viewport_coords['y'] + (viewport_coords['height'] / 2)
            
            # Add small random offset for natural behavior
            click_x += random.uniform(-2, 2)
            click_y += random.uniform(-2, 2)
            
            self.log(f"Clicking progress bar at screen position ({click_x:.1f}, {click_y:.1f})", "INFO")
            
            # Click using physical mouse
            MouseMoveAction.move_and_click_static(
                int(click_x), int(click_y),
                click_type="single_click",
                fast=False
            )
            
            time.sleep(random.uniform(0.5, 1))
            
            # Verify seek worked
            new_time = self.driver.execute_script(
                "return document.querySelector('video.html5-main-video') ? "
                "document.querySelector('video.html5-main-video').currentTime : null"
            )
            
            if new_time and abs(new_time - target_time) < 10:
                self.log(f"Successfully seeked to {new_time:.1f}s", "SUCCESS")
            else:
                self.log(f"Seek verification: now at {new_time:.1f}s", "INFO")
            
            return True
            
        except Exception as e:
            self.log(f"Seek error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    def _find_progress_bar(self):
        """Find YouTube progress bar element"""
        selectors = [
            '.ytp-progress-bar',
            'div.ytp-progress-bar-container',
            '.ytp-progress-bar-container .ytp-progress-bar'
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return element
            except:
                continue
        
        return None
