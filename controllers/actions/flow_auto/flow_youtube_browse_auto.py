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
        opened_profiles = self.parameters.get('opened_profiles', [])
        # ========== CHAIN 0: WARM UP BEFORE VIEW VIDEO (BẮT BUỘC) ==========
        self._warm_up_chain()
        self._interaction_website_chains()
        
        repeat_count = 2
        if len(opened_profiles) == 2:
            repeat_count = 6
        elif len(opened_profiles) == 1:
            repeat_count = 10
        
        for i in range(repeat_count):
            choice_browse = random.choice([1,2])
            if choice_browse == 1:
                self._second_action_chain()
            else:
                self._warm_up_chain()
                
            self._interaction_website_chains()
            
        self._last_action_chain()
      
        
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
        
        choice_browse = random.choice([1,2])
        if choice_browse == 1:
            chain_warm_up_actions.append(
                ("browse", BrowseWebsiteAutoAction(
                    profile_id=self.profile_id,
                    parameters = self.parameters,
                    area = "main",
                    choice = "youtube",
                    log_prefix=self.log_prefix,
                ))
            )
        else:
            chain_warm_up_actions.append(
                ("browse", BrowseWebsiteAutoAction(
                    profile_id=self.profile_id,
                    parameters = self.parameters,
                    area = "search",
                    choice = "youtube",
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
        
        
    def _second_action_chain(self):      
        chain_warm_up_actions = []
        
        choice_browse = random.choice([1,2])
        if choice_browse == 1:
            chain_warm_up_actions.append(
                ("browse", BrowseWebsiteAutoAction(
                    profile_id=self.profile_id,
                    parameters = self.parameters,
                    area = "search",
                    choice = "youtube",
                    log_prefix=self.log_prefix,
                ))
            )
        else:
            chain_warm_up_actions.append(
                ("browse", BrowseWebsiteAutoAction(
                    profile_id=self.profile_id,
                    parameters = self.parameters,
                    area = "sidebar",
                    choice = "youtube",
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
            'name': 'second_action_chain',
            'actions': chain_warm_up_actions
        }) 
        

    def _last_action_chain(self):      
        chain_warm_up_actions = []        
       
        chain_warm_up_actions.append(
            ("browse", BrowseWebsiteAutoAction(
                profile_id=self.profile_id,
                parameters = self.parameters,
                area = "search",
                choice = "web",
                log_prefix=self.log_prefix,
            ))
        )
       
        self.chain_queue.append({
            'name': 'last_action_chain',
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
                ("delay", random.randint(5,10))  # ← DELAY TUPLE: ("delay", seconds)
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
  