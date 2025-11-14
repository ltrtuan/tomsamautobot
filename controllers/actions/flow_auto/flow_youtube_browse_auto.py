# controllers/actions/flow_auto/flow_youtube_browse_auto.py


import random
# Import all action classes
from controllers.actions.flow_auto.actions_auto.youtube_navigate_auto_action import YouTubeNavigateAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_random_move_scroll_auto_action import YouTubeRandomMoveScrollAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_find_search_box_auto_action import YouTubeFindSearchBoxAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_find_click_video_auto_action import YouTubeFindClickVideoAutoAction

from controllers.actions.flow_auto.actions_auto.youtube_skip_ads_auto_action import YouTubeSkipAdsAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_mouse_move_auto_action import YouTubeMouseMoveAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_pause_resume_auto_action import YouTubePauseResumeAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_fullscreen_auto_action import YouTubeFullscreenAutoAction
from controllers.actions.flow_auto.actions_auto.youtube_prev_next_auto_action import YouTubePrevNextAutoAction
from controllers.actions.flow_auto.actions_auto.browse_website_auto_action import BrowseWebsiteAutoAction

from controllers.actions.flow_auto.base_youtube_flow_auto import BaseYouTubeFlowAutoIterator

class YouTubeFlowAutoBrowseIterator(BaseYouTubeFlowAutoIterator):
    """
    YouTube Auto Flow Iterator
    Compatible with round-robin execution pattern (giống Selenium version)
    """
    
    
    def _build_chain_queue(self):
        """
        Build chain queue (giống _build_chain_queue trong Selenium version)
        
        Chain 1: Search and start video (BẮT BUỘC - TẤT CẢ PROFILE ĐỀU CHẠY)
        Chain 2-N: Random video interactions (RANDOM SỐ LƯỢNG VÀ LOẠI)
        """
        # ========== CHAIN 0: WARM UP BEFORE VIEW VIDEO (BẮT BUỘC) ==========
        self._warm_up_chain()
        self._interaction_website_chains()
        self._warm_up_chain()
        self._interaction_website_chains()
        self._warm_up_chain()
        self._interaction_website_chains()
        # ========== CHAIN 1: SEARCH AND START VIDEO (BẮT BUỘC) ==========
        # self._build_search_and_start_video_chain()
        
        # # ========== CHAIN 2-N: VIDEO INTERACTIONS (RANDOM) ==========
        # self._build_video_interaction_chains()        
        
        # self._build_search_and_start_video_chain()
        
        # self._build_video_interaction_chains()
        
        self.log(f"Built {len(self.chain_queue)} chains")
        
    def _warm_up_chain(self):
        """
        Build Warmup Chain: 
        RANDOM 1 or 2
        Flow 1:
        1. Random enter keyword google or warm up link url to address bar -> Enter
        2. Random click link on 3/4 center screen
       
        Flow 2:
        1. Check current url is youtube or not -> navigate to youtube
        RANDOM A or B
            A:
                1. Find search box -> enter google keyword -> Enter
                2. Click random link video same 2-Flow 1
            B:
                1. Navigate to Youtube.com
                2. Click random link video same 2-Flow 1 on Home
        """
        chain_warm_up_actions = []
        
        chain_warm_up_actions.append(
            ("move_mouse", BrowseWebsiteAutoAction(
                profile_id=self.profile_id,
                parameters = self.parameters,
                log_prefix=self.log_prefix,
            ))
        )
        
        chain_warm_up_actions.append(
            ("move_mouse", YouTubeMouseMoveAutoAction(
                profile_id=self.profile_id,
                click=False,
                log_prefix=self.log_prefix,
            ))
        )
        self.chain_queue.append({
            'name': 'warm_up_before_view_video',
            'actions': chain_warm_up_actions
        })
        
        
    def _interaction_website_chains(self):
        """
        Build Chain 2-N: Random video interactions
    
        Random:
        - Số lượng chains: 3-6
        - Mỗi chain có 1-3 actions
        - Loại action: scroll, mouse_move, pause_resume, fullscreen
        """
       
        self.log(f"Building interaction chains")
    
        # Available action types
        action_types = ['mouse_move', 'scroll']
    
        chain_actions = []       
      
        
        # ========== RANDOM 1-3 ACTIONS PER CHAIN ==========
        num_actions = random.randint(2, 4)
        
        for j in range(num_actions):
            chain_actions.append(
                ("delay", random.randint(2,5))  # ← DELAY TUPLE: ("delay", seconds)
            )
            action_type = random.choice(action_types)
          
            if action_type == 'scroll':
                num_random_actions = random.randint(1, 3)
                action = YouTubeRandomMoveScrollAutoAction(
                    profile_id=self.profile_id,
                    num_actions=num_random_actions,
                    area="main",
                    log_prefix=self.log_prefix
                )
            
            elif action_type == 'mouse_move':              
                action = YouTubeMouseMoveAutoAction(
                    profile_id=self.profile_id,
                    click=False,
                    log_prefix=self.log_prefix,
                )        

            else:
                continue
            
            chain_actions.append((action_type, action))
        
        # Add chain to queue
        self.chain_queue.append({
            'name': f'interaction',
            'actions': chain_actions
        })
        
        self.log(f"Interaction chain built with {len(chain_actions)} actions")
    
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
        
        chain1_actions.append(
            ("delay", 3)  # ← DELAY TUPLE: ("delay", seconds)
        )
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
        keywords_list = self.parameters.get("keywords_youtube", [])
        if keywords_list:  # ← Check dict, not instance var       
            
            chain1_actions.append(
                ("find_search_box", YouTubeFindSearchBoxAutoAction(
                    self.profile_id, 
                    self.parameters,  # Pass full keywords dict
                    self.log_prefix
                ))
            )
         
            
        # Action 4: Find logo + Click video (combined action, support main/sidebar)
        chain1_actions.append(
            ("find_click_video", YouTubeFindClickVideoAutoAction(
                self.profile_id,
                self.parameters,     # Pass full keywords dict
                self.log_prefix,   # log_prefix (positional or keyword)
                area="search",        # area (keyword argument)
                flow_type="browse"
            ))
        )
        
        chain1_actions.append(
            ("delay", 1)  # ← DELAY TUPLE: ("delay", seconds)
        )
        
        chain1_actions.append(
            ("move_mouse", YouTubeMouseMoveAutoAction(
            profile_id=self.profile_id,
            click=False,
            log_prefix=self.log_prefix,
        ))
        )
      
        chain1_actions.append(
            ("delay", random.uniform(4, 7))  # ← DELAY TUPLE: ("delay", seconds)
        )   

        chain1_actions.append(
            ("skip_ads", YouTubeSkipAdsAutoAction(
                profile_id=self.profile_id,
                parameters=self.parameters,
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
        action_types = ['mouse_move', 'pause_resume', 'fullscreen', 'prev_next']
    
        chain_actions = []       
      
        
        # ========== RANDOM 1-3 ACTIONS PER CHAIN ==========
        num_actions = random.randint(2, 4)
        
        for j in range(num_actions):
            chain_actions.append(
                ("delay", random.randint(2,5))  # ← DELAY TUPLE: ("delay", seconds)
            )
            action_type = random.choice(action_types)
          
            if action_type == 'scroll':
                num_random_actions = random.randint(1, 3)
                action = YouTubeRandomMoveScrollAutoAction(
                    profile_id=self.profile_id,
                    num_actions=num_random_actions,
                    area="main",
                    log_prefix=self.log_prefix
                )
            
            elif action_type == 'mouse_move':              
                action = YouTubeMouseMoveAutoAction(
                    profile_id=self.profile_id,
                    click=False,
                    log_prefix=self.log_prefix,
                )
            
            elif action_type == 'pause_resume':
                action = YouTubePauseResumeAutoAction(
                    profile_id=self.profile_id,
                    log_prefix=self.log_prefix
                )
            
            elif action_type == 'fullscreen':
                action = YouTubeFullscreenAutoAction(
                    profile_id=self.profile_id,
                    log_prefix=self.log_prefix
                )
                
            elif action_type == 'prev_next':
                action = YouTubePrevNextAutoAction(
                    profile_id=self.profile_id,
                    log_prefix=self.log_prefix
                )                
        

            else:
                continue
            
            chain_actions.append((action_type, action))
        
        # Add chain to queue
        self.chain_queue.append({
            'name': f'interaction',
            'actions': chain_actions
        })
        
        self.log(f"Interaction chain built with {len(chain_actions)} actions")