import random
import time
import pyautogui
from global_variables import GlobalVariables
from human_like_movement import HumanLikeMovement
from image_searcher import ImageSearcher
from core.interfaces import ActionInterface

class ImageAction(ActionInterface):
    """Class thực hiện hành động tìm kiếm hình ảnh"""
    """Class thực hiện hành động tìm kiếm hình ảnh"""
    def __init__(self, parameters):
        self.parameters = parameters
        self.variables = GlobalVariables()
        
    def get_parameters(self):
        return self.parameters
        
    def set_parameters(self, parameters):
        self.parameters = parameters
        
    def execute(self):
        """Thực thi hành động tìm kiếm hình ảnh"""
        # Trích xuất tham số
        path = self.parameters.get("path", "")
        x = self.parameters.get("x", "0")
        y = self.parameters.get("y", "0")
        width = self.parameters.get("width", "0")
        height = self.parameters.get("height", "0")
        accuracy = self.parameters.get("accuracy", "80")
        random_time = int(float(self.parameters.get("random_time", "0")))
        double_click = self.parameters.get("double_click", False)
        random_skip = int(float(self.parameters.get("random_skip", "0")))
        variable = self.parameters.get("variable", "")
        program = self.parameters.get("program", "")
        break_conditions = self.parameters.get("break_conditions", [])
        
        # Kiểm tra điều kiện dừng
        if self._should_break(break_conditions):
            print("Breaking action due to condition")
            return False
            
        # Kiểm tra có nên bỏ qua hành động này không
        if random_skip > 0 and random.randint(1, random_skip) != 1:
            print("Randomly skipping action")
            return True
            
        # Kiểm tra và kích hoạt chương trình nếu được chỉ định
        if program:
            self._activate_program(program)
            
        # Chờ thời gian ngẫu nhiên nếu được chỉ định
        if random_time > 0:
            wait_time = random.uniform(0.1, float(random_time))
            print(f"Waiting random time: {wait_time:.2f} seconds")
            time.sleep(wait_time)
            
        # Thiết lập region
        region = None
        if int(float(width or 0)) > 0 and int(float(height or 0)) > 0:
            region = (x, y, width, height)
            
        # Tìm kiếm hình ảnh
        try:
            print(f"Searching for image: {path}")
            searcher = ImageSearcher(path, region, accuracy)
            found, position = searcher.search()
            
            # Lưu kết quả vào biến nếu được chỉ định
            if variable:
                self.variables.set(variable, 1 if found else 0)
                print(f"Set variable {variable} = {1 if found else 0}")
                
            # Nếu tìm thấy hình ảnh, click vào nó
            if found and position:
                center_x, center_y, confidence = position
                print(f"Image found at ({center_x}, {center_y}) with confidence: {confidence:.4f}")
                
                # Lấy vị trí chuột hiện tại
                current_x, current_y = pyautogui.position()
                
                # Di chuyển chuột đến vị trí với chuyển động tự nhiên
                # Tốc độ ngẫu nhiên từ 0.5 đến 2.0
                speed = random.uniform(0.5, 2.0)
                HumanLikeMovement.move_cursor(current_x, current_y, center_x, center_y, speed)
                
                # Click dựa trên tham số
                if double_click:
                    pyautogui.doubleClick()
                    print("Performed double click")
                else:
                    pyautogui.click()
                    print("Performed single click")
                    
                return True
            else:
                print("Image not found")
                
        except Exception as e:
            print(f"Error during image search: {e}")
            
        return False
        
    def _should_break(self, break_conditions):
        """Kiểm tra có nên dừng hành động dựa trên điều kiện không"""
        if not break_conditions:
            return False
            
        result = False
        first_condition = True
        
        for condition in break_conditions:
            variable_name = condition.get("variable", "")
            value = condition.get("value", "")
            logical_op = condition.get("logical_op", "")
            
            if not variable_name:
                continue
                
            # Chuyển đổi value sang kiểu đúng nếu có thể
            try:
                if value.isdigit():
                    value = int(value)
                elif value.replace(".", "", 1).isdigit():
                    value = float(value)
            except:
                pass
                
            # Lấy giá trị biến
            var_value = self.variables.get(variable_name, 0)
            
            # Đánh giá điều kiện
            condition_result = (var_value == value)
            
            # Áp dụng phép toán logic
            if first_condition:
                result = condition_result
                first_condition = False
            elif logical_op == "AND":
                result = result and condition_result
            elif logical_op == "OR":
                result = result or condition_result
                
        return result
        
    def _activate_program(self, program_path):
        """Kích hoạt chương trình được chỉ định"""
        try:
            import subprocess
            import os
            import psutil
            
            # Lấy tên chương trình từ đường dẫn
            program_name = os.path.basename(program_path)
            
            # Kiểm tra chương trình có đang chạy không
            program_running = False
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == program_name:
                    program_running = True
                    print(f"Program {program_name} is already running")
                    break
                    
            # Nếu không chạy, khởi động nó
            if not program_running:
                print(f"Starting program: {program_path}")
                subprocess.Popen([program_path])
                time.sleep(3)  # Chờ chương trình khởi động
            
            # Kích hoạt cửa sổ
            try:
                import pygetwindow as gw
                windows = gw.getWindowsWithTitle(program_name.split('.')[0])
                if windows:
                    window = windows[0]
                    if window.isMinimized:
                        print(f"Restoring minimized window: {program_name}")
                        window.restore()
                    window.activate()
                    time.sleep(1)  # Chờ cửa sổ được kích hoạt
            except Exception as e:
                print(f"Error activating window: {e}")
                
        except Exception as e:
            print(f"Error activating program: {e}")
