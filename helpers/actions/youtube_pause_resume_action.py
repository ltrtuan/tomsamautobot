# helpers/actions/youtube_pause_resume_action.py

from helpers.actions.base_youtube_action import BaseYouTubeAction
from selenium.webdriver.common.by import By
from controllers.actions.mouse_move_action import MouseMoveAction
import random
import time
import pyautogui

class YouTubePauseResumeAction(BaseYouTubeAction):
    """Pause video then resume after delay"""

    def execute(self):
        """Execute pause/resume"""
        try:
            self.log("Pausing video...", "INFO")
            
            # Exit fullscreen if needed
            if not self._exit_fullscreen_if_needed():
                self.log("Failed to exit fullscreen", "ERROR")
                return False
            
            # Find video player element
            video_element = self._find_video_element()
            if not video_element:
                self.log("Video element not found", "ERROR")
                return False
            
            # Check if video is in viewport
            if not self.is_element_in_viewport(video_element):
                self.log("Video not in viewport, scrolling to video...", "INFO")
                # Scroll to video
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                    video_element
                )
                time.sleep(random.uniform(1, 2))
            
            # ========== SỬ DỤNG VIEWPORT COORDINATES ==========
            viewport_coords = self.get_element_viewport_coordinates(video_element)
            if not viewport_coords:
                self.log("Failed to get video viewport coordinates", "ERROR")
                return False
            
            # Lấy vị trí browser window trên màn hình
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
                self.log("Failed to calculate click position", "ERROR")
                return False
            
            # Validate coords
            screen_width, screen_height = pyautogui.size()
            if not (0 <= click_x <= screen_width and 0 <= click_y <= screen_height):
                self.log(f"Invalid coords ({click_x:.1f}, {click_y:.1f})", "WARNING")
                return False
            
            self.log(f"Clicking video at coords: ({click_x:.1f}, {click_y:.1f})", "INFO")
            
            # Click to pause
            MouseMoveAction.move_and_click_static(
                int(click_x), int(click_y),
                click_type="single_click",
                fast=False
            )
            
            self.log("Video paused", "SUCCESS")
            
            # Wait 1-3 seconds
            pause_duration = random.uniform(1, 3)
            self.log(f"Waiting {pause_duration:.1f}s...", "INFO")
            time.sleep(pause_duration)
            
            # Click to resume (same position)
            MouseMoveAction.move_and_click_static(
                int(click_x), int(click_y),
                click_type="single_click",
                fast=False
            )
            
            self.log("Video resumed", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Pause/resume error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
