import cv2
import numpy as np
import pyautogui
import random
import time
import os
from PIL import ImageGrab


class ImageSearcher:
    """Class thực hiện tìm kiếm hình ảnh trên màn hình"""
    def __init__(self, image_path, region=None, accuracy=0.8):
        self.image_path = image_path
        self.region = region  # (x, y, width, height)
        self.accuracy = float(accuracy) / 100  # Chuyển đổi từ phần trăm (0-100) sang tỷ lệ (0-1)
        
        # Đảm bảo file hình ảnh tồn tại
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Đọc hình ảnh template
        self.template = cv2.imread(image_path, cv2.IMREAD_COLOR)
        
        if self.template is None:
            raise ValueError(f"Could not load image: {image_path}")
            
        # Chuyển về RGB để so sánh với screenshot
        self.template = cv2.cvtColor(self.template, cv2.COLOR_BGR2RGB)
    
    def search(self):
        """Tìm kiếm hình ảnh trên màn hình và trả về kết quả"""
        try:
            # Chụp màn hình
            if self.region:
                x, y, width, height = self.region
                x, y, width, height = int(float(x)), int(float(y)), int(float(width)), int(float(height))
                
                # Đảm bảo kích thước hợp lệ
                if width <= 0 or height <= 0:
                    screenshot = ImageGrab.grab()
                else:
                    screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            else:
                screenshot = ImageGrab.grab()
                
            # Chuyển về numpy array
            screenshot_np = np.array(screenshot)
            
            # Đảm bảo kích thước template phù hợp với screenshot
            h, w = self.template.shape[:2]
            screenshot_h, screenshot_w = screenshot_np.shape[:2]
            
            if h > screenshot_h or w > screenshot_w:
                return False, None
            
            # Tìm template trong screenshot
            result = cv2.matchTemplate(screenshot_np, self.template, cv2.TM_CCOEFF_NORMED)
            
            # Lấy vị trí và độ tin cậy cao nhất
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Kiểm tra nếu kết quả tốt hơn hoặc bằng ngưỡng accuracy
            if max_val >= self.accuracy:
                # Tính toán vị trí trung tâm của template
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                
                # Điều chỉnh tọa độ nếu sử dụng region
                if self.region:
                    center_x += x
                    center_y += y
                    
                return True, (center_x, center_y, max_val)
        except Exception as e:
            print(f"Error during image search: {e}")
            
        return False, None