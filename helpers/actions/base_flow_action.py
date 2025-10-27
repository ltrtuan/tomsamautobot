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



    def calculate_smart_click_position(self, viewport_coords, viewport_offset_x, viewport_offset_y, avoid_zone=None):
        """
        Calculate smart click position for any element:
        - Avoid edges (10px margin)
        - Avoid center (30% center zone) - for default behavior
        - Avoid specific zones (e.g., 'top-right' for YouTube Watch Later/Playlist icons)
        - Random in remaining safe areas
    
        Args:
            viewport_coords: Dict with {x, y, width, height} from get_element_viewport_coordinates()
            viewport_offset_x: Browser window X offset
            viewport_offset_y: Browser window Y offset
            avoid_zone: Optional string to specify zone to avoid:
                - None (default): Avoid center + edges (general use)
                - 'top-right': Avoid top-right corner (YouTube Watch Later/Playlist icons)
                - 'bottom-half': Avoid bottom 50% (YouTube main feed description area)
                - 'top-left': Avoid top-left corner
                - 'bottom-right': Avoid bottom-right corner
                - 'bottom-left': Avoid bottom-left corner
    
        Returns:
            (click_x, click_y): Screen coordinates to click, or (None, None) if error
        """
        try:
            import random
        
            width = viewport_coords['width']
            height = viewport_coords['height']
        
            # Edge margin (avoid clicking too close to edges)
            edge_margin = 10
        
            # ========== SPECIAL ZONE AVOIDANCE ==========
            if avoid_zone == 'top-right':
                # For YouTube sidebar thumbnails: Avoid top-right 30% where Watch Later/Playlist icons are
                # Safe zone: Left 70% and Center-Bottom 55% of thumbnail
                safe_x_min = width * 0.15   # Start from 15% from left (avoid left edge)
                safe_x_max = width * 0.70   # End at 70% from left (avoid right 30% with icons)
                safe_y_min = height * 0.35  # Start from 35% from top (avoid top area with icons)
                safe_y_max = height * 0.85  # End at 85% from top (avoid bottom edge)
            
                # Generate random position in safe zone
                random_offset_x = random.uniform(safe_x_min, safe_x_max)
                random_offset_y = random.uniform(safe_y_min, safe_y_max)
        
            elif avoid_zone == 'bottom-half':
                # For YouTube main feed: Avoid bottom 50% where description/metadata are
                # Safe zone: Top 50% (title + thumbnail area)
                safe_x_min = width * 0.15   # Avoid left edge (15%)
                safe_x_max = width * 0.85   # Avoid right edge (15%)
                safe_y_min = height * 0.15  # Avoid top edge (15%)
                safe_y_max = height * 0.50  # Only use top 50% (avoid bottom half)
            
                # Generate random position in safe zone
                random_offset_x = random.uniform(safe_x_min, safe_x_max)
                random_offset_y = random.uniform(safe_y_min, safe_y_max)
        
            elif avoid_zone == 'top-left':
                # Avoid top-left corner (30% width, 40% height)
                safe_x_min = width * 0.30
                safe_x_max = width * 0.85
                safe_y_min = height * 0.40
                safe_y_max = height * 0.85
            
                random_offset_x = random.uniform(safe_x_min, safe_x_max)
                random_offset_y = random.uniform(safe_y_min, safe_y_max)
        
            elif avoid_zone == 'bottom-right':
                # Avoid bottom-right corner (30% width, 40% height)
                safe_x_min = width * 0.15
                safe_x_max = width * 0.70
                safe_y_min = height * 0.15
                safe_y_max = height * 0.60
            
                random_offset_x = random.uniform(safe_x_min, safe_x_max)
                random_offset_y = random.uniform(safe_y_min, safe_y_max)
        
            elif avoid_zone == 'bottom-left':
                # Avoid bottom-left corner (30% width, 40% height)
                safe_x_min = width * 0.30
                safe_x_max = width * 0.85
                safe_y_min = height * 0.15
                safe_y_max = height * 0.60
            
                random_offset_x = random.uniform(safe_x_min, safe_x_max)
                random_offset_y = random.uniform(safe_y_min, safe_y_max)
        
            # ========== DEFAULT BEHAVIOR: AVOID CENTER + EDGES ==========
            else:
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


