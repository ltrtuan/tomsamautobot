# controllers/actions/text_search_action.py
from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
import os
import random
import re

class TextSearchAction(BaseAction):
    """Handler để thực thi hành động tìm text trên màn hình"""
    
    def prepare_play(self):
        """Thực hiện tìm text sau khi trì hoãn"""
        
        # Lấy danh sách text cần tìm
        search_texts = self.get_search_texts()
        
        if not search_texts:
            # Đặt variable = false nếu không có text
            variable = self.params.get("variable", "")
            if variable:
                GlobalVariables().set(variable, "false")
            return
        
        # Chọn text theo how_to_get
        how_to_get = self.params.get("how_to_get", "All")
        selected_texts = self.select_texts_by_mode(search_texts, how_to_get)
        
        # Lấy thông tin vùng quét
        region = self.get_region()
        x, y, width, height = region
        
        # Tạo region từ các tham số
        search_region = None
        if x > 0 or y > 0 or width > 0 or height > 0:
            search_region = (x, y, width, height)
        
        # Tìm kiếm text trên màn hình
        try:
            from models.text_searcher import TextSearcher
            
            # Tìm tất cả các text được chọn
            found = False
            result_location = None
            
            texts_to_search = selected_texts if isinstance(selected_texts, list) else [selected_texts]
            
            for text in texts_to_search:
                # Xử lý pattern đặc biệt trước khi search
                processed_text = self.process_text_pattern(text)
                
                text_searcher = TextSearcher(processed_text, search_region)
                found, result = text_searcher.search()
                
                if found and result:
                    result_location = result
                    break
            
            if found and result_location:
                center_x, center_y = result_location
                
                # Di chuyển chuột đến vị trí tìm thấy và thực hiện mouse action
                self.move_mouse(center_x, center_y, 1, 1)
                
                # Đặt variable = true
                variable = self.params.get("variable", "")
                if variable:
                    GlobalVariables().set(variable, "true")
            else:
                # Đặt variable = false
                variable = self.params.get("variable", "")
                if variable:
                    GlobalVariables().set(variable, "false")
                    
        except Exception as e:
            print(f"[TEXT_SEARCH_ACTION] Error: {e}")
            variable = self.params.get("variable", "")
            if variable:
                GlobalVariables().set(variable, "false")
    
    def get_search_texts(self):
        """Lấy danh sách text cần tìm, ưu tiên file txt"""
        text_file_path = self.params.get("text_file_path", "")
        
        # Ưu tiên file txt nếu có
        if text_file_path and os.path.exists(text_file_path):
            try:
                with open(text_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"[TEXT_SEARCH_ACTION] Error reading file: {e}")
                content = self.params.get("text_content", "")
        else:
            content = self.params.get("text_content", "")
        
        # Parse theo pattern (cách nhau bởi dấu ;)
        texts = [t.strip() for t in content.split(';') if t.strip()]
        return texts
    
    def select_texts_by_mode(self, texts, mode):
        """Chọn text theo mode"""
        if not texts:
            return []
        
        if mode == "All":
            return texts
        elif mode == "Random":
            return random.choice(texts)
        else:  # Sequential by loop
            # Lấy loop index từ global variables (nếu đang trong vòng lặp)
            loop_var = GlobalVariables().get("LOOP_INDEX", "0")
            try:
                loop_index = int(loop_var)
            except:
                loop_index = 0
            return texts[loop_index % len(texts)]
    
    def process_text_pattern(self, text):
        """
        Xử lý các pattern đặc biệt trong text
        - <VAR_NAME>: thay thế bằng giá trị biến
        - [1-10]: số ngẫu nhiên từ 1 đến 10
        - [1-10:C]: random 1-10 ký tự chữ
        - [1-10:N]: random 1-10 ký tự số
        - [1-10:CN]: random 1-10 ký tự chữ và số
        """
        import string
        
        # Xử lý biến <VAR_NAME>
        var_pattern = r'<([^>]+)>'
        variables = re.findall(var_pattern, text)
        for var in variables:
            var_value = GlobalVariables().get(var, "")
            text = text.replace(f"<{var}>", str(var_value))
        
        # Xử lý [min-max] hoặc [min-max:type]
        range_pattern = r'\[(\d+)-(\d+)(?::([CNcn]+))?\]'
        
        def replace_range(match):
            min_val = int(match.group(1))
            max_val = int(match.group(2))
            type_val = match.group(3)
            
            if type_val is None:
                # Chỉ có số
                return str(random.randint(min_val, max_val))
            else:
                # Random chuỗi ký tự
                length = random.randint(min_val, max_val)
                type_val = type_val.upper()
                
                if type_val == 'C':
                    # Chỉ chữ
                    chars = string.ascii_letters
                elif type_val == 'N':
                    # Chỉ số
                    chars = string.digits
                elif type_val == 'CN':
                    # Cả chữ và số
                    chars = string.ascii_letters + string.digits
                else:
                    chars = string.ascii_letters + string.digits
                
                return ''.join(random.choice(chars) for _ in range(length))
        
        text = re.sub(range_pattern, replace_range, text)
        
        return text
