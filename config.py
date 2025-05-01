# Configuration settings for the application
APP_TITLE = "Ứng dụng Điều Khiển Máy Tính"
APP_WIDTH = 600
APP_HEIGHT = 500


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


# Configuration settings for the application
import os
import hashlib
import json
import base64

# Define the directory for app_config.json
CONFIG_DIR = "C:\\tomsamautobot"
CONFIG_FILE = "app_config.json"
CONFIG_PATH = os.path.join(CONFIG_DIR, CONFIG_FILE)
AUTH_ENV_VAR = "tomsamautobot_auth"
# Thông tin đăng nhập mặc định (đã được mã hóa)
ENCRYPTED_USERNAME = "36997e66306f6da5c646ea4a605b533f61e62ccb702996dcc34d4d093b474140"
ENCRYPTED_PASSWORD = "ae6ef896e85acb354c5c699b2d934fdc19b92bd1f8c485d90bebdba5190299d2"

# Mã hóa dữ liệu bằng SHA-256
def encrypt_data(data):
    """Mã hóa dữ liệu bằng SHA-256"""
    data_bytes = data.encode('utf-8')
    hash_object = hashlib.sha256(data_bytes)
    return hash_object.hexdigest()

# Xác minh thông tin đăng nhập
def verify_credentials(username, password):
    """Kiểm tra thông tin đăng nhập có khớp với dữ liệu mã hóa không"""
    encrypted_user = encrypt_data(username)
    encrypted_pass = encrypt_data(password)    
    
    return encrypted_user == ENCRYPTED_USERNAME and encrypted_pass == ENCRYPTED_PASSWORD

# Lưu thông tin xác thực vào biến môi trường
def save_auth_to_env():
    """Lưu thông tin xác thực vào biến môi trường Windows"""
    # Tạo chuỗi xác thực
    auth_string = f"{ENCRYPTED_USERNAME}:{ENCRYPTED_PASSWORD}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    # Lưu vào biến môi trường (chỉ phiên hiện tại)
    os.environ[AUTH_ENV_VAR] = encoded_auth
    
    # Sử dụng lệnh hệ thống để lưu vĩnh viễn
    try:
        os.system(f'setx {AUTH_ENV_VAR} "{encoded_auth}"')
        return True
    except Exception as e:
        print(f"Lỗi khi lưu biến môi trường: {e}")
        return False

# Kiểm tra xác thực từ biến môi trường
def check_auth_from_env():
    """Kiểm tra xem biến môi trường xác thực có tồn tại và chính xác không"""
    try:       
        auth_string = None
        
        # Thử đọc từ registry trực tiếp vì đang chạy trên Windows
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment")
            value, _ = winreg.QueryValueEx(key, AUTH_ENV_VAR)
            auth_string = value
        except Exception as e:
            print(f"Lỗi khi đọc từ Registry: {e}")
        
        # Nếu không đọc được từ Registry, thử các phương thức thông thường
        if not auth_string:
            auth_string = os.getenv(AUTH_ENV_VAR)
            if not auth_string:
                return False
        
        # Giải mã chuỗi xác thực
        decoded_auth = base64.b64decode(auth_string.encode()).decode()
        stored_username, stored_password = decoded_auth.split(":")
        
        # Kiểm tra với giá trị đã mã hóa
        result = stored_username == ENCRYPTED_USERNAME and stored_password == ENCRYPTED_PASSWORD
        return result
    except Exception as e:
        print(f"Lỗi khi kiểm tra xác thực từ biến môi trường: {e}")
        return False


    

# Biến toàn cục
FILE_PATH = ""

# Ensure the config directory exists
def ensure_config_directory():
    if not os.path.exists(CONFIG_DIR):
        try:
            os.makedirs(CONFIG_DIR)
            print(f"Created config directory at {CONFIG_DIR}")
        except Exception as e:
            print(f"Error creating config directory: {e}")
            return False
    return True

# Hàm lưu cấu hình
def save_config():
    if not ensure_config_directory():
        return

    config_data = {
        "FILE_PATH": FILE_PATH
    }

    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config_data, f, indent=4)
        print(f"Configuration saved to {CONFIG_PATH}")
    except Exception as e:
        print(f"Error saving configuration: {e}")

# Hàm tải cấu hình
def load_config():
    global FILE_PATH
    
    # Ensure the config directory exists
    ensure_config_directory()
    
    # Check if the config file exists
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                config_data = json.load(f)
            FILE_PATH = config_data.get("FILE_PATH", "")
            print(f"Configuration loaded from {CONFIG_PATH}")
        except Exception as e:
            print(f"Error loading configuration: {e}")
    else:
        # Create a default config file
        save_config()
        print(f"Created default configuration file at {CONFIG_PATH}")