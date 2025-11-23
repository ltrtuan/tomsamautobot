# helpers/actions_headless/youtube_mouse_movement_headless.py

"""
Random mouse movement action for headless mode

HUMAN-LIKE BEHAVIOR:
- Random mouse movements across page
- Each movement has random pattern (natural/explore/random)
- Natural Bezier curve movements
- Random hover on elements
- Creates mouse event trail for bot detection avoidance

Uses Selenium ActionChains for full mouse event generation
"""

from helpers.actions_headless.base_youtube_action_headless import BaseYouTubeActionHeadless
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import random
import time
import math


class YouTubeMouseMovementHeadless(BaseYouTubeActionHeadless):
    """
    Random mouse movement using Selenium ActionChains (headless mode)
    
    Features:
    - Random pattern per movement (more human-like)
    - Natural curved paths (Bezier-like)
    - Random element hovers
    - Variable speed and patterns
    - Creates mouse event trail
    
    Anti-bot detection:
    - Generates mousemove events
    - Creates natural mouse trail
    - Random hover behaviors
    - Human-like timing
    - Pattern variation per movement
    """
    
    def __init__(self, driver, profile_id, log_prefix="[YOUTUBE HEADLESS]",
                 debugger_address=None, movements=None):
        """
        Initialize mouse movement action
        
        Args:
            driver: Selenium WebDriver
            profile_id: GoLogin profile ID
            log_prefix: Log prefix
            debugger_address: Chrome debugger address
            movements: Number of movements (None = random 3-7)
        """
        super().__init__(driver, profile_id, log_prefix, debugger_address)
        self.movements = movements
        
        # Pattern weights for random selection
        self.patterns = ["natural", "explore", "random"]
        self.weights = [0.4, 0.5, 0.1]  # 40% natural, 50% explore, 10% random
    
    def execute(self):
        """Execute random mouse movements with pattern variation"""
        try:
            # ========== STEP 1: DETERMINE MOVEMENT COUNT ==========
            if self.movements is None:
                movement_count = random.randint(1, 7)
            else:
                movement_count = self.movements
            
            self.log(f"Starting {movement_count} mouse movements (random patterns)...", "INFO")
            
            # ========== STEP 2: EXECUTE MOVEMENTS WITH RANDOM PATTERNS ==========
            success_count = 0
            
            for i in range(movement_count):
                # Select random pattern for THIS movement
                pattern = random.choices(self.patterns, weights=self.weights)[0]
                
                self.log(f"Movement {i+1}/{movement_count}: pattern={pattern}", "DEBUG")
                
                # Execute movement based on selected pattern
                if pattern == "natural":
                    success = self._natural_movement()
                elif pattern == "explore":
                    success = self._explore_elements()
                else:  # random
                    success = self._random_movement()
                
                if success:
                    success_count += 1
                    self.log(f"  ✓ Success", "DEBUG")
                else:
                    self.log(f"  ✗ Failed", "WARNING")
                
                # Random delay between movements (0.3-1.5s)
                if i < movement_count - 1:
                    delay = random.uniform(0.3, 1.5)
                    time.sleep(delay)
            
            self.log(f"✓ Completed {success_count}/{movement_count} mouse movements", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Execute error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    # ========== MOVEMENT PATTERNS ==========
    
    def _natural_movement(self):
        """
        Natural mouse movement with curved path
        Simulates human-like movement with Bezier curve
        """
        try:
            # Get viewport size
            viewport_width = self.driver.execute_script("return window.innerWidth;")
            viewport_height = self.driver.execute_script("return window.innerHeight;")
            
            # Random target position (avoid edges)
            target_x = random.randint(50, viewport_width - 50)
            target_y = random.randint(50, viewport_height - 50)
            
            # Create action chain
            actions = ActionChains(self.driver)
            
            # Move to body element first (starting point)
            body = self.driver.find_element(By.TAG_NAME, 'body')
            actions.move_to_element(body)
            
            # Move to random offset (creates curved path with multiple steps)
            steps = random.randint(3, 6)
            for step in range(steps):
                # Calculate intermediate position with curve
                progress = (step + 1) / steps
                
                # Add curve using sine wave
                curve_offset_x = int(math.sin(progress * math.pi) * random.randint(-20, 20))
                curve_offset_y = int(math.sin(progress * math.pi) * random.randint(-20, 20))
                
                step_x = int(target_x * progress) + curve_offset_x
                step_y = int(target_y * progress) + curve_offset_y
                
                # Move to intermediate position
                actions.move_by_offset(step_x // steps, step_y // steps)
                actions.pause(random.uniform(0.05, 0.15))
            
            # Execute movement
            actions.perform()
            
            return True
            
        except Exception as e:
            self.log(f"Natural movement error: {e}", "DEBUG")
            return False
    
    def _random_movement(self):
        """
        Random straight movement
        Faster but less natural than curved movement
        """
        try:
            # Get viewport size
            viewport_width = self.driver.execute_script("return window.innerWidth;")
            viewport_height = self.driver.execute_script("return window.innerHeight;")
            
            # Random movement delta
            delta_x = random.randint(-300, 300)
            delta_y = random.randint(-200, 200)
            
            # Ensure within viewport
            delta_x = max(50 - viewport_width // 2, min(delta_x, viewport_width // 2 - 50))
            delta_y = max(50 - viewport_height // 2, min(delta_y, viewport_height // 2 - 50))
            
            # Execute movement
            actions = ActionChains(self.driver)
            actions.move_by_offset(delta_x, delta_y)
            actions.perform()
            
            return True
            
        except Exception as e:
            self.log(f"Random movement error: {e}", "DEBUG")
            return False
    
    def _explore_elements(self):
        """
        Explore page by hovering over random elements
        Most human-like: actual interaction with page content
        """
        try:
            # Find hoverable elements
            hoverable_selectors = [
                'ytd-video-renderer',
                'ytd-rich-item-renderer',
                'ytd-compact-video-renderer',
                'button',
                'a[href*="/watch?v="]',
                '#thumbnail',
                'h3#video-title',
                '#channel-name',
                '#metadata'
            ]
            
            # Try to find elements
            elements = []
            for selector in hoverable_selectors:
                try:
                    found = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if found:
                        # Filter visible elements only
                        visible = [el for el in found[:5] if el.is_displayed()]
                        elements.extend(visible)
                except:
                    continue
            
            if not elements:
                self.log("No hoverable elements found, using random movement", "DEBUG")
                return self._random_movement()
            
            # Select random element
            target_element = random.choice(elements)
            
            # Move to element with slight offset
            actions = ActionChains(self.driver)
            offset_x = random.randint(-20, 20)
            offset_y = random.randint(-20, 20)
            
            actions.move_to_element_with_offset(target_element, offset_x, offset_y)
            actions.pause(random.uniform(0.3, 0.8))  # Hover duration
            actions.perform()
            
            return True
            
        except Exception as e:
            self.log(f"Explore elements error: {e}", "DEBUG")
            return self._random_movement()  # Fallback
    
    # ========== HELPER METHODS ==========
    
    def _get_viewport_size(self):
        """Get current viewport size"""
        try:
            width = self.driver.execute_script("return window.innerWidth;")
            height = self.driver.execute_script("return window.innerHeight;")
            return (width, height)
        except:
            return (1280, 720)  # Default size
