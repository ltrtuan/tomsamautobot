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
            if not self._exit_fullscreen_if_needed():
                self.log("Failed to exit fullscreen", "ERROR")
                return False
            try:
                import pyautogui
                screen_width, screen_height = pyautogui.size()
                
                # Move to right-center (safe area, no UI elements)
                # Move to right edge, random Y (avoid top/bottom 100px)
                safe_x = screen_width - 10  # 10px từ mép phải
                safe_y = random.randint(100, screen_height - 100)  # Random từ 100px đến (height-100)px

                MouseMoveAction.move_and_click_static(safe_x, safe_y, "single_click", fast=False)

                self.log(f"Moved mouse to safe area ({safe_x}, {safe_y}) before scroll", "INFO")
                time.sleep(0.3)  # Let UI settle
                
            except Exception as mouse_err:
                self.log(f"Could not move mouse: {mouse_err}", "WARNING")
                # Continue anyway, scroll might still work
            # ================================================================

            if random.random() < 0.5:
                self._random_scroll_pyautogui()
            else:
                # Determine direction
                if self.direction == "random":
                    direction_down = random.random() < 0.8
                else:
                    direction_down = (self.direction == "down")
        
                times = random.randint(15, 30)
            
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
