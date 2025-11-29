# controllers/actions/flow_auto/actions_auto/youtube_click_random_video_sidebar_auto_action.py

import time
import random
import pyautogui
from controllers.actions.mouse_move_action import MouseMoveAction
from controllers.actions.flow_auto.actions_auto.base_flow_auto_action import BaseFlowAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_random_move_scroll_auto_action import YouTubeRandomMoveScrollAutoAction
from models.global_variables import GlobalVariables

class YouTubeClickRandomVideoSidebarAutoAction(BaseFlowAutoAction):
    """
    Random scroll sidebar 1-3 times, then try to click random video in sidebar area.
    
    Logic:
    1. Random scroll sidebar 1-3 times (using YouTubeRandomMoveScrollAutoAction)
    2. Loop retry 3 times:
       - Random move mouse to sidebar area
       - Check if cursor is hand (clickable video)
       - If hand cursor → click and return success
    3. If all retries fail → return failure
    """
    
    def __init__(self, parameters, profile_id, log_prefix="[YOUTUBE AUTO]"):
        """
        Initialize action
        
        Args:
            profile_id: GoLogin profile ID
            log_prefix: Log prefix for messages
        """
        super().__init__(profile_id, log_prefix)      
        self.parameters = parameters
        
        # Get sidebar area params from GlobalVariables
        self.sidebar_x = int(parameters.get('youtube_sidebar_area_x', 0))
        self.sidebar_y = int(parameters.get('youtube_sidebar_area_y', 0))
        self.sidebar_width = int(parameters.get('youtube_sidebar_area_width', 400))
        self.sidebar_height = int(parameters.get('youtube_sidebar_area_height', 1080))
        
    def _execute_internal(self):
        """Execute the action"""
        try:
            # Step 1: Random scroll sidebar 1-3 times
            num_scrolls = random.randint(1, 3)
            self.log(f"Step 1: Random scroll sidebar {num_scrolls} times")
            
            scroll_action = YouTubeRandomMoveScrollAutoAction(
                profile_id=self.profile_id,
                num_actions=num_scrolls,
                area="sidebar",  # Use sidebar area for scroll
                log_prefix=self.log_prefix
            )
            
            scroll_success = scroll_action.execute()
            if not scroll_success:
                self.log("Scroll action failed, continuing anyway", "WARNING")
            
            # Small delay after scroll
            time.sleep(random.uniform(0.5, 1.0))
            
            # Step 2: Loop retry 3 times to find and click video
            self.log("Step 2: Try to find and click video in sidebar (max 3 retries)")
            max_retries = 3
            
            for retry in range(max_retries):
                self.log(f"Retry {retry + 1}/{max_retries}: Moving mouse to sidebar area")
                
                # Random position in sidebar area
                random_x = self.sidebar_x + random.randint(0, self.sidebar_width)
                random_y = self.sidebar_y + random.randint(0, self.sidebar_height)
                
                # Move mouse to random position in sidebar
                MouseMoveAction.move_and_click_static(
                    random_x, 
                    random_y, 
                    click_type="no_click",  # Don't click yet, just move
                    fast=False
                )
                
                self.log(f"Moved to ({random_x}, {random_y}), checking cursor...")
                
                # Wait a bit for cursor to update
                time.sleep(0.5)
                
                # Check if cursor is hand (clickable video)
                if self._is_hand_cursor():
                    self.log(f"✓ Hand cursor detected at ({random_x}, {random_y}), clicking video")
                    
                    # Click the video
                    pyautogui.click()
                    
                    self.log("✓ Successfully clicked video in sidebar")
                    
                    # Wait for video to load
                    time.sleep(random.uniform(1.5, 2.5))
                    return True
                else:
                    self.log(f"Not a clickable video at ({random_x}, {random_y}), retry...", "WARNING")
                    
                # Delay before next retry
                time.sleep(random.uniform(0.3, 0.7))
            
            # All retries failed
            self.log("✗ Failed to find clickable video after 3 retries", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"✗ Action failed with error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
