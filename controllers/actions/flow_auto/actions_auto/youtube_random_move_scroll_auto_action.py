# controllers/actions/flow_auto/actions_auto/youtube_random_move_scroll_auto_action.py

import time
import random
import pyautogui
from controllers.actions.mouse_move_action import MouseMoveAction
from controllers.actions.flow_auto.actions_auto.base_flow_auto_action import BaseFlowAutoAction

class YouTubeRandomMoveScrollAutoAction(BaseFlowAutoAction):
    """Random mouse move and scroll actions"""
    
    def __init__(self, profile_id, num_actions=2, area = "main", log_prefix="[YOUTUBE AUTO]"):
        self.profile_id = profile_id
        self.num_actions = num_actions
        self.area = area
        self.log_prefix = log_prefix
    
    def _execute_internal(self):
        """Execute random actions"""
        try:
            self.log(f"Performing {self.num_actions} random actions")
            screen_width, screen_height = pyautogui.size()
            for i in range(self.num_actions):               
                
                # Move to right-center (safe area, no UI elements)
                # Move to right edge, random Y (avoid top/bottom 100px)
                safe_x = screen_width - 18  # 10px từ mép phải
                safe_y = random.randint(100, screen_height - 100)  # Random từ 100px đến (height-100)px
                if i == 1:
                    MouseMoveAction.move_and_click_static(safe_x, safe_y, "single_click", fast=False)
                    self.log(f"Moved mouse to safe area ({safe_x}, {safe_y}) before scroll", "INFO")
                time.sleep(0.3)  # Let UI settle
                if self.area == "main":
                    scroll_amount = random.randint(-900, -800)  # Scroll down
                else:
                    scroll_amount = random.randint(-400, -200)  # Scroll down
                    
                pyautogui.scroll(scroll_amount)
            
            self.log("✓ Random actions completed")
            
            time.sleep(random.uniform(0.3, 1))
            return True
            
        except Exception as e:
            self.log(f"✗ Random actions failed: {e}", "ERROR")
            return False