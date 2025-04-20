# constants.py
from enum import Enum, auto

class ActionType(Enum):
    TIM_HINH_ANH = "Tìm Hình Ảnh"
    DI_CHUYEN_CHUOT = "Di Chuyển Chuột"
    
    @classmethod
    def get_display_values(cls):
        """Trả về danh sách các giá trị hiển thị cho ComboBox"""
        return [member.value for member in cls]
    
    @classmethod
    def from_display_value(cls, display_value):
        """Chuyển đổi từ giá trị hiển thị sang enum"""
        for member in cls:
            if member.value == display_value:
                return member
        raise ValueError(f"Không tìm thấy ActionType với giá trị: {display_value}")
    
    @classmethod
    def get_action_type_display(cls, action_type):
        """Chuyển đổi từ bất kỳ biểu diễn nào của ActionType sang giá trị hiển thị"""
        # Nếu action_type là một thể hiện của Enum
        if isinstance(action_type, cls):
            return action_type.value
        
        # Nếu action_type là chuỗi dạng "ActionType.TIM_HINH_ANH"
        if isinstance(action_type, str) and "." in action_type:
            try:
                # Lấy phần sau dấu chấm (TIM_HINH_ANH)
                enum_name = action_type.split(".")[-1]
                # Lấy Enum tương ứng
                return getattr(cls, enum_name).value
            except (AttributeError, KeyError):
                pass
    
        # Nếu là tên enum (TIM_HINH_ANH)
        try:
            return getattr(cls, action_type).value
        except (AttributeError, TypeError):
            # Trả về giá trị gốc nếu không thể chuyển đổi
            return action_type

# Các Enum khác có thể thêm vào đây
# class MouseButton(Enum):
#     TRAI = "left"
#     PHAI = "right"
#     GIUA = "middle"
    
#     @classmethod
#     def get_display_values(cls):
#         return [member.value for member in cls]
