# controllers/actions/flow_auto/actions_auto/youtube_skip_ads_auto_action.py

import time
import random
import pyautogui
import win32gui
from controllers.actions.flow_auto.actions_auto.youtube_mouse_move_auto_action import YouTubeMouseMoveAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_random_move_scroll_auto_action import YouTubeRandomMoveScrollAutoAction
from controllers.actions.flow_auto.actions_auto.base_flow_auto_action import BaseFlowAutoAction
from controllers.actions.mouse_move_action import MouseMoveAction
from helpers.app_helpers import is_hand_cursor
from models.global_variables import GlobalVariables

class YouTubeSkipAdsAutoAction(BaseFlowAutoAction):
    """
    Skip YouTube ads with new strategy:
    1. Hover mouse vào ADS area
    2. If cursor = hand:
       - 30% → Click ads (Case 1: Open tab → Interact → Close → Skip)
       - 70% → Move to Skip Ads area → Check hand → Click (Case 2)
    3. If cursor NOT hand → Try skip directly
    """
    
    def __init__(self, profile_id, parameters, log_prefix="[YOUTUBE AUTO]"):
        """
        Initialize skip ads action
        
        Args:
            profile_id: GoLogin profile ID
            parameters: Full parameters dict containing:
                - youtube_ads_area_x/y/width/height: Ads area coords
                - youtube_skip_ads_area_x/y/width/height: Skip ads area coords
            log_prefix: Log prefix
        """
        super().__init__(profile_id, log_prefix)
        self.profile_id = profile_id
        
        # ========== EXTRACT ADS AREA PARAMS (for clicking ads - Case 1) ==========
        ads_area_x = int(parameters.get('youtube_ads_area_x', 0))
        ads_area_y = int(parameters.get('youtube_ads_area_y', 0))
        ads_area_width = int(parameters.get('youtube_ads_area_width', 300))
        ads_area_height = int(parameters.get('youtube_ads_area_height', 150))
        
        self.ads_region = None
        if ads_area_width > 0 and ads_area_height > 0:
            self.ads_region = (ads_area_x, ads_area_y, ads_area_width, ads_area_height)
        
        # ========== EXTRACT SKIP ADS AREA PARAMS (for skip button - Case 2) ==========
        skip_ads_x = int(parameters.get('youtube_skip_ads_area_x', 0))
        skip_ads_y = int(parameters.get('youtube_skip_ads_area_y', 0))
        skip_ads_width = int(parameters.get('youtube_skip_ads_area_width', 200))
        skip_ads_height = int(parameters.get('youtube_skip_ads_area_height', 100))
        
        self.skip_ads_region = None
        if skip_ads_width > 0 and skip_ads_height > 0:
            self.skip_ads_region = (skip_ads_x, skip_ads_y, skip_ads_width, skip_ads_height)
        
        self.log(f"Ads region: {self.ads_region}, Skip Ads region: {self.skip_ads_region}")
    
    def _execute_internal(self):
        """Execute skip ads with new hover-first strategy"""
        # Logic : if click ads -> Ads (maybe) show one time. But if skip ads or miss skip ads , Ads maybe show 2 times
        try:
            self.log("Checking for ads")
            time.sleep(6)  # Wait for skip button to appear
            GlobalVariables().set(f'click_ads_{self.profile_id}', False)
            # ========== NEW STRATEGY: HOVER ADS AREA FIRST ==========
            
            # Cursor = hand → Random select Case 1 (30%) or Case 2 (70%)
            if random.random() < 0.3:
                # Step 1: Hover mouse vào ADS area
                ads_hand_cursor = self._hover_and_check_ads_area()            
                if ads_hand_cursor:
                    self.log("Selected CASE 1: Click ads → Interact → Skip (30%)")
                    self._case1_click_ads_then_skip()
                    
            already_click_ads = GlobalVariables().get(f'click_ads_{self.profile_id}', False)
            if not already_click_ads:
                self._case2_hover_skip_ads_then_click()
                time.sleep(random.uniform(5, 7))
                
            return self._case2_hover_skip_ads_then_click()
            
            
        except Exception as e:
            self.log(f"Skip ads error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return True  # Not critical
    
    def _hover_and_check_ads_area(self):
        """
        Hover mouse vào ADS area và check cursor
        
        Returns:
            bool: True if cursor = hand (clickable), False otherwise
        """
        if not self.ads_region:
            self.log("No ads region defined")
            return False
        
        region_x, region_y, region_width, region_height = self.ads_region
        
        # Random position in ads area
        random_x = region_x + random.randint(0, region_width)
        random_y = region_y + random.randint(0, region_height)
        
        self.log(f"Hovering ads area at ({random_x}, {random_y})")
        
        # Move mouse (NO CLICK)
        MouseMoveAction.move_and_click_static(
            random_x, random_y,
            click_type=None,  # No click, just hover
            fast=False
        )
        
        time.sleep(0.2)  # Wait for cursor to update
        
        # Check if cursor = hand
        is_hand = is_hand_cursor()
        
        if is_hand:
            self.log("✓ Cursor = HAND (ads clickable)")
        else:
            self.log("Cursor NOT hand (no clickable ads)")
        
        return is_hand
    
    def _case1_click_ads_then_skip(self):
        """Case 1 (30%): Click ads → Open tab → Interact → Close → Skip"""
        try:
            # Step 1: Click ads (mouse already hovering from _hover_and_check_ads_area)
            click_delay = random.uniform(0.5, 1.5)
            self.log(f"Clicking ads (delay {click_delay:.1f}s)")
            time.sleep(click_delay)
            pyautogui.click()
            self.log("✓ Clicked ads")
            GlobalVariables().set(f'click_ads_{self.profile_id}', True)
            # Step 2: Wait and check if new tab opened
            time.sleep(2)
            
            if not self._check_new_tab_opened():
                self.log("No new tab opened, falling back to direct skip")
                return self._try_skip_ads_once()
            
            self.log("✓ New tab opened, interacting...")
            
            # Step 3: Interact with new tab
            self._interact_with_new_tab()
            
            # Step 4: Close new tab
            self._close_new_tab()
            
            # Step 5: Return to YouTube tab
            self._return_to_youtube_tab()
            
            # Step 6: Resume YouTube video
            self._resume_youtube_video()
            
            # Step 7: Skip ads
            return self._try_skip_ads_once()
            
        except Exception as e:
            self.log(f"Case 1 error: {e}", "ERROR")
            return True
    
    def _case2_hover_skip_ads_then_click(self):
        """Case 2 (70%): Move to Skip Ads area → Check hand → Click"""
        try:
            # Reuse _try_skip_ads_once() (same logic: hover + check hand + click)
            if self._try_skip_ads_once():
                time.sleep(2)
                #Case : click on Logo Channel on the right bottom of the video
                if self._check_new_tab_opened():
                    # Step 4: Close new tab
                    self._close_new_tab()
            
                    # Step 5: Return to YouTube tab
                    self._return_to_youtube_tab()
            
                    # Step 6: Resume YouTube video
                    self._resume_youtube_video()
                
                return True      
            
            return False
                
        except Exception as e:
            self.log(f"Case 2 error: {e}", "ERROR")
            return True

    
    def _try_skip_ads_once(self):
        """Try to find and click skip button once (with hand cursor check)"""
        if self.skip_ads_region:
            region_x, region_y, region_width, region_height = self.skip_ads_region
            for attempt in range(1, 2):
                random_x = region_x + random.randint(0, region_width)
                random_y = region_y + random.randint(0, region_height)
            
                MouseMoveAction.move_and_click_static(
                    random_x, random_y,
                    click_type=None,
                    fast=False
                )
            
                time.sleep(1)
                
                if is_hand_cursor():
                    click_delay = random.uniform(0.5, 0.7)
                    time.sleep(click_delay)
                    pyautogui.click()
                    self.log(f"✓ Clicked skip button at ({random_x}, {random_y})")
                    time.sleep(1)
                    return True
            
        return False
    
    def _check_new_tab_opened(self):
        """
        Check if new tab opened by checking window title
        
        Returns:
            bool: True if new tab opened (not on YouTube)
        """
        try:
            # hwnd = win32gui.GetForegroundWindow()
            # window_title = win32gui.GetWindowText(hwnd)
            # is_youtube = "youtube" in window_title.lower()
            current_url = self._get_current_url()
            is_youtube = "youtube.com/watch" in current_url.lower()
            
            if is_youtube:
                self.log("Still on YouTube tab (no new tab opened)")
                return False
            else:
                self.log("✓ New tab detected (not YouTube)")
                return True
                
        except Exception as e:
            self.log(f"Error checking window title: {e}", "WARNING")
            return True
    
    def _interact_with_new_tab(self):
        """Random interactions in new tab: mouse move, scroll"""
        time.sleep(random.uniform(1.5, 2.5))
        num_actions = random.randint(2, 4)
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
                YouTubeRandomMoveScrollAutoAction(self.profile_id, 1, "main", self.log_prefix).execute()
            
            time.sleep(random.uniform(0.5, 1.5))
    
    def _close_new_tab(self):
        """Close current tab (Ctrl+W)"""
        self.log("Closing new tab (Ctrl+W)")
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(1)
    
    def _return_to_youtube_tab(self):
        """Return to YouTube tab after closing ads tab"""
        try:
            self.log("Switching back to YouTube tab")
            
            # Method 1: Try Ctrl+Shift+Tab (previous tab)
            pyautogui.hotkey('ctrl', 'shift', 'tab')
            time.sleep(0.5)
            
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
        """Check if current tab is YouTube"""
        try:
            # hwnd = win32gui.GetForegroundWindow()
            # window_title = win32gui.GetWindowText(hwnd)
            current_url = self._get_current_url()
            is_youtube = "youtube.com/watch" in current_url.lower()
            return is_youtube
        except:
            return False
    
    def _resume_youtube_video(self):
        """Resume YouTube video (press Space)"""
        self.log("Resuming YouTube video (Space)")
        time.sleep(1)
        pyautogui.press('space')
        time.sleep(0.5)
