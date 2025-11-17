# helpers/actions_headless/youtube_pause_resume_headless.py

"""
Pause and resume video action for headless mode

SIMPLIFIED VERSION:
- JavaScript video.pause() and video.play() (NO pyautogui click)
- No calculate click position
- No mouse movement

Fast, accurate, and efficient for headless background execution
"""

from helpers.actions_headless.base_youtube_action_headless import BaseYouTubeActionHeadless
from selenium.webdriver.common.by import By
import random
import time


class YouTubePauseResumeHeadless(BaseYouTubeActionHeadless):
    """
    Pause video then resume after delay using JavaScript (headless mode)
    
    Features:
    - Pause video using JavaScript
    - Random wait time (2-5 seconds)
    - Resume video using JavaScript
    - Verify pause/resume successful
    
    Differences from GUI:
    - JavaScript video.pause()/play() (no video click)
    - No calculate click position
    - Much simpler and more reliable
    """
    
    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE HEADLESS]", 
                 debugger_address=None, pause_time_range=(2, 5)):
        """
        Initialize pause/resume action
        
        Args:
            driver: Selenium WebDriver
            profile_id: GoLogin profile ID
            log_prefix: Log prefix
            debugger_address: Chrome debugger address
            pause_time_range: Tuple (min, max) seconds to pause
                             Default: (2, 5) - pause 2-5 seconds randomly
        """
        super().__init__(driver, profile_id, log_prefix, debugger_address)
        self.pause_time_range = pause_time_range
    
    def execute(self):
        """Execute pause/resume using JavaScript"""
        try:
            self.log("Pausing video...", "INFO")
            
            # ========== STEP 1: EXIT FULLSCREEN ==========
            if not self._exit_fullscreen_if_needed():
                self.log("Failed to exit fullscreen", "ERROR")
                return False
            
            # ========== STEP 2: FIND VIDEO ELEMENT ==========
            video_element = self._find_video_element()
            if not video_element:
                self.log("Video element not found", "ERROR")
                return False
            
            # ========== STEP 3: CHECK IF VIDEO IS PLAYING ==========
            is_playing = self._is_video_playing()
            
            if not is_playing:
                self.log("Video is not playing, cannot pause", "WARNING")
                return True  # Not an error - just skip
            
            # ========== STEP 4: PAUSE VIDEO (JAVASCRIPT) ==========
            success = self._pause_video_js()
            
            if not success:
                self.log("Failed to pause video", "ERROR")
                return False
            
            # Verify paused
            time.sleep(0.5)
            if not self._is_video_paused():
                self.log("⚠ Video not paused after pause command", "WARNING")
            else:
                self.log("✓ Video paused successfully", "SUCCESS")
            
            # ========== STEP 5: WAIT (RANDOM PAUSE TIME) ==========
            pause_time = random.uniform(self.pause_time_range[0], self.pause_time_range[1])
            self.log(f"Waiting {pause_time:.1f}s before resuming (anti-detection)...", "INFO")
            time.sleep(pause_time)
            
            # ========== STEP 6: RESUME VIDEO (JAVASCRIPT) ==========
            self.log("Resuming video...", "INFO")
            
            success = self._play_video_js()
            
            if not success:
                self.log("Failed to resume video", "ERROR")
                return False
            
            # Verify playing
            time.sleep(0.5)
            if not self._is_video_playing():
                self.log("⚠ Video not playing after resume command", "WARNING")
            else:
                self.log("✓ Video resumed successfully", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.log(f"Execute error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    # ========== HELPER METHODS ==========
    
    def _is_video_playing(self):
        """
        Check if video is currently playing
        
        Returns:
            bool: True if playing
        """
        try:
            is_playing = self.driver.execute_script("""
                var video = document.querySelector('video.html5-main-video');
                if (video) {
                    return !video.paused && !video.ended && video.readyState > 2;
                }
                return false;
            """)
            
            return is_playing
            
        except Exception as e:
            self.log(f"Check playing error: {e}", "ERROR")
            return False
    
    def _is_video_paused(self):
        """
        Check if video is currently paused
        
        Returns:
            bool: True if paused
        """
        try:
            is_paused = self.driver.execute_script("""
                var video = document.querySelector('video.html5-main-video');
                if (video) {
                    return video.paused;
                }
                return false;
            """)
            
            return is_paused
            
        except Exception as e:
            self.log(f"Check paused error: {e}", "ERROR")
            return False
    
    def _pause_video_js(self):
        """
        Pause video using JavaScript
        
        Returns:
            bool: True if success
        """
        try:
            # ===== JAVASCRIPT VIDEO PAUSE (NO PYAUTOGUI CLICK) =====
            self.driver.execute_script("""
                var video = document.querySelector('video.html5-main-video');
                if (video) {
                    video.pause();
                }
            """)
            
            # Small delay for pause to register
            time.sleep(random.uniform(0.3, 0.7))
            
            return True
            
        except Exception as e:
            self.log(f"JavaScript pause error: {e}", "ERROR")
            return False
    
    def _play_video_js(self):
        """
        Play/resume video using JavaScript
        
        Returns:
            bool: True if success
        """
        try:
            # ===== JAVASCRIPT VIDEO PLAY (NO PYAUTOGUI CLICK) =====
            self.driver.execute_script("""
                var video = document.querySelector('video.html5-main-video');
                if (video) {
                    video.play();
                }
            """)
            
            # Small delay for play to register
            time.sleep(random.uniform(0.3, 0.7))
            
            return True
            
        except Exception as e:
            self.log(f"JavaScript play error: {e}", "ERROR")
            return False
