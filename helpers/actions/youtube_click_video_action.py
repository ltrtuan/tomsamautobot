# helpers/actions/youtube_click_video_action.py

from helpers.actions.base_youtube_action import BaseYouTubeAction
from selenium.webdriver.common.by import By
from controllers.actions.mouse_move_action import MouseMoveAction
import random
import time
import pyautogui


class YouTubeClickVideoAction(BaseYouTubeAction):
    """Click random video and wait for it to start playing"""

    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE]", debugger_address=None, video_index_range=(1, 10)):
        super().__init__(driver, profile_id, log_prefix, debugger_address)
        self.video_index_range = video_index_range

    def execute(self):
        """Execute video click and wait for video to start playing"""
        try:
            self.log("Looking for videos to click...", "INFO")

            # Find video thumbnails/titles
            selectors = [
                'a#video-title',
                'ytd-thumbnail a',
                'a.ytd-video-renderer'
            ]

            for selector in selectors:
                try:
                    video_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_videos = [v for v in video_elements if v.is_displayed()]
                    
                    if visible_videos:
                        # Select random video from range
                        max_index = min(len(visible_videos), self.video_index_range[1])
                        min_index = self.video_index_range[0]
                        
                        if max_index >= min_index:
                            available_videos = visible_videos[min_index-1:max_index]
                            target_video = random.choice(available_videos)

                            # ========== FIX: SỬ DỤNG VIEWPORT COORDINATES ==========
                            viewport_coords = self.get_element_viewport_coordinates(target_video)
                            
                            if not viewport_coords:
                                self.log("Failed to get viewport coords, using Selenium fallback", "WARNING")
                                target_video.click()
                                self.random_sleep(0.5, 1.0)
                            else:                               
                                # Lấy vị trí browser window trên màn hình
                                viewport_offset_x = self.driver.execute_script(
                                    "return window.screenX + (window.outerWidth - window.innerWidth) / 2;"
                                )
                                viewport_offset_y = self.driver.execute_script(
                                    "return window.screenY + (window.outerHeight - window.innerHeight);"
                                )

                                # Tính tọa độ click = random trong vùng thumbnail (tránh viền 10px mỗi bên)
                                safe_margin = 10  # Tránh viền 10px

                                # Random X: từ left + 10px đến right - 10px
                                random_offset_x = random.uniform(safe_margin, viewport_coords['width'] - safe_margin)
                                # Random Y: từ top + 10px đến bottom - 10px
                                random_offset_y = random.uniform(safe_margin, viewport_coords['height'] - safe_margin)

                                click_x = viewport_offset_x + viewport_coords['x'] + random_offset_x
                                click_y = viewport_offset_y + viewport_coords['y'] + random_offset_y

                                
                                # Validate coordinates
                                screen_width, screen_height = pyautogui.size()
                                coords_valid = (
                                    click_x >= 0 and
                                    click_y >= 0 and
                                    click_x <= screen_width and
                                    click_y <= screen_height
                                )
                                
                                if coords_valid:
                                    self.log(f"Clicking video at viewport coords: ({click_x:.1f}, {click_y:.1f})", "INFO")
                                    try:
                                        MouseMoveAction.move_and_click_static(
                                            click_x, click_y, 
                                            click_type="single_click", 
                                            fast=False
                                        )
                                        self.random_sleep(0.5, 1.0)
                                    except Exception as pyautogui_err:
                                        self.log(f"PyAutoGUI click failed: {pyautogui_err}, using Selenium fallback", "WARNING")
                                        target_video.click()
                                        self.random_sleep(0.5, 1.0)
                                else:
                                    self.log(f"Invalid coords ({click_x:.1f}, {click_y:.1f}), using Selenium click", "WARNING")
                                    target_video.click()
                                    self.random_sleep(0.5, 1.0)
                            # ========================================================

                            # Wait for video to start playing
                            if self._wait_for_video_playing():
                                self.log("Video started playing", "SUCCESS")
                                return True
                            else:
                                self.log("Video did not start playing (timeout)", "WARNING")
                                return False

                except Exception as selector_err:
                    self.log(f"Selector '{selector}' failed: {selector_err}", "WARNING")
                    continue

            self.log("No clickable videos found", "WARNING")
            return False

        except Exception as e:
            self.log(f"Video click error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False

    def _wait_for_video_playing(self, timeout=15):
        """
        Wait for YouTube video to start playing
        
        Args:
            timeout: Maximum wait time in seconds
        
        Returns:
            bool: True if video is playing, False if timeout
        """
        self.log(f"Waiting for video to start playing (timeout: {timeout}s)...", "INFO")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check 1: Video player exists
                video_player = self.driver.find_element(By.CSS_SELECTOR, 'video.html5-main-video')
                if video_player:
                    # Check 2: Video is not paused (playing)
                    is_paused = self.driver.execute_script(
                        "return document.querySelector('video.html5-main-video').paused"
                    )
                    if not is_paused:
                        # Check 3: Current time > 0 (video has started)
                        current_time = self.driver.execute_script(
                            "return document.querySelector('video.html5-main-video').currentTime"
                        )
                        if current_time > 0:
                            elapsed = time.time() - start_time
                            self.log(f"Video playing confirmed (waited {elapsed:.1f}s)", "SUCCESS")
                            return True
                
                # Wait before checking again
                time.sleep(0.5)
                
            except Exception:
                # Video player might not be loaded yet
                time.sleep(0.5)
                continue
        
        # Timeout reached
        self.log(f"Video did not start playing after {timeout}s", "WARNING")
        return False
