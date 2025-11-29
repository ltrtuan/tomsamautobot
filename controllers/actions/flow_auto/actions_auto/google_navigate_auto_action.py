# controllers/actions/flow_auto/actions_auto/youtube_navigate_auto_action.py

import time
import random
import pyautogui
from helpers.gologin_profile_helper import GoLoginProfileHelper
from controllers.actions.flow_auto.actions_auto.base_flow_auto_action import BaseFlowAutoAction
import pyperclip

class GoogleNavigateAutoAction(BaseFlowAutoAction):
    """Navigate to YouTube using Ctrl+L keyboard shortcut"""
    
    def __init__(self, profile_id, log_prefix="[YOUTUBE AUTO]"):
       super().__init__(profile_id, log_prefix)
    
    def _execute_internal(self):
        """Execute navigate action"""
        try:
            self.log("Navigating to Google")
            
            # Bring to front
            result_bring = GoLoginProfileHelper.bring_profile_to_front(self.profile_id, driver=None)
            if result_bring:
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
                time.sleep(random.uniform(0.5, 1))
                pyautogui.press('enter')
            
                # Wait for page load
                wait_time = random.uniform(3, 5)
                self.log(f"Waiting {wait_time:.1f}s for page load")
                time.sleep(wait_time)
            
                self.log("✓ Navigate completed")
                return True
            return False
        except Exception as e:
            self.log(f"✗ Navigate failed: {e}", "ERROR")
            return False
    