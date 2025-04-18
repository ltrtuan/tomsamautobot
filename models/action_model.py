﻿class ActionItem:
    def __init__(self, action_type, parameters):
        self.action_type = action_type
        self.parameters = parameters
    
    def __str__(self):
        return f"{self.action_type}: {', '.join([f'{k}={v}' for k, v in self.parameters.items()])}"

class ActionModel:
    def __init__(self):
        self.actions = []
        
    def add_action(self, action):
        self.actions.append(action)
        return len(self.actions) - 1
        
    def update_action(self, index, action):
        if 0 <= index < len(self.actions):
            self.actions[index] = action
            return True
        return False
        
    def delete_action(self, index):
        if 0 <= index < len(self.actions):
            del self.actions[index]
            return True
        return False
        
    def move_action(self, from_index, to_index):
        if 0 <= from_index < len(self.actions) and 0 <= to_index < len(self.actions):
            action = self.actions.pop(from_index)
            self.actions.insert(to_index, action)
            return True
        return False
        
    def get_all_actions(self):
        return self.actions
        
    def get_action(self, index):
        if 0 <= index < len(self.actions):
            return self.actions[index]
        return None
        
    def add_sample_actions(self):
        self.add_action(ActionItem("Tìm Hình Ảnh", {"path": "C:/images/button.png", "confidence": "0.8"}))
        self.add_action(ActionItem("Di Chuyển Chuột", {"x": "500", "y": "300", "duration": "0.5"}))

    def reorder_action(self, old_index, new_index):
        """Di chuyển hành động từ vị trí cũ đến vị trí mới"""
        if old_index != new_index and 0 <= old_index < len(self.actions) and 0 <= new_index < len(self.actions):
            action = self.actions.pop(old_index)
            self.actions.insert(new_index, action)
            # Có thể lưu lại nếu cần

    def save_actions(self):
        """Lưu danh sách hành động vào storage"""
        try:
            with open(ACTIONS_JSON_PATH, 'w') as f:
                json.dump([a.to_dict() for a in self.actions], f, indent=2)
        except Exception as e:
            print(f"Lỗi khi lưu hành động: {str(e)}")