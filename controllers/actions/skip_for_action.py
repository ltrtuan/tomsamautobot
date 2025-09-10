from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables

class SkipForAction(BaseAction):
    def prepare_play(self):
        """Kiểm tra điều kiện Skip For action"""
        print(f"[SKIP FOR ACTION] Kiểm tra điều kiện Skip For")
        
        # Lấy break_conditions từ parameters
        break_conditions = self.action.parameters.get('break_conditions', [])
        
        # Nếu không có điều kiện nào, thực thi ngay
        if not break_conditions:
            print(f"[SKIP FOR ACTION] Không có điều kiện, thực thi Skip For ngay lập tức")
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
            
            print(f"[SKIP FOR ACTION] Điều kiện: {variable} = {expected_value}, Giá trị hiện tại: {current_value}, Kết quả: {condition_met}")
        
        if not condition_results:
            return False
        
        # Tất cả điều kiện phải đúng (AND logic)
        all_conditions_met = all(condition_results)
        
        print(f"[SKIP FOR ACTION] Tất cả điều kiện: {all_conditions_met}")
        return all_conditions_met
