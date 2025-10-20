# helpers/actions/youtube_scroll_action.py

from helpers.actions.base_youtube_action import BaseYouTubeAction
from controllers.actions.keyboard_action import KeyboardAction
from controllers.actions.mouse_move_action import MouseMoveAction
import random
import time


class YouTubeScrollAction(BaseYouTubeAction):
    """Scroll page using keyboard"""

    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE]", debugger_address=None, 
                 direction="random", times=None):
        super().__init__(driver, profile_id, log_prefix, debugger_address)
        self.direction = direction  # "up", "down", or "random"
        self.times = times  # None = random

    def execute(self):
        """Execute scroll action"""
        try:
            # ========== FIX: Move mouse to safe area before scroll ==========
            # Move mouse to right edge of screen to avoid dropdown/hover issues
            try:
                import pyautogui
                screen_width, screen_height = pyautogui.size()
                
                # Move to right-center (safe area, no UI elements)
                safe_x = screen_width - 50  # 50px from right edge
                safe_y = screen_height // 2  # Middle of screen
                
                MouseMoveAction.move_and_click_static(safe_x, safe_y, "single_click", fast=False)
                self.log(f"Moved mouse to safe area ({safe_x}, {safe_y}) before scroll", "INFO")
                time.sleep(0.3)  # Let UI settle
                
            except Exception as mouse_err:
                self.log(f"Could not move mouse: {mouse_err}", "WARNING")
                # Continue anyway, scroll might still work
            # ================================================================

            # Determine scroll method
            use_page_keys = random.random() < 0.5

            # Determine direction
            if self.direction == "random":
                direction_down = random.random() < 0.8
            else:
                direction_down = (self.direction == "down")

            # Determine times
            if self.times is None:
                if use_page_keys:
                    times = random.randint(1, 3)
                else:
                    times = random.randint(3, 8)
            else:
                times = self.times

            # Execute scroll
            if use_page_keys:
                key = "Page_Down" if direction_down else "Page_Up"
                key_sequence = ";".join([key] * times)
                KeyboardAction.press_key_static(key_sequence)
                self.log(f"Scrolled with {key} x{times}", "SUCCESS")
            else:
                key = "Down" if direction_down else "Up"
                key_sequence = ";".join([key] * times)
                KeyboardAction.press_key_static(key_sequence)
                self.log(f"Scrolled with Arrow {key} x{times}", "SUCCESS")

            return True

        except Exception as e:
            self.log(f"Scroll error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
