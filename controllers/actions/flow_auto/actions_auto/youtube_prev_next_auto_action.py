# controllers/actions/flow_auto/actions_auto/youtube_prev_next_auto_action.py
import time
import random
import pyautogui
from controllers.actions.flow_auto.actions_auto.base_flow_auto_action import BaseFlowAutoAction

class YouTubePrevNextAutoAction(BaseFlowAutoAction):
    """
    Random navigation: 70% next (skip forward 'L'), 30% prev (rewind 'J'), random 4-8 loops total.
    """
    
    def __init__(self, profile_id, log_prefix="[YOUTUBE AUTO]"):
        """
        Initialize prev/next navigation action
        
        Args:
            profile_id: GoLogin profile ID
            log_prefix: Log prefix
        """
        super().__init__(profile_id, log_prefix)
    
    def _execute_internal(self):
        """
        Execute random prev/next navigation action
        """
        try:
            # Random total loops between 4 and 8
            loop_times = random.randint(2, 6)
            self.log(f"Starting {loop_times} random navigation presses (70% next, 30% prev)")
            
            next_count = 0
            prev_count = 0
            
            for i in range(loop_times):
                # Small random delay before each press (0.5-1.5s)
                delay = random.uniform(0.5, 2)
                time.sleep(delay)
                
                # Random choice: 70% next ('L' skip forward), 30% prev ('J' rewind)
                if random.random() < 0.6:  # 70% probability
                    pyautogui.press('l')
                    self.log(f"Pressed 'L' (skip forward/next) - iteration {i+1}/{loop_times}")
                    next_count += 1
                else:  # 30% probability
                    pyautogui.press('j')
                    self.log(f"Pressed 'J' (rewind/prev) - iteration {i+1}/{loop_times}")
                    prev_count += 1
            
            # Wait after last press
            time.sleep(random.uniform(0.5, 1.0))
            self.log(f"✓ Navigation completed: {next_count} next, {prev_count} prev out of {loop_times} loops")
            
            return True
            
        except Exception as e:
            self.log(f"✗ Navigation error: {e}", "ERROR")
            return False
