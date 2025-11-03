# controllers/actions/flow_auto/flow_youtube_auto.py

import time
import random
import os
from helpers.gologin_profile_helper import GoLoginProfileHelper


class BaseYouTubeFlowAutoIterator:
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
        """Build chain queue (abstract - subclass must implement)"""
        raise NotImplementedError("Subclass must override _build_chain_queue()")

    def _build_search_and_start_video_chain(self):
        """Build chain 1 (abstract - subclass must implement)"""
        raise NotImplementedError("Subclass must override _build_search_and_start_video_chain()")
    
    def _build_video_interaction_chains(self):
        """Build chain 1 (abstract - subclass must implement)"""
        raise NotImplementedError("Subclass must override _build_search_and_start_video_chain()")
    
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
