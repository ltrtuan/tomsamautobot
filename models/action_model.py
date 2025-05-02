from constants import ActionType
import json
from pathlib import Path
import os
import uuid

# Định nghĩa đường dẫn lưu file - điều chỉnh theo cấu trúc dự án
# Kiểm tra và lấy giá trị FILE_PATH từ config.py
try:
    from config import FILE_PATH
    # Kiểm tra FILE_PATH có tồn tại và không rỗng
    if FILE_PATH and os.path.exists(FILE_PATH):
        # Sử dụng FILE_PATH thay vì thư mục hiện tại
        actions_path = os.path.join(FILE_PATH, "actions.json")
        ACTIONS_JSON_PATH = actions_path
    else:
        # Sử dụng thư mục mặc định nếu FILE_PATH không hợp lệ
        default_path = "C:/tomsamautobot"
        if not os.path.exists(default_path):
            os.makedirs(default_path)
        actions_path = os.path.join(default_path, "actions.json")
        ACTIONS_JSON_PATH = actions_path
except (ImportError, AttributeError):
    # Nếu không tìm thấy FILE_PATH, tạo thư mục mặc định ở C:/tomsamautobot/
    default_path = "C:/tomsamautobot"
    if not os.path.exists(default_path):
        os.makedirs(default_path)
    ACTIONS_JSON_PATH = os.path.join(default_path, "actions.json")


                
class ActionItem:
    
    def __init__(self, action_type, parameters):
        # Hoặc dùng UUID để đảm bảo tính duy nhất toàn cục
        self.id = str(uuid.uuid4())
        self.action_type = action_type
        self.parameters = parameters
    
    def __str__(self):
        return f"{self.action_type}: {', '.join([f'{k}={v}' for k, v in self.parameters.items()])}"
    
    def to_dict(self):
        return {
            "action_type": self.action_type.value if hasattr(self.action_type, "value") else self.action_type,
            "parameters": self.parameters
        }

class ActionModel:
    def __init__(self):
        self.actions = []
        self.is_modified = False  # Thêm flag theo dõi thay đổi
        
    def add_action(self, action):
        
        # Kiểm tra nếu action là một đối tượng có thuộc tính action_type
        if hasattr(action, "action_type"):
            # Nếu action_type đã là một enum
            if isinstance(action.action_type, ActionType):
                # Giữ nguyên - đã đúng định dạng
                pass
            else:
                # Nếu action_type là chuỗi, chuyển đổi sang enum
                try:
                    action_type_display = action.action_type
                    action_type = ActionType.from_display_value(action_type_display)
                    action.action_type = action_type
                except ValueError:
                    # Giữ nguyên nếu không thể chuyển đổi
                    pass
        # Trường hợp action là dictionary (tương thích ngược)
        elif isinstance(action, dict) and "action_type" in action:
            action_type_display = action["action_type"]
            try:
                action_type = ActionType.from_display_value(action_type_display)
                action["action_type"] = action_type
            except ValueError:
                pass
            # Chuyển đổi từ dict sang ActionItem
            action = ActionItem(action["action_type"], action.get("parameters", {}))
    
        self.actions.append(action)
        self.is_modified = True  # Đánh dấu đã thay đổi
        return len(self.actions) - 1
        
    def update_action(self, index, action):
        if 0 <= index < len(self.actions):
            self.actions[index] = action
            self.is_modified = True  # Đánh dấu đã thay đổi
            return True
        return False
        
    def delete_action(self, index):
        if 0 <= index < len(self.actions):
            del self.actions[index]
            self.is_modified = True  # Đánh dấu đã thay đổi
            return True
        return False
        
    def delete_all_actions(self):
        """Xóa tất cả các hành động"""
        self.actions = []  # Xóa toàn bộ danh sách actions
        self.is_modified = True  # Đánh dấu đã thay đổi
        return True

    def move_action(self, from_index, to_index):
        if 0 <= from_index < len(self.actions) and 0 <= to_index < len(self.actions):
            action = self.actions.pop(from_index)
            self.actions.insert(to_index, action)
            self.is_modified = True  # Đánh dấu đã thay đổi
            return True
        return False
        
    def get_all_actions(self):
        return self.actions
        
    def get_action(self, index):
        if 0 <= index < len(self.actions):
            return self.actions[index]
        return None
        
    def add_sample_actions(self):        
        # Thêm các actions mẫu
        self.add_action(ActionItem(ActionType.TIM_HINH_ANH, {
            "image_path": "C:/images/button.png", 
            "confidence": "0.8",
            "x": "0",
            "y": "0",
            "width": "100",
            "height": "100",
            "accuracy": "80",
            "random_time": "0",
            "double_click": False,
            "random_skip": "0",
            "variable": "",
            "program": ""
        }))
    
        self.add_action(ActionItem(ActionType.DI_CHUYEN_CHUOT, {
            "x": "500", 
            "y": "300", 
            "duration": "0.5"
        }))
    
        # Lưu ngay sau khi thêm sample actions
        # self.save_actions()

    def reorder_action(self, old_index, new_index):
        """Di chuyển hành động từ vị trí cũ đến vị trí mới"""
        if old_index != new_index and 0 <= old_index < len(self.actions) and 0 <= new_index < len(self.actions):
            action = self.actions.pop(old_index)
            self.actions.insert(new_index, action)
            # Có thể lưu lại nếu cần
            self.is_modified = True  # Đánh dấu đã thay đổi

    def save_actions(self):
        """Lưu danh sách hành động vào storage"""
        try:
            # Phần còn lại giữ nguyên
            with open(ACTIONS_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump([a.to_dict() for a in self.actions], f, indent=2)
            print(f"Đã lưu hành động vào {ACTIONS_JSON_PATH}")
            self.is_modified = False  # Reset flag sau khi lưu thành công
            return True
        except Exception as e:
            print(f"Lỗi khi lưu hành động: {str(e)}")
            return False

        
    def load_actions(self):
        """Tải danh sách hành động từ storage"""
        try:
            if os.path.exists(ACTIONS_JSON_PATH):
                with open(ACTIONS_JSON_PATH, 'r', encoding='utf-8') as f:
                    actions_data = json.load(f)
                    self.actions = []
                    if actions_data:  # Nếu file có dữ liệu
                        for action_data in actions_data:
                            action_type = action_data.get("action_type")
                            parameters = action_data.get("parameters", {})
                            self.add_action(ActionItem(action_type, parameters))
                        return True
                    else:  # Nếu file trống (empty array)
                        self.add_sample_actions()
                        return True
            else:
                # Tạo file trống nếu không tồn tại và thêm sample actions
                with open(ACTIONS_JSON_PATH, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                self.add_sample_actions()
                return True
        except Exception as e:
            print(f"Lỗi khi tải hành động: {str(e)}")
            # Nếu có lỗi, vẫn thêm sample actions
            self.add_sample_actions()
            return False