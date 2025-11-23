# controllers/actions/flow_auto/youtube_flow_factory.py

class YouTubeFlowAutoFactory:
    """
    YouTube Auto Flow Factory
    
    Creates appropriate flow iterator based on flow_type.
    Supports: "search" (default), "browse"
    """
    
    @staticmethod
    def create_flow_iterator(profile_id, parameters, log_prefix="[YOUTUBE AUTO]", flow_type="search"):
        """
        Create flow iterator
        
        Args:
            profile_id: GoLogin profile ID
            parameters: FULL parameters dict (from GoLoginAutoAction.params)
                Contains all params including youtube_channels, global settings, etc.
            log_prefix: Log prefix
            flow_type: Flow type - "search" (default) or "browse"
        
        Returns:
            Flow iterator instance (YouTubeFlowAutoIterator or YouTubeFlowAutoBrowseIterator)
        
        Raises:
            ValueError: If flow_type unknown
        """
        if flow_type == "search":
            from controllers.actions.flow_auto.flow_youtube_auto import YouTubeFlowAutoIterator
            return YouTubeFlowAutoIterator(profile_id, parameters, log_prefix)
        
        elif flow_type == "browse":
            from controllers.actions.flow_auto.flow_youtube_browse_auto import YouTubeFlowAutoBrowseIterator
            return YouTubeFlowAutoBrowseIterator(profile_id, parameters, log_prefix)
        
        else:
            raise ValueError(f"Unknown flow_type: '{flow_type}'. Supported: 'search', 'browse'")
