# controllers/actions/flow_auto/actions_auto/youtube_skip_ads_auto_action.py

import time
import random
import pyautogui
import win32gui
from controllers.actions.flow_auto.actions_auto.youtube_mouse_move_auto_action import YouTubeMouseMoveAutoAction
from controllers.actions.flow_auto.actions_auto.base_flow_auto_action import BaseFlowAutoAction
from controllers.actions.mouse_move_action import MouseMoveAction

class YouTubeSkipAdsAutoAction(BaseFlowAutoAction):
    """
    Skip YouTube ads with 2 strategies:
    - 30% Case 1: Click Ads Area → Open new tab → Interact → Close tab → Skip ads
    - 70% Case 2: Direct skip ads in Skip Ads Area
    """
    
    def __init__(self, profile_id, keywords, log_prefix="[YOUTUBE AUTO]"):
        """
        Initialize skip ads action
        
        Args:
            profile_id: GoLogin profile ID
            keywords: Dict containing ads area and skip ads area params
            log_prefix: Log prefix
        """
        super().__init__(profile_id, log_prefix)
        self.profile_id = profile_id
        # Extract Ads Area params (for clicking ads - Case 1)
        ads_area_x = int(keywords.get('youtube_ads_area_x', 0))
        ads_area_y = int(keywords.get('youtube_ads_area_y', 0))
        ads_area_width = int(keywords.get('youtube_ads_area_width', 300))
        ads_area_height = int(keywords.get('youtube_ads_area_height', 150))
        
        self.ads_region = None
        if ads_area_width > 0 and ads_area_height > 0:
            self.ads_region = (ads_area_x, ads_area_y, ads_area_width, ads_area_height)
        
        # Extract Skip Ads Area params (for skip button - Case 2)
        skip_ads_x = int(keywords.get('youtube_skip_ads_area_x', 0))
        skip_ads_y = int(keywords.get('youtube_skip_ads_area_y', 0))
        skip_ads_width = int(keywords.get('youtube_skip_ads_area_width', 200))
        skip_ads_height = int(keywords.get('youtube_skip_ads_area_height', 100))
        
        self.skip_ads_region = None
        if skip_ads_width > 0 and skip_ads_height > 0:
            self.skip_ads_region = (skip_ads_x, skip_ads_y, skip_ads_width, skip_ads_height)
        
        self.log(f"Ads region: {self.ads_region}, Skip Ads region: {self.skip_ads_region}")
    
    def execute(self):
        """Execute skip ads with random strategy"""
        try:
            self.log("Checking for ads")
            time.sleep(6)  # Wait for skip button to appear
            
            # Random strategy selection: 30% Case 1, 70% Case 2
            if random.random() < 0.3:
                self.log("Selected CASE 1: Click ads → Interact → Skip")
                return self._case1_click_ads_then_skip()
            else:
                self.log("Selected CASE 2: Direct skip ads")
                return self._case2_direct_skip()
            
        except Exception as e:
            self.log(f"Skip ads error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return True  # Not critical
    
    def _case1_click_ads_then_skip(self):
        """Case 1: Click ads area → Open new tab → Interact → Close → Skip"""
        try:
            # Step 1: Try to click ads
            if not self._click_ads_area():
                self.log("No clickable ads found, falling back to direct skip")
                return self._case2_direct_skip()
            
            # Step 2: Wait and check if new tab opened (by checking window title)
            time.sleep(2)
            
            if not self._check_new_tab_opened():
                self.log("No new tab opened, falling back to direct skip")
                return self._case2_direct_skip()
            
            self.log("✓ New tab opened, interacting...")
            
            # Step 3: Interact with new tab (random actions)
            self._interact_with_new_tab()
            
            # Step 4: Close new tab
            self._close_new_tab()
            
            # Step 5: Return to YouTube tab
            self._return_to_youtube_tab()
            
            # Step 6: Resume YouTube video
            self._resume_youtube_video()
            
            # Step 7: Skip ads (retry 3 times)
            return self._try_skip_ads_once()
            
        except Exception as e:
            self.log(f"Case 1 error: {e}", "ERROR")
            return True
    
    def _case2_direct_skip(self):
        """Case 2: Direct skip ads in Skip Ads Area"""
        skip_ads = self._try_skip_ads_once()
        if skip_ads:
            return skip_ads
        YouTubeMouseMoveAutoAction(profile_id=self.profile_id, click=False, log_prefix=self.log_prefix)
        time.sleep(random.uniform(5, 7))
        return self._try_skip_ads_once()    
    
    
    def _try_skip_ads_once(self):
        """Try to find and click skip button once"""
        if self.skip_ads_region:
            # Use defined skip ads area
            region_x, region_y, region_width, region_height = self.skip_ads_region
          
            random_x = region_x + random.randint(0, region_width)
            random_y = region_y + random.randint(0, region_height)
            MouseMoveAction.move_and_click_static(
                    random_x, random_y,
                    click_type=None,
                    fast=False
            )
            
            time.sleep(0.2)
                
            if self._is_hand_cursor():
                click_delay = random.uniform(0.5, 1)
                time.sleep(click_delay)
                pyautogui.click()
                self.log(f"✓ Clicked skip button at ({random_x}, {random_y})")
                time.sleep(1)
                return True
            
        return False


    def _click_ads_area(self):
        """Click random position in ads area if hand cursor found"""
        if not self.ads_region:
            self.log("No ads region defined")
            return False
        
        region_x, region_y, region_width, region_height = self.ads_region
        max_attempts = 5
        
        for attempt in range(1, max_attempts + 1):
            random_x = region_x + random.randint(0, region_width)
            random_y = region_y + random.randint(0, region_height)
            
            self.log(f"Ads click attempt {attempt}/{max_attempts}: ({random_x}, {random_y})")
            MouseMoveAction.move_and_click_static(
                    random_x, random_y,
                    click_type=None,
                    fast=False
            )
          
            time.sleep(0.2)
            
            if self._is_hand_cursor():
                click_delay = random.uniform(0.5, 1.5)
                self.log(f"✓ Found clickable ads, waiting {click_delay:.1f}s")
                time.sleep(click_delay)
                pyautogui.click()
                self.log("✓ Clicked ads")
                return True
        
        return False
    
    def _check_new_tab_opened(self):
        """
        Check if new tab opened by checking window title
        If title doesn't contain "YouTube", we're in new tab (ads page)
        
        Returns:
            bool: True if new tab opened (not on YouTube), False if still on YouTube
        """
        try:
            # Get foreground window title
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            
            self.log(f"Current window title: '{window_title}'")
            
            # Check if "YouTube" in title (case-insensitive)
            is_youtube = "youtube" in window_title.lower()
            
            if is_youtube:
                self.log("Still on YouTube tab (no new tab opened)")
                return False
            else:
                self.log("✓ New tab detected (not YouTube)")
                return True
                
        except Exception as e:
            self.log(f"Error checking window title: {e}", "WARNING")
            # Fallback: assume new tab opened
            return True
    
    def _interact_with_new_tab(self):
        """Random interactions in new tab: mouse move, fullscreen, scroll"""
        num_actions = random.randint(1, 3)
        self.log(f"Performing {num_actions} random actions in new tab")
        
        for i in range(num_actions):
            action = random.choice(['mouse_move', 'scroll'])
            
            if action == 'mouse_move':
                screen_width, screen_height = pyautogui.size()
                rand_x = random.randint(100, screen_width - 100)
                rand_y = random.randint(100, screen_height - 100)
                MouseMoveAction.move_and_click_static(
                        rand_x, rand_y,
                        click_type="single_click",
                        fast=False
                )               
                self.log(f"Action {i+1}: Mouse move to ({rand_x}, {rand_y})")
            
            elif action == 'scroll':
                scroll_clicks = random.randint(-900, -500)
                pyautogui.scroll(scroll_clicks)
                self.log(f"Action {i+1}: Scroll {abs(scroll_clicks)} clicks")
            
            time.sleep(random.uniform(0.5, 1.5))
    
    def _close_new_tab(self):
        """Close current tab (Ctrl+W)"""
        self.log("Closing new tab (Ctrl+W)")
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(1)
    
    def _return_to_youtube_tab(self):
        """
        Return to YouTube tab after closing ads tab
        Try Ctrl+Tab or Ctrl+Shift+Tab to switch to YouTube tab
        """
        try:
            self.log("Switching back to YouTube tab")
            
            # Method 1: Try Ctrl+Shift+Tab (previous tab)
            pyautogui.hotkey('ctrl', 'shift', 'tab')
            time.sleep(0.5)
            
            # Check if we're on YouTube now
            if self._is_on_youtube_tab():
                self.log("✓ Returned to YouTube tab")
                return True
            
            # Method 2: Try Ctrl+Tab multiple times
            for i in range(3):
                pyautogui.hotkey('ctrl', 'tab')
                time.sleep(0.5)
                
                if self._is_on_youtube_tab():
                    self.log("✓ Returned to YouTube tab")
                    return True
            
            self.log("Could not confirm YouTube tab, proceeding anyway", "WARNING")
            return True
            
        except Exception as e:
            self.log(f"Error returning to YouTube tab: {e}", "WARNING")
            return True
    
    def _is_on_youtube_tab(self):
        """
        Check if current tab is YouTube
        
        Returns:
            bool: True if on YouTube tab
        """
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            return "youtube" in window_title.lower()
        except:
            return False
    
    def _resume_youtube_video(self):
        """Resume YouTube video (press Space)"""
        self.log("Resuming YouTube video (Space)")
        time.sleep(1)
        pyautogui.press('space')
        time.sleep(0.5)