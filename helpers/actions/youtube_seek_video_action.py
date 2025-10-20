# helpers/actions/youtube_seek_video_action.py

from helpers.actions.base_youtube_action import BaseYouTubeAction
from selenium.webdriver.common.by import By
from controllers.actions.mouse_move_action import MouseMoveAction
import random
import time
import pyautogui

class YouTubeSeekVideoAction(BaseYouTubeAction):
    """Seek video to random position using physical mouse click"""

    def execute(self):
        """Execute video seek by clicking on timeline"""
        try:
            self.log("Seeking video position...", "INFO")
            
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
            
            # Find progress bar element
            progress_bar = self._find_progress_bar()
            if not progress_bar:
                self.log("Progress bar not found", "ERROR")
                return False
            
            # ========== SỬ DỤNG VIEWPORT COORDINATES (từ BaseFlowAction) ==========
            viewport_coords = self.get_element_viewport_coordinates(progress_bar)
            if not viewport_coords:
                self.log("Failed to get progress bar viewport coordinates", "ERROR")
                return False
            
            # Lấy vị trí browser window trên màn hình
            viewport_offset_x = self.driver.execute_script(
                "return window.screenX + (window.outerWidth - window.innerWidth) / 2;"
            )
            viewport_offset_y = self.driver.execute_script(
                "return window.screenY + (window.outerHeight - window.innerHeight);"
            )
            
            # Tính vị trí seek mới (70% forward, 30% backward)
            if random.random() < 0.7:
                # Seek forward
                target_time = current_time + random.uniform(5, 30)
            else:
                # Seek backward
                target_time = max(0, current_time - random.uniform(5, 15))
            
            target_time = min(target_time, duration - 5)
            
            # Tính phần trăm vị trí trên timeline
            seek_percentage = target_time / duration
            
            # Tính tọa độ click trên progress bar
            # click_x = viewport_offset + progress_bar_left + (progress_bar_width * seek_percentage)
            progress_click_offset_x = viewport_coords['width'] * seek_percentage
            click_x = viewport_offset_x + viewport_coords['x'] + progress_click_offset_x
            click_y = viewport_offset_y + viewport_coords['y'] + viewport_coords['height'] / 2 + random.uniform(-2, 2)
            
            # Validate coordinates
            screen_width, screen_height = pyautogui.size()
            coords_valid = (
                click_x >= 0 and
                click_y >= 0 and
                click_x <= screen_width and
                click_y <= screen_height
            )
            
            if not coords_valid:
                self.log(f"Invalid coords ({click_x:.1f}, {click_y:.1f}), cannot seek", "WARNING")
                return False
            
            self.log(f"Seeking from {current_time:.1f}s to {target_time:.1f}s ({seek_percentage*100:.1f}%)", "INFO")
            self.log(f"Clicking timeline at coords: ({click_x:.1f}, {click_y:.1f})", "INFO")
            
            # Click progress bar using MouseMoveAction
            try:
                MouseMoveAction.move_and_click_static(
                    click_x, click_y,
                    click_type="single_click",
                    fast=False
                )
                self.log("Timeline clicked successfully", "SUCCESS")
                self.random_sleep(1, 2)
                return True
                
            except Exception as click_err:
                self.log(f"Click failed: {click_err}", "ERROR")
                return False
            
        except Exception as e:
            self.log(f"Seek error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    def _find_progress_bar(self):
        """Find YouTube progress bar element"""
        selectors = [
            '.ytp-progress-bar-container',
            '.ytp-progress-bar',
            'div.ytp-progress-bar-container',
            '.html5-progress-bar'
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return element
            except:
                continue
        
        return None
