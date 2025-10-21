# helpers/actions/youtube_click_video_action.py

from helpers.actions.base_youtube_action import BaseYouTubeAction
from selenium.webdriver.common.by import By
from controllers.actions.mouse_move_action import MouseMoveAction
import random
import time

class YouTubeClickVideoAction(BaseYouTubeAction):
    """Click random video and wait for it to start playing"""
    
    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE]", debugger_address=None, video_index_range=(1, 10), location="main"):
        super().__init__(driver, profile_id, log_prefix, debugger_address)
        self.video_index_range = video_index_range
        self.location = location  # 'main' hoặc 'side'

    
    def execute(self):
        """Execute video click and wait for video to start playing"""
        try:
            self.log("Looking for videos to click...", "INFO")
            
             # Select selectors based on location
            if self.location == 'side':
                self.log("Looking for sidebar videos to click...", "INFO")
                # Sidebar video selectors (when watching a video)
                selectors = [
                    '#related ytd-compact-video-renderer a',
                    '#secondary ytd-compact-video-renderer a',
                    'ytd-compact-video-renderer a#thumbnail',
                    '#related a.ytd-compact-video-renderer'
                ]
            else:
                self.log("Looking for main videos to click...", "INFO")
                # Main page video selectors
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
                            
                            # Use base class method for click position
                            screen_x, screen_y = self.get_random_click_position(target_video)
                            
                            # Click video
                            self.log(f"Clicking video at position ({screen_x}, {screen_y})", "INFO")
                            MouseMoveAction.move_and_click_static(screen_x, screen_y, click_type="single_click", fast=False)
                            
                            # Wait for video to start playing
                            if self._wait_for_video_playing():
                                self.log("Video started playing", "SUCCESS")
                                return True
                            else:
                                self.log("Video did not start playing (timeout)", "WARNING")
                                return False
                except:
                    continue
            
            self.log("No clickable videos found", "WARNING")
            return False
            
        except Exception as e:
            self.log(f"Video click error: {e}", "ERROR")
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
                    is_paused = self.driver.execute_script("return document.querySelector('video.html5-main-video').paused")
                    
                    if not is_paused:
                        # Check 3: Current time > 0 (video has started)
                        current_time = self.driver.execute_script("return document.querySelector('video.html5-main-video').currentTime")
                        
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
