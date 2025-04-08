from core.interfaces import VariableManagerInterface

class GlobalVariables(VariableManagerInterface):
    """Class quản lý biến toàn cục giữa các hành động"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalVariables, cls).__new__(cls)
            cls._instance.variables = {}
        return cls._instance

    def set(self, name, value):
        self.variables[name] = value

    def get(self, name, default=0):
        return self.variables.get(name, default)

    def get_all(self):
        return self.variables.copy()
