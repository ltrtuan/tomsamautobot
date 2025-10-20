# helpers/actions/youtube_mouse_move_action.py

from helpers.actions.base_youtube_action import BaseYouTubeAction
from controllers.actions.mouse_move_action import MouseMoveAction
import random

class YouTubeMouseMoveAction(BaseYouTubeAction):
    """Move mouse to random position within viewport"""
    
    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE]", debugger_address=None, click=False):
        super().__init__(driver, profile_id, log_prefix, debugger_address)
        self.click = click
    
    def execute(self):
        """Execute mouse move"""
        try:
            import pyautogui
            
            # Get viewport size
            viewport_width = self.driver.execute_script("return window.innerWidth")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # Get screen offset
            viewport_offset_x = self.driver.execute_script("return window.screenX + (window.outerWidth - window.innerWidth);")
            viewport_offset_y = self.driver.execute_script("return window.screenY + (window.outerHeight - window.innerHeight);")
            
            # Generate random position
            random_x = random.randint(int(viewport_width * 0.2), int(viewport_width * 0.8))
            random_y = random.randint(int(viewport_height * 0.2), int(viewport_height * 0.8))
            
            screen_x = int(viewport_offset_x + random_x)
            screen_y = int(viewport_offset_y + random_y)
            
            # Move mouse
            click_type = "single_click" if self.click else None
            MouseMoveAction.move_and_click_static(screen_x, screen_y, click_type=click_type, fast=False)
            
            if click_type:
                self.log(f"Moved mouse to ({screen_x}, {screen_y}) and clicked", "SUCCESS")
            else:
                self.log(f"Moved mouse to ({screen_x}, {screen_y})", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.log(f"Mouse move error: {e}", "ERROR")
            return False
