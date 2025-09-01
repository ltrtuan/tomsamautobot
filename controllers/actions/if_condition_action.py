from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from constants import ActionType
import uuid

class IfConditionAction(BaseAction):
    
    def prepare_play(self):
        """Xử lý điều kiện IF với logic đơn giản"""
        # Tạo ID duy nhất cho IF này
        self.condition_id = str(uuid.uuid4())
        
        # Đánh giá điều kiện
        condition_result = not self.should_break_action()
        
        # Hiển thị kết quả
        if hasattr(self, 'action_frame') and self.action_frame:
            result_text = "Đúng" if condition_result else "Sai"
            self.action_frame.show_temporary_notification(f"IF điều kiện: {result_text}")
        
        if condition_result:
            # IF đúng: thực thi khối IF
            self._execute_if_block()
        else:
            # IF sai: tìm và thực thi ELSE IF hoặc ELSE
            self._execute_else_block()
        
        return False  # Luôn trả về False để ActionController không xử lý thêm
    


    def _execute_if_block(self):
        """Thực thi các action trong khối IF"""
        all_actions = self.model.get_all_actions()
        current_index = self._find_current_index(all_actions)
    
        if current_index == -1:
            return
    
        # Thực thi từ action sau IF đến ELSE IF/END IF
        i = current_index + 1
        nesting_level = 0
    
        while i < len(all_actions):
            action = all_actions[i]
        
            if action.action_type == ActionType.IF_CONDITION:
                nesting_level += 1
                # Xử lý IF lồng
                self._handle_nested_if(action, i)
            
                # Tìm END_IF tương ứng với IF lồng này
                inner_level = 1
                j = i + 1
                while j < len(all_actions) and inner_level > 0:
                    inner_action = all_actions[j]
                    if inner_action.action_type == ActionType.IF_CONDITION:
                        inner_level += 1
                    elif inner_action.action_type == ActionType.END_IF_CONDITION:
                        inner_level -= 1
                    j += 1
            
                # Đặt i = j để bỏ qua toàn bộ khối IF lồng
                i = j
                continue  # Bỏ qua phần increment cuối vòng lặp
            
            elif action.action_type == ActionType.END_IF_CONDITION:
                if nesting_level == 0:
                    break  # Kết thúc khối IF
                nesting_level -= 1
            elif action.action_type == ActionType.ELSE_IF_CONDITION and nesting_level == 0:
                break  # Gặp ELSE IF cùng cấp, dừng lại
            else:
                # Chỉ thực thi action thông thường (không phải IF/ELSE IF/END IF)
                if nesting_level == 0:
                    self._execute_single_action(action, i)
        
            i += 1


    
    def _execute_else_block(self):
        """Tìm và thực thi ELSE IF hoặc ELSE"""
        all_actions = self.model.get_all_actions()
        current_index = self._find_current_index(all_actions)
        
        if current_index == -1:
            return
        
        # Tìm ELSE IF đầu tiên cùng cấp
        i = current_index + 1
        nesting_level = 0
        
        while i < len(all_actions):
            action = all_actions[i]
            
            if action.action_type == ActionType.IF_CONDITION:
                nesting_level += 1
            elif action.action_type == ActionType.END_IF_CONDITION:
                if nesting_level == 0:
                    break  # Hết khối, không có ELSE IF nào
                nesting_level -= 1
            elif action.action_type == ActionType.ELSE_IF_CONDITION and nesting_level == 0:
                # Tìm thấy ELSE IF cùng cấp, thực thi nó
                self._execute_single_action(action, i)
                return
            
            i += 1
    
    def _execute_single_action(self, action, index):
        """Thực thi một action đơn lẻ"""
        from controllers.actions.action_factory import ActionFactory
        
        handler = ActionFactory.get_handler(
            self.controller.root, action, self.view, self.model, self.controller
        )
        
        if handler:
            # Thiết lập action frame
            action_frame = next((f for f in self.view.action_frames 
                               if f.action.id == action.id), None)
            if action_frame:
                handler.action_frame = action_frame
            
            handler.play()
            
    def _handle_nested_if(self, nested_if_action, nested_index):
        """Xử lý IF lồng - chỉ đánh giá điều kiện và để IF tự xử lý"""
        # Tạo handler cho IF lồng
        from controllers.actions.action_factory import ActionFactory
        nested_handler = ActionFactory.get_handler(
            self.controller.root, nested_if_action, self.view, self.model, self.controller
        )
    
        if nested_handler:
            # Thiết lập action frame
            action_frame = next((f for f in self.view.action_frames 
                               if f.action.id == nested_if_action.id), None)
            if action_frame:
                nested_handler.action_frame = action_frame
        
            # Chỉ gọi play() và để IF lồng tự xử lý logic của nó
            nested_handler.play()

    
    def _find_current_index(self, all_actions):
        """Tìm index của IF hiện tại"""
        for i, action in enumerate(all_actions):
            if action.id == self.action.id:
                return i
        return -1

    