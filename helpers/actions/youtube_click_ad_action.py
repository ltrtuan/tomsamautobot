# helpers/actions/youtube_click_ad_action.py

from helpers.actions.base_youtube_action import BaseYouTubeAction
from selenium.webdriver.common.by import By
from controllers.actions.mouse_move_action import MouseMoveAction
import random
import time
import pyautogui


class YouTubeClickAdAction(BaseYouTubeAction):
    """Click on ad, scroll ad page, then close"""

    def execute(self):
        """Execute ad click"""
        try:
            self.log("Looking for ads to click...", "INFO")

            ad_selectors = [
                '.ytp-ad-overlay-image',
                '.ytp-ad-text-overlay',
                'div.ytp-ad-button',
                'a[href*="googleadservices"]',
                'div[class*="ad-container"] a'
            ]

            ad_clicked = False
            main_tab = self.driver.current_window_handle

            for selector in ad_selectors:
                try:
                    ad_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_ads = [ad for ad in ad_elements if ad.is_displayed()]
                    
                    if visible_ads:
                        target_ad = random.choice(visible_ads)

                        # ========== FIX: SỬ DỤNG VIEWPORT COORDINATES ==========
                        viewport_coords = self.get_element_viewport_coordinates(target_ad)
                        
                        if not viewport_coords:
                            self.log("Failed to get ad coords, skipping", "WARNING")
                            continue

                        # Lấy vị trí browser window trên màn hình
                        viewport_offset_x = self.driver.execute_script(
                            "return window.screenX + (window.outerWidth - window.innerWidth) / 2;"
                        )
                        viewport_offset_y = self.driver.execute_script(
                            "return window.screenY + (window.outerHeight - window.innerHeight);"
                        )

                        # Tính tọa độ click = viewport offset + element viewport coords
                        click_x = viewport_offset_x + viewport_coords['x'] + viewport_coords['width'] / 2 + random.uniform(0.3, 0.7)
                        click_y = viewport_offset_y + viewport_coords['y'] + viewport_coords['height'] / 2 + random.uniform(0.3, 0.7)

                        # Validate coords
                        screen_width, screen_height = pyautogui.size()
                        if not (0 <= click_x <= screen_width and 0 <= click_y <= screen_height):
                            self.log(f"Invalid ad coords ({click_x:.1f}, {click_y:.1f})", "WARNING")
                            continue

                        MouseMoveAction.move_and_click_static(
                            int(click_x), int(click_y), 
                            click_type="single_click", 
                            fast=False
                        )
                        self.log("Clicked ad", "SUCCESS")
                        ad_clicked = True
                        time.sleep(3)
                        break
                except:
                    continue

            if ad_clicked:
                # Handle ad tab
                if len(self.driver.window_handles) > 1:
                    new_tab = self.driver.window_handles[-1]
                    self.driver.switch_to.window(new_tab)
                    self.log("Switched to ad tab", "INFO")

                    # Scroll ad page
                    scroll_duration = random.uniform(10, 20)
                    self.log(f"Scrolling ad page for {scroll_duration:.1f}s...", "INFO")
                    
                    num_scrolls = random.randint(3, 6)
                    for i in range(num_scrolls):
                        scroll_amount = random.randint(200, 500)
                        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                        time.sleep(scroll_duration / num_scrolls)

                    # Close ad tab
                    self.driver.close()
                    self.driver.switch_to.window(main_tab)
                    self.log("Closed ad tab, back to YouTube", "SUCCESS")

                    # Resume video if paused
                    time.sleep(1)
                    is_paused = self.driver.execute_script(
                        "return document.querySelector('video.html5-main-video') ? "
                        "document.querySelector('video.html5-main-video').paused : false"
                    )
                    if is_paused:
                        self.log("Video paused, resuming...", "INFO")
                        viewport_width = self.driver.execute_script("return window.innerWidth")
                        viewport_height = self.driver.execute_script("return window.innerHeight")
                        MouseMoveAction.move_and_click_static(
                            int(viewport_width / 2), int(viewport_height / 2),
                            click_type="single_click", fast=False
                        )
                return True
            else:
                self.log("No ads found", "INFO")
                return False

        except Exception as e:
            self.log(f"Ad click error: {e}", "ERROR")
            try:
                self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
            return False
