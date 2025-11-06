# controllers/actions/flow_auto/flow_youtube_auto.py


import random
from models.global_variables import GlobalVariables
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
from controllers.actions.flow_auto.base_youtube_flow_auto import BaseYouTubeFlowAutoIterator

class YouTubeFlowAutoIterator(BaseYouTubeFlowAutoIterator):
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
        # ========== CHAIN 1: SEARCH AND START VIDEO (BẮT BUỘC) ==========
        self._build_search_and_start_video_chain()
        
        # ========== CHAIN 2-N: VIDEO INTERACTIONS (RANDOM) ==========
        
        opened_profiles = self.parameters.get('opened_profiles', [])
        max_workers = self.parameters.get('max_workers', [])
        #
        # This code to guarantee the profile run enough time to get new proxy (min 6 minutes). 3+ profiles run in minimum 6+ minutes for 2 chain actions
        #
        repeat_count = 2
       
        if int(max_workers) - len(opened_profiles) == 1:
            repeat_count = 6
        elif int(max_workers) - len(opened_profiles) == 2:
            repeat_count = 14
        
        for i in range(repeat_count):
            self._build_video_interaction_chains() 
    
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
        GlobalVariables().set('clicked_second_video', False)
        chain1_actions = []
        
        chain1_actions.append(
            ("delay", 3)  # ← DELAY TUPLE: ("delay", seconds)
        )
        # Action 1: Navigate to YouTube
        chain1_actions.append(
            ("navigate_youtube", YouTubeNavigateAutoAction(self.profile_id, self.log_prefix))
        )        

        GlobalVariables().set('found_video_home', False)
        
        if random.random() < 0.35:
            chain1_actions.append(
                ("move_mouse", YouTubeMouseMoveAutoAction(
                    profile_id=self.profile_id,
                    click=False,
                    log_prefix=self.log_prefix,
                ))
            )
            # Search video hone
            chain1_actions.append(
                ("find_click_video", YouTubeFindClickVideoAutoAction(
                    self.profile_id,
                    self.parameters,     # Pass full keywords dict
                    self.log_prefix,   # log_prefix (positional or keyword)
                    area="main"        # area (keyword argument)
                ))
            )
            

        found_video_home = GlobalVariables().get('found_video_home', False)
        if not found_video_home:
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
                    area="search"        # area (keyword argument)
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
            ("delay", random.uniform(1, 3))  # ← DELAY TUPLE: ("delay", seconds)
        )   

        chain1_actions.append(
            ("skip_ads", YouTubeSkipAdsAutoAction(
                profile_id=self.profile_id,
                parameters=self.parameters,  # Pass keywords dict for ads area params
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
        chain_actions = []    
        self.log(f"Building interaction chains")
        clicked_second_video = GlobalVariables().get('clicked_second_video', False)
        
        if not clicked_second_video:
            # 40% oppotunity to click second video of the channel - sidebar or channel page
            if random.random() < 0.4:
                GlobalVariables().set('clicked_second_video', True)
                clicked_second_video = True
                
                second_video = ['sidebar', 'channel']
                second_video_area = random.choice(second_video)
                if second_video_area == "sidebar":
                    action = YouTubeFindClickVideoAutoAction(
                        self.profile_id,
                        self.parameters,     # Pass full keywords dict
                        self.log_prefix,   # log_prefix (positional or keyword)
                        area="sidebar"        # area (keyword argument)
                    )
                    chain_actions.append(("sidebar", action))                
               
                else:
                    # Scroll small to see the logo channe;
                    action = YouTubeRandomMoveScrollAutoAction(
                        profile_id=self.profile_id,
                        num_actions=1,
                        area="sidebar",
                        log_prefix=self.log_prefix
                    )
                    chain_actions.append(("scroll", action))  
                
                    # Step 1 click logo channel -> If true store to Global Variabel
                    action = YouTubeFindClickVideoAutoAction(
                        self.profile_id,
                        self.parameters,     # Pass full keywords dict
                        self.log_prefix,   # log_prefix (positional or keyword)
                        area="channel"        # area (keyword argument)
                    )
                    chain_actions.append(("channel", action))  
                
                    # Step 2 click menu Videos channel
                    action = YouTubeFindClickVideoAutoAction(
                        self.profile_id,
                        self.parameters,     # Pass full keywords dict
                        self.log_prefix,   # log_prefix (positional or keyword)
                        area="menu_videos_channel"        # area (keyword argument)
                    )
                    chain_actions.append(("menu_videos_channel", action))  
                
                    # Step 3 random click Videos channel
                    action = YouTubeFindClickVideoAutoAction(
                        self.profile_id,
                        self.parameters,     # Pass full keywords dict
                        self.log_prefix,   # log_prefix (positional or keyword)
                        area="video_channel"        # area (keyword argument)
                    )
                    chain_actions.append(("video_channel", action))  
                
                chain_actions.append(
                    ("delay", random.uniform(1, 3))  # ← DELAY TUPLE: ("delay", seconds)
                )
                
                action = YouTubeSkipAdsAutoAction(
                    self.profile_id,
                    self.parameters,     # Pass full keywords dict
                    self.log_prefix,   # log_prefix (positional or keyword)
                )
                chain_actions.append(("skip_ads", action))
                
    
        # If already click second video -> just run 1 loop random action
        if not clicked_second_video:
            num_actions = random.randint(2, 4)
        else:
            num_actions = 1
       
        action_types = ['mouse_move', 'pause_resume', 'fullscreen', 'prev_next']
        
        
        for j in range(num_actions):
            chain_actions.append(
                ("delay", random.randint(2,10))  # ← DELAY TUPLE: ("delay", seconds)
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

