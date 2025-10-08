from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from constants import ActionType
import uuid

class IfConditionAction(BaseAction):
    def prepare_play(self):
        """Xử lý điều kiện IF - Thực thi IF block khi đúng, xử lý ELSE_IF khi sai"""
        # Tạo ID duy nhất cho IF này
        self.condition_id = str(uuid.uuid4())
        
        # Đánh giá điều kiện
        condition_result = not self.should_break_action()       
        
        if condition_result:
            # IF đúng: thực thi khối IF
            self._execute_if_block()
        else:
            # IF sai: tìm và thực thi ELSE_IF
            self._execute_else_block()
        
        return not condition_result # True nếu điều kiện sai, False nếu đúng

    def _execute_if_block(self):
        """Thực thi các action trong khối IF khi điều kiện đúng"""
        print(f"[IF DEBUG] Thực thi khối IF tại index {self._find_current_index(self.model.get_all_actions())}")
        all_actions = self.model.get_all_actions()
        current_index = self._find_current_index(all_actions)
    
        if current_index == -1:
            return

        # Khởi tạo danh sách các vùng đã được xử lý
        if not hasattr(self, '_handled_ranges'):
            self._handled_ranges = []

        # Thực thi từ action sau IF đến ELSE_IF/END_IF
        i = current_index + 1
        nesting_level = 0
    
        while i < len(all_actions):
            action = all_actions[i]
            
            # ← THÊM CHECK DISABLED (ƯU TIÊN CAO NHẤT)
            if action.is_disabled:
                print(f"[IF DEBUG] ⏭️ Skipping disabled action at index {i}")
                i += 1
                continue
        
            # Kiểm tra xem index i có nằm trong vùng đã được xử lý không
            is_handled = False
            for start, end in self._handled_ranges:
                if start <= i <= end:
                    is_handled = True
                    i = end + 1  # Nhảy qua toàn bộ vùng đã xử lý
                    break
        
            if is_handled:
                continue
            
            if action.action_type == ActionType.IF_CONDITION:
                nesting_level += 1
                self._handle_nested_if(action, i)
            elif action.action_type == ActionType.END_IF_CONDITION:
                if nesting_level == 0:
                    break # Kết thúc khối IF
                nesting_level -= 1
            elif action.action_type == ActionType.ELSE_IF_CONDITION and nesting_level == 0:
                break # Gặp ELSE_IF cùng cấp, dừng lại
            else:
                # Chỉ thực thi action thông thường khi ở nesting level 0
                if nesting_level == 0:
                    self._execute_single_action(action, i)
        
            i += 1


    def _execute_else_block(self):
        """Tìm và thực thi ELSE_IF đầu tiên cùng cấp khi IF sai"""
        print(f"[IF DEBUG] IF sai, tìm ELSE_IF cho IF tại index {self._find_current_index(self.model.get_all_actions())}")
        all_actions = self.model.get_all_actions()
        current_index = self._find_current_index(all_actions)
        
        if current_index == -1:
            return

        # Tìm ELSE_IF đầu tiên cùng cấp
        i = current_index + 1
        nesting_level = 0
        
        while i < len(all_actions):
            action = all_actions[i]
            # ← THÊM CHECK DISABLED (ƯU TIÊN CAO NHẤT)
            if action.is_disabled:
                print(f"[IF DEBUG] ⏭️ Skipping disabled action at index {i}")
                i += 1
                continue
            
            if action.action_type == ActionType.IF_CONDITION:
                nesting_level += 1
            elif action.action_type == ActionType.END_IF_CONDITION:
                if nesting_level == 0:
                    print(f"[IF DEBUG] Không tìm thấy ELSE_IF nào cho IF tại index {current_index}")
                    break # Hết khối, không có ELSE_IF nào
                nesting_level -= 1
            elif action.action_type == ActionType.ELSE_IF_CONDITION and nesting_level == 0:
                print(f"[IF DEBUG] Tìm thấy ELSE_IF tại index {i}, bắt đầu thực thi")
                # Đánh giá điều kiện ELSE_IF
                if self._evaluate_and_execute_else_if(action, i):
                    return # ELSE_IF đã được thực thi, dừng tìm kiếm
                # ELSE_IF sai, tiếp tục tìm ELSE_IF tiếp theo
            
            i += 1

    def _evaluate_and_execute_else_if(self, else_if_action, else_if_index):
        """Đánh giá và thực thi ELSE_IF nếu điều kiện đúng"""
        from controllers.actions.action_factory import ActionFactory
        
        else_if_handler = ActionFactory.get_handler(
            self.controller.root, else_if_action, self.view, self.model, self.controller
        )
        
        if else_if_handler:
            # Đánh giá điều kiện ELSE_IF
            else_if_result = else_if_handler.should_break_action()
            else_if_condition = not else_if_result
            
            print(f"[IF DEBUG] ELSE_IF tại index {else_if_index} điều kiện: {'Đúng' if else_if_condition else 'Sai'}")
            
            if else_if_condition:
                # ELSE_IF đúng: thực thi khối ELSE_IF
                self._execute_else_if_block(else_if_index)
                return True # ELSE_IF đã được thực thi
        
        return False # ELSE_IF sai hoặc không thể đánh giá

    def _execute_else_if_block(self, else_if_index):
        """Thực thi các action bên trong khối ELSE_IF"""
        print(f"[IF DEBUG] Thực thi khối ELSE_IF tại index {else_if_index}")
        all_actions = self.model.get_all_actions()

        # Thực thi từ action sau ELSE_IF đến ELSE_IF tiếp theo/END_IF
        i = else_if_index + 1
        nesting_level = 0
        
        while i < len(all_actions):
            action = all_actions[i]
            
            # ← THÊM CHECK DISABLED (ƯU TIÊN CAO NHẤT)
            if action.is_disabled:
                print(f"[IF DEBUG] ⏭️ Skipping disabled action at index {i}")
                i += 1
                continue
            
            if action.action_type == ActionType.IF_CONDITION:
                nesting_level += 1
                self._handle_nested_if(action, i)
            elif action.action_type == ActionType.END_IF_CONDITION:
                if nesting_level == 0:
                    break # Kết thúc khối ELSE_IF
                nesting_level -= 1
            elif action.action_type == ActionType.ELSE_IF_CONDITION and nesting_level == 0:
                break # Gặp ELSE_IF tiếp theo, dừng lại
            else:
                # Chỉ thực thi action thông thường khi ở nesting level 0
                if nesting_level == 0:
                    self._execute_single_action(action, i)
            
            i += 1

    def _execute_single_action(self, action, index):
        """Thực thi một action đơn lẻ"""
        print(f"[IF DEBUG] Thực thi action tại index {index}, type: {action.action_type}")
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
        """Xử lý IF lồng - để IF lồng tự xử lý logic của mình"""
        print(f"[IF DEBUG] Xử lý nested IF tại index {nested_index}")
        from controllers.actions.action_factory import ActionFactory
    
        nested_handler = ActionFactory.get_handler(
            self.controller.root, nested_if_action, self.view, self.model, self.controller
        )
    
        if nested_handler:
            action_frame = next((f for f in self.view.action_frames 
                                if f.action.id == nested_if_action.id), None)
            if action_frame:
                nested_handler.action_frame = action_frame
        
            # THAY ĐỔI: Gọi prepare_play() thay vì play() để nested IF tự xử lý ELSE_IF
            result = nested_handler.prepare_play()
        
            # QUAN TRỌNG: Bỏ qua các action đã được nested IF xử lý
            self._skip_actions_handled_by_nested_if(nested_index)

    def _skip_actions_handled_by_nested_if(self, nested_if_index):
        """Đánh dấu các action đã được nested IF xử lý để parent IF bỏ qua"""
        all_actions = self.model.get_all_actions()
    
        # Tìm END_IF tương ứng với nested IF
        i = nested_if_index + 1
        nesting_level = 0
    
        while i < len(all_actions):
            action = all_actions[i]
        
            if action.action_type == ActionType.IF_CONDITION:
                nesting_level += 1
            elif action.action_type == ActionType.END_IF_CONDITION:
                if nesting_level == 0:
                    # Đánh dấu vùng từ nested_if_index đến i đã được xử lý
                    if not hasattr(self, '_handled_ranges'):
                        self._handled_ranges = []
                    self._handled_ranges.append((nested_if_index, i))
                    break
                nesting_level -= 1
        
            i += 1


    def _find_current_index(self, all_actions):
        """Tìm index của IF hiện tại"""
        for i, action in enumerate(all_actions):
            if action.id == self.action.id:
                return i
        return -1
