import math
import random
import time
import pyautogui


class HumanLikeMovement:
    """Tạo chuyển động chuột tự nhiên như người với 10 styles khác nhau"""

    @staticmethod
    def _bezier_curve(t, p0, p1, p2, p3):
        """Tính điểm trên đường cong Bezier bậc 3"""
        return (
            (1-t)**3 * p0 +
            3 * (1-t)**2 * t * p1 +
            3 * (1-t) * t**2 * p2 +
            t**3 * p3
        )

    # ==================== 10 STYLES ====================
    
    @staticmethod
    def _bezier_path(start, end):
        """Style 1: Đường cong Bezier mượt mà"""
        path = []
        distance = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        steps = random.randint(15, 25)
        
        offset_x = random.uniform(-0.3, 0.3) * distance
        offset_y = random.uniform(-0.3, 0.3) * distance
        
        p0 = start
        p3 = end
        p1 = (start[0] + distance/3 + offset_x, start[1] + offset_y)
        p2 = (end[0] - distance/3 + offset_x, end[1] + offset_y)
        
        for i in range(steps + 1):
            t = i / steps
            x = HumanLikeMovement._bezier_curve(t, p0[0], p1[0], p2[0], p3[0])
            y = HumanLikeMovement._bezier_curve(t, p0[1], p1[1], p2[1], p3[1])
            
            if i < steps * 0.2 or i > steps * 0.8:
                pause = random.uniform(0.001, 0.003)
            else:
                pause = random.uniform(0.0005, 0.002)
            
            path.append((x, y, pause))
        
        return path

    @staticmethod
    def _fast_line_path(start, end):
        """Style 2: Đường thẳng nhanh với nhiễu nhẹ"""
        path = []
        distance = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        steps = random.randint(8, 15)
        
        for i in range(steps + 1):
            t = i / steps
            noise_x = random.uniform(-2, 2)
            noise_y = random.uniform(-2, 2)
            x = start[0] + t * (end[0] - start[0]) + noise_x
            y = start[1] + t * (end[1] - start[1]) + noise_y
            pause = random.uniform(0.0005, 0.002)
            path.append((x, y, pause))
        
        return path

    @staticmethod
    def _zigzag_path(start, end):
        """Style 3: Đi zigzag từ A đến B"""
        path = []
        segments = random.randint(4, 7)
        amplitude = random.uniform(20, 50)
        
        dx = (end[0] - start[0]) / segments
        dy = (end[1] - start[1]) / segments
        
        for i in range(segments + 1):
            if i == 0:
                x, y = start
            elif i == segments:
                x, y = end
            else:
                x = start[0] + dx * i
                offset = amplitude if i % 2 == 0 else -amplitude
                y = start[1] + dy * i + offset
            
            pause = random.uniform(0.005, 0.015)
            path.append((x, y, pause))
        
        return path

    @staticmethod
    def _circle_arc_path(start, end):
        """Style 4: Đi theo vòng cung hoặc vòng tròn"""
        path = []
        mid = ((start[0] + end[0])/2, (start[1] + end[1])/2)
        radius = random.uniform(30, 80)
        points = random.randint(10, 16)
        angle_start = random.uniform(0, math.pi * 2)
        
        path.append((start[0], start[1], random.uniform(0.002, 0.005)))
        
        for i in range(1, points):
            angle = angle_start + i * (2 * math.pi / points)
            x = mid[0] + radius * math.cos(angle)
            y = mid[1] + radius * math.sin(angle)
            pause = random.uniform(0.003, 0.008)
            path.append((x, y, pause))
        
        path.append((end[0], end[1], random.uniform(0.002, 0.005)))
        return path

    @staticmethod
    def _random_waypoints_path(start, end):
        """Style 5: Đi qua nhiều waypoint ngẫu nhiên"""
        path = []
        waypoints = random.randint(3, 6)
        
        path.append((start[0], start[1], random.uniform(0.001, 0.003)))
        
        for _ in range(waypoints):
            x = random.uniform(min(start[0], end[0]) - 50, max(start[0], end[0]) + 50)
            y = random.uniform(min(start[1], end[1]) - 50, max(start[1], end[1]) + 50)
            pause = random.uniform(0.005, 0.02)
            path.append((x, y, pause))
        
        path.append((end[0], end[1], random.uniform(0.001, 0.003)))
        return path

    @staticmethod
    def _right_angle_path(start, end):
        """Style 6: Đi theo hình chữ L (góc vuông)"""
        path = []
        
        # Random chọn đi ngang trước hay dọc trước
        if random.choice([True, False]):
            # Ngang trước
            mid = (end[0], start[1])
        else:
            # Dọc trước
            mid = (start[0], end[1])
        
        # Từ start đến mid
        steps1 = random.randint(10, 15)
        for i in range(steps1 + 1):
            t = i / steps1
            x = start[0] + t * (mid[0] - start[0])
            y = start[1] + t * (mid[1] - start[1])
            pause = random.uniform(0.002, 0.006)
            path.append((x, y, pause))
        
        # Dừng tại góc
        path.append((mid[0], mid[1], random.uniform(0.05, 0.15)))
        
        # Từ mid đến end
        steps2 = random.randint(10, 15)
        for i in range(1, steps2 + 1):
            t = i / steps2
            x = mid[0] + t * (end[0] - mid[0])
            y = mid[1] + t * (end[1] - mid[1])
            pause = random.uniform(0.002, 0.006)
            path.append((x, y, pause))
        
        return path

    @staticmethod
    def _square_around_path(start, end):
        """Style 7: Đi lệch ra ngoài tạo hình vuông rồi về B"""
        path = []
        
        offset = random.uniform(40, 80)
        corner1 = (start[0] + offset, start[1])
        corner2 = (start[0] + offset, end[1])
        
        waypoints = [start, corner1, corner2, end]
        
        for i, point in enumerate(waypoints):
            if i == 0:
                path.append((point[0], point[1], random.uniform(0.001, 0.003)))
            else:
                prev = waypoints[i-1]
                steps = random.randint(8, 12)
                for j in range(1, steps + 1):
                    t = j / steps
                    x = prev[0] + t * (point[0] - prev[0])
                    y = prev[1] + t * (point[1] - prev[1])
                    pause = random.uniform(0.003, 0.008)
                    path.append((x, y, pause))
        
        return path

    @staticmethod
    def _spiral_in_path(start, end):
        """Style 8: Chuyển động xoắn ốc hẹp dần về điểm cuối"""
        path = []
        mid = ((start[0] + end[0])/2, (start[1] + end[1])/2)
        
        turns = random.uniform(1.5, 3)
        points = random.randint(20, 30)
        max_radius = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2) / 2
        
        for i in range(points + 1):
            t = i / points
            angle = t * turns * 2 * math.pi
            radius = max_radius * (1 - t)
            
            x = mid[0] + radius * math.cos(angle) + t * (end[0] - mid[0])
            y = mid[1] + radius * math.sin(angle) + t * (end[1] - mid[1])
            pause = random.uniform(0.002, 0.006)
            path.append((x, y, pause))
        
        return path

    @staticmethod
    def _step_stutter_path(start, end):
        """Style 9: Di chuyển từng đoạn ngắn, dừng lại, lặp lại (giống lag)"""
        path = []
        segments = random.randint(5, 9)
        
        for i in range(segments + 1):
            t = i / segments
            x = start[0] + t * (end[0] - start[0])
            y = start[1] + t * (end[1] - start[1])
            
            # Move nhanh đến điểm
            path.append((x, y, random.uniform(0.001, 0.003)))
            
            # Dừng lại lâu (stutter)
            if i < segments:
                path.append((x, y, random.uniform(0.1, 0.3)))
        
        return path

    @staticmethod
    def _multi_pause_path(start, end):
        """Style 10: Đi thẳng/curve nhưng dừng ngẫu nhiên nhiều lần"""
        path = []
        steps = random.randint(15, 25)
        pause_points = random.sample(range(1, steps), random.randint(3, 5))
        
        for i in range(steps + 1):
            t = i / steps
            # Thêm chút curve
            curve_offset = math.sin(t * math.pi) * random.uniform(10, 30)
            x = start[0] + t * (end[0] - start[0]) + curve_offset
            y = start[1] + t * (end[1] - start[1])
            
            if i in pause_points:
                pause = random.uniform(0.2, 0.5)
            else:
                pause = random.uniform(0.001, 0.005)
            
            path.append((x, y, pause))
        
        return path

    # ==================== MAIN API ====================

    @staticmethod
    def move_cursor_humanlike(start_x, start_y, end_x, end_y, fast = False):
        """
        Di chuyển chuột kiểu người với random 1 trong 10 style khác nhau.
        Không cần truyền tham số style, tự động random.
        """
        if fast:
            return HumanLikeMovement.move_cursor_fast(start_x, start_y, end_x, end_y)
        
        styles = [
            HumanLikeMovement._bezier_path,
            HumanLikeMovement._fast_line_path,
            HumanLikeMovement._zigzag_path,
            HumanLikeMovement._circle_arc_path,            
            HumanLikeMovement._right_angle_path,
            HumanLikeMovement._square_around_path,
            HumanLikeMovement._spiral_in_path,
            HumanLikeMovement._random_waypoints_path,
            HumanLikeMovement._random_waypoints_path,
            HumanLikeMovement._random_waypoints_path,
            HumanLikeMovement._random_waypoints_path,
            HumanLikeMovement._random_waypoints_path,
            HumanLikeMovement._random_waypoints_path,
            HumanLikeMovement._random_waypoints_path,
            HumanLikeMovement._random_waypoints_path,
            HumanLikeMovement._random_waypoints_path,
            HumanLikeMovement._random_waypoints_path,            
            HumanLikeMovement._step_stutter_path,
            HumanLikeMovement._step_stutter_path,
            HumanLikeMovement._step_stutter_path,
            HumanLikeMovement._step_stutter_path,
            HumanLikeMovement._step_stutter_path,
            HumanLikeMovement._step_stutter_path,
            HumanLikeMovement._step_stutter_path,
            HumanLikeMovement._step_stutter_path,
            HumanLikeMovement._step_stutter_path,
            HumanLikeMovement._multi_pause_path,
            HumanLikeMovement._multi_pause_path,
            HumanLikeMovement._multi_pause_path,
            HumanLikeMovement._multi_pause_path,
            HumanLikeMovement._multi_pause_path,
            HumanLikeMovement._multi_pause_path,
            HumanLikeMovement._multi_pause_path,
            HumanLikeMovement._multi_pause_path,
            HumanLikeMovement._multi_pause_path,
            HumanLikeMovement._multi_pause_path,
            HumanLikeMovement._multi_pause_path,
            HumanLikeMovement._multi_pause_path,
        ]
        
        style_func = random.choice(styles)
        path = style_func((start_x, start_y), (end_x, end_y))
        
        for x, y, pause in path:
            pyautogui.moveTo(x, y)
            time.sleep(pause)

    # ==================== GIỮ NGUYÊN CÁC HÀM CŨ (BACKWARD COMPATIBLE) ====================
    
    @staticmethod
    # def move_cursor(start_x, start_y, end_x, end_y, speed_factor=1.0, stop_check=None):
    #     """Di chuyển chuột theo đường cong tự nhiên với tốc độ ngẫu nhiên (API cũ)"""
    #     # Tính toán các điểm kiểm soát cho đường cong
    #     distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        
    #     # Kiểm tra xem có cần di chuyển siêu nhanh không
    #     if speed_factor > 5.0:
    #         return HumanLikeMovement.move_cursor_fast(start_x, start_y, end_x, end_y, stop_check)
        
    #     # QUAN TRỌNG: Đảo ngược logic speed_factor - chia thay vì nhân
    #     # Số bước giảm khi speed_factor tăng
    #     steps = int(distance * random.uniform(0.3, 0.5) / max(speed_factor, 0.1))
    #     steps = min(max(steps, 3), 25)  # Giới hạn trong khoảng 3-25 bước
        
    #     # Tạo độ lệch ngẫu nhiên cho các điểm điều khiển - giảm biên độ cho chuyển động nhanh
    #     offset_factor = min(0.2, 1.0 / speed_factor)  # Giảm offset khi tốc độ tăng
    #     offset_x = random.uniform(-offset_factor, offset_factor) * distance
    #     offset_y = random.uniform(-offset_factor, offset_factor) * distance
        
    #     # Các điểm điều khiển cho đường cong Bezier
    #     p0 = (start_x, start_y)
    #     p3 = (end_x, end_y)
    #     p1 = (start_x + distance/3 + offset_x, start_y + offset_y)
    #     p2 = (end_x - distance/3 + offset_x, end_y + offset_y)
        
    #     # Di chuyển chuột theo đường cong
    #     for i in range(steps + 1):
    #         # Kiểm tra điều kiện dừng nếu có
    #         if stop_check and stop_check():
    #             return False
            
    #         t = i / steps
            
    #         # Vị trí chuột tại thời điểm t trên đường cong
    #         x = HumanLikeMovement._bezier_curve(t, p0[0], p1[0], p2[0], p3[0])
    #         y = HumanLikeMovement._bezier_curve(t, p0[1], p1[1], p2[1], p3[1])
            
    #         # Di chuyển chuột
    #         pyautogui.moveTo(x, y)
            
    #         # Bỏ qua delay ở một số bước để tăng tốc
    #         if i % 2 == 0 or speed_factor < 1.0:  # Chỉ delay ở mỗi bước thứ 2 nếu tốc độ cao
    #             # Tốc độ không đều (chậm lại ở điểm bắt đầu và kết thúc)
    #             if i < steps * 0.2 or i > steps * 0.8:
    #                 delay = random.uniform(0.0005, 0.001) / speed_factor
    #             else:
    #                 delay = random.uniform(0.0001, 0.0005) / speed_factor
    #             time.sleep(delay)
        
    #     return True

    @staticmethod
    def move_cursor_fast(start_x, start_y, end_x, end_y):
        """Phương thức di chuyển siêu nhanh với ít bước và delay cực thấp"""
        distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        
        # Số bước rất thấp cho di chuyển nhanh
        steps = min(max(int(distance/20), 2), 10)
        
        # Di chuyển theo đường thẳng với chút nhiễu
        for i in range(steps + 1):        
            
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
