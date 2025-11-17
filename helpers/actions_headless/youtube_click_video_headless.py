# helpers/actions_headless/youtube_click_video_headless.py

"""
Click video action for headless mode

ENHANCED VERSION:
- Direct Selenium .click() (NO pyautogui)
- Random click areas (thumbnail, title, description) - AVOID channel logo
- Complete filtering (4-method shorts detection, 3-method ad detection)
- Same filtering logic as GUI version

Fast and efficient for headless background execution
"""

from helpers.actions_headless.base_youtube_action_headless import BaseYouTubeActionHeadless
from helpers.actions_headless.youtube_scroll_headless import YouTubeScrollHeadless
from selenium.webdriver.common.by import By
import random
import time
from selenium.webdriver.common.action_chains import ActionChains

class YouTubeClickVideoHeadless(BaseYouTubeActionHeadless):
    """
    Click random video using Selenium direct click (headless mode)
    
    Features:
    - Filter shorts and ads (COMPLETE - same as GUI)
    - Random video selection
    - Random click area (thumbnail, title, description)
    - Wait for video playing
    - Support main feed and sidebar
    
    Differences from GUI:
    - Direct Selenium click (no pyautogui)
    - No calculate click position
    - Simpler and faster
    """
    
    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE HEADLESS]", 
             debugger_address=None, location="main"):
        """
        Initialize click video action
    
        Args:
            driver: Selenium WebDriver
            profile_id: GoLogin profile ID
            log_prefix: Log prefix
            debugger_address: Chrome debugger address
            location: 'main' for main feed, 'side' for sidebar
        """
        super().__init__(driver, profile_id, log_prefix, debugger_address)
        self.location = location
        

    
    def execute(self):
        """Execute video click using Selenium direct click"""
        try:
            self.log("Looking for videos to click...", "INFO")
            
            # Exit fullscreen if needed
            if not self._exit_fullscreen_if_needed():
                self.log("Failed to exit fullscreen", "ERROR")
                return False
            
            # Branch based on location
            if self.location == "side":
                return self._click_sidebar_video()
            else:
                return self._click_main_feed_video()
                
        except Exception as e:
            self.log(f"Execute error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    # ========== SIDEBAR VIDEO CLICK ==========
    
    def _click_sidebar_video(self):
        """Click sidebar video"""
        try:
            self.log("Looking for sidebar videos...", "INFO")
            
            # Scroll sidebar to load videos
            self._scroll_sidebar_into_view()
            
            # Sidebar video selectors (prioritized order)
            video_selectors = [
                '#secondary a[href*="/watch?v="]:not([href*="&list="]):not([aria-label*="Short"])',
                '#related a[href*="/watch?v="]:not([href*="&list="]):not([aria-label*="Short"])',
                'ytd-compact-video-renderer',
                'ytd-video-renderer',
                '#secondary ytd-compact-video-renderer',
                'ytd-watch-next-secondary-results-renderer a[href*="/watch?v="]'
            ]
            
            # Try selectors until find valid videos
            for selector in video_selectors:
                try:
                    self.log(f"Trying selector: {selector}", "DEBUG")
                    
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if not elements:
                        continue
                    
                    # Filter valid videos
                    valid_videos = self._filter_valid_videos(elements)
                    
                    if valid_videos:
                        self.log(f"Found {len(valid_videos)} valid sidebar videos", "INFO")
                        
                        # Select random video
                        target_video = self._select_random_video(valid_videos)
                        
                        # ===== RANDOM CLICK ON CLICKABLE AREAS =====
                        if self._click_video_random_area(target_video):
                            # Wait for video playing
                            if self._wait_for_video_playing():
                                self.log("✓ Sidebar video started playing", "SUCCESS")
                                return True
                            else:
                                self.log("Video did not start playing", "WARNING")
                                return False
                                
                except Exception as e:
                    self.log(f"Selector '{selector}' error: {e}", "DEBUG")
                    continue
            
            self.log("⚠ No clickable sidebar videos found", "WARNING")
            return False
            
        except Exception as e:
            self.log(f"Click sidebar video error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    # ========== MAIN FEED VIDEO CLICK ==========
    
    def _click_main_feed_video(self):
        """Click main feed video (enhanced version)"""
        try:
            self.log("Looking for main feed videos...", "INFO")
        
            # ===== WAIT FOR PAGE TO LOAD (CRITICAL) =====
            self.log("Waiting for page to fully load...", "INFO")
            time.sleep(random.uniform(3, 5))  # ← Increase from 2s to 3-5s
        
            # ===== WAIT FOR YOUTUBE TO RENDER VIDEOS =====
            try:
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
            
                # Wait for video grid to appear
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 
                        'ytd-rich-grid-renderer, ytd-two-column-browse-results-renderer'))
                )
                self.log("✓ YouTube grid loaded", "DEBUG")
            except:
                self.log("⚠ Grid wait timeout, continuing anyway...", "WARNING")
        
            # ===== SCROLL TO LOAD MORE VIDEOS =====
            scroll_times = random.randint(2, 6)  # ← Increase from 1-4 to 2-4
            self.log(f"Scrolling {scroll_times} times to load more videos...", "INFO")
        
            scroll_action = YouTubeScrollHeadless(
                driver=self.driver,
                profile_id=self.profile_id,
                log_prefix=self.log_prefix,
                debugger_address=self.debugger_address,
                direction="down",
                times=scroll_times
            )
            scroll_action.execute()
        
            # Wait after scroll for videos to render
            time.sleep(random.uniform(1, 2))
        
            # ===== ENHANCED SELECTORS (LESS STRICT) =====
            # Try multiple selector strategies (progressive fallback)
            selector_strategies = [
                # Strategy 1: Homepage grid (most specific)
                [
                    'ytd-rich-item-renderer a#thumbnail',
                    'ytd-rich-item-renderer a#video-title-link'
                ],
                # Strategy 2: Search results list
                [
                    'ytd-video-renderer a#thumbnail',
                    'ytd-video-renderer a#video-title-link'
                ],
                # Strategy 3: Any video link (least specific, most compatible)
                [
                    'a[href*="/watch?v="]:not([href*="&list="]):not([aria-label*="Short"])',
                    'ytd-thumbnail a[href*="/watch?v="]'
                ]
            ]
        
            # ===== TRY STRATEGIES =====
            for strategy_num, video_selectors in enumerate(selector_strategies, 1):
                self.log(f"Trying strategy {strategy_num}/{len(selector_strategies)}...", "DEBUG")
            
                for selector in video_selectors:
                    try:
                        self.log(f"  Selector: {selector}", "DEBUG")
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                        if not elements:
                            self.log(f"  No elements found", "DEBUG")
                            continue
                    
                        self.log(f"  Found {len(elements)} elements, filtering...", "DEBUG")
                    
                        # Filter valid videos
                        valid_videos = self._filter_valid_videos(elements)
                    
                        if valid_videos:
                            self.log(f"✓ Found {len(valid_videos)} valid main feed videos", "INFO")
                        
                            # Select random video
                            target_video = self._select_random_video(valid_videos)
                        
                            # Click video
                            if self._click_video_random_area(target_video):
                                # Wait for video playing
                                if self._wait_for_video_playing():
                                    self.log("✓ Main feed video started playing", "SUCCESS")
                                    return True
                                else:
                                    self.log("Video did not start playing", "WARNING")
                                    return False
                
                    except Exception as e:
                        self.log(f"  Selector '{selector}' error: {e}", "DEBUG")
                        continue
        
            # ===== ALL STRATEGIES FAILED =====
            self.log("⚠ No clickable main feed videos found (all strategies failed)", "WARNING")
        
            # DEBUG: Print page source snippet
            try:
                page_source = self.driver.page_source[:500]
                self.log(f"Page source snippet: {page_source}", "DEBUG")
            except:
                pass
        
            return False
        
        except Exception as e:
            self.log(f"Click main feed video error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False


    
    # ========== HELPER METHODS ==========
    
    def _click_video_random_area(self, video_container):
        """
        Click video at random clickable area (thumbnail, title, description)
        FIXED: Always search for child areas first for randomness
        """
        try:
            # ===== STEP 1: FIND ALL CHILD CLICKABLE AREAS =====
            clickable_areas = []
        
            # Area 1: Thumbnail
            try:
                thumbnails = video_container.find_elements(By.CSS_SELECTOR, 
                    'a#thumbnail, ytd-thumbnail a, a[href*="/watch?v="]')
                for thumb in thumbnails:
                    href = thumb.get_attribute('href')
                    if href and '/watch?v=' in href and thumb.is_displayed():
                        clickable_areas.append(('thumbnail', thumb))
                        break
            except:
                pass
        
            # Area 2: Title link
            try:
                title_links = video_container.find_elements(By.CSS_SELECTOR,
                    'a#video-title-link, a#video-title, h3 a[href*="/watch?v="]')
                for title in title_links:
                    href = title.get_attribute('href')
                    if href and '/watch?v=' in href and title.is_displayed():
                        clickable_areas.append(('title', title))
                        break
            except:
                pass
        
            # Area 3: Metadata/description
            try:
                metadata_links = video_container.find_elements(By.CSS_SELECTOR,
                    '#metadata a[href*="/watch?v="], ytd-video-meta-block a[href*="/watch?v="]')
                for meta in metadata_links:
                    href = meta.get_attribute('href')
                    if href and '/watch?v=' in href and meta.is_displayed():
                        clickable_areas.append(('metadata', meta))
                        break
            except:
                pass
        
            # ===== STEP 2: FILTER OUT CHANNEL/SHORTS LINKS =====
            filtered_areas = []
            for area_name, area_element in clickable_areas:
                try:
                    href = area_element.get_attribute('href')
                
                    # Skip channel links
                    if any(pattern in href for pattern in ['/@', '/channel/', '/c/', '/user/']):
                        continue
                
                    # Skip shorts
                    if '/shorts/' in href:
                        continue
                
                    # Keep video links
                    if '/watch?v=' in href:
                        filtered_areas.append((area_name, area_element))
                except:
                    continue
        
            # ===== STEP 3: RANDOM SELECTION =====
            if filtered_areas:
                selected_area_name, selected_element = random.choice(filtered_areas)
                self.log(f"✓ Randomly selected click area: {selected_area_name}", "INFO")
            
                # Use JavaScript click to avoid intercept
                return self._click_element_selenium(selected_element)
        
            # ===== STEP 4: FALLBACK - CHECK IF CONTAINER IS LINK =====
            try:
                container_href = video_container.get_attribute('href')
                if container_href and '/watch?v=' in container_href:
                    self.log("No child areas, clicking container link (fallback)", "DEBUG")
                    return self._click_element_selenium(video_container)
            except:
                pass
        
            self.log("⚠ No clickable video elements found", "WARNING")
            return False
        
        except Exception as e:
            self.log(f"Click video random area error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False


    
    def _filter_valid_videos(self, elements):
        """
        Filter valid videos (visible, in viewport, not ads, not shorts)
        
        Args:
            elements: List of video elements
            
        Returns:
            List of valid video elements
        """
        valid_videos = []
        
        for element in elements:
            try:
                # Check visibility
                if not element.is_displayed():
                    continue               
                
                # Filter ads (COMPLETE - 3 methods)
                if self._is_ad_element(element):
                    continue
                
                # Filter shorts (COMPLETE - 4 methods)
                if self._is_shorts_video(element):
                    continue
                
                valid_videos.append(element)
                
            except:
                continue
        
        return valid_videos
    
    def _select_random_video(self, videos):
        """
        Select random video from ALL filtered videos
    
        Args:
            videos: List of valid video elements (already filtered)
        
        Returns:
            Selected video element (random choice from all)
        """
        # Simple random choice from all filtered videos
        # After scroll, we have many videos loaded → random from all
        return random.choice(videos)

    
    def _click_element_selenium(self, element):
        """
        Click element using Selenium ActionChains (HUMAN-LIKE)
    
        Creates natural mouse movement and events:
        - mouseover → mousemove → mouseenter → mousedown → mouseup → click
    
        Args:
            element: Element to click
        Returns:
            bool: True if success
        """
        try:
            # Scroll into view first
            if not self._scroll_element_into_view(element):
                self.log("Failed to scroll element into view", "WARNING")
                return False
        
            # Wait for scroll animation (human-like)
            time.sleep(random.uniform(0.3, 0.7))
        
            # ===== OPTIONAL: PRE-HOVER (70% chance) =====
            if random.random() < 0.7:
                try:
                    hover_actions = ActionChains(self.driver)
                    hover_actions.move_to_element(element)
                    hover_actions.perform()
                
                    # Human reading/thinking time
                    hover_duration = random.uniform(0.5, 1.2)
                    self.log(f"Hovering for {hover_duration:.1f}s (human behavior)...", "DEBUG")
                    time.sleep(hover_duration)
                except Exception as hover_error:
                    self.log(f"Hover error (non-critical): {hover_error}", "DEBUG")
        
            # ===== HUMAN-LIKE CLICK WITH ACTIONCHAINS =====
            self.log("Performing human-like click (ActionChains)...", "INFO")
        
            actions = ActionChains(self.driver)
        
            # Add slight random offset (humans don't click exact center)
            x_offset = random.randint(-15, 15)
            y_offset = random.randint(-15, 15)
        
            # Build action chain (creates full mouse event sequence)
            actions.move_to_element_with_offset(element, x_offset, y_offset)
            actions.pause(random.uniform(0.1, 0.3))  # Human delay before click
            actions.click()
            actions.perform()
        
            # Wait after click (human reaction time)
            time.sleep(random.uniform(0.5, 1.0))
        
            self.log("✓ Human-like click executed", "INFO")
            return True
        
        except Exception as e:
            self.log(f"ActionChains click error: {e}", "ERROR")
        
            # Fallback: Try simple click
            try:
                self.log("Fallback: Trying simple element.click()...", "DEBUG")
                element.click()
                time.sleep(random.uniform(0.5, 1.0))
                self.log("✓ Fallback click succeeded", "INFO")
                return True
            except Exception as e2:
                self.log(f"✗ Fallback click also failed: {e2}", "ERROR")
                return False

    
    def _scroll_sidebar_into_view(self):
        """Scroll sidebar to load videos"""
        try:
            sidebar_selectors = ['#secondary', '#secondary-inner', 'ytd-watch-next-secondary-results-renderer']
            
            for selector in sidebar_selectors:
                try:
                    sidebar = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if sidebar:
                        # Scroll sidebar
                        self.driver.execute_script("arguments[0].scrollBy(0, 200);", sidebar)
                        time.sleep(0.5)
                        self.log("✓ Scrolled sidebar", "DEBUG")
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            self.log(f"Scroll sidebar error: {e}", "DEBUG")
            return False
    
    def _is_shorts_video(self, element):
        """
        Check if video element is a Shorts video
        COMPLETE VERSION - 4 detection methods (copied from GUI)
        
        Args:
            element: Video element
            
        Returns:
            True if Shorts video, False otherwise
        """
        try:
            # Method 1: Check href contains '/shorts/'
            href = element.get_attribute('href')
            if href and '/shorts/' in href:
                return True
            
            # Method 2: Check parent ytd-reel-item-renderer (Shorts container)
            try:
                parent = element.find_element(By.XPATH, './ancestor::ytd-reel-item-renderer')
                if parent:
                    return True
            except:
                pass
            
            # Method 3: Check aria-label containing "Shorts"
            try:
                aria_label = element.get_attribute('aria-label')
                if aria_label and 'shorts' in aria_label.lower():
                    return True
            except:
                pass
            
            # Method 4: Check ytd-rich-grid-slim-media (Shorts grid layout)
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
        COMPLETE VERSION - 3 detection methods (copied from GUI)
        
        Args:
            element: Video element
            
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
    
    def _wait_for_video_playing(self, timeout=15):
        """Wait for video to start playing"""
        try:
            self.log(f"Waiting for video to start playing (timeout: {timeout}s)...", "INFO")
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    is_playing = self.driver.execute_script(
                        "return document.querySelector('video.html5-main-video') ? "
                        "!document.querySelector('video.html5-main-video').paused : false"
                    )
                    
                    if is_playing:
                        elapsed = time.time() - start_time
                        self.log(f"Video playing confirmed (waited {elapsed:.1f}s)", "SUCCESS")
                        return True
                        
                except:
                    pass
                
                time.sleep(0.5)
            
            self.log(f"Video did not start playing after {timeout}s", "WARNING")
            return False
            
        except Exception as e:
            self.log(f"Wait for video error: {e}", "ERROR")
            return False
