# Configuration settings for the application
APP_TITLE = "Ứng dụng Điều Khiển Máy Tính"
APP_WIDTH = 600
APP_HEIGHT = 500

# Available action types
ACTION_TYPES = ["Tìm Hình Ảnh", "Di Chuyển Chuột"]

# Default values
DEFAULT_CONFIDENCE = 0.8
DEFAULT_DURATION = 0.2

# Màu sắc chính
PRIMARY_COLOR = "#0078d4"  # Màu xanh Microsoft
SECONDARY_COLOR = "#106ebe"
LIGHT_BG_COLOR = "#f5f5f5"
HOVER_COLOR = "#f0f0f0"
BORDER_COLOR = "#e0e0e0"
DANGER_COLOR = "#d13438"
SUCCESS_COLOR = "#107c10"

# Padding và spacing
SMALL_PADDING = 2
MEDIUM_PADDING = 5
LARGE_PADDING = 10

# Font
DEFAULT_FONT = ("Segoe UI", 10)
HEADER_FONT = ("Segoe UI", 11, "bold")
TITLE_FONT = ("Segoe UI", 14, "bold")

# Màu sắc bổ sung cho kéo thả
DRAG_PLACEHOLDER_COLOR = "#f2f3ed"     # Màu xám đậm cho placeholder
DRAG_HANDLE_COLOR = "#666666"          # Màu cho nút kéo thả
DRAG_HIGHLIGHT_COLOR = "#0066cc"       # Màu viền khi đang kéo
DRAG_ACTIVE_BG = "#e0e0e0"             # Màu nền khi đang kéo


# Biến toàn cục
FILE_PATH = ""

# Hàm lưu cấu hình
def save_config():
    import json
    import os
    
    config_data = {
        "FILE_PATH": FILE_PATH
    }
    
    # Lưu vào file config
    config_file = os.path.join(os.path.dirname(__file__), "app_config.json")
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=4)

# Hàm tải cấu hình
def load_config():
    import json
    import os
    global FILE_PATH
    
    config_file = os.path.join(os.path.dirname(__file__), "app_config.json")
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config_data = json.load(f)
                FILE_PATH = config_data.get("FILE_PATH", "")
        except Exception as e:
            print(f"Lỗi khi tải cấu hình: {e}")