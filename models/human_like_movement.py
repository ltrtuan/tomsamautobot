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
    def move_cursor(start_x, start_y, end_x, end_y, speed_factor=1.0, stop_check=None):
        """Di chuyển chuột theo đường cong tự nhiên với tốc độ ngẫu nhiên"""
        # Tính toán các điểm kiểm soát cho đường cong
        distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        
        # Kiểm tra xem có cần di chuyển siêu nhanh không
        if speed_factor > 5.0:
            return HumanLikeMovement.move_cursor_fast(start_x, start_y, end_x, end_y, stop_check)
        
        # QUAN TRỌNG: Đảo ngược logic speed_factor - chia thay vì nhân
        # Số bước giảm khi speed_factor tăng
        steps = int(distance * random.uniform(0.3, 0.5) / max(speed_factor, 0.1))
        steps = min(max(steps, 3), 25)  # Giới hạn trong khoảng 3-25 bước
        
        # Tạo độ lệch ngẫu nhiên cho các điểm điều khiển - giảm biên độ cho chuyển động nhanh
        offset_factor = min(0.2, 1.0 / speed_factor)  # Giảm offset khi tốc độ tăng
        offset_x = random.uniform(-offset_factor, offset_factor) * distance
        offset_y = random.uniform(-offset_factor, offset_factor) * distance
        
        # Các điểm điều khiển cho đường cong Bezier
        p0 = (start_x, start_y)
        p3 = (end_x, end_y)
        p1 = (start_x + distance/3 + offset_x, start_y + offset_y)
        p2 = (end_x - distance/3 + offset_x, end_y + offset_y)
        
        # Di chuyển chuột theo đường cong
        for i in range(steps + 1):
            # Kiểm tra điều kiện dừng nếu có
            if stop_check and stop_check():
                return False
                
            t = i / steps
            
            # Vị trí chuột tại thời điểm t trên đường cong
            x = HumanLikeMovement._bezier_curve(t, p0[0], p1[0], p2[0], p3[0])
            y = HumanLikeMovement._bezier_curve(t, p0[1], p1[1], p2[1], p3[1])
            
            # Di chuyển chuột
            pyautogui.moveTo(x, y)
            
            # Bỏ qua delay ở một số bước để tăng tốc
            if i % 2 == 0 or speed_factor < 1.0:  # Chỉ delay ở mỗi bước thứ 2 nếu tốc độ cao
                # Tốc độ không đều (chậm lại ở điểm bắt đầu và kết thúc)
                if i < steps * 0.2 or i > steps * 0.8:
                    delay = random.uniform(0.0005, 0.001) / speed_factor
                else:
                    delay = random.uniform(0.0001, 0.0005) / speed_factor
                
                time.sleep(delay)
        
        return True
    
    @staticmethod
    def move_cursor_fast(start_x, start_y, end_x, end_y, stop_check=None):
        """Phương thức di chuyển siêu nhanh với ít bước và delay cực thấp"""
        distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        
        # Số bước rất thấp cho di chuyển nhanh
        steps = min(max(int(distance/20), 2), 10)
        
        # Di chuyển theo đường thẳng với chút nhiễu
        for i in range(steps + 1):
            if stop_check and stop_check():
                return False
                
            t = i / steps
            
            # Thêm chút nhiễu nhỏ để trông tự nhiên nhưng vẫn nhanh
            rand_x = random.uniform(-1, 1) 
            rand_y = random.uniform(-1, 1)
            
            x = start_x + t * (end_x - start_x) + rand_x
            y = start_y + t * (end_y - start_y) + rand_y
            
            pyautogui.moveTo(x, y)
            
            # Chỉ delay ở bước đầu và cuối để trông tự nhiên
            if i == 0 or i == steps:
                time.sleep(0.001)
        
        return True
