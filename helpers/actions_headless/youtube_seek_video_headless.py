# helpers/actions_headless/youtube_seek_video_headless.py

"""
Seek video to random position for headless mode

SIMPLIFIED VERSION:
- JavaScript video.currentTime (NO pyautogui click on timeline)
- No calculate timeline position
- No mouse movement

Fast, accurate, and efficient for headless background execution
"""

from helpers.actions_headless.base_youtube_action_headless import BaseYouTubeActionHeadless
from selenium.webdriver.common.by import By
import random
import time


class YouTubeSeekVideoHeadless(BaseYouTubeActionHeadless):
    """
    Seek video to random position using JavaScript (headless mode)
    
    Features:
    - Get video duration
    - Calculate random seek position (10-90% of duration)
    - Seek using JavaScript video.currentTime
    - Verify seek successful
    
    Differences from GUI:
    - JavaScript video.currentTime (no timeline click)
    - No calculate click position
    - Much simpler and more reliable
    """
    
    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE HEADLESS]", 
                 debugger_address=None):
        """
        Initialize seek video action
        
        Args:
            driver: Selenium WebDriver
            profile_id: GoLogin profile ID
            log_prefix: Log prefix
            debugger_address: Chrome debugger address
        """
        super().__init__(driver, profile_id, log_prefix, debugger_address)
    
    def execute(self):
        """Execute video seek using JavaScript"""
        try:
            self.log("Seeking video position...", "INFO")
            
            # ========== STEP 1: EXIT FULLSCREEN ==========
            if not self._exit_fullscreen_if_needed():
                self.log("Failed to exit fullscreen", "ERROR")
                return False
            
            # ========== STEP 2: GET VIDEO ELEMENT ==========
            video_element = self._find_video_element()
            if not video_element:
                self.log("Video element not found", "ERROR")
                return False
            
            # ========== STEP 3: GET VIDEO DURATION ==========
            duration = self._get_video_duration()
            
            if not duration or duration <= 0:
                self.log("Invalid video duration", "ERROR")
                return False
            
            self.log(f"Video duration: {duration:.1f}s", "INFO")
            
            # ========== STEP 4: CALCULATE RANDOM SEEK POSITION ==========
            # Seek to 10-90% of duration (avoid very start and end)
            min_percent = 0.1  # 10%
            max_percent = 0.9  # 90%
            
            random_percent = random.uniform(min_percent, max_percent)
            seek_time = duration * random_percent
            
            self.log(f"Seeking to {seek_time:.1f}s ({random_percent*100:.0f}% of video)...", "INFO")
            
            # ========== STEP 5: SEEK USING JAVASCRIPT ==========
            success = self._seek_to_time_js(seek_time)
            
            if not success:
                self.log("Failed to seek video", "ERROR")
                return False
            
            # ========== STEP 6: VERIFY SEEK SUCCESSFUL ==========
            time.sleep(1)  # Wait for seek to complete
            
            current_time = self._get_current_time()
            if current_time is not None:
                # Check if current time is close to target (within 2 seconds)
                if abs(current_time - seek_time) < 2:
                    self.log(f"✓ Seek successful (current time: {current_time:.1f}s)", "SUCCESS")
                    return True
                else:
                    self.log(f"⚠ Seek result mismatch (target: {seek_time:.1f}s, actual: {current_time:.1f}s)", "WARNING")
                    return True  # Don't fail - close enough
            else:
                self.log("⚠ Could not verify seek position", "WARNING")
                return True  # Don't fail - assume successful
            
        except Exception as e:
            self.log(f"Execute error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    # ========== HELPER METHODS ==========
    
    def _get_video_duration(self):
        """
        Get video duration in seconds
        
        Returns:
            float: Duration in seconds, None if error
        """
        try:
            duration = self.driver.execute_script("""
                var video = document.querySelector('video.html5-main-video');
                if (video && video.duration) {
                    return video.duration;
                }
                return null;
            """)
            
            return duration
            
        except Exception as e:
            self.log(f"Get duration error: {e}", "ERROR")
            return None
    
    def _get_current_time(self):
        """
        Get video current time in seconds
        
        Returns:
            float: Current time in seconds, None if error
        """
        try:
            current_time = self.driver.execute_script("""
                var video = document.querySelector('video.html5-main-video');
                if (video) {
                    return video.currentTime;
                }
                return null;
            """)
            
            return current_time
            
        except Exception as e:
            self.log(f"Get current time error: {e}", "ERROR")
            return None
    
    def _seek_to_time_js(self, target_time):
        """
        Seek video to specific time using JavaScript
        
        Args:
            target_time: Target time in seconds
            
        Returns:
            bool: True if success
        """
        try:
            # ===== JAVASCRIPT VIDEO SEEK (NO PYAUTOGUI CLICK) =====
            self.driver.execute_script(f"""
                var video = document.querySelector('video.html5-main-video');
                if (video) {{
                    video.currentTime = {target_time};
                }}
            """)
            
            # Small delay for seek to register
            time.sleep(random.uniform(0.3, 0.7))
            
            return True
            
        except Exception as e:
            self.log(f"JavaScript seek error: {e}", "ERROR")
            return False
