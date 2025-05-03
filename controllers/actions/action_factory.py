from constants import ActionType
from controllers.actions.mouse_move_action import MouseMoveAction
from controllers.actions.image_search_action import ImageSearchAction
from controllers.actions.tao_bien_action import TaoBienAction

class ActionFactory:
    """Factory tạo ra play handler dựa vào loại action"""
    
    @staticmethod
    def get_handler(root, action, view):
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
        
        if action_type == ActionType.DI_CHUYEN_CHUOT:
            return MouseMoveAction(root, action, view)
        elif action_type == ActionType.TIM_HINH_ANH:
            return ImageSearchAction(root, action, view)
        elif action_type == ActionType.TAO_BIEN:
            return TaoBienAction(root, action, view)
        else:
            # Trả về None nếu không tìm thấy handler phù hợp
            return None
