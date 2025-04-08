from abc import ABC, abstractmethod

class ActionInterface(ABC):
    """Interface chuẩn cho các loại hành động"""
    
    @abstractmethod
    def execute(self):
        """Thực hiện hành động"""
        pass
        
    @abstractmethod
    def get_parameters(self):
        """Lấy các tham số của hành động"""
        pass
        
    @abstractmethod
    def set_parameters(self, parameters):
        """Thiết lập các tham số của hành động"""
        pass

class VariableManagerInterface(ABC):
    """Interface cho quản lý biến"""
    
    @abstractmethod
    def set(self, name, value):
        """Thiết lập giá trị cho biến"""
        pass
        
    @abstractmethod
    def get(self, name, default=None):
        """Lấy giá trị của biến"""
        pass
