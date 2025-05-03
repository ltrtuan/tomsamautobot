from views.action_params.base_params import BaseActionParams
import tkinter as tk
from tkinter import ttk
import config as cfg

class TaoBienParams(BaseActionParams):
    def __init__(self, parent_frame, parameters=None):
        """
        Create UI for mouse movement parameters
        
        Args:
            parent_frame: The parent frame to place UI elements
            parameters: Dictionary containing parameters (if editing an action)
        """
        super().__init__(parent_frame, parameters)
        
    def create_params(self):
        """Create UI for mouse movement parameters"""
        # Clear any existing widgets
        self.clear_frame()            
      
        # ========== PHẦN THAM SỐ CHUNG ==========
        self.create_common_params(show_result_action=True)
        return {}
        
