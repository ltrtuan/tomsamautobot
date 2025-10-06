from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from models.image_search import ImageSearcher
import os

class ImageSearchAction(BaseAction):
    """Handler để thực thi hành động tìm hình ảnh"""    
    
    def prepare_play(self):
        """Thực hiện tìm hình ảnh sau khi trì hoãn"""
        # Lấy các tham số cần thiết
        image_path = self.params.get("image_path", "")
        # Lấy thông tin vùng quét sử dụng phương thức từ BaseAction
        region = self.get_region()
        x, y, width, height = region
        accuracy = int(self.params.get("accuracy", 80))
        
        # Kiểm tra nếu không có đường dẫn hình ảnh hoặc file không tồn tại
        if not image_path or not os.path.exists(image_path):
            
            # Đặt variable = false nếu có
            variable = self.params.get("variable", "")
            if variable:                
                GlobalVariables().set(variable, "false")                
            return
        
        # Tạo region từ các tham số
        region = None
        if x > 0 or y > 0 or width > 0 or height > 0:
            region = (x, y, width, height)
        
        # Tìm kiếm hình ảnh
        try:
            
            # Tạo instance của ImageSearcher
            image_searcher = ImageSearcher(image_path, region, accuracy)
            
            # Thực hiện tìm kiếm
            found, result = image_searcher.search()
            
            if found and result:
                center_x, center_y, confidence = result
            
                
                # Di chuyển chuột đến vị trí tìm thấy
                # Lấy clickable area params
                import random
    
                # Lấy giá trị từ params, nếu rỗng thì mặc định = 1
                click_min_width = self.params.get("click_min_width", "")
                click_max_width = self.params.get("click_max_width", "")
                click_min_height = self.params.get("click_min_height", "")
                click_max_height = self.params.get("click_max_height", "")
    
                # Xử lý width
                if click_min_width and click_max_width:
                    try:
                        min_w = int(click_min_width)
                        max_w = int(click_max_width)
                        random_width = random.randint(min_w, max_w)
                    except (ValueError, TypeError):
                        random_width = 1
                else:
                    random_width = 1
    
                # Xử lý height
                if click_min_height and click_max_height:
                    try:
                        min_h = int(click_min_height)
                        max_h = int(click_max_height)
                        random_height = random.randint(min_h, max_h)
                    except (ValueError, TypeError):
                        random_height = 1
                else:
                    random_height = 1
    
                # Di chuyển chuột đến vị trí tìm thấy với clickable area
                # move_mouse sẽ tự động xử lý click từ self.params
                self.move_mouse(center_x, center_y, random_width, random_height)
                
                # Đặt variable = true nếu có
                variable = self.params.get("variable", "")
                if variable:                    
                    GlobalVariables().set(variable, "true")
            else:
                
                # Đặt variable = false nếu có
                variable = self.params.get("variable", "")
                if variable:
                    
                    GlobalVariables().set(variable, "false")
        except Exception as e:
                
            # Đặt variable = false nếu có
            variable = self.params.get("variable", "")
            if variable:                
                GlobalVariables().set(variable, "false")
