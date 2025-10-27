# helpers/actions/youtube_click_video_action.py

from helpers.actions.base_youtube_action import BaseYouTubeAction
from selenium.webdriver.common.by import By
from controllers.actions.mouse_move_action import MouseMoveAction
import random
import time
import pyautogui

class YouTubeClickVideoAction(BaseYouTubeAction):
    """Click random video and wait for it to start playing"""
    
    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE]", debugger_address=None, video_index_range=(1, 10), location="main"):
        super().__init__(driver, profile_id, log_prefix, debugger_address)
        self.video_index_range = video_index_range
        self.location = location  # 'main' hoặc 'side'
    
    def execute(self):
        """Execute video click and wait for video to start playing"""
        try:
            self.log("Looking for videos to click...", "INFO")
        
            if not self._exit_fullscreen_if_needed():
                self.log("Failed to exit fullscreen", "ERROR")
                return False
        
            # ========== SELECT SELECTORS BASED ON LOCATION ==========
            if self.location == 'side':
                self.log("Looking for sidebar videos...", "INFO")
    
                # Scroll sidebar to ensure videos are loaded
                self._scroll_sidebar_into_view()
    
                # Debug: inspect actual DOM structure
                self._debug_sidebar_structure()
    
                # For sidebar: Try multiple selectors including generic link selectors
                video_selectors = [
                    # New structure - try video links in secondary
                    '#secondary a[href*="/watch?v="]:not([href*="&list="]):not([aria-label*="Short"])',
                    '#related a[href*="/watch?v="]:not([href*="&list="]):not([aria-label*="Short"])',
        
                    # Standard ytd renderers
                    'ytd-compact-video-renderer',
                    'ytd-video-renderer',
                    'ytd-rich-item-renderer',
        
                    # Nested structures
                    'ytd-item-section-renderer ytd-compact-video-renderer',
                    '#secondary ytd-compact-video-renderer',
                    'ytd-watch-next-secondary-results-renderer ytd-compact-video-renderer',
        
                    # Fallback: any video link in sidebar
                    'ytd-watch-next-secondary-results-renderer a[href*="/watch?v="]',
                    '#secondary ytd-thumbnail a[href*="/watch?v="]'
                ]

            else:
                self.log("Looking for main feed videos...", "INFO")
                # For main feed: Keep original behavior (thumbnail/title)
                video_selectors = {
                    'thumbnail': [
                        'ytd-rich-item-renderer a#thumbnail:not([aria-label*="Short"])',
                        'ytd-video-renderer a#thumbnail:not([aria-label*="Short"])'
                    ],
                    'title': [
                        'ytd-rich-item-renderer a#video-title-link:not([aria-label*="Short"])',
                        'ytd-video-renderer a#video-title-link:not([aria-label*="Short"])',
                        'ytd-rich-item-renderer #video-title:not([aria-label*="Short"])',
                        'ytd-video-renderer #video-title:not([aria-label*="Short"])'
                    ]
                }
        
            # ========== SIDEBAR: SIMPLIFIED LOGIC ==========
            if self.location == 'side':
                for selector in video_selectors:
                    try:
                        self.log(f"🔍 Trying selector: {selector}", "DEBUG")
                        video_containers = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        self.log(f"   Found {len(video_containers)} total elements", "DEBUG")
                    
                        if not video_containers:
                            self.log(f"   ❌ No elements found with this selector", "DEBUG")
                            continue
                    
                        visible_containers = [v for v in video_containers if v.is_displayed()]
                        self.log(f"   Found {len(visible_containers)} visible elements", "DEBUG")
                    
                        if not visible_containers:
                            self.log(f"   No visible video containers with selector: {selector}", "DEBUG")
                            continue
                    
                        self.log(f"Found {len(visible_containers)} visible sidebar video containers", "INFO")
                    
                        # Filter out ads and shorts
                        valid_containers = []
                        not_in_viewport_count = 0
                        ad_count = 0
                        shorts_count = 0
                    
                        for container in visible_containers:
                            # Check if in viewport
                            if not self.is_element_in_viewport(container):
                                not_in_viewport_count += 1
                                continue
                        
                            # Filter ads
                            if self._is_ad_element(container):
                                ad_count += 1
                                continue
                        
                            # Filter shorts
                            if self._is_shorts_video(container):
                                shorts_count += 1
                                continue
                        
                            # Valid container
                            valid_containers.append(container)
                    
                        # Log filtering results
                        self.log(f"   Filtered: {not_in_viewport_count} not in viewport, {ad_count} ads, {shorts_count} shorts", "DEBUG")
                    
                        if valid_containers:
                            self.log(f"Found {len(valid_containers)} valid sidebar videos (non-shorts, non-ads)", "INFO")
                        
                            # Select random container from range
                            max_index = min(len(valid_containers), self.video_index_range[1])
                            min_index = self.video_index_range[0]
                        
                            if max_index >= min_index:
                                available_containers = valid_containers[min_index-1:max_index]
                                target_container = random.choice(available_containers)
                            
                                # Check if target_container is already a clickable link
                                clicked = False

                                # Check if element is already an <a> tag (link)
                                tag_name = target_container.tag_name.lower()

                                if tag_name == 'a':
                                    # Element is already a link, click it directly
                                    self.log("   Element is already a link, clicking directly", "DEBUG")
                                    success = self._click_video_smart(target_container, target_type='link')
                                    clicked = success
                                else:
                                    # Element is a container, try to find clickable child
                                    # Try 1: Click thumbnail inside container
                                    try:
                                        thumbnail = target_container.find_element(By.CSS_SELECTOR, 'a#thumbnail, a.ytd-thumbnail')
                                        if thumbnail and thumbnail.is_displayed():
                                            self.log("   Trying to click thumbnail inside container", "DEBUG")
                                            success = self._click_video_smart(thumbnail, target_type='thumbnail')
                                            if success:
                                                clicked = True
                                    except Exception as e:
                                        self.log(f"   No thumbnail found in container: {e}", "DEBUG")
    
                                    # Try 2: Click container if thumbnail failed
                                    if not clicked:
                                        self.log("   Trying to click container directly", "DEBUG")
                                        success = self._click_video_smart(target_container, target_type='container')
                                        clicked = success

                                if clicked:
                                    # Wait for video to start playing
                                    if self._wait_for_video_playing():
                                        self.log("✓ Sidebar video started playing", "SUCCESS")
                                        return True
                                    else:
                                        self.log("Video did not start playing (timeout)", "WARNING")
                                        return False

                        else:
                            self.log(f"   No valid sidebar videos after filtering (selector: {selector})", "DEBUG")
                        
                    except Exception as e:
                        self.log(f"Error with selector {selector}: {e}", "WARNING")
                        import traceback
                        traceback.print_exc()
                        continue
            
                self.log("⚠ No clickable sidebar videos found", "WARNING")
                return False
        
            # ========== MAIN FEED: ORIGINAL LOGIC WITH THUMBNAIL/TITLE ==========
            else:
                # Try both target types (thumbnail first, then title as fallback)
                target_types_to_try = ['thumbnail', 'title']
                random.shuffle(target_types_to_try)  # Randomize order
            
                for click_target in target_types_to_try:
                    self.log(f"Trying target type: {click_target}", "INFO")
                
                    # Try to find and click target
                    for selector in video_selectors[click_target]:
                        try:
                            video_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if not video_elements:
                                continue
                        
                            visible_videos = [v for v in video_elements if v.is_displayed()]
                            if not visible_videos:
                                self.log(f"No visible videos with selector: {selector}", "DEBUG")
                                continue
                        
                            self.log(f"Found {len(visible_videos)} visible videos with selector: {selector}", "DEBUG")
                        
                            # Filter out shorts and ads
                            non_shorts_videos = []
                            for video in visible_videos:
                                # Check if in viewport
                                if not self.is_element_in_viewport(video):
                                    continue
                            
                                # Filter ads
                                if self._is_ad_element(video):
                                    self.log(f"• Filtered out Ad", "DEBUG")
                                    continue
                            
                                if not self._is_shorts_video(video):
                                    non_shorts_videos.append(video)
                                else:
                                    self.log(f"Filtered out Shorts video", "DEBUG")
                        
                            if non_shorts_videos:
                                self.log(f"Found {len(non_shorts_videos)} valid videos (non-shorts, non-ads)", "INFO")
                            
                                # Select random video from range
                                max_index = min(len(non_shorts_videos), self.video_index_range[1])
                                min_index = self.video_index_range[0]
                            
                                if max_index >= min_index:
                                    available_videos = non_shorts_videos[min_index-1:max_index]
                                    target_video = random.choice(available_videos)
                                
                                    # Click video with random position
                                    success = self._click_video_smart(target_video, click_target)
                                
                                    if success:
                                        # Wait for video to start playing
                                        if self._wait_for_video_playing():
                                            self.log(f"✓ Video started playing (clicked: {click_target})", "SUCCESS")
                                            return True
                                        else:
                                            self.log("Video did not start playing (timeout)", "WARNING")
                                            return False
                            else:
                                self.log(f"No valid videos after filtering (selector: {selector})", "DEBUG")
                    
                        except Exception as e:
                            self.log(f"Error with selector {selector}: {e}", "WARNING")
                            import traceback
                            traceback.print_exc()
                            continue
                
                    self.log(f"No clickable videos found for target type: {click_target}", "WARNING")
            
                # If both target types failed
                self.log("⚠ No clickable videos found (tried both thumbnail and title)", "WARNING")
                return False
    
        except Exception as e:
            self.log(f"Error executing click video: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False


    def _debug_sidebar_structure(self):
        """Debug method to inspect actual sidebar DOM structure"""
        try:
            self.log("🔍 Inspecting sidebar DOM structure...", "DEBUG")
        
            # Try to find sidebar container first
            sidebar_containers = [
                '#secondary',
                '#secondary-inner',
                'ytd-watch-next-secondary-results-renderer',
                '#related'
            ]
        
            for container_selector in sidebar_containers:
                try:
                    container = self.driver.find_element(By.CSS_SELECTOR, container_selector)
                    if container:
                        self.log(f"✓ Found sidebar container: {container_selector}", "DEBUG")
                    
                        # Get all child elements with tag names
                        script = """
                        const container = arguments[0];
                        const children = container.querySelectorAll('*');
                        const tags = new Set();
                        children.forEach(el => {
                            if (el.tagName && el.tagName.toLowerCase().includes('ytd-')) {
                                tags.add(el.tagName.toLowerCase());
                            }
                        });
                        return Array.from(tags).slice(0, 20);
                        """
                        ytd_tags = self.driver.execute_script(script, container)
                    
                        if ytd_tags:
                            self.log(f"   Found ytd-* tags: {', '.join(ytd_tags)}", "DEBUG")
                    
                        # Try to find ANY video-like elements
                        potential_selectors = [
                            'a[href*="/watch?v="]',
                            'ytd-video-renderer',
                            'ytd-compact-video-renderer',
                            'ytd-rich-item-renderer',
                            '[id*="video"]',
                            '[class*="video"]'
                        ]
                    
                        for sel in potential_selectors:
                            try:
                                elements = container.find_elements(By.CSS_SELECTOR, sel)
                                if elements:
                                    self.log(f"   ✓ Selector '{sel}' found {len(elements)} elements", "DEBUG")
                            except:
                                pass
                    
                        return True
                except:
                    continue
        
            self.log("❌ Could not find any sidebar container", "DEBUG")
            return False
        
        except Exception as e:
            self.log(f"Debug sidebar structure error: {e}", "DEBUG")
            return False


    def _scroll_sidebar_into_view(self):
        """Scroll sidebar to make sure videos are loaded and visible"""
        try:
            # Find sidebar container
            sidebar_selectors = [
                '#secondary',
                '#secondary-inner',
                'ytd-watch-next-secondary-results-renderer'
            ]
        
            for selector in sidebar_selectors:
                try:
                    sidebar = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if sidebar:
                        # Scroll sidebar a bit to trigger lazy loading
                        self.driver.execute_script(
                            "arguments[0].scrollBy(0, 200);", sidebar
                        )
                        time.sleep(0.5)
                        self.log("✓ Scrolled sidebar to load videos", "DEBUG")
                        return True
                except:
                    continue
        
            self.log("⚠ Could not find sidebar to scroll", "DEBUG")
            return False
        except Exception as e:
            self.log(f"Scroll sidebar error: {e}", "DEBUG")
            return False

    
    def _is_shorts_video(self, element):
        """
        Check if video element is a Shorts video
        Args:
            element: Video element (thumbnail or title link)
        Returns:
            True if Shorts video, False otherwise
        """
        try:
            # Method 1: Check href contains '/shorts/'
            href = element.get_attribute('href')
            if href and '/shorts/' in href:
                return True
            
            # Method 2: Check parent element has shorts-specific class
            try:
                # Try to find parent ytd-reel-item-renderer (Shorts container)
                parent = element.find_element(By.XPATH, './ancestor::ytd-reel-item-renderer')
                if parent:
                    return True
            except:
                pass
            
            # Method 3: Check for aria-label containing "Shorts" (title links)
            try:
                aria_label = element.get_attribute('aria-label')
                if aria_label and 'shorts' in aria_label.lower():
                    return True
            except:
                pass
            
            # Method 4: Check for ytd-rich-grid-slim-media (Shorts grid layout)
            try:
                parent = element.find_element(By.XPATH, './ancestor::ytd-rich-grid-slim-media')
                if parent:
                    return True
            except:
                pass
            
            return False
            
        except Exception as e:
            # If error checking, assume it's not Shorts (safer to click)
            return False
    
    def _is_ad_element(self, element):
        """
        Check if element is an ad
        Args:
            element: Video element (thumbnail or title link)
        Returns:
            True if ad, False otherwise
        """
        try:
            # Method 1: Check parent has ad badge
            try:
                parent = element.find_element(By.XPATH, './ancestor::ytd-compact-video-renderer')
                if parent:
                    # Check for ad badge
                    ad_badges = parent.find_elements(By.CSS_SELECTOR, '.badge-style-type-ad, .ytp-ad-badge')
                    if ad_badges:
                        return True
                    
                    # Check for "AD" or "Sponsored" text
                    parent_text = parent.text.lower()
                    if 'ad' in parent_text or 'sponsored' in parent_text or 'quảng cáo' in parent_text:
                        return True
            except:
                pass
            
            # Method 2: Check href contains ad-related patterns
            try:
                href = element.get_attribute('href')
                if href:
                    # Ads usually have different URL patterns
                    ad_patterns = ['/aclk?', '/pagead/', 'googleadservices.com', 'doubleclick.net']
                    if any(pattern in href for pattern in ad_patterns):
                        return True
            except:
                pass
            
            # Method 3: Check for ytd-ad-slot-renderer parent (sidebar ads container)
            try:
                ad_container = element.find_element(By.XPATH, './ancestor::ytd-ad-slot-renderer')
                if ad_container:
                    return True
            except:
                pass
            
            return False
            
        except Exception as e:
            # If error checking, assume it's not ad (safer to click)
            return False


    def _click_video_smart(self, element, target_type=None):
        """
        Click video element at random position (avoid center and edges)
    
        Args:
            element: Video element to click (thumbnail/title/container)
            target_type: Type of element ('thumbnail', 'title', or None for container)
    
        Returns:
            bool: True if click successful
        """
        try:
            # Get viewport coordinates
            viewport_coords = self.get_element_viewport_coordinates(element)
            if not viewport_coords:
                self.log("Failed to get element viewport coordinates", "WARNING")
                return False
        
            # Get viewport offset
            try:
                viewport_offset_x = self.driver.execute_script(
                    "return window.screenX + (window.outerWidth - window.innerWidth) / 2;"
                )
                viewport_offset_y = self.driver.execute_script(
                    "return window.screenY + (window.outerHeight - window.innerHeight);"
                )
            
                if viewport_offset_x is None or viewport_offset_y is None:
                    self.log("Failed to get viewport offset", "WARNING")
                    return False
            except Exception as e:
                self.log(f"Viewport offset error: {e}", "WARNING")
                return False        
         
            # Calculate smart click position
            # For sidebar videos: avoid top-right corner (Watch Later/Playlist icons)
            avoid_zone = 'top-right' if self.location == 'side' else None

            click_x, click_y = self.calculate_smart_click_position(
                viewport_coords,
                viewport_offset_x,
                viewport_offset_y,
                avoid_zone=avoid_zone
            )
        
            if click_x is None or click_y is None:
                self.log("Failed to calculate click position", "WARNING")
                return False
        
            # Validate coordinates
            screen_width, screen_height = pyautogui.size()
            if not (0 <= click_x <= screen_width and 0 <= click_y <= screen_height):
                self.log(f"Invalid coords ({click_x:.0f}, {click_y:.0f}), skipping", "WARNING")
                return False
        
            # Determine log message based on target_type
            if target_type:
                target_desc = target_type
            else:
                target_desc = "container"
        
            self.log(f"Clicking {target_desc} at position ({int(click_x)}, {int(click_y)})", "INFO")
        
            # Click element
            MouseMoveAction.move_and_click_static(
                int(click_x), int(click_y),
                click_type="single_click",
                fast=False
            )
        
            time.sleep(random.uniform(0.5, 1))
            return True
        
        except Exception as e:
            self.log(f"Click video error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False

    
    def _wait_for_video_playing(self, timeout=15):
        """Wait for video to start playing"""
        try:
            self.log(f"Waiting for video to start playing (timeout: {timeout}s)...", "INFO")
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    # Check if video is playing
                    is_playing = self.driver.execute_script(
                        "return document.querySelector('video.html5-main-video') ? "
                        "!document.querySelector('video.html5-main-video').paused : false"
                    )
                    
                    if is_playing:
                        elapsed = time.time() - start_time
                        self.log(f"Video playing confirmed (waited {elapsed:.1f}s)", "SUCCESS")
                        return True
                    
                    time.sleep(0.5)
                except:
                    time.sleep(0.5)
                    continue
            
            self.log(f"Video did not start playing after {timeout}s", "WARNING")
            return False
            
        except Exception as e:
            self.log(f"Wait for video error: {e}", "ERROR")
            return False
