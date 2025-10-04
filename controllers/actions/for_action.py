from controllers.actions.base_action import BaseAction
from models.global_variables import GlobalVariables

class ForAction(BaseAction):
    def prepare_play(self):
        """For action được xử lý trực tiếp trong ActionController.run_sequence()"""
        print(f"[FOR ACTION] For action prepare_play() - Logic được xử lý trong controller")
        return False  # Không cần xử lý gì thêm ở đây
