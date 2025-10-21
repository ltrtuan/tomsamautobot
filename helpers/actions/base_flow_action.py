class BaseFlowAction:
    def __init__(self, driver):
        self.driver = driver

    def get_element_viewport_coordinates(self, element):
        """
        Trả về tọa độ (x, y), chiều dài, chiều cao, right, bottom của element relative to viewport hiện tại.
        Kết quả: dict {x, y, width, height, right, bottom}
        """
        try:
            rect = self.driver.execute_script("""
                var rect = arguments[0].getBoundingClientRect();
                return {
                    'x': rect.left,
                    'y': rect.top,
                    'width': rect.width,
                    'height': rect.height,
                    'right': rect.right,
                    'bottom': rect.bottom
                };
            """, element)
            return rect
        except Exception as e:
            print(f"[BaseFlowAction] Get viewport coordinates error: {e}")
            return None

    def is_element_in_viewport(self, element):
        """
        Kiểm tra xem element có nằm trong vùng nhìn thấy của user trên màn hình browser chưa.
        Element chỉ cần 1 phần visible là đủ (không cần toàn bộ visible)
        """
        try:
            return self.driver.execute_script("""
                var rect = arguments[0].getBoundingClientRect();
                var windowHeight = window.innerHeight || document.documentElement.clientHeight;
                var windowWidth = window.innerWidth || document.documentElement.clientWidth;
            
                // Element is visible if ANY part of it is in viewport
                return (
                    rect.top < windowHeight &&  // Top edge above bottom of viewport
                    rect.bottom > 0 &&           // Bottom edge below top of viewport
                    rect.left < windowWidth &&   // Left edge before right of viewport
                    rect.right > 0               // Right edge after left of viewport
                );
            """, element)
        except Exception as e:
            print(f"[BaseFlowAction] Check viewport error: {e}")
            return False



    def calculate_smart_click_position(self, viewport_coords, viewport_offset_x, viewport_offset_y):
        """
        Calculate smart click position for any element:
        - Avoid edges (10px margin)
        - Avoid center (30% center zone)
        - Random in remaining areas (left/right/top/bottom zones)
        
        Args:
            viewport_coords: Dict with {x, y, width, height} from get_element_viewport_coordinates()
            viewport_offset_x: Browser window X offset
            viewport_offset_y: Browser window Y offset
            
        Returns:
            (click_x, click_y): Screen coordinates to click, or (None, None) if error
        """
        try:
            import random
            
            width = viewport_coords['width']
            height = viewport_coords['height']
            
            # Edge margin (avoid clicking too close to edges)
            edge_margin = 10
            
            # Center zone to avoid (30% of width/height around center)
            center_zone_width = width * 0.3
            center_zone_height = height * 0.3
            
            # Calculate center zone boundaries
            center_left = (width / 2) - (center_zone_width / 2)
            center_right = (width / 2) + (center_zone_width / 2)
            center_top = (height / 2) - (center_zone_height / 2)
            center_bottom = (height / 2) + (center_zone_height / 2)
            
            # Define clickable zones (avoid edges and center)
            zones = []
            
            # Left zone (avoid center)
            if center_left > edge_margin:
                zones.append({
                    'name': 'left',
                    'x_min': edge_margin,
                    'x_max': center_left,
                    'y_min': edge_margin,
                    'y_max': height - edge_margin
                })
            
            # Right zone (avoid center)
            if width - center_right > edge_margin:
                zones.append({
                    'name': 'right',
                    'x_min': center_right,
                    'x_max': width - edge_margin,
                    'y_min': edge_margin,
                    'y_max': height - edge_margin
                })
            
            # Top zone (avoid center, between left and right zones)
            if center_top > edge_margin:
                zones.append({
                    'name': 'top',
                    'x_min': center_left,
                    'x_max': center_right,
                    'y_min': edge_margin,
                    'y_max': center_top
                })
            
            # Bottom zone (avoid center, between left and right zones)
            if height - center_bottom > edge_margin:
                zones.append({
                    'name': 'bottom',
                    'x_min': center_left,
                    'x_max': center_right,
                    'y_min': center_bottom,
                    'y_max': height - edge_margin
                })
            
            # If no zones available, fallback to simple random (avoid edges only)
            if not zones:
                print("[BaseFlowAction] No zones available, using fallback")
                random_offset_x = random.uniform(edge_margin, width - edge_margin)
                random_offset_y = random.uniform(edge_margin, height - edge_margin)
            else:
                # Random choose a zone
                chosen_zone = random.choice(zones)
                
                # Random position in chosen zone
                random_offset_x = random.uniform(chosen_zone['x_min'], chosen_zone['x_max'])
                random_offset_y = random.uniform(chosen_zone['y_min'], chosen_zone['y_max'])
            
            # Calculate final screen coordinates
            click_x = viewport_offset_x + viewport_coords['x'] + random_offset_x
            click_y = viewport_offset_y + viewport_coords['y'] + random_offset_y
            
            return click_x, click_y
            
        except Exception as e:
            print(f"[BaseFlowAction] Calculate position error: {e}")
            return None, None
