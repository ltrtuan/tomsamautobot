# controllers/actions/image_search_live_action.py
from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
import pyautogui
import time
import cv2
import numpy as np
from PIL import ImageGrab
import os
import tempfile

class ImageSearchLiveAction(BaseAction):
    """Handler để so sánh 2 screenshots để phát hiện thay đổi (video play/pause)"""
    
    def prepare_play(self):
        """Thực hiện so sánh 2 screenshots sau khi trì hoãn"""
        
        try:
            # Lấy parameters
            compare_delay = float(self.params.get("compare_delay", "2"))
            similarity_threshold = float(self.params.get("similarity_threshold", "95"))
            
            # Lấy vùng screenshot
            region = self.get_region()
            x, y, width, height = region
            
            # Tạo region tuple
            screenshot_region = None
            if x > 0 or y > 0 or width > 0 or height > 0:
                screenshot_region = (int(x), int(y), int(width), int(height))
            
            print(f"[IMAGE_SEARCH_LIVE] Taking first screenshot... Region: {screenshot_region}")
            
            # Screenshot 1
            screenshot1 = self.take_screenshot(screenshot_region)
            
            # Delay
            print(f"[IMAGE_SEARCH_LIVE] Waiting {compare_delay} seconds...")
            time.sleep(compare_delay)
            
            # Screenshot 2
            print(f"[IMAGE_SEARCH_LIVE] Taking second screenshot...")
            screenshot2 = self.take_screenshot(screenshot_region)
            
            # So sánh 2 screenshots
            is_similar, similarity_score = self.compare_screenshots(
                screenshot1, 
                screenshot2, 
                similarity_threshold
            )
            
            print(f"[IMAGE_SEARCH_LIVE] Similarity: {similarity_score:.2f}% | Threshold: {similarity_threshold}%")
            print(f"[IMAGE_SEARCH_LIVE] Result: {'SIMILAR (pause)' if is_similar else 'DIFFERENT (playing)'}")
            
            # Gán vào variable
            variable = self.params.get("variable", "")
            if variable:
                GlobalVariables().set(variable, "true" if is_similar else "false")
                print(f"[IMAGE_SEARCH_LIVE] Set variable '{variable}' = {'true' if is_similar else 'false'}")
            
            # ← SỬA PHẦN NÀY: Di chuyển chuột ngẫu nhiên trong vùng
            import random
        
            if screenshot_region:
                # Random position trong vùng screenshot
                x, y, width, height = screenshot_region
            
                # Margin 10% từ mỗi cạnh (tùy chọn)
                margin_x = int(width * 0.1) if width > 20 else 0
                margin_y = int(height * 0.1) if height > 20 else 0
            
                # Random x, y
                safe_width = max(1, width - 2 * margin_x)
                safe_height = max(1, height - 2 * margin_y)
            
                random_x = x + margin_x + random.randint(0, safe_width)
                random_y = y + margin_y + random.randint(0, safe_height)
            
                print(f"[IMAGE_SEARCH_LIVE] Moving mouse to random position in region: ({random_x}, {random_y})")
            else:
                # Nếu không có region, random trong toàn màn hình
                screen_width, screen_height = pyautogui.size()
                random_x = random.randint(50, screen_width - 50)
                random_y = random.randint(50, screen_height - 50)
            
                print(f"[IMAGE_SEARCH_LIVE] Moving mouse to random position (full screen): ({random_x}, {random_y})")
        
            self.move_mouse(random_x, random_y, 1, 1)
            
        except Exception as e:
            print(f"[IMAGE_SEARCH_LIVE] Error: {e}")
            import traceback
            traceback.print_exc()
            
            # Set variable = false nếu có lỗi
            variable = self.params.get("variable", "")
            if variable:
                GlobalVariables().set(variable, "false")
    
    def take_screenshot(self, region=None):
        """
        Chụp screenshot và return numpy array
        
        Args:
            region: (x, y, width, height) hoặc None cho toàn màn hình
        
        Returns:
            numpy array của screenshot
        """
        if region:
            x, y, width, height = region
            screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        else:
            screenshot = ImageGrab.grab()
        
        # Convert to numpy array
        screenshot_np = np.array(screenshot)
        
        # Convert RGB to BGR (OpenCV format)
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        return screenshot_bgr
    
    def compare_screenshots(self, img1, img2, threshold):
        """
        So sánh 2 screenshots và trả về kết quả
    
        Args:
            img1: numpy array của screenshot 1
            img2: numpy array của screenshot 2
            threshold: Ngưỡng phần trăm (0-100)
    
        Returns:
            tuple: (is_similar: bool, similarity_score: float)
                - is_similar: True nếu giống nhau, False nếu khác
                - similarity_score: Điểm tương đồng (0-100)
        """
        try:
            # Đảm bảo 2 ảnh cùng kích thước
            if img1.shape != img2.shape:
                print(f"[IMAGE_SEARCH_LIVE] Shape mismatch: {img1.shape} vs {img2.shape}")
                return False, 0.0
        
            # Convert to grayscale first (for all methods)
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
            # ← FIX: Try SSIM method
            try:
                from skimage.metrics import structural_similarity as ssim
            
                # Calculate SSIM với data_range
                similarity_index = ssim(gray1, gray2, data_range=gray1.max() - gray1.min())
                similarity_score = similarity_index * 100  # Convert to percentage
            
                print(f"[IMAGE_SEARCH_LIVE] Using SSIM method | SSIM: {similarity_index:.4f}")
            
                # ← QUAN TRỌNG: SSIM rất nhạy, threshold nên thấp hơn
                # SSIM > 0.95 (95%) = rất giống → video pause
                # SSIM < 0.95 (95%) = khác biệt → video playing
                is_similar = similarity_score >= threshold
            
                return is_similar, similarity_score
            
            except ImportError as e:
                print(f"[IMAGE_SEARCH_LIVE] Cannot import SSIM: {e}")
                print("[IMAGE_SEARCH_LIVE] Using pixel difference method instead")
            except Exception as e:
                print(f"[IMAGE_SEARCH_LIVE] SSIM error: {e}, falling back to pixel diff")
        
            # ← FALLBACK: Improved pixel difference detection
            # Calculate absolute difference
            diff = cv2.absdiff(gray1, gray2)
        
            # Threshold to detect significant changes (ignore small noise)
            # Pixels with diff > 30 are considered "changed"
            _, binary_diff = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        
            # Count changed pixels
            changed_pixels = np.count_nonzero(binary_diff)
            total_pixels = gray1.shape[0] * gray1.shape[1]
        
            # Calculate percentage of unchanged pixels
            unchanged_ratio = (total_pixels - changed_pixels) / total_pixels
            similarity_score = unchanged_ratio * 100
        
            changed_percent = (changed_pixels / total_pixels) * 100
            print(f"[IMAGE_SEARCH_LIVE] Pixel diff method | Changed: {changed_pixels}/{total_pixels} ({changed_percent:.2f}%)")
        
            is_similar = similarity_score >= threshold
        
            return is_similar, similarity_score
        
        except Exception as e:
            print(f"[IMAGE_SEARCH_LIVE] Error in comparison: {e}")
            import traceback
            traceback.print_exc()
            return False, 0.0

