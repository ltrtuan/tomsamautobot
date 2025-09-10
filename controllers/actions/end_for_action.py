from controllers.actions.base_action import BaseAction

class EndForAction(BaseAction):
    def prepare_play(self):
        """End For action được xử lý trong logic For Loop"""
        print(f"[END FOR ACTION] End For action prepare_play() - Logic được xử lý trong For Loop")
        return False
