# controllers/actions/flow_auto/actions_auto/youtube_fullscreen_auto_action.py

import time
import random
import pyautogui
from controllers.actions.flow_auto.actions_auto.base_flow_auto_action import BaseFlowAutoAction

class YouTubeFullscreenAutoAction(BaseFlowAutoAction):
    """Toggle fullscreen mode using 'f' key"""
    
    def __init__(self, profile_id, log_prefix="[YOUTUBE AUTO]"):
        """
        Initialize fullscreen action
        
        Args:
            profile_id: GoLogin profile ID
            log_prefix: Log prefix
        """
        super().__init__(profile_id, log_prefix)
    
    def _execute_internal(self):
        """Execute fullscreen toggle action"""
        try:
            # Enter fullscreen
            self.log("Entering fullscreen mode (F key)")
            pyautogui.press('f')
            
            # Wait in fullscreen (2-5s)
            fullscreen_duration = random.uniform(1, 5)
            self.log(f"Staying in fullscreen for {fullscreen_duration:.1f}s")
            time.sleep(fullscreen_duration)
            
            # Exit fullscreen
            self.log("Exiting fullscreen mode (F key)")
            pyautogui.press('f')
            
            # Wait after exit
            time.sleep(random.uniform(0.5, 1.0))
            
            self.log("✓ Fullscreen toggle completed")
            return True
            
        except Exception as e:
            self.log(f"✗ Fullscreen error: {e}", "ERROR")
            return False
