from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from constants import ActionType
import uuid

class IfConditionAction(BaseAction):
    
    def prepare_play(self):
        """Xử lý điều kiện IF"""
        # Tạo ID duy nhất cho IF hiện tại
        condition_id = str(uuid.uuid4())
        self.current_internal_condition_id = condition_id # LƯU ID NÀY LẠI

        # Lấy cấp độ lồng hiện tại
        globals_var = GlobalVariables()
        current_level = globals_var.get("__condition_stack_size", 0)

        # Debug thông tin
        if hasattr(self, 'action_frame') and self.action_frame:
            self.action_frame.show_temporary_notification(
                f"IF (cấp {current_level}) - ID: {condition_id[:8]}"
            )

        # Đánh giá điều kiện
        condition_result = not self.should_break_action()

        # Hiển thị kết quả điều kiện
        if hasattr(self, 'action_frame') and self.action_frame:
            result_text = "Đúng" if condition_result else "Sai"
            self.action_frame.show_temporary_notification(f"Điều kiện: {result_text}")

        # Đẩy thông tin IF này vào stack
        globals_var.set("__condition_stack_size", current_level + 1)
        globals_var.set(f"__condition_id_{current_level}", condition_id)
        globals_var.set(f"__condition_result_{condition_id}", condition_result) # QUAN TRỌNG: Lưu kết quả của CHÍNH IF NÀY
        globals_var.set(f"__condition_type_{condition_id}", "IF")
        globals_var.set(f"__condition_parent_{condition_id}",
                        globals_var.get(f"__condition_id_{current_level-1}", "") if current_level > 0 else "")

        # Khi chạy độc lập (nút Play) hoặc được gọi từ ActionController
        if hasattr(self, 'view') and self.view and self.model: # Điều kiện này đúng khi play từng action
            if condition_result:
                # Điều kiện đúng: thực thi các action trong khối
                self._execute_condition_block(condition_id)
            # else:
                 # Điều kiện sai: action_controller sẽ gọi _find_matching_else_if
                 # không cần gọi ở đây khi play() vì nó sẽ bị gọi 2 lần.
                 # self._find_matching_else_if(condition_id) # Bỏ dòng này

        # Khôi phục stack khi kết thúc (chỉ khi chạy độc lập hoàn toàn)
        # Nếu không phải chạy sequence, thì sau khi play xong 1 IF, stack level phải được khôi phục.
        # Tuy nhiên, trong ngữ cảnh _execute_condition_block, việc này sẽ do EndIfCondition xử lý.
        # Tạm thời để như cũ, nhưng cần xem xét lại nếu có lỗi về stack level.
        # globals_var.set("__condition_stack_size", current_level) # Có thể gây lỗi nếu _execute_condition_block chạy

        return not condition_result # Trả về True nếu điều kiện IF của CHÍNH NÓ là Sai

   
    def _find_matching_else_if(self, condition_id_of_this_if_that_was_false=None): # Đổi tên param
        from controllers.actions.action_factory import ActionFactory # Đảm bảo import

        """Tìm ELSE IF tương ứng khi điều kiện của IF (condition_id_of_this_if_that_was_false) là SAI."""
        all_actions = self.model.get_all_actions()
        # current_index là index của IF (condition_id_of_this_if_that_was_false)
        current_if_index = next((i for i, a in enumerate(all_actions) if a.id == self.action.id), -1)
        if current_if_index < 0:
            return False

        globals_var = GlobalVariables()
        # current_level_of_this_if là cấp độ của IF (condition_id_of_this_if_that_was_false)
        # current_level_of_this_if = globals_var.get("__condition_stack_size", 0) - 1 # Stack đã được IF này tăng

        # Nếu không truyền condition_id, sử dụng ID nội bộ của IF này
        if not condition_id_of_this_if_that_was_false and hasattr(self, 'current_internal_condition_id'):
            condition_id_of_this_if_that_was_false = self.current_internal_condition_id
        elif not condition_id_of_this_if_that_was_false:
             # Fallback nếu current_internal_condition_id không tồn tại
            current_level_of_this_if = globals_var.get("__condition_stack_size", 0) -1
            condition_id_of_this_if_that_was_false = globals_var.get(f"__condition_id_{current_level_of_this_if}", "")


        if hasattr(self, 'action_frame') and self.action_frame:
            self.action_frame.show_temporary_notification(
                f"IF-{condition_id_of_this_if_that_was_false[:8] if condition_id_of_this_if_that_was_false else 'Unknown'} SAI, tìm ELSE IF..."
            )

        # block_internal_nesting_level để theo dõi các IF/END_IF lồng bên trong phạm vi tìm kiếm
        block_internal_nesting_level = 0

        for i in range(current_if_index + 1, len(all_actions)):
            action_in_search = all_actions[i]
            action_type_in_search = action_in_search.action_type

            if action_type_in_search == ActionType.IF_CONDITION:
                block_internal_nesting_level += 1
            elif action_type_in_search == ActionType.ELSE_IF_CONDITION:
                if block_internal_nesting_level == 0:
                    # Tìm thấy ELSE IF cùng cấp với IF (condition_id_of_this_if_that_was_false)
                    if hasattr(self, 'action_frame') and self.action_frame:
                        self.action_frame.show_temporary_notification(f"→ Tìm thấy ELSE IF tại index {i}")

                    # QUAN TRỌNG: Truyền ID của IF gốc (condition_id_of_this_if_that_was_false)
                    # cho ELSE IF để nó biết nó thuộc về khối IF nào.
                    globals_var.set("__current_else_if_parent", condition_id_of_this_if_that_was_false)

                    # Tạo handler và thực thi ELSE IF
                    else_if_handler = ActionFactory.get_handler(
                        self.controller.root, action_in_search, self.view, self.model, self.controller
                    )
                    if else_if_handler:
                        else_if_action_frame = next((f for f in self.view.action_frames
                                                   if f.action.id == action_in_search.id), None)
                        if else_if_action_frame:
                            else_if_handler.action_frame = else_if_action_frame
                    
                        else_if_handler.play() # Sẽ gọi prepare_play của ElseIfConditionAction
                        return True # Đã tìm và xử lý một ELSE IF
            elif action_type_in_search == ActionType.END_IF_CONDITION:
                if block_internal_nesting_level == 0:
                    # Đã tìm thấy END IF của IF (condition_id_of_this_if_that_was_false) mà không có ELSE IF nào được thực thi
                    if hasattr(self, 'action_frame') and self.action_frame:
                        self.action_frame.show_temporary_notification(f"→ Không tìm thấy ELSE IF, kết thúc khối.")
                    return False # Không tìm thấy ELSE IF phù hợp
                block_internal_nesting_level -= 1
        return False # Quét hết mà không tìm thấy END IF (có thể là lỗi cấu trúc)


        
    def _execute_condition_block(self, condition_id_of_this_block): # Đổi tên param để rõ ràng
        """Thực thi các action trong khối điều kiện của IF này"""
        from controllers.actions.action_factory import ActionFactory
        from constants import ActionType
        from models.global_variables import GlobalVariables # Đảm bảo import

        all_actions = self.model.get_all_actions()
        # current_index là index của IF hiện tại (ví dụ IF L1)
        current_block_start_index = next((i for i, a in enumerate(all_actions) if a.id == self.action.id), -1)
        if current_block_start_index < 0:
            return

        globals_var = GlobalVariables()
        # current_level_of_this_block là cấp độ của IF đang chứa khối này
        # current_level_of_this_block = globals_var.get("__condition_stack_size", 0) - 1 # Stack đã tăng trong prepare_play

        if hasattr(self, 'action_frame') and self.action_frame:
            self.action_frame.show_temporary_notification(
                f"Bắt đầu khối IF-{condition_id_of_this_block[:8]}"
            )

        # block_level dùng để theo dõi các IF/END_IF lồng nhau BÊN TRONG khối này
        block_internal_nesting_level = 0

        i = current_block_start_index + 1
        while i < len(all_actions):
            action_to_execute_inside_block = all_actions[i]
            action_type_inside_block = action_to_execute_inside_block.action_type

            # Xử lý thoát khỏi khối IF hiện tại
            if action_type_inside_block == ActionType.ELSE_IF_CONDITION and block_internal_nesting_level == 0:
                # Gặp ELSE IF cùng cấp với IF hiện tại (condition_id_of_this_block), dừng thực thi khối này
                break
            if action_type_inside_block == ActionType.END_IF_CONDITION:
                if block_internal_nesting_level == 0:
                    # Gặp END IF của IF hiện tại (condition_id_of_this_block), dừng thực thi khối này
                    break
                block_internal_nesting_level -= 1 # Giảm level cho IF lồng bên trong

            # Lấy handler cho action bên trong khối
            inner_handler = ActionFactory.get_handler(
                self.controller.root, action_to_execute_inside_block, self.view, self.model, self.controller
            )

            if inner_handler:
                # Thiết lập action frame
                inner_action_frame = next((f for f in self.view.action_frames
                                       if f.action.id == action_to_execute_inside_block.id), None)
                if inner_action_frame:
                    inner_handler.action_frame = inner_action_frame
                    inner_action_frame.show_temporary_notification(
                        f"Trong IF-{condition_id_of_this_block[:8]}"
                    )

                if action_type_inside_block == ActionType.IF_CONDITION:
                    block_internal_nesting_level += 1 # Tăng level cho IF lồng bên trong
                    # inner_handler ở đây là một IfConditionAction khác (IF lồng)
                
                    # Thực thi IF lồng
                    nested_if_play_result = inner_handler.play() # Sẽ gọi prepare_play của IF lồng

                    # nested_if_play_result là TRUE nếu điều kiện của IF LỒNG là SAI

                    # Kiểm tra thuộc tính condition_evaluated của IF lồng
                    # (được set trong BaseAction.play qua should_break_action)
                    if hasattr(inner_handler, 'condition_evaluated') and not inner_handler.condition_evaluated:
                        # IF lồng đã bị bỏ qua do điều kiện break của chính nó (should_break_action trả về true)
                        # Điều này có nghĩa là điều kiện của IF lồng là SAI.
                        if inner_action_frame:
                            inner_action_frame.show_temporary_notification(
                                f"IF lồng (break) SAI, tìm ELSE IF..."
                            )
                        # Tìm và thực thi ELSE IF cho IF lồng này
                        # Sử dụng ID của IF lồng được tạo trong prepare_play của nó
                        if hasattr(inner_handler, 'current_internal_condition_id'):
                            self.controller.root.after(100, lambda h=inner_handler, c_id=inner_handler.current_internal_condition_id: h._find_matching_else_if(c_id))


                        # Nhảy đến END_IF của IF lồng này
                        # Cần cẩn thận với block_internal_nesting_level ở đây
                        temp_search_level = block_internal_nesting_level -1 # Vì IF này đã được tính vào block_internal_nesting_level
                        for j in range(i + 1, len(all_actions)):
                            search_action = all_actions[j]
                            if search_action.action_type == ActionType.IF_CONDITION:
                                temp_search_level += 1
                            elif search_action.action_type == ActionType.END_IF_CONDITION:
                                if temp_search_level == (block_internal_nesting_level -1) : # END IF của IF lồng hiện tại
                                    i = j # Nhảy đến END_IF này
                                    break
                                temp_search_level -= 1
                        # Bỏ qua phần còn lại của vòng lặp hiện tại, để i được tăng và xử lý END_IF
                        continue # Quan trọng

                    elif nested_if_play_result: # Điều kiện của IF lồng là SAI (play() trả về True)
                        if inner_action_frame:
                            inner_action_frame.show_temporary_notification(
                                f"IF lồng (play) SAI, tìm ELSE IF..."
                            )
                        # Tìm và thực thi ELSE IF cho IF lồng này
                        if hasattr(inner_handler, 'current_internal_condition_id'):
                             self.controller.root.after(100, lambda h=inner_handler, c_id=inner_handler.current_internal_condition_id: h._find_matching_else_if(c_id))

                        # Nhảy đến END_IF của IF lồng này
                        temp_search_level = block_internal_nesting_level - 1
                        for j in range(i + 1, len(all_actions)):
                            search_action = all_actions[j]
                            if search_action.action_type == ActionType.IF_CONDITION:
                                temp_search_level += 1
                            elif search_action.action_type == ActionType.END_IF_CONDITION:
                                if temp_search_level == (block_internal_nesting_level -1):
                                    i = j # Nhảy đến END_IF này
                                    break
                                temp_search_level -= 1
                        continue # Quan trọng
                    # Nếu IF lồng ĐÚNG (nested_if_play_result is False), không làm gì thêm, nó sẽ tự thực thi khối của nó
                    # qua _execute_condition_block của chính nó.
                else:
                    # Các loại action khác không phải IF (ví dụ: MouseMove, ElseIf, EndIf)
                    # ElseIf và EndIf sẽ được xử lý bởi logic thoát khối ở đầu vòng lặp while.
                    # Chỉ thực thi các action khác (như MouseMove).
                    if action_type_inside_block not in [ActionType.ELSE_IF_CONDITION, ActionType.END_IF_CONDITION]:
                        inner_handler.play()
            i += 1

