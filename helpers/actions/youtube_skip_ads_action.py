# helpers/actions/youtube_skip_ads_action.py

from helpers.actions.base_youtube_action import BaseYouTubeAction
from selenium.webdriver.common.by import By
from controllers.actions.mouse_move_action import MouseMoveAction
import time
import random
import pyautogui


class YouTubeSkipAdsAction(BaseYouTubeAction):
    """Skip YouTube ads if present"""

    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE]", debugger_address=None, wait_time=2):
        super().__init__(driver, profile_id, log_prefix, debugger_address)
        self.wait_time = wait_time

    def execute(self):
        """Execute ad skip"""
        try:
            self.log("Checking for ads...", "INFO")

            # Wait for ad to potentially show
            time.sleep(self.wait_time)

            # Look for skip button
            skip_selectors = [
                '.ytp-ad-skip-button',
                '.ytp-ad-skip-button-modern',
                'button.ytp-ad-skip-button',
                '.ytp-skip-ad-button',
                '.ytp-ad-skip-button-slot',
                'button[class*="skip"]'
            ]

            for selector in skip_selectors:
                try:
                    skip_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if skip_button and skip_button.is_displayed():
                        
                        # ========== FIX: SỬ DỤNG VIEWPORT COORDINATES ==========
                        viewport_coords = self.get_element_viewport_coordinates(skip_button)
                        
                        if not viewport_coords:
                            self.log("Failed to get viewport coords, using Selenium fallback", "WARNING")
                            skip_button.click()
                            self.log("Skipped ad (Selenium click)", "SUCCESS")
                            time.sleep(2)
                            return True
                        else:
                            # Lấy vị trí browser window trên màn hình
                            viewport_offset_x = self.driver.execute_script(
                                "return window.screenX + (window.outerWidth - window.innerWidth) / 2;"
                            )
                            viewport_offset_y = self.driver.execute_script(
                                "return window.screenY + (window.outerHeight - window.innerHeight);"
                            )

                            # Tính tọa độ click = viewport offset + element viewport coords
                            click_x = viewport_offset_x + viewport_coords['x'] + viewport_coords['width'] / 2 + random.uniform(-5, 5)
                            click_y = viewport_offset_y + viewport_coords['y'] + viewport_coords['height'] / 2 + random.uniform(-3, 3)
                            
                            # Validate coordinates
                            screen_width, screen_height = pyautogui.size()
                            coords_valid = (
                                click_x >= 0 and
                                click_y >= 0 and
                                click_x <= screen_width and
                                click_y <= screen_height
                            )
                            
                            if coords_valid:
                                self.log(f"Clicking skip button at viewport coords: ({click_x:.1f}, {click_y:.1f})", "INFO")
                                try:
                                    MouseMoveAction.move_and_click_static(
                                        click_x, click_y, 
                                        click_type="single_click", 
                                        fast=False
                                    )
                                    self.log("Skipped ad", "SUCCESS")
                                    time.sleep(2)
                                    return True
                                except Exception as pyautogui_err:
                                    self.log(f"PyAutoGUI click failed: {pyautogui_err}, using Selenium fallback", "WARNING")
                                    skip_button.click()
                                    self.log("Skipped ad (Selenium fallback)", "SUCCESS")
                                    time.sleep(2)
                                    return True
                            else:
                                self.log(f"Invalid coords ({click_x:.1f}, {click_y:.1f}), using Selenium click", "WARNING")
                                skip_button.click()
                                self.log("Skipped ad (Selenium click)", "SUCCESS")
                                time.sleep(2)
                                return True
                        # ========================================================

                except Exception as selector_err:
                    # Selector không tìm thấy hoặc element không visible
                    continue

            self.log("No ads detected or skip button not available yet", "INFO")
            return False

        except Exception as e:
            self.log(f"Ad skip error: {e}", "WARNING")
            import traceback
            traceback.print_exc()
            return False
