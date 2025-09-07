from controllers.actions.base_action import BaseAction
from constants import ActionType

class ElseIfConditionAction(BaseAction):
    
    def prepare_play(self):
        print(f"[ELSE_IF DEBUG] ElseIfConditionAction.prepare_play() được gọi!")
        print(f"[ELSE_IF DEBUG] Action ID: {self.action.id}")
        """Xử lý điều kiện ELSE IF với logic đơn giản"""
        # Đánh giá điều kiện
        condition_result = not self.should_break_action()       
       
        
        if condition_result:
            # ELSE IF đúng: thực thi khối ELSE IF
            self._execute_else_if_block()
        else:
            # ELSE IF sai: tìm ELSE IF tiếp theo
            self._find_next_else_if()
        
        return False
    
    def _execute_else_if_block(self):
        """Thực thi các action trong khối ELSE IF"""
        all_actions = self.model.get_all_actions()
        current_index = self._find_current_index(all_actions)
        
        if current_index == -1:
            return
        
        # Thực thi từ action sau ELSE IF đến ELSE IF tiếp theo/END IF
        i = current_index + 1
        nesting_level = 0
        
        while i < len(all_actions):
            action = all_actions[i]
            
            if action.action_type == ActionType.IF_CONDITION:
                nesting_level += 1
            elif action.action_type == ActionType.END_IF_CONDITION:
                if nesting_level == 0:
                    break
                nesting_level -= 1
            elif action.action_type == ActionType.ELSE_IF_CONDITION and nesting_level == 0:
                break
            
            self._execute_single_action(action, i)
            i += 1
    
    def _find_next_else_if(self):
        """Tìm ELSE IF tiếp theo"""
        all_actions = self.model.get_all_actions()
        current_index = self._find_current_index(all_actions)
        
        if current_index == -1:
            return
        
        i = current_index + 1
        nesting_level = 0
        
        while i < len(all_actions):
            action = all_actions[i]
            
            if action.action_type == ActionType.IF_CONDITION:
                nesting_level += 1
            elif action.action_type == ActionType.END_IF_CONDITION:
                if nesting_level == 0:
                    break
                nesting_level -= 1
            elif action.action_type == ActionType.ELSE_IF_CONDITION and nesting_level == 0:
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
            action_frame = next((f for f in self.view.action_frames 
                               if f.action.id == action.id), None)
            if action_frame:
                handler.action_frame = action_frame
            
            handler.play()
    
    def _find_current_index(self, all_actions):
        """Tìm index của ELSE IF hiện tại"""
        for i, action in enumerate(all_actions):
            if action.id == self.action.id:
                return i
        return -1
