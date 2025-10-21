# helpers/actions/youtube_fullscreen_action.py

from helpers.actions.base_youtube_action import BaseYouTubeAction
from selenium.webdriver.common.by import By
from controllers.actions.mouse_move_action import MouseMoveAction
from controllers.actions.keyboard_action import KeyboardAction
import random
import time
import pyautogui

class YouTubeFullscreenAction(BaseYouTubeAction):
    """Toggle fullscreen mode on YouTube video"""
    
    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE]", debugger_address=None):
        super().__init__(driver, profile_id, log_prefix, debugger_address)
    
    def execute(self):
        """Execute fullscreen toggle"""
        try:
            # Check current fullscreen state
            is_fullscreen = self._check_fullscreen_state()
        
            if is_fullscreen:
                self.log("Already in fullscreen mode, pressing F11 to exit", "INFO")
                KeyboardAction.press_key_static("Escape")
                time.sleep(random.uniform(0.5, 1))
                self.log("Exited fullscreen mode", "SUCCESS")
                return True
        
            self.log("Not in fullscreen, entering fullscreen...", "INFO")
        
            # Step 1: Move mouse to video area to show controls FIRST
            self.log("Preparing to enter fullscreen - showing controls...", "INFO")
            move_success = self._move_mouse_to_video_area()

            if not move_success:
                self.log("Failed to move mouse to video, falling back to F11", "WARNING")
                # Fallback to F11
                KeyboardAction.press_key_static("f11")
                time.sleep(random.uniform(0.5, 1))
                self.log("Entered fullscreen via F11", "SUCCESS")
                return True

            # Try to find and click fullscreen button
            fullscreen_button = self._find_fullscreen_button()
        
            if fullscreen_button:
                self.log("Found fullscreen button, clicking...", "INFO")
            
                # Get viewport coordinates
                viewport_coords = self.get_element_viewport_coordinates(fullscreen_button)
            
                if viewport_coords:
                    success = self._click_fullscreen_button(viewport_coords)
                    if success:
                        self.log("Entered fullscreen via button click", "SUCCESS")
                        return True
                    else:
                        self.log("Button click failed, falling back to F11", "WARNING")
                else:
                    self.log("Failed to get button coordinates, falling back to F11", "WARNING")
            else:
                self.log("Fullscreen button not found, falling back to F11", "WARNING")
        
            # Fallback: Use F11 key
            self.log("Using F11 to enter fullscreen", "INFO")
            KeyboardAction.press_key_static("f11")
            time.sleep(random.uniform(0.5, 1))
            self.log("Entered fullscreen via F11", "SUCCESS")
            return True
        
        except Exception as e:
            self.log(f"Fullscreen error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False

    
    def _check_fullscreen_state(self):
        """
        Check if video is currently in fullscreen mode
        Returns: True if fullscreen, False otherwise
        """
        try:
            # Check via JavaScript (YouTube uses .ytp-fullscreen class when in fullscreen)
            is_fullscreen = self.driver.execute_script("""
                // Check if document is in fullscreen
                if (document.fullscreenElement || 
                    document.webkitFullscreenElement || 
                    document.mozFullScreenElement || 
                    document.msFullscreenElement) {
                    return true;
                }
                
                // Check YouTube player fullscreen state
                var player = document.querySelector('.html5-video-player');
                if (player && player.classList.contains('ytp-fullscreen')) {
                    return true;
                }
                
                return false;
            """)
            
            return bool(is_fullscreen)
            
        except Exception as e:
            self.log(f"Failed to check fullscreen state: {e}", "WARNING")
            return False
    
    def _find_fullscreen_button(self):
        """Find YouTube fullscreen button"""
        selectors = [
            'button.ytp-fullscreen-button',
            '.ytp-fullscreen-button',
            'button[aria-label*="Fullscreen"]',
            'button[aria-label*="Full screen"]',
            '.ytp-button[aria-label*="fullscreen"]'
        ]
        
        for selector in selectors:
            try:
                button = self.driver.find_element(By.CSS_SELECTOR, selector)
                if button and button.is_displayed():
                    return button
            except:
                continue
        
        return None
    
    def _click_fullscreen_button(self, viewport_coords):
        """
        Click fullscreen button using physical mouse
        First move to video area to show controls, then click fullscreen button
    
        Args:
            viewport_coords: dict with x, y, width, height of fullscreen button
        Returns:
            True if click succeeded, False otherwise
        """
        try:
           
        
            # Step 2: Click fullscreen button
            # Get viewport offset
            viewport_offset_x = self.driver.execute_script(
                "return window.screenX + (window.outerWidth - window.innerWidth) / 2;"
            )
            viewport_offset_y = self.driver.execute_script(
                "return window.screenY + (window.outerHeight - window.innerHeight);"
            )
        
            if viewport_offset_x is None or viewport_offset_y is None:
                self.log("Failed to get viewport offset", "WARNING")
                return False
        
            # Calculate click position (center + small random offset)
            click_x = viewport_offset_x + viewport_coords['x'] + viewport_coords['width'] / 2 + random.uniform(-10, 10)
            click_y = viewport_offset_y + viewport_coords['y'] + viewport_coords['height'] / 2 + random.uniform(-3, 3)
        
            # Validate coordinates
            import pyautogui
            screen_width, screen_height = pyautogui.size()
            coords_valid = (
                click_x >= 0 and
                click_y >= 0 and
                click_x <= screen_width and
                click_y <= screen_height
            )
        
            if not coords_valid:
                self.log(f"Invalid coords ({click_x:.1f}, {click_y:.1f})", "WARNING")
                return False
        
            self.log(f"Clicking fullscreen button at ({click_x:.1f}, {click_y:.1f})", "INFO")
        
            # Click button
            from controllers.actions.mouse_move_action import MouseMoveAction
            MouseMoveAction.move_and_click_static(
                int(click_x), int(click_y),
                click_type="single_click",
                fast=False
            )
        
            time.sleep(random.uniform(0.5, 1))
            return True
        
        except Exception as e:
            self.log(f"Click fullscreen button error: {e}", "ERROR")
            return False


    def _move_mouse_to_video_area(self):
        """
        Move mouse to video area to trigger controls visibility
        Returns: True if successful, False otherwise
        """
        try:
            # Find video element (now from base class)
            video_element = self._find_video_element()
            if not video_element:
                self.log("Video element not found for hover", "WARNING")
                return False
        
            # Get video viewport coordinates
            video_coords = self.get_element_viewport_coordinates(video_element)
            if not video_coords:
                self.log("Failed to get video coordinates", "WARNING")
                return False
        
            # Get viewport offset
            viewport_offset_x = self.driver.execute_script(
                "return window.screenX + (window.outerWidth - window.innerWidth) / 2;"
            )
            viewport_offset_y = self.driver.execute_script(
                "return window.screenY + (window.outerHeight - window.innerHeight);"
            )
        
            if viewport_offset_x is None or viewport_offset_y is None:
                self.log("Failed to get viewport offset", "WARNING")
                return False
        
            # Calculate random position in video area
            video_click_x, video_click_y = self.calculate_smart_click_position(
                video_coords,
                viewport_offset_x,
                viewport_offset_y
            )
        
            if not video_click_x or not video_click_y:
                self.log("Failed to calculate click position", "WARNING")
                return False
        
            self.log(f"Moving to video area at ({video_click_x:.1f}, {video_click_y:.1f})", "INFO")
        
            MouseMoveAction.move_and_click_static(
                int(video_click_x), 
                int(video_click_y),
                click_type=None,  # No click, just move
                fast=False
            )
            time.sleep(random.uniform(0.3, 0.5))  # Wait for controls to appear
        
            self.log("Controls should now be visible", "INFO")
            return True
        
        except Exception as e:
            self.log(f"Move mouse to video area error: {e}", "ERROR")
            return False
