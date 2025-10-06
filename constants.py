# constants.py
from enum import Enum, auto

class ActionType(str, Enum):
    TIM_HINH_ANH = "Image Search"
    IMAGE_SEARCH_LIVE = "Image Search Live"
    TEXT_SEARCH = "Text Search"
    DI_CHUYEN_CHUOT = "Mouse Move"
    TAO_BIEN = "Set Variable"
    IF_CONDITION = "If condition"
    ELSE_IF_CONDITION = "Else if condition"
    END_IF_CONDITION = "End If condition"
    FOR_LOOP = "For loop"
    END_FOR_LOOP = "End For loop"
    BREAK_FOR_LOOP = "Break For loop"
    SKIP_FOR_LOOP = "Skip For loop"
    BANPHIM       = "Keyboard"
    INPUT_TEXT = "Input Text"
    READ_TXT = "Read TXT File"
    READ_CSV = "Read CSV/Excel File"
    WRITE_TXT = "Write TXT File"
    WRITE_CSV = "Write CSV File"
    SHOW_HIDE_PROGRAM = "Show Hide Program"
    CHECK_FULLSCREEN = "Check Fullscreen"
    COPY_FOLDER = "Copy File/Folder"
    RUN_CMD = "Run CMD"
    GOLOGIN_CREATE_LAUNCH = "GoLogin Create and Launch Profile"
    
    
    @classmethod
    def get_display_values(cls):
        """Trả về danh sách các giá trị hiển thị cho ComboBox"""
        return [member.value for member in cls]
    
    @classmethod
    def from_display_value(cls, display_value):
        """Chuyển đổi từ giá trị hiển thị sang enum"""
        # Kiểm tra giá trị hiển thị trực tiếp
        for member in cls:
            if member.value == display_value:
                return member
    
        # Nếu display_value có dạng "ActionType.TIM_HINH_ANH"
        if isinstance(display_value, str) and "." in display_value:
            try:
                # Lấy phần sau dấu chấm (TIM_HINH_ANH)
                enum_name = display_value.split(".")[-1]
                # Lấy Enum tương ứng
                return getattr(cls, enum_name) #return <ActionType.TIM_HINH_ANH = "Tìm hình ảnh">
            except (AttributeError, KeyError):
                pass
    
        # Nếu không thể chuyển đổi, ném ra lỗi
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
            return action_type #return Tìm Hình Ảnh

# Các Enum khác có thể thêm vào đây
# class MouseButton(Enum):
#     TRAI = "left"
#     PHAI = "right"
#     GIUA = "middle"
    
#     @classmethod
#     def get_display_values(cls):
#         return [member.value for member in cls]
