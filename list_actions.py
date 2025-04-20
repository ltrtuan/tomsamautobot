from enum import Enum, auto

class ActionType(Enum):
    TIM_HINH_ANH = "Tìm Hình Ảnh"
    DI_CHUYEN_CHUOT = "Di Chuyển Chuột"
    
    @classmethod
    def get_display_values(cls):
        """Trả về danh sách các giá trị hiển thị"""
        return [member.value for member in cls]