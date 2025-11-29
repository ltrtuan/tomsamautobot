# controllers/actions/flow_auto/actions_auto/youtube_navigate_auto_action.py

import time
import random
import pyautogui
from helpers.gologin_profile_helper import GoLoginProfileHelper
from controllers.actions.flow_auto.actions_auto.base_flow_auto_action import BaseFlowAutoAction
from models.global_variables import GlobalVariables
import pyperclip

class YouTubeNavigateAutoAction(BaseFlowAutoAction):
    """Navigate to YouTube using Ctrl+L keyboard shortcut"""
    
    def __init__(self, profile_id, parameters, log_prefix="[YOUTUBE AUTO]"):
        super().__init__(profile_id, log_prefix)
        self.parameters = parameters
    
    def _execute_internal(self):
        """Execute navigate action"""
        try:
            self.log("Navigating to YouTube")
            not_full_load = int(GlobalVariables().get(f'not_full_load_{self.profile_id}', 0));
            if not_full_load >= 3 :
                return False
            
            # Bring to front
            result_bring = GoLoginProfileHelper.bring_profile_to_front(self.profile_id, driver=None)
            if result_bring:
                time.sleep(1)
                self._close_extra_tabs_keep_first()
                time.sleep(1)
                # Ctrl+L to focus address bar
                pyautogui.keyDown('ctrl')
                time.sleep(0.1)
                pyautogui.press('l')
                time.sleep(0.1)
                pyautogui.keyUp('ctrl')
                time.sleep(0.3)
            
                # Type URL
                pyperclip.copy('youtube.com')

                # Paste using Ctrl+V
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(random.uniform(0.5, 1))
                pyautogui.press('enter')
                
                GlobalVariables().set(f'not_full_load_{self.profile_id}', not_full_load + 1)
                self.log(f"Waiting for page load")
                
                if self.check_page_fully_loaded():
                    self.log("✓ Navigate completed")
                    GlobalVariables().set(f'not_full_load_{self.profile_id}', 0)
                    return True
                
                self.log("✗ Navigate Failed")
                return False
            return False
        except Exception as e:
            self.log(f"✗ Navigate failed: {e}", "ERROR")
            return False
    