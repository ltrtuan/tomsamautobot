from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables
from exceptions.loop_exceptions import LoopBreakException

class BreakForAction(BaseAction):

    def prepare_play(self):
        """Kiểm tra điều kiện Break For action"""
        print(f"[BREAK FOR ACTION] Kiểm tra điều kiện Break For")
        
        # Lấy break_conditions từ parameters
        break_conditions = self.action.parameters.get('break_conditions', [])
        
        # Nếu không có điều kiện nào, thực thi ngay
        if not break_conditions:
            print(f"[BREAK FOR ACTION] Không có điều kiện, thực thi Break For ngay lập tức")
            return True
        
        # Kiểm tra điều kiện
        global_vars = GlobalVariables()
        condition_results = []
        
        for condition in break_conditions:
            variable = condition.get('variable', '').strip()
            expected_value = condition.get('value', '').strip()
            
            if not variable:
                continue
            
            # Lấy giá trị hiện tại của biến
            current_value = str(global_vars.get(variable, "")).strip()
            
            # So sánh giá trị
            condition_met = (current_value == expected_value)
            condition_results.append(condition_met)
            
            print(f"[BREAK FOR ACTION] Điều kiện: {variable} = {expected_value}, Giá trị hiện tại: {current_value}, Kết quả: {condition_met}")
        
        if not condition_results:
            return False
        
        # Tất cả điều kiện phải đúng (AND logic)
        all_conditions_met = all(condition_results)
        print(f"[BREAK FOR ACTION] Tất cả điều kiện: {all_conditions_met}")
        
        return all_conditions_met

    def play(self):
        """QUAN TRỌNG: Throw exception để thoát ngay lập tức"""
        if self.prepare_play():
            print(f"[BREAK FOR ACTION] 🚫 THROWING LoopBreakException - Thoát tất cả vòng lặp ngay lập tức!")
            raise LoopBreakException("Break For condition met - exiting all loops immediately")
        
        return False
