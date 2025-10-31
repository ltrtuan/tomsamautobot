# controllers/actions/flow_auto/actions_auto/youtube_mouse_move_auto_action.py

from controllers.actions.flow_auto.actions_auto.base_flow_auto_action import BaseFlowAutoAction
from controllers.actions.mouse_move_action import MouseMoveAction
import random
import pyautogui

class YouTubeMouseMoveAutoAction(BaseFlowAutoAction):
    """Move mouse to random position within screen (full screen)"""
    
    def __init__(self, profile_id, click=False, log_prefix="[YOUTUBE AUTO]"):
        """
        Initialize mouse move action
        
        Args:
            profile_id: GoLogin profile ID
            window_info: Browser window info (optional, for viewport-based movement)
            click: Whether to click after moving (True/False)
            log_prefix: Prefix for log messages
        """
        super().__init__(profile_id, log_prefix)
        self.click = click
    
    def execute(self):
        """Execute mouse move action"""
        try:
            # Get screen size
            screen_width, screen_height = pyautogui.size()
        
            # Generate random position within screen (avoid edges)
            random_x = random.randint(int(screen_width * 0.2), int(screen_width * 0.8))
            random_y = random.randint(int(screen_height * 0.2), int(screen_height * 0.8))
        
            # Move mouse using MouseMoveAction (human-like movement)
            click_type = "single_click" if self.click else None
            MouseMoveAction.move_and_click_static(random_x, random_y, click_type=click_type, fast=False)
        
            if click_type:
                self.log(f"✓ Moved mouse to ({random_x}, {random_y}) and clicked")
            else:
                self.log(f"✓ Moved mouse to ({random_x}, {random_y})")
        
            return True
        
        except Exception as e:
            self.log(f"✗ Mouse move error: {e}", "ERROR")
            return False
