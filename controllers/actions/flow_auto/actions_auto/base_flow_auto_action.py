# controllers/actions/flow_auto/actions_auto/base_flow_auto_action.py

import time
import random
import pyautogui

class BaseFlowAutoAction:
    """
    Base class cho tất cả Auto Flow Actions
    Chứa các helper methods chung
    """
    
    def __init__(self, profile_id, log_prefix="[AUTO ACTION]"):
        """
        Initialize base action
        
        Args:
            profile_id: GoLogin profile ID
            log_prefix: Prefix for log messages
        """
        self.profile_id = profile_id
        self.log_prefix = log_prefix
    
    # ========== TYPING METHODS ==========
    
    def _type_human_like(self, text):
        """
        Type text with human-like delays
        
        Args:
            text: Text to type
        """
        for char in text:
            pyautogui.write(char)
            
            # 70% fast typing, 30% slow typing (more human-like)
            if random.random() < 0.7:
                time.sleep(random.uniform(0.05, 0.15))
            else:
                time.sleep(random.uniform(0.15, 0.25))
    
    def _type_with_mistakes(self, text, mistake_rate=0.05):
        """
        Type text with occasional mistakes and corrections (more realistic)
        
        Args:
            text: Text to type
            mistake_rate: Probability of making a mistake (0-1)
        """
        for i, char in enumerate(text):
            # Random chance to make a typo
            if random.random() < mistake_rate and i > 0:
                # Type wrong character
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                pyautogui.write(wrong_char)
                time.sleep(random.uniform(0.05, 0.1))
                
                # Realize mistake, backspace
                pyautogui.press('backspace')
                time.sleep(random.uniform(0.1, 0.2))
            
            # Type correct character
            pyautogui.write(char)
            
            # Human-like delay
            if random.random() < 0.7:
                time.sleep(random.uniform(0.05, 0.15))
            else:
                time.sleep(random.uniform(0.15, 0.25))
    
    # ========== CURSOR CHECKING ==========
    
    def _is_hand_cursor(self):
        """
        Check if cursor is hand pointer (clickable element)
        
        Returns:
            bool: True if hand cursor
        """
        try:
            import win32gui
            time.sleep(0.1)
            
            cursor_info = win32gui.GetCursorInfo()
            hand_cursor_handles = [32649, 65567, 65563, 65561, 60171, 60169, 32513]
            
            return cursor_info[1] in hand_cursor_handles
        except Exception as e:
            self.log(f"Error checking cursor: {e}", "WARNING")
            return False
    
    # ========== RANDOM DELAYS ==========
    
    def _random_delay(self, min_seconds=0.5, max_seconds=2.0):
        """
        Random delay to simulate human behavior
        
        Args:
            min_seconds: Minimum delay
            max_seconds: Maximum delay
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def _random_short_pause(self):
        """Random short pause (0.1-0.3s)"""
        time.sleep(random.uniform(0.1, 0.3))
    
    def _random_thinking_pause(self):
        """Random thinking pause (0.5-1.5s)"""
        time.sleep(random.uniform(0.5, 1.5))
        
    # ========== KEYWORD GENERATION (REUSABLE) ==========

    def _generate_keyword(self, keywords):
        """
        Generate keyword with variation (giống Non-Auto version)
        Reusable cho YouTube Search, Google Search, etc.
    
        Args:
            keywords: Dict containing keywords_youtube/keywords_google and suffix_prefix
        
        Returns:
            str: Final keyword with suffix/prefix or None
        """
        try:
            # Get keywords list (support both youtube and google)
            keywords_list = keywords.get('keywords_youtube', []) or keywords.get('keywords_google', [])
        
            if not keywords_list:
                self.log("No keywords in params", "WARNING")
                return None
        
            # Random chọn 1 keyword
            keyword = random.choice(keywords_list)
            self.log(f"Selected base keyword: '{keyword}'")
        
            # Get suffix_prefix string
            suffix_prefix_string = keywords.get('suffix_prefix', '')
        
            if not suffix_prefix_string:
                # No variation, return original keyword
                return keyword
        
            # Parse suffix_prefix thành list
            from helpers.keyword_variation_helper import KeywordVariationHelper
            suffix_prefix_list = KeywordVariationHelper.parse_suffix_prefix_list(suffix_prefix_string)
        
            # Generate keyword variation
            final_keyword = KeywordVariationHelper.generate_keyword_variation(
                keyword, suffix_prefix_list
            )
        
            self.log(f"Generated keyword variation: '{final_keyword}'")
            return final_keyword
        
        except Exception as e:
            self.log(f"Error generating keyword: {e}", "ERROR")
            import traceback
            traceback.print_exc()
        
            # Fallback: return first keyword if available
            keywords_list = keywords.get('keywords_youtube', []) or keywords.get('keywords_google', [])
            if keywords_list:
                return keywords_list[0]
            return None

    # ========== IMAGE DETECTION (REUSABLE) ==========

    def _find_image_on_screen(self, image_path, region=None, accuracy=0.7, click_offset_x=0, click_offset_y=0):
        """
        Find image on screen using template matching
        Reusable cho search icon, channel logo, button detection, etc.
    
        Args:
            image_path: Path to template image
            region: Search region (x, y, width, height) or None for full screen
            accuracy: Match accuracy (0.0 - 1.0) - will be converted to 0-100 for ImageSearcher
            click_offset_x: X offset from found image center (for clickable area)
            click_offset_y: Y offset from found image center (for clickable area)
    
        Returns:
            dict: {
                'found': bool,
                'center': (x, y),  # Center of found image
                'click_position': (x, y)  # Position with offset applied
            } or None if not found
        """
        try:
            from models.image_search import ImageSearcher
        
            # Convert accuracy from 0-1 to 0-100 (ImageSearcher expects percentage)
            accuracy_percent = accuracy * 100
        
            # Create searcher with image_path, region, and accuracy
            searcher = ImageSearcher(
                image_path=image_path,
                region=region,
                accuracy=accuracy_percent
            )
        
            # Search returns: (success: bool, result: tuple or None)
            success, result = searcher.search()
        
            if success and result:
                center_x, center_y, confidence = result
                click_x = center_x + click_offset_x
                click_y = center_y + click_offset_y
            
                self.log(f"✓ Found image at ({center_x}, {center_y}), confidence: {confidence:.2f}, click position: ({click_x}, {click_y})")
            
                return {
                    'found': True,
                    'center': (center_x, center_y),
                    'click_position': (click_x, click_y),
                    'confidence': confidence
                }
            else:
                self.log(f"Image not found: {image_path}")
                return None
            
        except Exception as e:
            self.log(f"Image detection error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return None


    def _find_multiple_images(self, image_path, region=None, accuracy=0.7):
        """
        Find all occurrences of image on screen
        Useful for finding multiple channel logos, buttons, etc.
    
        Args:
            image_path: Path to template image
            region: Search region (x, y, width, height) or None for full screen
            accuracy: Match accuracy (0.0 - 1.0)
        
        Returns:
            list: List of dicts with 'center' and 'click_position', or empty list
        """
        try:
            import pyautogui
        
            # Find all matches
            matches = list(pyautogui.locateAllOnScreen(image_path, confidence=accuracy, region=region))
        
            if not matches:
                self.log(f"No matches found for: {image_path}", "WARNING")
                return []
        
            results = []
            for match in matches:
                center_x = match.left + (match.width // 2)
                center_y = match.top + (match.height // 2)
            
                results.append({
                    'center': (center_x, center_y),
                    'click_position': (center_x, center_y),
                    'bbox': (match.left, match.top, match.width, match.height)
                })
        
            self.log(f"✓ Found {len(results)} matches")
            return results
        
        except Exception as e:
            self.log(f"Multiple image detection error: {e}", "ERROR")
            return []



    # ========== LOGGING ==========
    
    def log(self, message, level="INFO"):
        """
        Log message with prefix
        
        Args:
            message: Log message
            level: Log level (INFO, WARNING, ERROR, DEBUG)
        """
        print(f"{self.log_prefix} [{level}] {message}")
    
    # ========== ABSTRACT METHOD ==========
    
    def execute(self):
        """
        Execute action (must be implemented by subclass)
        
        Returns:
            bool: True if successful, False otherwise
        """
        raise NotImplementedError("Subclass must implement execute() method")
