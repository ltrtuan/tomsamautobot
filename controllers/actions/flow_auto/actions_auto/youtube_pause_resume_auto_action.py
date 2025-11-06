# controllers/actions/flow_auto/actions_auto/youtube_pause_resume_auto_action.py

import time
import random
import pyautogui
from controllers.actions.flow_auto.actions_auto.base_flow_auto_action import BaseFlowAutoAction

class YouTubePauseResumeAutoAction(BaseFlowAutoAction):
    """Pause and resume video using spacebar"""
    
    def __init__(self, profile_id, log_prefix="[YOUTUBE AUTO]"):
        """
        Initialize pause/resume action
        
        Args:
            profile_id: GoLogin profile ID
            log_prefix: Log prefix
        """
        super().__init__(profile_id, log_prefix)
    
    def _execute_internal(self):
        """Execute pause/resume action"""
        try:
            # Pause video
            self.log("Pausing video (Spacebar)")
            pyautogui.press('space')
            
            # Wait random time (1-3s)
            pause_duration = random.uniform(1, 5)
            self.log(f"Video paused for {pause_duration:.1f}s")
            time.sleep(pause_duration)
            
            # Resume video
            self.log("Resuming video (Spacebar)")
            pyautogui.press('space')
            
            # Wait after resume
            time.sleep(random.uniform(0.5, 1.0))
            
            self.log("✓ Pause/Resume completed")
            return True
            
        except Exception as e:
            self.log(f"✗ Pause/Resume error: {e}", "ERROR")
            return False
