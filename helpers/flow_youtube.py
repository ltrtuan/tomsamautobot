# helpers/flow_youtube.py

import time
import random
from selenium.webdriver.common.by import By
from helpers.action_chain_manager import ActionChainManager

# Import modular actions
from helpers.actions.youtube_navigate_action import YouTubeNavigateAction
from helpers.actions.youtube_search_action import YouTubeSearchAction
from helpers.actions.youtube_skip_ads_action import YouTubeSkipAdsAction
from helpers.actions.youtube_click_video_action import YouTubeClickVideoAction
from helpers.actions.youtube_scroll_action import YouTubeScrollAction
from helpers.actions.youtube_mouse_move_action import YouTubeMouseMoveAction
from helpers.actions.youtube_seek_video_action import YouTubeSeekVideoAction
from helpers.actions.youtube_pause_resume_action import YouTubePauseResumeAction
from helpers.actions.youtube_click_ad_action import YouTubeClickAdAction
from helpers.actions.youtube_fullscreen_action import YouTubeFullscreenAction


from helpers.gologin_profile_helper import GoLoginProfileHelper


class YouTubeFlowIterator:
    """
    YouTube Flow với chain iterator pattern - Hỗ trợ round-robin execution
    
    Thay vì execute toàn bộ flow, class này cho phép execute từng chain một
    và chờ coordinator gọi lại để execute chain tiếp theo.
    
    Workflow:
    1. __init__: Tạo danh sách chains cần execute
    2. has_next_chain(): Kiểm tra còn chain nào chưa execute
    3. execute_next_chain(): Execute 1 chain, tăng index, return result
    """
    
    def __init__(self, driver, keywords, profile_id, debugger_address, log_prefix="[YOUTUBE]"):
        """
        Khởi tạo flow iterator
        
        Args:
            driver: Selenium WebDriver instance
            keyword: Keyword để search YouTube
            profile_id: Profile ID
            debugger_address: Chrome debugger address
            log_prefix: Prefix cho log messages
        """
        self.driver = driver
        self.keywords = keywords
        self.profile_id = profile_id
        self.debugger_address = debugger_address
        self.log_prefix = log_prefix
        
        # Build danh sách chains
        self.chains = self._build_chain_queue()
        self.current_chain_index = 0
        
        print(f"{log_prefix} [{profile_id}] ✓ Flow iterator initialized with {len(self.chains)} chains")
    
    def _build_chain_queue(self):
        """
        Tạo danh sách chains cần execute
        
        Returns:
            list: Danh sách tuples (chain_function, chain_args)
        """
        chains = []
        
        # Chain 1: Search and start video (LOCKED - khoảng 30s)
        chains.append({
            'name': 'search_and_start_video',
            'function': YouTubeFlow._search_and_start_video_chain,
            'args': (self.driver, self.keywords, self.profile_id, self.debugger_address, self.log_prefix)
        })
        
        # Chains 2-N: Random interaction cycles (mỗi cycle là 1 chain)
        # Random 3-6 interaction cycles
        # num_interaction_cycles = random.randint(3, 6)
        # print(f"{self.log_prefix} [{self.profile_id}] Planning {num_interaction_cycles} interaction cycles")
        
        # for cycle_num in range(1, num_interaction_cycles + 1):
        #     chains.append({
        #         'name': f'interaction_cycle_{cycle_num}',
        #         'function': YouTubeFlow._video_interaction_chain,
        #         'args': (self.driver, self.keywords, self.profile_id, self.debugger_address, self.log_prefix, cycle_num)
        #     })
        chains.append({
                'name': f'interaction_cycle',
                'function': YouTubeFlow._video_interaction_chain,
                'args': (self.driver, self.keywords, self.profile_id, self.debugger_address, self.log_prefix, 0)
            })
        return chains
    
    def has_next_chain(self):
        """
        Kiểm tra còn chain nào chưa execute
        
        Returns:
            bool: True nếu còn chain, False nếu đã hết
        """
        return self.current_chain_index < len(self.chains)
    
    def execute_next_chain(self):
        """
        Execute chain tiếp theo trong queue
        
        Process:
        1. Lấy chain hiện tại
        2. Execute chain thông qua ActionChainManager (LOCKED)
        3. Tăng index
        4. Return result
        
        Returns:
            bool: True nếu chain thành công, False nếu failed
        """
        if not self.has_next_chain():
            print(f"{self.log_prefix} [{self.profile_id}] ⚠ No more chains to execute")
            return False
        
        # Lấy chain hiện tại
        chain_info = self.chains[self.current_chain_index]
        chain_name = chain_info['name']
        chain_function = chain_info['function']
        chain_args = chain_info['args']
        
        print(f"{self.log_prefix} [{self.profile_id}] ========================================")
        print(f"{self.log_prefix} [{self.profile_id}] Executing chain {self.current_chain_index + 1}/{len(self.chains)}: {chain_name}")
        print(f"{self.log_prefix} [{self.profile_id}] ========================================")
        
        # Execute chain thông qua ActionChainManager (tự động acquire/release lock)
        from helpers.action_chain_manager import ActionChainManager
        
        result = ActionChainManager.execute_chain(
            self.profile_id,
            chain_function,
            *chain_args
        )
        
        # Tăng index cho lần execute tiếp theo
        self.current_chain_index += 1
        
        if result:
            print(f"{self.log_prefix} [{self.profile_id}] ✓ Chain '{chain_name}' completed successfully")
        else:
            print(f"{self.log_prefix} [{self.profile_id}] ✗ Chain '{chain_name}' failed")
        
        return result
    
    def get_progress(self):
        """
        Lấy thông tin tiến độ
        
        Returns:
            dict: {'current': int, 'total': int, 'percentage': float}
        """
        return {
            'current': self.current_chain_index,
            'total': len(self.chains),
            'percentage': (self.current_chain_index / len(self.chains) * 100) if len(self.chains) > 0 else 0
        }



class YouTubeFlow:
    """
    YouTube Flow Orchestrator - Natural interaction mode
    Profiles perform interactions whenever they get lock, organically
    """
    
    @staticmethod
    def execute_main_flow(driver, keywords, profile_id, debugger_address, log_prefix="[YOUTUBE]"):
        """
        MAIN FLOW - Natural mode:
        1. Search & Click video (LOCKED)
        2. Release lock
        3. Periodic interactions (LOCKED when active, compete with other profiles)
        4. Thread completes when interaction cycles done (video may still be playing - that's OK!)
        
        Returns:
            bool: True if successful
        """
     
        # ========== PHASE 1: SEARCH & START VIDEO (LOCKED) ==========
        chain_success = ActionChainManager.execute_chain(
            profile_id,
            YouTubeFlow._search_and_start_video_chain,
            driver, keywords, profile_id, debugger_address, log_prefix
        )
        
        if not chain_success:
            print(f"{log_prefix} [{profile_id}] ✗ Initial chain failed")
            return False
        
        # ========== PHASE 2: NATURAL INTERACTION CYCLES ==========
        print(f"{log_prefix} [{profile_id}] ========== VIDEO PLAYING, ENTERING NATURAL INTERACTION MODE ==========")
        
        # Random number of interaction cycles (3-6 times)
        # num_interaction_cycles = random.randint(3, 6)
        # print(f"{log_prefix} [{profile_id}] Will perform {num_interaction_cycles} interaction cycles")
        
        # for cycle in range(num_interaction_cycles):
        #     # NO SLEEP HERE - Profile tries to acquire lock immediately
        #     # Other profiles may get lock first, that's natural!
            
        #     print(f"{log_prefix} [{profile_id}] [Cycle {cycle+1}/{num_interaction_cycles}] Competing for lock...")
            
        #     # Execute interaction cycle (LOCKED - will wait for lock if needed)
        #     interaction_success = ActionChainManager.execute_chain(
        #         profile_id,
        #         YouTubeFlow._video_interaction_chain,
        #         driver, keyword, profile_id, debugger_address, log_prefix, cycle + 1
        #     )
            
        #     if not interaction_success:
        #         print(f"{log_prefix} [{profile_id}] ⚠ Interaction cycle {cycle+1} failed, continuing...")
        interaction_success = ActionChainManager.execute_chain(
            profile_id,
            YouTubeFlow._video_interaction_chain,
            driver, keywords, profile_id, debugger_address, log_prefix,0
        )
            
        if not interaction_success:
            print(f"{log_prefix} [{profile_id}] ⚠ Interaction cycle 0 failed, continuing...")
        print(f"{log_prefix} [{profile_id}] ✓ Finished all interaction cycles (video may still be playing - that's natural)")
        return True
    
    @staticmethod
    def create_flow_iterator(driver, keywords, profile_id, debugger_address, log_prefix="[YOUTUBE]"):
        """
        Factory method để tạo flow iterator cho round-robin execution
    
        Args:
            driver: Selenium WebDriver instance
            keyword: Keyword để search
            profile_id: Profile ID
            debugger_address: Chrome debugger address
            log_prefix: Prefix cho log
    
        Returns:
            YouTubeFlowIterator: Flow iterator instance
        """
        return YouTubeFlowIterator(driver, keywords, profile_id, debugger_address, log_prefix)

    
    @staticmethod
    def _search_and_start_video_chain(driver, keywords, profile_id, debugger_address, log_prefix):
        """
        LOCKED CHAIN: Navigate → Search → Click video → Wait for playing
        Lock is released immediately after video starts playing
        """
        print(f"{log_prefix} [{profile_id}] ========== LOCKED CHAIN START: SEARCH & PLAY ==========")
        
        try:
            # THÊM ĐOẠN NÀY VÀO ĐẦU (TRONG LOCK)
            # Fix crashed tabs INSIDE lock to prevent window focus conflicts
            # PAUSE health monitoring during crashed tab fix
            from helpers.profile_health_monitor import get_health_monitor

            monitor = get_health_monitor()
            monitor.pause_monitoring(profile_id)

            print(f"{log_prefix} [{profile_id}] Checking for crashed tabs...")
            crashed_fix_success = GoLoginProfileHelper.check_and_fix_crashed_tabs(driver, debugger_address, log_prefix)

            # RESUME health monitoring after fix
            monitor.resume_monitoring(profile_id)

            if not crashed_fix_success:
                print(f"{log_prefix} [{profile_id}] ✗ Failed to fix crashed tab - closing profile")
                return False

        
            # Bring window to front AFTER fixing crashed tabs
            GoLoginProfileHelper.bring_profile_to_front(profile_id, driver=driver, log_prefix=log_prefix)
            time.sleep(2)
            
            # Step 1: Navigate to YouTube            
            YouTubeNavigateAction(driver, profile_id, log_prefix, debugger_address).execute()
            time.sleep(random.uniform(2, 4))
            
            # Step 2: Pre-search random actions
            YouTubeFlow._random_actions(driver, profile_id, debugger_address, log_prefix, num_actions=2)
            
            
            # Step 3: Search keyword
            # RE-BRING TO FRONT before critical action (in case other profile closed during setup)
            print(f"{log_prefix} [{profile_id}] Re-activating window before search...")
            GoLoginProfileHelper.bring_profile_to_front(profile_id, driver=driver, log_prefix=log_prefix)
            time.sleep(0.5)
            
            YouTubeSearchAction(driver, profile_id, keywords, log_prefix, debugger_address).execute()
            time.sleep(random.uniform(2, 4))
            
            ################################### Retry logic: Try to click video up to 3 times, scroll between retries
            video_clicked = False
            max_retries = 3

            for attempt in range(1, max_retries + 1):
                print(f"{log_prefix} [{profile_id}] ℹ Attempting to click video (try {attempt}/{max_retries})...")
    
                video_action = YouTubeClickVideoAction(
                    driver, profile_id, log_prefix, debugger_address,
                    video_index_range=(1, 10)
                ).execute()
    
                if video_action:
                    # Success: video clicked and started playing
                    video_clicked = True
                    print(f"{log_prefix} [{profile_id}] ✓ Video clicked successfully on attempt {attempt}")
                    break
                else:
                    # Failed to find/click video
                    if attempt < max_retries:
                        print(f"{log_prefix} [{profile_id}] ⚠ No video found on screen, scrolling to find more...")
            
                        # Scroll down to load more videos
                        YouTubeScrollAction(
                            driver, profile_id, log_prefix, debugger_address,
                            direction="down",
                            times=random.randint(2, 4)
                        ).execute()
            
                        # Wait for videos to load
                        time.sleep(random.uniform(1.5, 2.5))
                    else:
                        print(f"{log_prefix} [{profile_id}] ✗ Failed to find clickable video after {max_retries} attempts")

            # Check final result
            if not video_clicked:
                print(f"{log_prefix} [{profile_id}] ✗ Failed to start video playback")
                return False
            

            YouTubeMouseMoveAction(driver, profile_id, log_prefix, debugger_address).execute()
            
            # 70% skip, 30% click
            ads_choice = 'skip' if random.random() < 0.7 else 'click'
            if ads_choice == 'skip':
                time.sleep(random.uniform(5, 10))
                YouTubeSkipAdsAction(driver, profile_id, log_prefix, debugger_address, wait_time=1).execute()
                time.sleep(random.uniform(5, 10))
                YouTubeSkipAdsAction(driver, profile_id, log_prefix, debugger_address, wait_time=1).execute()
            else:
                YouTubeClickAdAction(driver, profile_id, log_prefix, debugger_address).execute()
            
           
            time.sleep(random.uniform(5, 10))
            
            # Step 5: Skip ads if present
            YouTubeSkipAdsAction(driver, profile_id, log_prefix, debugger_address, wait_time=1).execute()          
            
            # VIDEO IS PLAYING - CHAIN COMPLETE
            print(f"{log_prefix} [{profile_id}] ========== LOCKED CHAIN END: VIDEO PLAYING ==========")
            return True
            
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ✗ Error in chain: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def _video_interaction_chain(driver, keywords, profile_id, debugger_address, log_prefix, cycle_number):
        """
        LOCKED CHAIN: Perform human-like interactions
        Random selection and random repetitions = organic watch time
        
        Possible actions:
        - Move mouse randomly
        - Click video timeline (seek)
        - Pause/Resume video
        - Fullscreen toggle
        - Click on ad (open new tab, scroll, close)
        - Scroll page
        - Volume control
        """
        print(f"{log_prefix} [{profile_id}] ========== INTERACTION CHAIN START: CYCLE {cycle_number} ==========")
        
        try:
            # Check if video ended or autoplayed to next video - that's OK!
            try:
                current_url = driver.current_url
                print(f"{log_prefix} [{profile_id}] Current URL: {current_url}")
            except:
                pass
            print(f"{log_prefix} [{profile_id}] Will perform YouTubeSeekVideoAction")
            YouTubeSeekVideoAction(driver, profile_id, log_prefix, debugger_address).execute()
            time.sleep(2)
            print(f"{log_prefix} [{profile_id}] Will perform YouTubePauseResumeAction")
            YouTubePauseResumeAction(driver, profile_id, log_prefix, debugger_address).execute()
            time.sleep(2)
            print(f"{log_prefix} [{profile_id}] Will perform YouTubeClickAdAction")
            YouTubeClickAdAction(driver, profile_id, log_prefix, debugger_address).execute()
            time.sleep(2)
            print(f"{log_prefix} [{profile_id}] Will perform YouTubeFullscreenAction")
            YouTubeFullscreenAction(driver, profile_id, log_prefix, debugger_address).execute()
            time.sleep(2)
            print(f"{log_prefix} [{profile_id}] Will perform YouTubeClickVideoAction sideeeeeee")
            YouTubeClickVideoAction(driver, profile_id, log_prefix, debugger_address, (1,5), 'side').execute()
            time.sleep(2)
            print(f"{log_prefix} [{profile_id}] Will perform YouTubeSkipAdsAction")
            YouTubeSkipAdsAction(driver, profile_id, log_prefix, debugger_address).execute()
            time.sleep(2)
            print(f"{log_prefix} [{profile_id}] Will perform YouTubeSearchAction")
            YouTubeSearchAction(driver, profile_id, keywords, log_prefix, debugger_address).execute()
            
            # # Random number of interactions in this cycle (1-4)
            # num_interactions_this_cycle = random.randint(1, 4)
            
            # # Random selection of interaction types
            # interaction_types = [               
            #     'seek_video',
            #     'pause_resume',
            #     'click_ad',
            #     'skip_ads',
            #     'scroll_page',
            #     'full_screen',
            #     'click_video_side',
            #     'search_video'
            # ]
            
            # selected_interactions = random.sample(
            #     interaction_types, 
            #     min(num_interactions_this_cycle, len(interaction_types))
            # )
            
            # print(f"{log_prefix} [{profile_id}] Will perform {num_interactions_this_cycle} interactions: {selected_interactions}")
            
            # for interaction in selected_interactions:
            #     YouTubeMouseMoveAction(driver, profile_id, log_prefix, debugger_address, click=False).execute()               
    
            #     if interaction == 'seek_video':
            #         YouTubeSeekVideoAction(driver, profile_id, log_prefix, debugger_address).execute()
    
            #     elif interaction == 'pause_resume':
            #         YouTubePauseResumeAction(driver, profile_id, log_prefix, debugger_address).execute()
    
            #     elif interaction == 'click_ad':
            #         YouTubeClickAdAction(driver, profile_id, log_prefix, debugger_address).execute()
    
            #     elif interaction == 'scroll_page':
            #         YouTubeScrollAction(driver, profile_id, log_prefix, debugger_address).execute()
                    
            #     elif interaction == 'full_screen':
            #         YouTubeFullscreenAction(driver, profile_id, log_prefix, debugger_address).execute()
                    
            #     elif interaction == 'click_video_side':
            #         YouTubeClickVideoAction(driver, profile_id, log_prefix, debugger_address, (1,5), 'side').execute()
                    
            #     elif interaction == 'skip_ads':
            #         YouTubeSkipAdsAction(driver, profile_id, log_prefix, debugger_address).execute()
                    
            #     elif interaction == 'search_video':
            #         YouTubeSearchAction(driver, profile_id, keyword, log_prefix, debugger_address).execute()
                
            #     # Random wait between interactions (organic timing)
            #     wait_time = random.uniform(1, 5)
            #     print(f"{log_prefix} [{profile_id}] Waiting {wait_time:.1f}s before next interaction...")
            #     time.sleep(wait_time)
            
            print(f"{log_prefix} [{profile_id}] ========== INTERACTION CHAIN END: CYCLE {cycle_number} ==========")
            return True
            
        except Exception as e:
            print(f"{log_prefix} [{profile_id}] ✗ Error in interaction chain: {e}")
            return False
    
    @staticmethod
    def _random_actions(driver, profile_id, debugger_address, log_prefix, num_actions=2):
        """Perform random scroll/mouse move actions"""
        print(f"{log_prefix} [{profile_id}] Performing {num_actions} random actions...")
        
        for i in range(num_actions):
            action_type = random.choice(['scroll', 'mouse_move'])
            
            if action_type == 'scroll':
                YouTubeScrollAction(driver, profile_id, log_prefix, debugger_address, direction="down").execute()
            else:
                YouTubeMouseMoveAction(driver, profile_id, log_prefix, debugger_address, click=False).execute()
            
            time.sleep(random.uniform(1, 2))
