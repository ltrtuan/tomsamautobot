# controllers/actions/flow_auto/base_youtube_flow_auto.py

import time
import random
import os
from helpers.gologin_profile_helper import GoLoginProfileHelper


class BaseYouTubeFlowAutoIterator:
    """
    Base YouTube Auto Flow Iterator
    Compatible with round-robin execution pattern
    
    Provides common initialization and chain execution logic.
    """
    
    def __init__(self, profile_id, parameters, log_prefix="[YOUTUBE AUTO]"):
        """
        Initialize YouTube Auto Flow Iterator
    
        Args:
            profile_id: GoLogin profile ID
            parameters: FULL parameters dict (from GoLoginAutoAction.params)
                Contains all params including:
                - youtube_channels: Array of channel configs (MANDATORY)
                - youtube_area_x/y/width/height: Main area coords
                - youtube_sidebar_area_x/y/width/height: Sidebar coords
                - youtube_search_icon_path: Search icon path
                - ... (other params)
            log_prefix: Prefix for log messages
        """
        self.profile_id = profile_id
        self.parameters = parameters
        self.log_prefix = log_prefix
    
        # ========== MULTI-CHANNEL LOGIC ==========
        # Select random enabled channel (MANDATORY)
        self.selected_channel = self._select_random_channel()
    
        if self.selected_channel:
            # Load channel-specific data
            success = self._load_channel_data(self.selected_channel)
        
            if success:
                channel_index = self.selected_channel.get('channel_index', '?')
                logo_path = self.selected_channel.get('logo_path', 'N/A')
                self.log(f"Multi-Channel: Selected Channel {channel_index} (Logo: {logo_path})")
            else:
                # Keywords load failed - will skip search actions
                self.log("Multi-Channel: Channel selected but keywords load failed - search actions will be skipped", "WARNING")
        else:
            # No channels available - critical error
            self.log("Multi-Channel: No channels available! Flow cannot execute properly.", "ERROR")
        # =========================================
    
        # Window info (cached)
        self.window_info = None
    
        # Build chain queue (subclass must implement _build_chain_queue)
        self.chain_queue = []
        self.current_chain_index = 0
        self._build_chain_queue()
    
        self.total_chains = len(self.chain_queue)
        self.log(f"Initialized with {self.total_chains} total chains")


        
        
    def _select_random_channel(self):
        """
        Select random enabled channel from youtube_channels array
    
        Returns:
            dict: Selected channel data or None if no enabled channels
        """
        channels = self.parameters.get("youtube_channels", [])
    
        if not channels:
            return None
    
        # Filter enabled channels only
        enabled_channels = [ch for ch in channels if ch.get("enabled", True)]
    
        if not enabled_channels:
            self.log("No enabled channels found!", "WARNING")
            return None
    
        # Select random channel
        selected = random.choice(enabled_channels)
    
        return selected
    

    def _load_channel_data(self, channel):
        """
        Load channel-specific data and override parameters dict
    
        Args:
            channel (dict): Selected channel data
                {
                    "channel_id": "ch_1",
                    "channel_index": 1,
                    "enabled": True,
                    "logo_path": "logo1.png",
                    "main_image_search_path": "main1.png",
                    "sidebar_image_search_path": "sidebar1.png",
                    "suffix_prefix": "watch; how to",
                    "keywords_file_path": "keywords1.txt"
                }
    
        Returns:
            bool: True if keywords loaded successfully, False otherwise
        """
        # ========== LOAD KEYWORDS FROM FILE ==========
        keywords_file_path = channel.get("keywords_file_path", "")
    
        if not keywords_file_path:
            self.log("No keywords file specified for this channel", "ERROR")
            self.parameters["keywords_youtube"] = []  # Set empty list
            return False
    
        try:
            with open(keywords_file_path, 'r', encoding='utf-8') as f:
                keywords_list = [line.strip() for line in f if line.strip()]
        
            if not keywords_list:
                self.log(f"Keywords file is empty: {keywords_file_path}", "ERROR")
                self.parameters["keywords_youtube"] = []
                return False
        
            # ✅ UPDATE DICT (NO instance variable)
            self.parameters["keywords_youtube"] = keywords_list
            self.log(f"Loaded {len(keywords_list)} keywords from: {keywords_file_path}")
        
        except FileNotFoundError:
            self.log(f"Keywords file not found: {keywords_file_path}", "ERROR")
            self.parameters["keywords_youtube"] = []
            return False
        
        except Exception as e:
            self.log(f"Error reading keywords file '{keywords_file_path}': {e}", "ERROR")
            self.parameters["keywords_youtube"] = []
            return False
    
        # ========== OVERRIDE SUFFIX/PREFIX ==========
        self.parameters["suffix_prefix"] = channel.get("suffix_prefix", "")
    
        # ========== OVERRIDE IMAGE PATHS ==========
        self.parameters["youtube_image_search_path"] = channel.get("main_image_search_path", "")
        self.parameters["youtube_sidebar_image_search_path"] = channel.get("sidebar_image_search_path", "")
    
        # ========== STORE LOGO PATH (for future use) ==========
        self.parameters["youtube_channel_logo_path"] = channel.get("logo_path", "")
    
        self.log(f"Channel params overridden: "
                 f"keywords={len(self.parameters.get('keywords_youtube', []))}, "
                 f"suffix='{self.parameters.get('suffix_prefix', '')}', "
                 f"main_image='{self.parameters.get('youtube_image_search_path', 'N/A')}', "
                 f"sidebar_image='{self.parameters.get('youtube_sidebar_image_search_path', 'N/A')}'")
    
        return True




        
    def _build_chain_queue(self):
        """Build chain queue (abstract - subclass must implement)"""
        raise NotImplementedError("Subclass must override _build_chain_queue()")

    def _build_search_and_start_video_chain(self):
        """Build search and start video chain (abstract - subclass must implement)"""
        raise NotImplementedError("Subclass must override _build_search_and_start_video_chain()")
    
    def _build_video_interaction_chains(self):
        """Build video interaction chains (abstract - subclass must implement)"""
        raise NotImplementedError("Subclass must override _build_video_interaction_chains()")
    
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
            result_bring = GoLoginProfileHelper.bring_profile_to_front(self.profile_id, driver=None)
            if result_bring:
                time.sleep(1)
        
                # ========== EXECUTE ALL ACTIONS IN CHAIN ==========
                for action_name, action_obj in chain_actions:
                    # Check if this is a delay tuple
                    if action_name == "delay":
                        delay_seconds = action_obj  # action_obj is actually the delay value
                        self.log(f" → Delay: {delay_seconds:.1f} seconds")
                        time.sleep(delay_seconds)
                        continue  # Skip to next action
    
                    # Normal action execution
                    self.log(f" → Action: {action_name}")
                    if action_obj:
                        success = action_obj.execute()
                        if not success:
                            self.log(f" ✗ Action '{action_name}' failed", "WARNING")
                        else:
                            self.log(f" ✓ Action '{action_name}' completed")

        
                self.log(f"✓ Chain '{chain_name}' completed")
        
                # Move to next chain
                self.current_chain_index += 1
        
                return True
            
            return False
        
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
