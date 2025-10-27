# helpers/actions/youtube_search_action.py

from helpers.actions.base_youtube_action import BaseYouTubeAction  # ← CHỈ CẦN IMPORT NÀY
from selenium.webdriver.common.by import By
from controllers.actions.mouse_move_action import MouseMoveAction
from controllers.actions.keyboard_action import KeyboardAction
import time
import random
import pyautogui
import os


class YouTubeSearchAction(BaseYouTubeAction):  # ← CHỈ KẾ THỪA BaseYouTubeAction
    """Search for keyword on YouTube"""

    def __init__(self, driver, profile_id, keywords, log_prefix="[YOUTUBE]", debugger_address=None):
        super().__init__(driver, profile_id, log_prefix, debugger_address)
        self.keywords = keywords

    def execute(self):
        """Execute YouTube search"""
        try:
            import random
            keywords_youtube = self.keywords.get('keywords_youtube', [])
            keyword = random.choice(keywords_youtube)
            # Get suffix_prefix string từ keywords dict
            suffix_prefix_string = self.keywords.get('suffix_prefix', '')

            # Parse thành list
            from helpers.keyword_variation_helper import KeywordVariationHelper
            suffix_prefix_list = KeywordVariationHelper.parse_suffix_prefix_list(suffix_prefix_string)

            # Generate keyword variation
            keyword = KeywordVariationHelper.generate_keyword_variation(
                keyword, suffix_prefix_list
            )
            
            self.log(f"Searching for keyword: '{keyword}'", "INFO")
            
            # Exit fullscreen if needed (search box is hidden in fullscreen)
            if not self._exit_fullscreen_if_needed():
                self.log("Failed to exit fullscreen", "ERROR")
                return False
            
            # Find search box
            search_box = self._find_search_box()
            if not search_box:
                self.log("Search box not found", "ERROR")
                return False
            
            # ========== SỬ DỤNG VIEWPORT COORDINATES (từ BaseFlowAction) ==========
            viewport_coords = self.get_element_viewport_coordinates(search_box)
            if not viewport_coords:
                self.log("Failed to get viewport coordinates, using Selenium fallback", "WARNING")
                search_box.click()
                self.random_sleep(0.3, 0.7)
            else:
                # Lấy vị trí browser window trên màn hình
                viewport_offset_x = self.driver.execute_script(
                    "return window.screenX + (window.outerWidth - window.innerWidth) / 2;"
                )
                viewport_offset_y = self.driver.execute_script(
                    "return window.screenY + (window.outerHeight - window.innerHeight);"
                )
                
                # Calculate smart click position (method from BaseFlowAction)
                click_x, click_y = self.calculate_smart_click_position(
                    viewport_coords,
                    viewport_offset_x,
                    viewport_offset_y
                )
                
                if click_x is None or click_y is None:
                    self.log("Failed to calculate click position, using Selenium fallback", "WARNING")
                    search_box.click()
                    self.random_sleep(0.3, 0.7)
                else:
                    # Validate coordinates in screen bounds
                    screen_width, screen_height = pyautogui.size()
                    coords_valid = (
                        click_x >= 0 and
                        click_y >= 0 and
                        click_x <= screen_width and
                        click_y <= screen_height
                    )
                    
                    if coords_valid:
                        self.log(f"Clicking search box at smart position: ({click_x:.1f}, {click_y:.1f})", "INFO")
                        try:
                            MouseMoveAction.move_and_click_static(
                                click_x, click_y,
                                click_type="single_click",
                                fast=False
                            )
                            self.random_sleep(0.3, 0.7)
                        except Exception as pyautogui_err:
                            self.log(f"PyAutoGUI click failed: {pyautogui_err}, using Selenium fallback", "WARNING")
                            search_box.click()
                            self.random_sleep(0.3, 0.7)
                    else:
                        self.log(f"Invalid coords ({click_x:.1f}, {click_y:.1f}), using Selenium click", "WARNING")
                        search_box.click()
                        self.random_sleep(0.3, 0.7)
            
            # Clear search box
            KeyboardAction.press_key_static("Ctrl+a")
            time.sleep(0.1)
            KeyboardAction.press_key_static("Del")
            self.random_sleep(0.2, 0.5)
            
            # Type keyword with human-like typing
            self._type_human_like(keyword)
            
            # Submit search
            self.random_sleep(0.5, 1.5)
            KeyboardAction.press_key_static("Enter")
            self.log("Search submitted", "SUCCESS")
            
            # Wait for search results
            time.sleep(random.uniform(2.5, 4.5))
            
            # ========== SEARCH FOR CHANNEL LOGO IN MAIN AREA ==========
            video_element = self._search_for_channel_logo_in_area(
                area_type="main",
                max_attempts=5
            )
        
            if video_element:
                self.log("✓ Found video by channel logo, clicking video...", "SUCCESS")
            
                # Click video (avoid logo, only click title/thumbnail)
                result = self._click_video_by_logo(video_element, area_type="main")
                if result:
                    self.log("✓ Clicked video successfully", "SUCCESS")
                    # Wait for video page to load and start playing
                    time.sleep(random.uniform(2.0, 3.0))
                    self.log("✓ Video should be playing now", "SUCCESS")
                    return True
                else:
                    self.log("⚠ Failed to click video, trying fallback", "WARNING")
                    # Fall through to fallback
            else:
                self.log("⚠ Logo not found after all attempts", "WARNING")
        
            # ========== FALLBACK: Click random video ==========
            self.log("Using fallback: clicking random video...", "INFO")
            fallback_result = self._click_random_video_fallback()
        
            if fallback_result:
                self.log("✓ Fallback: Clicked random video successfully", "SUCCESS")
                # Wait for video page to load and start playing
                time.sleep(random.uniform(2.0, 3.0))
                self.log("✓ Video should be playing now", "SUCCESS")
                return True
            else:
                self.log("✗ Fallback: Failed to click any video", "ERROR")
                return False

            
        except Exception as e:
            self.log(f"Search error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False

    def _search_for_channel_logo_in_area(self, area_type="main", max_attempts=4):
        """
        Generic method to search for channel logo and find video container
        
        Flow:
        1. ImageSearcher tìm logo trên screen → (logo_x, logo_y)
        2. Selenium tìm video containers → Filter visible + in viewport
        3. Check container nào chứa logo position
        4. Return container element
        
        Args:
            area_type: "main" or "sidebar"
            max_attempts: Number of scroll attempts (3-4)
        
        Returns:
            video_element (Selenium WebElement) or None
        """
        try:
            # ========== GET PARAMS BASED ON AREA TYPE ==========
            if area_type == "main":
                area_x = self.keywords.get('youtube_main_area_x', 0)
                area_y = self.keywords.get('youtube_main_area_y', 0)
                area_width = self.keywords.get('youtube_main_area_width', 1920)
                area_height = self.keywords.get('youtube_main_area_height', 1080)
                logo_image_path = self.keywords.get('youtube_image_search_path', '')
            elif area_type == "sidebar":
                area_x = self.keywords.get('youtube_sidebar_area_x', 0)
                area_y = self.keywords.get('youtube_sidebar_area_y', 0)
                area_width = self.keywords.get('youtube_sidebar_area_width', 400)
                area_height = self.keywords.get('youtube_sidebar_area_height', 1080)
                logo_image_path = self.keywords.get('youtube_sidebar_image_search_path', '')
            else:
                self.log(f"Unknown area type: {area_type}", "ERROR")
                return None
            
            # ========== CHECK PARAMS ==========
            if not logo_image_path or not os.path.exists(logo_image_path):
                self.log(f"No logo image path configured for {area_type} area", "WARNING")
                return None
            
            self.log(f"Searching for channel logo in {area_type} area...", "INFO")
            self.log(f"  Area: ({area_x}, {area_y}, {area_width}x{area_height})", "INFO")
            self.log(f"  Logo: {logo_image_path}", "INFO")
            
            # ========== LOOP: SEARCH LOGO WITH SCROLLING ==========
            for attempt in range(max_attempts):
                self.log(f"Logo search attempt {attempt+1}/{max_attempts}", "INFO")
                
                # Search logo using ImageSearcher (tìm trên SCREEN)
                from models.image_search import ImageSearcher
                region = (area_x, area_y, area_width, area_height)
                image_searcher = ImageSearcher(logo_image_path, region, accuracy=80)
                found, result = image_searcher.search()
                
                if found and result:
                    center_x, center_y, confidence = result
                    self.log(f"✓ Found logo at screen ({center_x}, {center_y}), confidence: {confidence}%", "SUCCESS")
                    
                    # Find video container that contains this logo
                    video_element = self._find_container_by_logo_position(
                        center_x, center_y, area_type
                    )
                    
                    if video_element:
                        self.log(f"✓ Found video container for {area_type} area", "SUCCESS")
                        return video_element
                    else:
                        self.log(f"⚠ Logo found but video container not found (might be off-screen)", "WARNING")
                
                # If not found, scroll and try again
                if attempt < max_attempts - 1:  # Don't scroll on last attempt
                    self.log(f"Logo not found, scrolling...", "INFO")
                    self._random_scroll_pyautogui(area_type)
                    time.sleep(random.uniform(1.0, 1.5))  # Wait for new content to load
            
            # Not found after all attempts
            self.log(f"✗ Logo not found in {area_type} area after {max_attempts} attempts", "WARNING")
            return None
        
        except Exception as e:
            self.log(f"Error searching for logo in {area_type} area: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return None
    
    def _find_container_by_logo_position(self, logo_screen_x, logo_screen_y, area_type="main"):
        """
        Find video container that contains logo at given screen position
    
        Logic: Giống youtube_click_video_action.py:
        1. Get all video containers bằng Selenium
        2. Filter: visible + in viewport
        3. Get viewport coords của mỗi container
        4. Check: logo position có nằm trong container bounds không?
    
        Args:
            logo_screen_x, logo_screen_y: Screen coordinates của logo (from ImageSearcher)
            area_type: "main" or "sidebar"
    
        Returns:
            video_element (Selenium WebElement) or None
        """
        try:
            # ========== GET VIDEO CONTAINERS (BASED ON AREA TYPE) ==========
            if area_type == "main":
                selectors = [
                    'ytd-video-renderer',        # List view (search results)
                    'ytd-grid-video-renderer',   # Grid view
                    'ytd-rich-item-renderer'     # Home feed
                ]
            elif area_type == "sidebar":
                # ← FIX: Sidebar chỉ dùng compact-video-renderer
                selectors = ['ytd-compact-video-renderer']
            else:
                self.log(f"Unknown area type: {area_type}", "ERROR")
                return None
        
            video_containers = []
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    video_containers.extend(elements)
                except:
                    pass
        
            if not video_containers:
                self.log("No video containers found on page", "ERROR")
                return None
        
            self.log(f"Found {len(video_containers)} total containers, filtering...", "INFO")
        
            # ========== FILTER: Visible + In Viewport ==========
            visible_containers = []
            for container in video_containers:
                try:
                    # Check displayed
                    if not container.is_displayed():
                        continue
                
                    # Check in viewport
                    if not self.is_element_in_viewport(container):
                        continue
                
                    visible_containers.append(container)
            
                except:
                    continue
        
            self.log(f"Found {len(visible_containers)} visible containers in viewport", "INFO")
        
            if not visible_containers:
                return None
        
            # ========== FIND CONTAINER CHỨA LOGO ==========
            for container in visible_containers:
                try:
                    # Get viewport coords
                    viewport_coords = self.get_element_viewport_coordinates(container)
                    if not viewport_coords:
                        continue
                
                    # Check if logo screen position is inside container bounds
                    # Logo screen coords == viewport coords (vì ImageSearcher tìm trên visible screen)
                    container_left = viewport_coords['x']
                    container_top = viewport_coords['y']
                    container_right = viewport_coords['right']
                    container_bottom = viewport_coords['bottom']
                
                    # Add tolerance (logo might be near edge)
                    tolerance = 20
                
                    if (container_left - tolerance <= logo_screen_x <= container_right + tolerance and
                        container_top - tolerance <= logo_screen_y <= container_bottom + tolerance):
                    
                        self.log(f"✓ Found matching container at viewport ({container_left}, {container_top})", "SUCCESS")
                        return container
            
                except Exception as e:
                    continue
        
            self.log("No container found containing logo position", "WARNING")
            return None
    
        except Exception as e:
            self.log(f"Error finding container by logo position: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return None

    
    def _click_video_by_logo(self, video_element, area_type="main"):
        """
        Click video container (avoid description, click title/thumbnail)
    
        Logic: 
        - Random priority: 50% prefer thumbnail, 50% prefer title
        - Fallback: If preferred not found, try the other
        - Last resort: Click container with safe zones
    
        Args:
            video_element: Video container element
            area_type: "main" or "sidebar"
    
        Returns:
            True if clicked successfully, False otherwise
        """
        try:
            # ========== RANDOM PRIORITY: THUMBNAIL vs TITLE ==========
            prefer_thumbnail = random.choice([True, False])  # 50/50
        
            clickable_element = None
            target_type = None
        
            # ========== DEFINE SEARCH METHODS ==========
            def find_thumbnail():
                """Try to find thumbnail element"""
                try:
                    thumbnail = video_element.find_element(By.CSS_SELECTOR, 'a#thumbnail, a.ytd-thumbnail')
                    if thumbnail and thumbnail.is_displayed():
                        return thumbnail
                except:
                    pass
                return None
        
            def find_title():
                """Try to find title element"""
                title_selectors = [
                    'a#video-title-link',
                    'a#video-title',
                    '#video-title a',
                    'h3 a'
                ]
                for selector in title_selectors:
                    try:
                        title = video_element.find_element(By.CSS_SELECTOR, selector)
                        if title and title.is_displayed():
                            return title
                    except:
                        continue
                return None
        
            # ========== TRY PREFERRED TARGET FIRST ==========
            if prefer_thumbnail:
                # Prefer thumbnail first
                clickable_element = find_thumbnail()
                if clickable_element:
                    target_type = 'thumbnail'
                    self.log("✓ Found thumbnail (preferred)", "DEBUG")
                else:
                    # Fallback to title
                    clickable_element = find_title()
                    if clickable_element:
                        target_type = 'title'
                        self.log("✓ Found title (fallback from thumbnail)", "DEBUG")
            else:
                # Prefer title first
                clickable_element = find_title()
                if clickable_element:
                    target_type = 'title'
                    self.log("✓ Found title (preferred)", "DEBUG")
                else:
                    # Fallback to thumbnail
                    clickable_element = find_thumbnail()
                    if clickable_element:
                        target_type = 'thumbnail'
                        self.log("✓ Found thumbnail (fallback from title)", "DEBUG")
        
            # ========== LAST RESORT: CLICK CONTAINER ==========
            if not clickable_element:
                clickable_element = video_element
                target_type = 'container'
                self.log("⚠ No thumbnail/title found, clicking container with safe zones", "WARNING")
        
            # ========== GET VIEWPORT OFFSET ==========
            try:
                viewport_offset_x = self.driver.execute_script(
                    "return window.screenX + (window.outerWidth - window.innerWidth) / 2;"
                )
                viewport_offset_y = self.driver.execute_script(
                    "return window.screenY + (window.outerHeight - window.innerHeight);"
                )
            
                if viewport_offset_x is None or viewport_offset_y is None:
                    self.log("Failed to get viewport offset", "ERROR")
                    return False
        
            except Exception as e:
                self.log(f"Viewport offset error: {e}", "ERROR")
                return False
        
            # ========== GET VIEWPORT COORDINATES ==========
            viewport_coords = self.get_element_viewport_coordinates(clickable_element)
            if not viewport_coords:
                self.log("Failed to get viewport coordinates", "ERROR")
                return False
        
            # ========== CALCULATE SAFE CLICK POSITION ==========
            if target_type in ['thumbnail', 'title']:
                # Thumbnail/title are safe
                avoid_zone = 'top-right' if area_type == "sidebar" else None
            else:
                # Container: avoid description area
                avoid_zone = 'bottom-half' if area_type == "main" else 'top-right'
        
            click_x, click_y = self.calculate_smart_click_position(
                viewport_coords,
                viewport_offset_x,
                viewport_offset_y,
                avoid_zone=avoid_zone
            )
        
            if click_x is None or click_y is None:
                self.log("Failed to calculate click position", "ERROR")
                return False
        
            # ========== VALIDATE COORDINATES ==========
            screen_width, screen_height = pyautogui.size()
            if not (0 <= click_x <= screen_width and 0 <= click_y <= screen_height):
                self.log(f"Invalid coords ({int(click_x)}, {int(click_y)}), skipping", "WARNING")
                return False
        
            # ========== CLICK VIDEO ==========
            self.log(f"Clicking video {target_type} at ({int(click_x)}, {int(click_y)})", "INFO")
        
            MouseMoveAction.move_and_click_static(
                int(click_x), int(click_y),
                click_type="single_click",
                fast=False
            )
        
            time.sleep(random.uniform(0.5, 1.0))
            return True
    
        except Exception as e:
            self.log(f"Error clicking video: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False

    


    def _find_search_box(self):
        """Find YouTube search box"""
        selectors = [
            'input#search',
            'input[name="search_query"]',
            'input[placeholder*="Search"]',
            'input.ytd-searchbox'
        ]
        
        for selector in selectors:
            try:
                search_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                if search_box and search_box.is_displayed():
                    return search_box
            except:
                continue
        
        return None
    
    def _click_random_video_fallback(self):
        """
        Fallback: Click random video when logo not found
        Similar to youtube_click_video_action.py logic
        
        Returns:
            True if clicked successfully, False otherwise
        """
        try:
            self.log("Searching for any visible video to click (fallback)...", "INFO")
            
            # ========== GET ALL VIDEO CONTAINERS ==========
            selectors = [
                'ytd-video-renderer',        # List view (search results)
                'ytd-grid-video-renderer',   # Grid view
                'ytd-rich-item-renderer'     # Home feed
            ]
            
            all_containers = []
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    all_containers.extend(elements)
                except:
                    pass
            
            if not all_containers:
                self.log("No video containers found on page", "ERROR")
                return False
            
            self.log(f"Found {len(all_containers)} total video containers", "INFO")
            
            # ========== FILTER: Visible + In Viewport ==========
            visible_containers = []
            for container in all_containers:
                try:
                    # Check displayed
                    if not container.is_displayed():
                        continue
                    
                    # Check in viewport
                    if not self.is_element_in_viewport(container):
                        continue
                    
                    visible_containers.append(container)
                
                except:
                    continue
            
            if not visible_containers:
                self.log("No visible video containers found in viewport", "ERROR")
                return False
            
            self.log(f"Found {len(visible_containers)} visible video containers", "INFO")
            
            # ========== PICK RANDOM VIDEO ==========
            random_container = random.choice(visible_containers)
            self.log(f"Selected random video container (index: {visible_containers.index(random_container) + 1}/{len(visible_containers)})", "INFO")
            
            # ========== CLICK USING SAME LOGIC ==========
            return self._click_video_by_logo(random_container, area_type="main")
        
        except Exception as e:
            self.log(f"Fallback click error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False


    def _type_human_like(self, text):
        """Type text with human-like delays"""
        for char in text:
            pyautogui.write(char)
            if random.random() < 0.7:
                time.sleep(random.uniform(0.05, 0.15))
            else:
                time.sleep(random.uniform(0.15, 0.25))
