# helpers/flow_youtube_headless.py

"""
YouTube Flow for Headless Mode

SIMPLIFIED VERSION:
- No ActionChainManager (no lock, no round-robin)
- No bring_profile_to_front
- Direct chain execution (parallel safe)
- Uses headless actions (Selenium/JS only, no pyautogui)

Designed for parallel execution in headless mode
"""

import time
import random
from selenium.webdriver.common.by import By

# Import headless actions
from helpers.actions_headless.youtube_search_headless import YouTubeSearchHeadless
from helpers.actions_headless.youtube_click_video_headless import YouTubeClickVideoHeadless
from helpers.actions_headless.youtube_skip_ads_headless import YouTubeSkipAdsHeadless
from helpers.actions_headless.youtube_scroll_headless import YouTubeScrollHeadless
from helpers.actions_headless.youtube_seek_video_headless import YouTubeSeekVideoHeadless
from helpers.actions_headless.youtube_pause_resume_headless import YouTubePauseResumeHeadless
from helpers.actions_headless.youtube_dismiss_premium_headless import YouTubeDismissPremiumHeadless
from helpers.actions_headless.youtube_mouse_movement_headless import YouTubeMouseMovementHeadless

# Import GUI navigate action (no pyautogui, can reuse)
from helpers.actions.youtube_navigate_action import YouTubeNavigateAction

# Import helper
from helpers.gologin_profile_helper import GoLoginProfileHelper


class YouTubeFlowIteratorHeadless:
    """
    YouTube Flow Iterator for Headless Mode
    
    Key differences from GUI flow:
    - No ActionChainManager (direct execution)
    - No physical lock (parallel safe)
    - No bring_to_front
    - Uses headless actions
    
    Workflow:
    1. __init__: Build chain queue
    2. has_next_chain(): Check remaining chains
    3. execute_next_chain(): Execute chain directly (NO LOCK)
    """
    
    def __init__(self, driver, keywords, profile_id, debugger_address, log_prefix="[YOUTUBE HEADLESS]"):
        """
        Initialize headless flow iterator
        
        Args:
            driver: Selenium WebDriver
            keywords: Keywords dict
            profile_id: Profile ID
            debugger_address: Chrome debugger address
            log_prefix: Log prefix
        """
        self.driver = driver
        self.keywords = keywords
        self.profile_id = profile_id
        self.debugger_address = debugger_address
        self.log_prefix = log_prefix
        
        # Build chain queue
        self.chains = self._build_chain_queue()
        self.current_chain_index = 0
        
        print(f"{log_prefix} [{profile_id}] ✓ Headless flow iterator initialized with {len(self.chains)} chains")
    
    def _build_chain_queue(self):
        """
        Build chain queue for headless execution
        
        Returns:
            list: List of chain dicts
        """
        chains = []
        
        chains.append({
            'name': 'navigate_youtube',
            'function': YouTubeFlowHeadless._navigate_youtube,
            'args': (self.driver, self.keywords, self.profile_id, self.debugger_address, self.log_prefix)
        })
        choice = random.choice([1, 2])
        if choice == 1:
            # Chain 1: Search and start video
            chains.append({
                'name': 'search_and_start_video',
                'function': YouTubeFlowHeadless._search_and_start_video_chain,
                'args': (self.driver, self.keywords, self.profile_id, self.debugger_address, self.log_prefix)
            })
        else:
            chains.append({
                'name': 'random_click_video_home_chain',
                'function': YouTubeFlowHeadless._random_click_video_home_chain,
                'args': (self.driver, self.keywords, self.profile_id, self.debugger_address, self.log_prefix)
            })    
        
        
        # Chains 2-N: Random interaction cycles (mỗi cycle là 1 chain)
        # Random 3-6 interaction cycles
        # num_interaction_cycles = random.randint(3, 6)
        # print(f"{self.log_prefix} [{self.profile_id}] Planning {num_interaction_cycles} interaction cycles")
        choice_cycle = random.choice([1, 2, 3, 4, 5 , 6])
        for cycle_num in range(1, 5):
            chains.append({
                'name': f'first_interaction_cycle_{cycle_num}',
                'function': YouTubeFlowHeadless._video_interaction_chain,
                'args': (self.driver, self.keywords, self.profile_id, self.debugger_address, self.log_prefix)
            })
            if choice_cycle == 1:
                chains.append({
                    'name': f'random_click_video_sidebar_chain_{cycle_num}',
                    'function': YouTubeFlowHeadless._random_click_video_sidebar_chain,
                    'args': (self.driver, self.keywords, self.profile_id, self.debugger_address, self.log_prefix)
                })
            elif choice_cycle == 2:
                chains.append({
                    'name': f'search_and_start_video_{cycle_num}',
                    'function': YouTubeFlowHeadless._search_and_start_video_chain,
                    'args': (self.driver, self.keywords, self.profile_id, self.debugger_address, self.log_prefix)
                })
            elif choice_cycle == 3:
                chains.append({
                    'name': f'random_click_video_home_chain_{cycle_num}',
                    'function': YouTubeFlowHeadless._random_click_video_home_chain,
                    'args': (self.driver, self.keywords, self.profile_id, self.debugger_address, self.log_prefix)
                })
            else:
                chains.append({
                    'name': f'interaction_cycle_{cycle_num}',
                    'function': YouTubeFlowHeadless._video_interaction_chain,
                    'args': (self.driver, self.keywords, self.profile_id, self.debugger_address, self.log_prefix)
                })
        # Chain 2: Video interaction
        # chains.append({
        #     'name': 'interaction_cycle',
        #     'function': YouTubeFlowHeadless._video_interaction_chain,
        #     'args': (self.driver, self.keywords, self.profile_id, self.debugger_address, self.log_prefix)
        # })
        
        return chains
    
    def has_next_chain(self):
        """Check if there are remaining chains"""
        return self.current_chain_index < len(self.chains)
    
    def execute_next_chain(self):
        """
        Execute next chain WITHOUT ActionChainManager (direct execution)
        
        Returns:
            bool: True if success
        """
        if not self.has_next_chain():
            print(f"{self.log_prefix} [{self.profile_id}] ⚠ No more chains to execute")
            return False
        
        # Get current chain
        chain_info = self.chains[self.current_chain_index]
        chain_name = chain_info['name']
        chain_function = chain_info['function']
        chain_args = chain_info['args']
        
        print(f"{self.log_prefix} [{self.profile_id}] ========================================")
        print(f"{self.log_prefix} [{self.profile_id}] Executing chain {self.current_chain_index + 1}/{len(self.chains)}: {chain_name}")
        print(f"{self.log_prefix} [{self.profile_id}] ========================================")
        
        # ===== DIRECT EXECUTION (NO ActionChainManager, NO LOCK) =====
        try:
            result = chain_function(*chain_args)
        except Exception as e:
            print(f"{self.log_prefix} [{self.profile_id}] ✗ Chain execution error: {e}")
            import traceback
            traceback.print_exc()
            result = False
        
        # Increment index
        self.current_chain_index += 1
        
        if result:
            print(f"{self.log_prefix} [{self.profile_id}] ✓ Chain '{chain_name}' completed successfully")
        else:
            print(f"{self.log_prefix} [{self.profile_id}] ✗ Chain '{chain_name}' failed")
        
        return result
    
    def get_progress(self):
        """Get execution progress"""
        return {
            'current': self.current_chain_index,
            'total': len(self.chains),
            'percentage': (self.current_chain_index / len(self.chains) * 100) if len(self.chains) > 0 else 0
        }


class YouTubeFlowHeadless:
    """
    YouTube Flow Orchestrator for Headless Mode
    
    Static methods for chain execution without locks
    """
    
    @staticmethod
    def create_flow_iterator(driver, keywords, profile_id, debugger_address, log_prefix="[YOUTUBE HEADLESS]"):
        """
        Factory method to create headless flow iterator
        
        Returns:
            YouTubeFlowIteratorHeadless: Flow iterator instance
        """
        return YouTubeFlowIteratorHeadless(driver, keywords, profile_id, debugger_address, log_prefix)

    # ========== CHAIN METHODS (STATIC) ==========
    @staticmethod
    def _navigate_youtube(driver, keywords, profile_id, debugger_address, log_prefix):
        """
        Chain 1: Navigate → Search → Click video → Skip ads
        
        Returns:
            bool: True if success
        """
        try:
            print(f"{log_prefix} [{profile_id}] ========== Chain 1: Search and Start Video ==========")
            
            # ===== ACTION 1: NAVIGATE TO YOUTUBE =====
            print(f"{log_prefix} [{profile_id}] Action 1/4: Navigate to YouTube...")
            navigate_action = YouTubeNavigateAction(
                driver=driver,
                profile_id=profile_id,
                log_prefix=log_prefix,
                debugger_address=debugger_address,
                url="https://www.youtube.com"
            )
            
            if not navigate_action.execute():
                print(f"{log_prefix} [{profile_id}] ✗ Failed to navigate to YouTube")
                return False
            
            # GoLoginProfileHelper.capture_page_screenshot(
            #     driver=driver,
            #     collect_file_path= keywords.get('youtube_image_search_path', ""),
            #     profile_id=profile_id
            # )
            # Wait after navigation
            time.sleep(random.uniform(1, 3))
          
            
            print(f"{log_prefix} [{profile_id}] ✓ Chain 1 completed successfully")
            return True
            
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ✗ Chain 1 error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    
    @staticmethod
    def _search_and_start_video_chain(driver, keywords, profile_id, debugger_address, log_prefix):
        """
        Chain 1: Navigate → Search → Click video → Skip ads
        
        Returns:
            bool: True if success
        """
        try:
            print(f"{log_prefix} [{profile_id}] ========== Chain 1: Search and Start Video ==========")
            
            # ===== ACTION 2: SEARCH KEYWORD =====
            print(f"{log_prefix} [{profile_id}] Action 2/4: Search keyword...")
            search_action = YouTubeSearchHeadless(
                driver=driver,
                profile_id=profile_id,
                keywords=keywords,
                log_prefix=log_prefix,
                debugger_address=debugger_address
            )
            
            if not search_action.execute():
                print(f"{log_prefix} [{profile_id}] ✗ Failed to search keyword")
                return False
            
       
            
            # Wait for search results to load
            time.sleep(random.uniform(2, 4))
            
            # ===== ACTION 3: CLICK VIDEO =====
            print(f"{log_prefix} [{profile_id}] Action 3/4: Click video from search results...")
            click_video_action = YouTubeClickVideoHeadless(
                driver=driver,
                profile_id=profile_id,
                log_prefix=log_prefix,
                debugger_address=debugger_address,
                location="main"  # Main search results
            )
            
            if not click_video_action.execute():
                print(f"{log_prefix} [{profile_id}] ✗ Failed to click video")
                return False
            
          
            # Wait for video page to load
            time.sleep(random.uniform(2, 4))
            
            # ===== ACTION 4: SKIP ADS (IF ANY) =====
            print(f"{log_prefix} [{profile_id}] Action 4/4: Skip ads (if present)...")
            skip_ads_action = YouTubeSkipAdsHeadless(
                driver=driver,
                profile_id=profile_id,
                log_prefix=log_prefix,
                debugger_address=debugger_address,
                wait_time=7,
                watch_ad_time_range=(2, 5)  # Watch ad 7-10s before skipping
            )
            
            skip_ads_action.execute()  # Don't fail chain if no ads
         
            
            # Dismiss premium popup if present
            dismiss_premium = YouTubeDismissPremiumHeadless(
                driver=driver,
                profile_id=profile_id,
                log_prefix=log_prefix,
                debugger_address=debugger_address,
                wait_time=3
            )
            dismiss_premium.execute()
            
          
            time.sleep(random.uniform(1, 3))
          
            
            print(f"{log_prefix} [{profile_id}] ✓ Chain 1 completed successfully")
            return True
            
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ✗ Chain 1 error: {e}")
            import traceback
            traceback.print_exc()
            return False
        

    @staticmethod
    def _random_click_video_home_chain(driver, keywords, profile_id, debugger_address, log_prefix):
        """
        Chain 1: Navigate → Search → Click video → Skip ads
        
        Returns:
            bool: True if success
        """
        try:
            navigate_action = YouTubeNavigateAction(
                driver=driver,
                profile_id=profile_id,
                log_prefix=log_prefix,
                debugger_address=debugger_address,
                url="https://www.youtube.com"
            )
            
            if not navigate_action.execute():
                print(f"{log_prefix} [{profile_id}] ✗ Failed to navigate to YouTube")
                return False
            # Wait for search results to load
            time.sleep(random.uniform(2, 4))
            
            # ===== ACTION 3: CLICK VIDEO =====          
            click_video_action = YouTubeClickVideoHeadless(
                driver=driver,
                profile_id=profile_id,
                log_prefix=log_prefix,
                debugger_address=debugger_address,
                location="main"  # Main search results
            )
            
            if not click_video_action.execute():
                print(f"{log_prefix} [{profile_id}] ✗ Failed to click video")
                return False
            
          
            # Wait for video page to load
            time.sleep(random.uniform(2, 4))
            
            # ===== ACTION 4: SKIP ADS (IF ANY) =====
            print(f"{log_prefix} [{profile_id}] Action 4/4: Skip ads (if present)...")
            skip_ads_action = YouTubeSkipAdsHeadless(
                driver=driver,
                profile_id=profile_id,
                log_prefix=log_prefix,
                debugger_address=debugger_address,
                wait_time=7,
                watch_ad_time_range=(2, 5)  # Watch ad 7-10s before skipping
            )
            
            skip_ads_action.execute()  # Don't fail chain if no ads
         
            
            # Dismiss premium popup if present
            dismiss_premium = YouTubeDismissPremiumHeadless(
                driver=driver,
                profile_id=profile_id,
                log_prefix=log_prefix,
                debugger_address=debugger_address,
                wait_time=3
            )
            dismiss_premium.execute()
            
          
            time.sleep(random.uniform(1, 3))
          
            
            print(f"{log_prefix} [{profile_id}] ✓ Chain 1 completed successfully")
            return True
            
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ✗ Chain 1 error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    @staticmethod
    def _random_click_video_sidebar_chain(driver, keywords, profile_id, debugger_address, log_prefix):
        """
        Chain 1: Navigate → Search → Click video → Skip ads
        
        Returns:
            bool: True if success
        """
        try:
           
            
            # ===== ACTION 3: CLICK VIDEO =====          
            click_video_action = YouTubeClickVideoHeadless(
                driver=driver,
                profile_id=profile_id,
                log_prefix=log_prefix,
                debugger_address=debugger_address,
                location="side"  # Main search results
            )
            
            if not click_video_action.execute():
                print(f"{log_prefix} [{profile_id}] ✗ Failed to click video")
                return False
            
          
            # Wait for video page to load
            time.sleep(random.uniform(2, 4))
            
            # ===== ACTION 4: SKIP ADS (IF ANY) =====
            print(f"{log_prefix} [{profile_id}] Action 4/4: Skip ads (if present)...")
            skip_ads_action = YouTubeSkipAdsHeadless(
                driver=driver,
                profile_id=profile_id,
                log_prefix=log_prefix,
                debugger_address=debugger_address,
                wait_time=7,
                watch_ad_time_range=(2, 5)  # Watch ad 7-10s before skipping
            )
            
            skip_ads_action.execute()  # Don't fail chain if no ads
         
            
            # Dismiss premium popup if present
            dismiss_premium = YouTubeDismissPremiumHeadless(
                driver=driver,
                profile_id=profile_id,
                log_prefix=log_prefix,
                debugger_address=debugger_address,
                wait_time=3
            )
            dismiss_premium.execute()
            
          
            time.sleep(random.uniform(1, 3))
          
            
            print(f"{log_prefix} [{profile_id}] ✓ Chain 1 completed successfully")
            return True
            
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ✗ Chain 1 error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def _video_interaction_chain(driver, keywords, profile_id, debugger_address, log_prefix):
        """
        Chain 2: Video interactions (scroll, seek, pause/resume)
        
        Returns:
            bool: True if success
        """
        try:

            print(f"{log_prefix} [{profile_id}] ========== Chain 2: Video Interaction ==========")
            
            # Random number of interactions (2-4)
            num_interactions = random.randint(2, 4)
            print(f"{log_prefix} [{profile_id}] Will perform {num_interactions} random interactions...")
            
            # Available interaction types
            interaction_types = ['scroll', 'seek', 'pause_resume', 'move_mouse']
            
            for i in range(2):
                # Random select interaction type
                interaction_type = random.choice(interaction_types)
                
                print(f"{log_prefix} [{profile_id}] Interaction {i+1}/{num_interactions}: {interaction_type}...")
                
                try:
                    if interaction_type == 'scroll':
                        # Scroll page
                        scroll_action = YouTubeScrollHeadless(
                            driver=driver,
                            profile_id=profile_id,
                            log_prefix=log_prefix,
                            debugger_address=debugger_address,
                            direction="random",
                            times=random.randint(2, 4)
                        )
                        scroll_action.execute()
                        
                    elif interaction_type == 'seek':
                        # Seek video to random position
                        seek_action = YouTubeSeekVideoHeadless(
                            driver=driver,
                            profile_id=profile_id,
                            log_prefix=log_prefix,
                            debugger_address=debugger_address
                        )
                        seek_action.execute()
                        
                    elif interaction_type == 'pause_resume':
                        # Pause and resume video
                        pause_action = YouTubePauseResumeHeadless(
                            driver=driver,
                            profile_id=profile_id,
                            log_prefix=log_prefix,
                            debugger_address=debugger_address,
                            pause_time_range=(2, 5)
                        )
                        pause_action.execute()
                        
                    else:
                        # Basic usage - all defaults (3-7 movements, random patterns)
                        mouse_action = YouTubeMouseMovementHeadless(
                            driver=driver,
                            profile_id=profile_id,
                            log_prefix=log_prefix,
                            debugger_address=debugger_address
                        )

                        # Execute
                        mouse_action.execute()
                    
                    # Random delay between interactions (anti-detection)
                   
                    delay = random.uniform(15, 35)
                    print(f"{log_prefix} [{profile_id}] Waiting {delay:.1f}s before next interaction...")
                    time.sleep(delay)
                    
                except Exception as e:
                    print(f"{log_prefix} [{profile_id}] ⚠ Interaction '{interaction_type}' error: {e}")
                    # Continue with next interaction
            
            print(f"{log_prefix} [{profile_id}] ✓ Chain 2 completed successfully")
            return True
            
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ✗ Chain 2 error: {e}")
            import traceback
            traceback.print_exc()
            return False
