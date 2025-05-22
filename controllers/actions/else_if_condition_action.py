from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from constants import ActionType

class ElseIfConditionAction(BaseAction):
    
    def prepare_play(self):
        """Xử lý điều kiện ELSE IF"""
        globals_var = GlobalVariables()
        # current_level là cấp độ của khối IF/ELSEIF/ENDIF mà ELSEIF này thuộc về
        current_level_of_block = globals_var.get("__condition_stack_size", 0) -1 # Stack đã được IF cha tăng lên

        # parent_id là ID của IF_CONDITION khởi tạo khối này, được truyền qua _find_matching_else_if
        parent_id_of_original_if = globals_var.get("__current_else_if_parent", "")

        if not parent_id_of_original_if:
            # Fallback: nếu không được truyền (ví dụ chạy độc lập ELSE IF), cố gắng lấy ID IF cùng cấp
            # Điều này có thể không chính xác trong mọi trường hợp, nhưng là nỗ lực cuối cùng
            parent_id_of_original_if = globals_var.get(f"__condition_id_{current_level_of_block}", "")
            if hasattr(self, 'action_frame') and self.action_frame and not parent_id_of_original_if:
                self.action_frame.show_temporary_notification("Không tìm thấy IF cha trực tiếp!")


        if hasattr(self, 'action_frame') and self.action_frame:
            self.action_frame.show_temporary_notification(
                f"ELSE IF (khối cấp {current_level_of_block}), IF gốc ID: {parent_id_of_original_if[:8] if parent_id_of_original_if else 'None'}"
            )

        # Khi chạy độc lập ELSE IF (nhấn nút Play riêng của nó)
        if not parent_id_of_original_if and hasattr(self, 'view') and self.view and self.model:
            import uuid
            # Tạo ID giả cho IF cha và giả lập nó sai
            parent_id_of_original_if = str(uuid.uuid4())
            globals_var.set(f"__condition_id_{current_level_of_block}", parent_id_of_original_if)
            globals_var.set(f"__condition_result_{parent_id_of_original_if}", False) # Giả lập IF cha SAI
            # Đánh dấu khối này chưa được thỏa mãn
            globals_var.set(f"__condition_block_satisfied_{parent_id_of_original_if}", False)


        # Kiểm tra xem khối IF (bắt đầu bằng parent_id_of_original_if) đã có điều kiện nào ĐÚNG chưa
        # Sử dụng một biến mới: __condition_block_satisfied_{ID_IF_GỐC}
        block_already_satisfied = globals_var.get(f"__condition_block_satisfied_{parent_id_of_original_if}", False)

        if block_already_satisfied:
            if hasattr(self, 'action_frame') and self.action_frame:
                self.action_frame.show_temporary_notification(
                    f"Bỏ qua ELSE IF: Khối IF-{parent_id_of_original_if[:8]} đã có điều kiện đúng."
                )
            return False # Trả về False vì điều kiện ELSE IF không được đánh giá (và nó không đúng)

        # Nếu khối chưa được thỏa mãn, đánh giá điều kiện của ELSE IF này
        current_else_if_condition_result = not self.should_break_action()

        if hasattr(self, 'action_frame') and self.action_frame:
            result_text = "Đúng" if current_else_if_condition_result else "Sai"
            self.action_frame.show_temporary_notification(f"Điều kiện ELSE IF: {result_text}")

        if current_else_if_condition_result:
            # Nếu ELSE IF này đúng, đánh dấu khối IF gốc là đã được thỏa mãn
            globals_var.set(f"__condition_block_satisfied_{parent_id_of_original_if}", True)
            # Thực thi các action lồng nếu chạy độc lập
            if hasattr(self, 'view') and self.view and self.model:
                self._execute_condition_block(parent_id_of_original_if) # Truyền ID IF gốc

        # prepare_play của BaseAction trả về True nếu điều kiện sai (để play() của ActionController biết)
        # Nhưng ElseIfConditionAction phức tạp hơn.
        # Nếu block_already_satisfied là True, thì ElseIf này không chạy -> coi như nó "sai".
        # Nếu block_already_satisfied là False, thì kết quả phụ thuộc vào current_else_if_condition_result.
        if block_already_satisfied:
            return True # Tương đương với điều kiện của ELSE IF này là SAI (vì nó bị skip)
        else:
            return not current_else_if_condition_result # Trả về True nếu điều kiện của ELSE IF này là SAI

    
    def _execute_condition_block(self, parent_id):
        """Thực thi các action trong khối ELSE IF"""
        from controllers.actions.action_factory import ActionFactory
        
        all_actions = self.model.get_all_actions()
        current_index = next((i for i, a in enumerate(all_actions) if a.id == self.action.id), -1)
        if current_index < 0:
            return
        
        # Lấy cấp độ lồng hiện tại
        globals_var = GlobalVariables()
        current_level = globals_var.get("__condition_stack_size", 0) - 1
        
        # Debug thông tin
        if hasattr(self, 'action_frame') and self.action_frame:
            self.action_frame.show_temporary_notification(
                f"Thực thi khối ELSE IF (cấp {current_level})"
            )
        
        # Biến theo dõi số lượng IF/ELSE_IF/END_IF đã gặp
        block_level = 0
        
        # Duyệt và thực thi các action trong khối
        i = current_index + 1
        while i < len(all_actions):
            action = all_actions[i]
            
            # Kiểm tra loại action để điều chỉnh block_level
            if action.action_type == ActionType.IF_CONDITION:
                block_level += 1
            elif action.action_type == ActionType.ELSE_IF_CONDITION:
                if block_level == 0:
                    # Gặp ELSE IF khác cùng cấp, dừng lại
                    break
            elif action.action_type == ActionType.END_IF_CONDITION:
                if block_level == 0:
                    # Đã tìm thấy END IF của khối hiện tại
                    break
                block_level -= 1
            
            # Chỉ thực thi action nếu đang ở trong khối điều kiện
            if block_level >= 0:
                # Lấy handler và thực thi
                handler = ActionFactory.get_handler(
                    self.controller.root, action, self.view, self.model, self.controller
                )
                
                if handler:
                    # Thiết lập action frame
                    action_frame = next((f for f in self.view.action_frames
                                       if f.action.id == action.id), None)
                    if action_frame:
                        handler.action_frame = action_frame
                        action_frame.show_temporary_notification(
                            f"Đang thực thi trong ELSE IF"
                        )
                    
                    # Thực thi action
                    if action.action_type == ActionType.IF_CONDITION:
                        # Xử lý đặc biệt cho IF lồng
                        result = handler.play()
                        
                        if result:  # IF lồng sai
                            # Tìm đến END IF của IF lồng
                            inner_level = block_level
                            for j in range(i + 1, len(all_actions)):
                                inner_action = all_actions[j]
                                
                                if inner_action.action_type == ActionType.IF_CONDITION:
                                    inner_level += 1
                                elif inner_action.action_type == ActionType.END_IF_CONDITION:
                                    inner_level -= 1
                                    if inner_level < block_level:
                                        # Nhảy đến sau END IF của IF lồng
                                        i = j
                                        break
                    else:
                        # Các loại action khác
                        handler.play()
            
            # Chuyển đến action tiếp theo
            i += 1
