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
LOG_RETENTION_DAYS = 7
# ========== SMTP Email Configuration (NEW) ==========
SMTP_ENABLED = False
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USE_TLS = True
SMTP_USERNAME = ""       # Email gửi (sender)
SMTP_PASSWORD = ""       # Password (plain text - simple project)
SMTP_TO_EMAIL = ""       # Email nhận cảnh báo (recipient)
SMTP_FROM_EMAIL = ""
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
        "FILE_PATH": FILE_PATH,
        "LOG_RETENTION_DAYS": LOG_RETENTION_DAYS,
        # ========== SMTP Config (NEW) ==========
        "SMTP_ENABLED": SMTP_ENABLED,
        "SMTP_HOST": SMTP_HOST,
        "SMTP_PORT": SMTP_PORT,
        "SMTP_USE_TLS": SMTP_USE_TLS,
        "SMTP_USERNAME": SMTP_USERNAME,
        "SMTP_PASSWORD": SMTP_PASSWORD,
        "SMTP_TO_EMAIL": SMTP_TO_EMAIL,
        "SMTP_FROM_EMAIL": SMTP_FROM_EMAIL,
    }

    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config_data, f, indent=4)
        print(f"Configuration saved to {CONFIG_PATH}")
    except Exception as e:
        print(f"Error saving configuration: {e}")

# Hàm tải cấu hình
def load_config():    
    global FILE_PATH, SMTP_ENABLED, SMTP_HOST, SMTP_PORT, SMTP_USE_TLS, LOG_RETENTION_DAYS
    global SMTP_USERNAME, SMTP_PASSWORD, SMTP_TO_EMAIL, SMTP_FROM_EMAIL
    # Ensure the config directory exists
    ensure_config_directory()
    
    # Check if the config file exists
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                config_data = json.load(f)
            FILE_PATH = config_data.get("FILE_PATH", "")
            LOG_RETENTION_DAYS = config_data.get("LOG_RETENTION_DAYS", 7)
            # ========== Load SMTP Config (NEW) ==========
            SMTP_ENABLED = config_data.get("SMTP_ENABLED", False)
            SMTP_HOST = config_data.get("SMTP_HOST", "smtp.gmail.com")
            SMTP_PORT = config_data.get("SMTP_PORT", 587)
            SMTP_USE_TLS = config_data.get("SMTP_USE_TLS", True)
            SMTP_USERNAME = config_data.get("SMTP_USERNAME", "")
            SMTP_PASSWORD = config_data.get("SMTP_PASSWORD", "")
            SMTP_TO_EMAIL = config_data.get("SMTP_TO_EMAIL", "")
            SMTP_FROM_EMAIL = config_data.get("SMTP_FROM_EMAIL", "")

            print(f"Configuration loaded from {CONFIG_PATH}")
        except Exception as e:
            print(f"Error loading configuration: {e}")
    else:
        # Create a default config file
        save_config()
        print(f"Created default configuration file at {CONFIG_PATH}")



# ============================================================================
# AUTO RESTART CONFIGURATION - Quản lý biến môi trường cho tính năng auto restart
# Đã thêm 13 functions mới:

# ✅ get_auto_restart_minutes() - Đọc setting số phút restart
# ✅ set_auto_restart_minutes(minutes) - Lưu setting
# ✅ get_crash_timestamp() - Đọc timestamp crash
# ✅ set_crash_timestamp(timestamp) - Ghi timestamp crash
# ✅ clear_crash_timestamp() - Xóa timestamp
# ✅ get_crash_count() - Đọc số lần crash
# ✅ increment_crash_count() - Tăng counter
# ✅ reset_crash_count() - Reset counter về 0
# ✅ get_last_crash_reset() - Đọc timestamp lần reset cuối
# ✅ set_last_crash_reset(timestamp) - Ghi timestamp reset
# ✅ set_app_running(is_running) - Đánh dấu app đang Start
# ✅ is_app_running() - Check app có đang Start không
# ✅ get_restart_countdown() - Đọc countdown
# ✅ set_restart_countdown(minutes) - Ghi countdown

# Pattern đã follow:

# ✅ Đọc từ Windows Registry trước (giống check_auth_from_env)
# ✅ Fallback sang os.getenv()
# ✅ Ghi bằng setx (giống set_auth_to_env)
# ✅ Update luôn os.environ của process hiện tại
# ============================================================================

def get_auto_restart_minutes():
    """
    Lấy số phút đợi trước khi auto restart app sau khi crash
    
    Returns:
        int: Số phút (default = 6)
    
    Logic:
        1. Thử đọc từ Windows Registry (HKEY_CURRENT_USER\\Environment)
        2. Nếu fail → đọc từ os.getenv()
        3. Nếu không có → trả về default = 6
    """
    restart_minutes = None
    
    # Thử đọc từ Windows Registry trước
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment")
        value, _ = winreg.QueryValueEx(key, "TOMSAM_AUTO_RESTART_MINUTES")
        restart_minutes = int(value)
        winreg.CloseKey(key)
    except Exception as e:
        # Không có trong Registry hoặc lỗi đọc
        pass
    
    # Nếu không đọc được từ Registry, thử os.getenv()
    if restart_minutes is None:
        try:
            env_value = os.getenv("TOMSAM_AUTO_RESTART_MINUTES")
            if env_value:
                restart_minutes = int(env_value)
        except (ValueError, TypeError):
            pass
    
    # Nếu vẫn không có, trả về default = 6
    if restart_minutes is None:
        restart_minutes = 6
    
    return restart_minutes


def set_auto_restart_minutes(minutes):
    """
    Lưu số phút auto restart vào biến môi trường Windows (persistent)
    
    Args:
        minutes (int): Số phút đợi (>= 0, 0 = tắt auto restart)
    
    Logic:
        1. Dùng lệnh setx để ghi vào Windows Registry
        2. Update luôn os.environ của process hiện tại
    """
    # Validate input
    try:
        minutes = int(minutes)
        if minutes < 0:
            minutes = 0
    except (ValueError, TypeError):
        minutes = 6  # Default nếu input không hợp lệ
    
    # Ghi vào Windows Registry bằng setx
    os.system(f'setx TOMSAM_AUTO_RESTART_MINUTES {minutes}')
    
    # Update biến môi trường của process hiện tại (để không cần restart app)
    os.environ['TOMSAM_AUTO_RESTART_MINUTES'] = str(minutes)


def get_crash_timestamp():
    """
    Lấy timestamp của lần crash cuối cùng
    
    Returns:
        str: Timestamp dạng "2025-11-23 14:33:00" hoặc "" nếu chưa có
    """
    crash_timestamp = None
    
    # Thử đọc từ Windows Registry trước
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment")
        value, _ = winreg.QueryValueEx(key, "TOMSAM_CRASH_TIMESTAMP")
        crash_timestamp = value
        winreg.CloseKey(key)
    except Exception:
        pass
    
    # Nếu không đọc được từ Registry, thử os.getenv()
    if not crash_timestamp:
        crash_timestamp = os.getenv("TOMSAM_CRASH_TIMESTAMP", "")
    
    return crash_timestamp


def set_crash_timestamp(timestamp):
    """
    Ghi timestamp khi app crash
    
    Args:
        timestamp (str): Timestamp dạng "2025-11-23 14:33:00"
    """
    # Ghi vào Windows Registry
    os.system(f'setx TOMSAM_CRASH_TIMESTAMP "{timestamp}"')
    
    # Update process hiện tại
    os.environ['TOMSAM_CRASH_TIMESTAMP'] = timestamp


def clear_crash_timestamp():
    """
    Xóa timestamp crash (khi đã xử lý xong hoặc user Start thủ công)
    """
    # Ghi chuỗi rỗng vào Registry
    os.system('setx TOMSAM_CRASH_TIMESTAMP ""')
    
    # Update process hiện tại
    os.environ['TOMSAM_CRASH_TIMESTAMP'] = ''


def get_crash_count():
    """
    Lấy số lần crash gần đây (dùng để limit max 3 lần/10 phút)
    
    Returns:
        int: Số lần crash (default = 0)
    """
    crash_count = None
    
    # Thử đọc từ Registry
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment")
        value, _ = winreg.QueryValueEx(key, "TOMSAM_CRASH_COUNT")
        crash_count = int(value)
        winreg.CloseKey(key)
    except Exception:
        pass
    
    # Fallback sang os.getenv()
    if crash_count is None:
        try:
            env_value = os.getenv("TOMSAM_CRASH_COUNT")
            if env_value:
                crash_count = int(env_value)
        except (ValueError, TypeError):
            pass
    
    # Default = 0
    if crash_count is None:
        crash_count = 0
    
    return crash_count


def increment_crash_count():
    """
    Tăng counter crash lên 1 (gọi mỗi khi app crash)
    """
    current_count = get_crash_count()
    new_count = current_count + 1
    
    # Ghi vào Registry
    os.system(f'setx TOMSAM_CRASH_COUNT {new_count}')
    
    # Update process hiện tại
    os.environ['TOMSAM_CRASH_COUNT'] = str(new_count)


def reset_crash_count():
    """
    Reset counter crash về 0 (gọi sau khi hết 10 phút)
    """
    os.system('setx TOMSAM_CRASH_COUNT 0')
    os.environ['TOMSAM_CRASH_COUNT'] = '0'


def get_last_crash_reset():
    """
    Lấy timestamp lần cuối reset crash counter
    
    Returns:
        str: Timestamp dạng "2025-11-23 14:33:00" hoặc "" nếu chưa có
    """
    last_reset = None
    
    # Đọc từ Registry
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment")
        value, _ = winreg.QueryValueEx(key, "TOMSAM_LAST_CRASH_RESET")
        last_reset = value
        winreg.CloseKey(key)
    except Exception:
        pass
    
    # Fallback
    if not last_reset:
        last_reset = os.getenv("TOMSAM_LAST_CRASH_RESET", "")
    
    return last_reset


def set_last_crash_reset(timestamp):
    """
    Ghi timestamp lần cuối reset counter
    
    Args:
        timestamp (str): Timestamp dạng "2025-11-23 14:33:00"
    """
    os.system(f'setx TOMSAM_LAST_CRASH_RESET "{timestamp}"')
    os.environ['TOMSAM_LAST_CRASH_RESET'] = timestamp


def set_app_running(is_running):
    """
    Đánh dấu app có đang chạy (Start button đã được bấm) hay không
    
    Args:
        is_running (bool): True = đang chạy, False = đã Stop hoặc chưa Start
    
    Logic:
        Ghi "1" nếu True, "0" nếu False
        Watchdog sẽ check biến này để tự exit khi user đã Start thủ công
    """
    value = '1' if is_running else '0'
    
    os.system(f'setx TOMSAM_APP_IS_RUNNING {value}')
    os.environ['TOMSAM_APP_IS_RUNNING'] = value


def is_app_running():
    """
    Check app có đang chạy (Start) hay không
    
    Returns:
        bool: True nếu đang chạy, False nếu không
    """
    app_running = None
    
    # Đọc từ Registry
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment")
        value, _ = winreg.QueryValueEx(key, "TOMSAM_APP_IS_RUNNING")
        app_running = value
        winreg.CloseKey(key)
    except Exception:
        pass
    
    # Fallback
    if app_running is None:
        app_running = os.getenv("TOMSAM_APP_IS_RUNNING", "0")
    
    return app_running == '1'


def get_restart_countdown():
    """
    Lấy số phút còn lại đến khi watchdog tự động restart app
    
    Returns:
        int: Số phút còn lại (0 = không có countdown)
    
    Note:
        Biến này do watchdog_monitor.py ghi, ActionListView đọc để hiển thị countdown
    """
    countdown = None
    
    # Đọc từ Registry
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment")
        value, _ = winreg.QueryValueEx(key, "TOMSAM_RESTART_COUNTDOWN")
        countdown = int(value)
        winreg.CloseKey(key)
    except Exception:
        pass
    
    # Fallback
    if countdown is None:
        try:
            env_value = os.getenv("TOMSAM_RESTART_COUNTDOWN")
            if env_value:
                countdown = int(env_value)
        except (ValueError, TypeError):
            pass
    
    # Default = 0
    if countdown is None:
        countdown = 0
    
    return countdown


def set_restart_countdown(minutes):
    """
    Ghi số phút còn lại đến khi restart (watchdog gọi function này)
    
    Args:
        minutes (int): Số phút còn lại
    """
    os.system(f'setx TOMSAM_RESTART_COUNTDOWN {minutes}')
    os.environ['TOMSAM_RESTART_COUNTDOWN'] = str(minutes)


# ========== AUTO-START DELAY SETTING ==========
def get_auto_start_delay():
    """
    Get delay (in seconds) before auto-triggering play after restart
    
    Returns:
        int: Delay in seconds (0 = disable auto-trigger, default = 60)
    """
    try:
        return int(os.environ.get('TOMSAM_AUTO_START_DELAY', '60'))
    except:
        return 60  # Default 60 seconds

def set_auto_start_delay(seconds):
    """
    Set delay before auto-trigger
    
    Args:
        seconds (int): Delay in seconds (0 to disable)
    """
    os.environ['TOMSAM_AUTO_START_DELAY'] = str(int(seconds))
# ==============================================
