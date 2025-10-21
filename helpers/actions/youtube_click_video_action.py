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
            # Select selectors based on location
            if self.location == 'side':
                self.log("Looking for sidebar videos to click...", "INFO")
                # Sidebar video selectors (when watching a video)
                video_selectors = {
                    'thumbnail': [
                        'ytd-watch-next-secondary-results-renderer ytd-compact-video-renderer a#thumbnail',
                        '#related ytd-compact-video-renderer a#thumbnail',
                        '#secondary ytd-compact-video-renderer a#thumbnail',
                    ],
                    'title': [
                        'ytd-watch-next-secondary-results-renderer ytd-compact-video-renderer a#video-title',
                        '#related ytd-compact-video-renderer a#video-title',
                        '#secondary ytd-compact-video-renderer a#video-title',
                    ]
                }

            else:
                self.log("Looking for main videos to click...", "INFO")
                # Main page video selectors
                video_selectors = {
                    'thumbnail': [
                        'ytd-thumbnail a#thumbnail',
                        'ytd-video-renderer a#thumbnail',
                        'ytd-grid-video-renderer a#thumbnail',
                    ],
                    'title': [
                        'a#video-title.ytd-video-renderer',
                        'ytd-video-renderer a#video-title',
                        'ytd-grid-video-renderer a#video-title',
                    ]
                }
            
            # Random choose: 50% thumbnail, 50% title
            click_target = random.choice(['thumbnail', 'title'])
            self.log(f"Target type: {click_target}", "INFO")
            
            # Try to find and click target
            for selector in video_selectors[click_target]:
                try:
                    video_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    visible_videos = [v for v in video_elements if v.is_displayed()]
                    
                    # ========== FILTER OUT SHORTS VIDEOS ==========
                    non_shorts_videos = []
                    for video in visible_videos:
                        # Check if in viewport FIRST
                        if not self.is_element_in_viewport(video):
                            continue  # Skip if not in viewport
                        
                        # Filter out ads
                        if self._is_ad_element(video):
                            self.log(f"• Filtered out Ad", "DEBUG")
                            continue
                        
                        if not self._is_shorts_video(video):
                            non_shorts_videos.append(video)
                        else:
                            self.log(f"Filtered out Shorts video", "DEBUG")
                    
                    if non_shorts_videos:
                        # Select random video from range (excluding shorts)
                        max_index = min(len(non_shorts_videos), self.video_index_range[1])
                        min_index = self.video_index_range[0]
                        
                        if max_index >= min_index:
                            available_videos = non_shorts_videos[min_index-1:max_index]
                            target_video = random.choice(available_videos)
                            
                            # Click video with random position (avoid center and edges)
                            success = self._click_video_smart(target_video, click_target)
                            
                            if success:
                                # Wait for video to start playing
                                if self._wait_for_video_playing():
                                    self.log("Video started playing", "SUCCESS")
                                    return True
                                else:
                                    self.log("Video did not start playing (timeout)", "WARNING")
                                    return False
                            
                except Exception as e:
                    self.log(f"Error with selector {selector}: {e}", "WARNING")
                    continue
            
            self.log("No clickable videos found", "WARNING")
            return False
            
        except Exception as e:
            self.log(f"Video click error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
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


    def _click_video_smart(self, element, target_type):
        """
        Click video with smart position (avoid center and edges)
        Args:
            element: Video element to click
            target_type: 'thumbnail' or 'title'
        Returns:
            True if click succeeded, False otherwise
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
            
            # Calculate random click position (avoid center and edges)
            click_x, click_y = self.calculate_smart_click_position(
                viewport_coords, 
                viewport_offset_x, 
                viewport_offset_y
            )
            
            if click_x is None or click_y is None:
                self.log("Failed to calculate click position", "WARNING")
                return False
            
            # Validate coordinates
            screen_width, screen_height = pyautogui.size()
            if not (0 <= click_x <= screen_width and 0 <= click_y <= screen_height):
                self.log(f"Invalid coords ({click_x:.0f}, {click_y:.0f}), skipping", "WARNING")
                return False
            
            # Click video
            self.log(f"Clicking {target_type} at position ({int(click_x)}, {int(click_y)})", "INFO")
            MouseMoveAction.move_and_click_static(
                int(click_x), int(click_y),
                click_type="single_click",
                fast=False
            )
            
            time.sleep(random.uniform(0.5, 1))
            return True
            
        except Exception as e:
            self.log(f"Click video error: {e}", "ERROR")
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
