from constants import ActionType
from controllers.actions.mouse_move_action import MouseMoveAction
from controllers.actions.image_search_action import ImageSearchAction
from controllers.actions.tao_bien_action import TaoBienAction
from controllers.actions.if_condition_action import IfConditionAction
from controllers.actions.else_if_condition_action import ElseIfConditionAction
from controllers.actions.end_if_condition_action import EndIfConditionAction
from controllers.actions.for_action import ForAction
from controllers.actions.end_for_action import EndForAction
from controllers.actions.break_for_action import BreakForAction
from controllers.actions.skip_for_action import SkipForAction

class ActionFactory:
    """Factory tạo ra play handler dựa vào loại action"""
    
    @staticmethod
    def get_handler(root, action, view, model, controller):
        """
        Trả về handler phù hợp với loại action
        
        Args:
            root: Tkinter root window
            action: ActionItem được thực thi
            view: View để hiển thị thông báo
            
        Returns:
            BasePlayHandler: Handler phù hợp
        """
        action_type = action.action_type
        
        print(f"[FACTORY DEBUG] Creating handler for: {action_type}")
        
        if action_type == ActionType.DI_CHUYEN_CHUOT:
            return MouseMoveAction(root, action, view, model, controller)
        elif action_type == ActionType.TIM_HINH_ANH:
            return ImageSearchAction(root, action, view, model, controller)
        elif action_type == ActionType.TAO_BIEN:
            return TaoBienAction(root, action, view, model, controller)
        elif action_type == ActionType.IF_CONDITION:
            return IfConditionAction(root, action, view, model, controller)
        elif action_type == ActionType.ELSE_IF_CONDITION:
            handler = ElseIfConditionAction(root, action, view, model, controller)
            print(f"[FACTORY DEBUG] Created ElseIfConditionAction: {handler}")
            return handler
        elif action_type == ActionType.END_IF_CONDITION:
            return EndIfConditionAction(root, action, view, model, controller)
        elif action_type == ActionType.FOR_LOOP:
            return ForAction(root, action, view, model, controller)
        elif action_type == ActionType.END_FOR_LOOP:
            return EndForAction(root, action, view, model, controller)
        elif action_type == ActionType.BREAK_FOR_LOOP:
            return BreakForAction(root, action, view, model, controller)
        elif action_type == ActionType.SKIP_FOR_LOOP:
            return SkipForAction(root, action, view, model, controller)
        else:
            # Trả về None nếu không tìm thấy handler phù hợp
            return None
