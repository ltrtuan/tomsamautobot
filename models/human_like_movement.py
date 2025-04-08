import math
import random
import time
import pyautogui

class HumanLikeMovement:
    """Tạo chuyển động chuột tự nhiên như người"""
    
    @staticmethod
    def _bezier_curve(t, p0, p1, p2, p3):
        """Tính điểm trên đường cong Bezier bậc 3"""
        return (
            (1-t)**3 * p0 +
            3 * (1-t)**2 * t * p1 +
            3 * (1-t) * t**2 * p2 +
            t**3 * p3
        )
        
    @staticmethod
    def move_cursor(start_x, start_y, end_x, end_y, speed_factor=1.0):
        """Di chuyển chuột theo đường cong tự nhiên với tốc độ ngẫu nhiên"""
        # Tính toán các điểm kiểm soát cho đường cong
        distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        
        # Tạo độ lệch ngẫu nhiên cho các điểm điều khiển
        offset_x = random.uniform(-0.5, 0.5) * distance
        offset_y = random.uniform(-0.5, 0.5) * distance
        
        # Các điểm điều khiển cho đường cong Bezier
        p0 = (start_x, start_y)
        p3 = (end_x, end_y)
        p1 = (start_x + distance/3 + offset_x, start_y + offset_y)
        p2 = (end_x - distance/3 + offset_x, end_y + offset_y)
        
        # Tính số bước dựa vào khoảng cách và tốc độ
        steps = int(distance * random.uniform(0.8, 1.2) * speed_factor)
        steps = max(steps, 10)  # Ít nhất 10 bước
        
        # Di chuyển chuột theo đường cong
        for i in range(steps + 1):
            t = i / steps
            
            # Vị trí chuột tại thời điểm t trên đường cong
            x = HumanLikeMovement._bezier_curve(t, p0[0], p1[0], p2[0], p3[0])
            y = HumanLikeMovement._bezier_curve(t, p0[1], p1[1], p2[1], p3[1])
            
            # Tốc độ không đều (chậm lại ở điểm bắt đầu và kết thúc)
            if i < steps * 0.2 or i > steps * 0.8:
                delay = random.uniform(0.01, 0.02) / speed_factor
            else:
                delay = random.uniform(0.005, 0.01) / speed_factor
                
            # Di chuyển chuột
            pyautogui.moveTo(x, y)
            time.sleep(delay)
