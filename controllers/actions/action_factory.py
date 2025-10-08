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
from controllers.actions.keyboard_action import KeyboardAction
from controllers.actions.input_text_action import InputTextAction
from controllers.actions.read_txt_action import ReadTxtAction
from controllers.actions.read_csv_action import ReadCsvAction
from controllers.actions.write_txt_action import WriteTxtAction
from controllers.actions.write_csv_action import WriteCsvAction
from controllers.actions.text_search_action import TextSearchAction
from controllers.actions.show_hide_program_action import ShowHideProgramAction
from controllers.actions.check_fullscreen_action import CheckFullscreenAction
from controllers.actions.image_search_live_action import ImageSearchLiveAction
from controllers.actions.copy_folder_action import CopyFolderAction
from controllers.actions.run_cmd_action import RunCmdAction
from controllers.actions.gologin_create_action import GoLoginCreateAction
from controllers.actions.gologin_start_action import GoLoginStartAction
from controllers.actions.gologin_stop_action import GoLoginStopAction
from controllers.actions.upload_script_action import UploadScriptAction

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
        elif action_type == ActionType.BANPHIM:
             return KeyboardAction(root, action, view, model, controller)
        elif action_type == ActionType.INPUT_TEXT:
            return InputTextAction(root, action, view, model, controller)
        elif action_type == ActionType.READ_TXT:
            return ReadTxtAction(root, action, view, model, controller)
        elif action_type == ActionType.READ_CSV:
            return ReadCsvAction(root, action, view, model, controller)
        elif action_type == ActionType.WRITE_TXT:
            return WriteTxtAction(root, action, view, model, controller)
        elif action_type == ActionType.WRITE_CSV:
            return WriteCsvAction(root, action, view, model, controller)
        elif action_type == ActionType.TEXT_SEARCH:
            return TextSearchAction(root, action, view, model, controller)
        elif action_type == ActionType.SHOW_HIDE_PROGRAM:
            return ShowHideProgramAction(root, action, view, model, controller)
        elif action_type == ActionType.CHECK_FULLSCREEN:
            return CheckFullscreenAction(root, action, view, model, controller)
        elif action_type == ActionType.IMAGE_SEARCH_LIVE:
            return ImageSearchLiveAction(root, action, view, model, controller)
        elif action_type == ActionType.COPY_FOLDER:
            return CopyFolderAction(root, action, view, model, controller)
        elif action_type == ActionType.RUN_CMD:
            return RunCmdAction(root, action, view, model, controller)
        elif action_type == ActionType.GOLOGIN_CREATE_PROFILE:
            return GoLoginCreateAction(root, action, view, model, controller)

        elif action_type == ActionType.GOLOGIN_START_PROFILE:
            return GoLoginStartAction(root, action, view, model, controller)

        elif action_type == ActionType.GOLOGIN_STOP_PROFILE:
            return GoLoginStopAction(root, action, view, model, controller)
        
        elif action_type == ActionType.UPLOAD_SCRIPT:
            return UploadScriptAction(root, action, view, model, controller)
        else:
            # Trả về None nếu không tìm thấy handler phù hợp
            return None
