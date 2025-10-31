# controllers/actions/flow_auto/flow_youtube_auto.py

import time
import random
import os
from helpers.gologin_profile_helper import GoLoginProfileHelper

# Import all action classes
from controllers.actions.flow_auto.actions_auto.youtube_navigate_auto_action import YouTubeNavigateAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_random_move_scroll_auto_action import YouTubeRandomMoveScrollAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_find_search_box_auto_action import YouTubeFindSearchBoxAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_find_click_video_auto_action import YouTubeFindClickVideoAutoAction

from controllers.actions.flow_auto.actions_auto.youtube_skip_ads_auto_action import YouTubeSkipAdsAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_mouse_move_auto_action import YouTubeMouseMoveAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_pause_resume_auto_action import YouTubePauseResumeAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_fullscreen_auto_action import YouTubeFullscreenAutoAction


class YouTubeFlowAutoIterator:
    """
    YouTube Auto Flow Iterator
    Compatible with round-robin execution pattern (giống Selenium version)
    """
    
    def __init__(self, profile_id, keywords, log_prefix="[YOUTUBE AUTO]"):
        """
        Initialize YouTube Auto Flow Iterator
        
        Args:
            profile_id: GoLogin profile ID
            keywords: Dict containing keywords and params
            log_prefix: Prefix for log messages
        """
        self.profile_id = profile_id
        self.keywords = keywords
        self.log_prefix = log_prefix
        
        # Extract params
        self.keywords_youtube = keywords.get("keywords_youtube", [])
        self.suffix_prefix = keywords.get("suffix_prefix", "")      
        
        # Window info (cached)
        self.window_info = None
        
        # Build chain queue
        self.chain_queue = []
        self.current_chain_index = 0
        self._build_chain_queue()
        
        self.total_chains = len(self.chain_queue)
        self.log(f"Initialized with {self.total_chains} total chains")
    
    def _build_chain_queue(self):
        """
        Build chain queue (giống _build_chain_queue trong Selenium version)
        
        Chain 1: Search and start video (BẮT BUỘC - TẤT CẢ PROFILE ĐỀU CHẠY)
        Chain 2-N: Random video interactions (RANDOM SỐ LƯỢNG VÀ LOẠI)
        """
        # ========== CHAIN 1: SEARCH AND START VIDEO (BẮT BUỘC) ==========
        self._build_search_and_start_video_chain()
        
        # ========== CHAIN 2-N: VIDEO INTERACTIONS (RANDOM) ==========
        self._build_video_interaction_chains()
        
        self.log(f"Built {len(self.chain_queue)} chains")
    
    def _build_search_and_start_video_chain(self):
        """
        Build Chain 1: Search and start video
        
        Flow:
        1. Navigate to YouTube
        2. Random move/scroll (2-3 actions)
        3. Search (click search box + input keyword)
        4. Find logo with retry (4-6 scrolls, 500-700px each)
        5. Click video (logo-based or random fallback)
        """
        chain1_actions = []
        
        # Action 1: Navigate to YouTube
        chain1_actions.append(
            ("navigate_youtube", YouTubeNavigateAutoAction(self.profile_id, self.log_prefix))
        )
        
        # Action 2: Random move/scroll before search
        num_random_actions = random.randint(1, 3)
        chain1_actions.append(
            ("random_move_scroll", YouTubeRandomMoveScrollAutoAction(self.profile_id, num_random_actions, "main", self.log_prefix))
        )
        
        # Action 3: Search (if keywords available)
        if self.keywords_youtube:         
            
            chain1_actions.append(
                ("find_search_box", YouTubeFindSearchBoxAutoAction(
                    self.profile_id, 
                    self.keywords,  # Pass full keywords dict
                    self.log_prefix
                ))
            )
         
            
        # Action 4: Find logo + Click video (combined action, support main/sidebar)
        chain1_actions.append(
            ("find_click_video", YouTubeFindClickVideoAutoAction(
                self.profile_id,
                self.keywords,     # Pass full keywords dict
                self.log_prefix,   # log_prefix (positional or keyword)
                area="main"        # area (keyword argument)
            ))
        )
        time.sleep(1)
        chain1_actions.append(
            ("move_mouse", YouTubeMouseMoveAutoAction(
            profile_id=self.profile_id,
            click=False,
            log_prefix=self.log_prefix,
        ))
        )
      
        time.sleep(random.uniform(4, 7))            

        chain1_actions.append(
            ("skip_ads", YouTubeSkipAdsAutoAction(
                profile_id=self.profile_id,
                keywords=self.keywords,  # Pass keywords dict for ads area params
                log_prefix=self.log_prefix
            ))
        )
        
        
        # Add Chain 1 to queue
        self.chain_queue.append({
            'name': 'search_and_start_video',
            'actions': chain1_actions
        })
        
        self.log(f"Chain 1 built with {len(chain1_actions)} actions")
    
    def _build_video_interaction_chains(self):
        """
        Build Chain 2-N: Random video interactions
    
        Random:
        - Số lượng chains: 3-6
        - Mỗi chain có 1-3 actions
        - Loại action: scroll, mouse_move, pause_resume, fullscreen
        """
       
        self.log(f"Building interaction chains")
    
        # Available action types
        action_types = ['scroll', 'mouse_move', 'pause_resume', 'fullscreen']
    
        chain_actions = []       
          
        action = YouTubeMouseMoveAutoAction(
            profile_id=self.profile_id,
            click=False,
            log_prefix=self.log_prefix,
        )
        chain_actions.append(('mouse_move', action))
        
        action = YouTubePauseResumeAutoAction(
            profile_id=self.profile_id,
            log_prefix=self.log_prefix
        )
        chain_actions.append(('YouTubePauseResumeAutoAction', action))
        time.sleep(3)
        action = YouTubeFullscreenAutoAction(
            profile_id=self.profile_id,
            log_prefix=self.log_prefix
        )
        chain_actions.append(('YouTubeFullscreenAutoAction', action))
        # ========== RANDOM 1-3 ACTIONS PER CHAIN ==========
        # num_actions = random.randint(1, 3)
        
        # for j in range(num_actions):
        #     action_type = random.choice(action_types)
            
        #     if action_type == 'scroll':
        #         action = YouTubeScrollAutoAction(
        #             profile_id=self.profile_id,
        #             log_prefix=self.log_prefix
        #         )
            
        #     elif action_type == 'mouse_move':              
        #         action = YouTubeMouseMoveAutoAction(
        #             profile_id=self.profile_id,
        #             click=False,
        #             log_prefix=self.log_prefix,
        #         )
            
        #     elif action_type == 'pause_resume':
        #         action = YouTubePauseResumeAutoAction(
        #             profile_id=self.profile_id,
        #             log_prefix=self.log_prefix
        #         )
            
        #     elif action_type == 'fullscreen':
        #         action = YouTubeFullscreenAutoAction(
        #             profile_id=self.profile_id,
        #             log_prefix=self.log_prefix
        #         )
            
        #     else:
        #         continue
            
        #     chain_actions.append((action_type, action))
        
        # Add chain to queue
        self.chain_queue.append({
            'name': f'interaction',
            'actions': chain_actions
        })
        
        self.log(f"Interaction chain built with {len(chain_actions)} actions")

    
    def has_next_chain(self):
        """Check if there are more chains to execute"""
        return self.current_chain_index < self.total_chains
    
    def execute_next_chain(self):
        """
        Execute the next chain in queue
        Returns control after completing 1 chain (for round-robin)
    
        Returns:
            bool: True if chain executed successfully
        """
        if not self.has_next_chain():
            self.log("No more chains to execute", "WARNING")
            return False
    
        current_chain = self.chain_queue[self.current_chain_index]
        chain_name = current_chain['name']
        chain_actions = current_chain['actions']
    
        self.log(f"Executing chain {self.current_chain_index + 1}/{self.total_chains}: {chain_name}")
    
        try:
            # Bring profile to front before executing chain
            GoLoginProfileHelper.bring_profile_to_front(self.profile_id, driver=None)
            time.sleep(1)
        
            # ========== EXECUTE ALL ACTIONS IN CHAIN ==========
            for action_name, action_obj in chain_actions:
                self.log(f"  → Action: {action_name}")
            
                if action_obj:
                    success = action_obj.execute()
                
                    if not success:
                        self.log(f"  ✗ Action '{action_name}' failed", "WARNING")
                    else:
                        self.log(f"  ✓ Action '{action_name}' completed")
        
            self.log(f"✓ Chain '{chain_name}' completed")
        
            # Move to next chain
            self.current_chain_index += 1
        
            return True
        
        except Exception as e:
            self.log(f"✗ Exception in chain '{chain_name}': {e}", "ERROR")
            import traceback
            traceback.print_exc()
        
            # Move to next chain even on error
            self.current_chain_index += 1
            return False

    
    def get_progress(self):
        """
        Get execution progress
        
        Returns:
            dict: {current, total, percentage}
        """
        percentage = (self.current_chain_index / self.total_chains * 100) if self.total_chains > 0 else 0
        return {
            'current': self.current_chain_index,
            'total': self.total_chains,
            'percentage': percentage
        }   
    
    def log(self, message, level="INFO"):
        """Log message with prefix"""
        print(f"{self.log_prefix} [{level}] {message}")


class YouTubeFlowAuto:
    """
    YouTube Auto Flow - Factory class
    Compatible with Selenium Start Action pattern
    """
    
    @staticmethod
    def create_flow_iterator(profile_id, keywords, log_prefix="[YOUTUBE AUTO]"):
        """
        Create flow iterator for round-robin execution
        
        Args:
            profile_id: GoLogin profile ID
            keywords: Dict containing keywords and params
            log_prefix: Prefix for log messages
            
        Returns:
            YouTubeFlowAutoIterator: Iterator instance
        """
        return YouTubeFlowAutoIterator(profile_id, keywords, log_prefix)
