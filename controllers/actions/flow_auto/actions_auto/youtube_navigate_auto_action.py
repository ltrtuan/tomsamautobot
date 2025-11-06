# controllers/actions/flow_auto/actions_auto/youtube_navigate_auto_action.py

import time
import random
import pyautogui
from helpers.gologin_profile_helper import GoLoginProfileHelper
from controllers.actions.flow_auto.actions_auto.base_flow_auto_action import BaseFlowAutoAction
import pyperclip

class YouTubeNavigateAutoAction(BaseFlowAutoAction):
    """Navigate to YouTube using Ctrl+L keyboard shortcut"""
    
    def __init__(self, profile_id, log_prefix="[YOUTUBE AUTO]"):
        self.profile_id = profile_id
        self.log_prefix = log_prefix
    
    def _execute_internal(self):
        """Execute navigate action"""
        try:
            self.log("Navigating to YouTube")
            
            # Bring to front
            GoLoginProfileHelper.bring_profile_to_front(self.profile_id, driver=None)
            time.sleep(1)
            self._close_extra_tabs_keep_first()
            time.sleep(1)
            # Ctrl+L to focus address bar
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.3)
            
            # Type URL
            pyperclip.copy('youtube.com')

            # Paste using Ctrl+V
            pyautogui.hotkey('ctrl', 'v')
            
            pyautogui.press('enter')
            
            # Wait for page load
            wait_time = random.uniform(3, 5)
            self.log(f"Waiting {wait_time:.1f}s for page load")
            time.sleep(wait_time)
            
            self.log("✓ Navigate completed")
            return True
            
        except Exception as e:
            self.log(f"✗ Navigate failed: {e}", "ERROR")
            return False
    