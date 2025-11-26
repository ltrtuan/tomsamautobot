# helpers/logger.py
import logging
import os
import glob
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
import config

class CustomRotatingFileHandler(RotatingFileHandler):
    """
    Custom RotatingFileHandler với naming format:
    - tomsamautobot-log-{d}-{m}-{y}.log
    - tomsamautobot-log-{d}-{m}-{y}-{index}.log (nếu rotate nhiều lần trong ngày)
    """
    
    def __init__(self, base_dir, maxBytes=10*1024*1024, backupCount=999, encoding='utf-8'):
        """
        Args:
            base_dir: Thư mục lưu logs (FILE_PATH/logs/)
            maxBytes: Kích thước tối đa mỗi file (default 10MB)
            backupCount: Số lượng backup files tối đa
            encoding: UTF-8 để support Vietnamese
        """
        self.base_dir = base_dir
        self.current_date = datetime.now().strftime("%d-%m-%Y")
        
        # ========== LƯU PARAMETERS VÀO self (FIX) ==========
        self._maxBytes = maxBytes
        self._backupCount = backupCount
        # ===================================================
        
        # Tạo thư mục logs nếu chưa có
        os.makedirs(base_dir, exist_ok=True)
        
        # Tìm file log hiện tại hoặc tạo mới
        filename = self._get_current_log_filename()
        
        # Gọi parent __init__
        super().__init__(
            filename=filename,
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding=encoding
        )
    
    def _get_current_log_filename(self):
        """
        Tìm file log hiện tại hoặc tạo mới
        
        Returns:
            str: Full path đến file log
        """
        base_name = f"tomsamautobot-log-{self.current_date}"
        
        # Tìm file hiện tại (nếu có)
        pattern = os.path.join(self.base_dir, f"{base_name}*.log")
        existing_files = glob.glob(pattern)
        
        if not existing_files:
            # Chưa có file → Tạo file mới
            return os.path.join(self.base_dir, f"{base_name}.log")
        
        # Có file rồi → Tìm file mới nhất
        existing_files.sort()
        latest_file = existing_files[-1]
        
        # Check format: tomsamautobot-log-{date}-{index}.log
        basename = os.path.basename(latest_file)
        
        if basename == f"{base_name}.log":
            # Format: tomsamautobot-log-{date}.log
            max_index = 0
        else:
            # Format: tomsamautobot-log-{date}-{index}.log
            try:
                # Extract index từ filename
                index_part = basename.replace(f"{base_name}-", "").replace(".log", "")
                max_index = int(index_part)
            except ValueError:
                max_index = 0
        
        # Kiểm tra file hiện tại có còn chỗ không
        if os.path.exists(latest_file) and os.path.getsize(latest_file) >= self._maxBytes:
            # File đã đạt maxBytes → Tạo file mới với index tăng
            max_index += 1
            return os.path.join(self.base_dir, f"{base_name}-{max_index}.log")
        else:
            # File còn chỗ → Dùng file hiện tại
            return latest_file
    
    def shouldRollover(self, record):
        """
        Override method để check rollover
        
        Rollover khi:
        1. File size >= maxBytes
        2. Ngày thay đổi (tạo file mới cho ngày mới)
        """
        # Check ngày thay đổi
        current_date = datetime.now().strftime("%d-%m-%Y")
        if current_date != self.current_date:
            # Ngày mới → Rollover
            self.current_date = current_date
            return True
        
        # Check file size
        if self.stream is None:
            self.stream = self._open()
        
        # ========== FIX: DÙNG self._maxBytes THAY VÌ self.maxBytes ==========
        if self._maxBytes > 0:
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  # Seek to end
            if self.stream.tell() + len(msg.encode('utf-8')) >= self._maxBytes:
                return True
        # =====================================================================
        
        return False
    
    def doRollover(self):
        """Override method để rollover với custom naming"""
        if self.stream:
            self.stream.close()
            self.stream = None
        
        # Tìm file mới
        self.baseFilename = self._get_current_log_filename()
        
        # Open file mới
        self.stream = self._open()



def cleanup_old_logs(log_dir, retention_days):
    """
    Xóa logs cũ hơn retention_days
    
    Args:
        log_dir: Thư mục chứa logs
        retention_days: Số ngày giữ logs (từ config.LOG_RETENTION_DAYS)
    """
    if not os.path.exists(log_dir):
        return
    
    cutoff_time = time.time() - (retention_days * 86400)  # 86400s = 1 day
    
    # Tìm tất cả .log files
    pattern = os.path.join(log_dir, "tomsamautobot-log-*.log")
    log_files = glob.glob(pattern)
    
    deleted_count = 0
    for log_file in log_files:
        try:
            # Kiểm tra thời gian modify của file
            file_mtime = os.path.getmtime(log_file)
            if file_mtime < cutoff_time:
                os.remove(log_file)
                deleted_count += 1
        except Exception as e:
            print(f"[LOG CLEANUP] Warning: Cannot delete {log_file}: {e}")
    
    if deleted_count > 0:
        print(f"[LOG CLEANUP] Deleted {deleted_count} old log file(s)")


def setup_logger():
    """Setup logger - gọi 1 lần duy nhất khi app start"""
    logger = logging.getLogger('TomSamAutobot')
    
    # ========== FIX: REMOVE OLD HANDLERS TRƯỚC KHI SETUP (NEW) ==========
    # Xóa tất cả handlers cũ để tránh duplicate hoặc stale handlers
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    
    print("[LOGGER] Setting up logger...")
    # =====================================================================
    
    logger.setLevel(logging.DEBUG)
    
    # Lấy log directory
    log_dir = os.path.join(config.FILE_PATH, 'logs') if config.FILE_PATH else 'logs'
    
    # ========== FILE HANDLER (ROTATING) ==========
    file_handler = CustomRotatingFileHandler(
        base_dir=log_dir,
        maxBytes=10*1024*1024,
        backupCount=999,
        encoding='utf-8'
    )
    
    file_formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] [%(funcName)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    print(f"[LOGGER] ✓ File handler added: {file_handler.baseFilename}")
    # ============================================
    
    # ========== CONSOLE HANDLER (NEW) ==========
    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.DEBUG)
    
    # console_formatter = logging.Formatter(
    #     fmt='[%(levelname)s] [%(filename)s:%(lineno)d] %(message)s'
    # )
    # console_handler.setFormatter(console_formatter)
    # logger.addHandler(console_handler)
    
    # print(f"[LOGGER] ✓ Console handler added")
    # ===========================================
    
    # Cleanup old logs
    try:
        cleanup_old_logs(log_dir, config.LOG_RETENTION_DAYS)
    except Exception as e:
        print(f"[LOG CLEANUP] Error: {e}")    
   
    
    return logger


def reset_logger():
    """Reset logger khi FILE_PATH thay đổi"""
    logger = logging.getLogger('TomSamAutobot')
    
    # Remove all handlers
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    
    # Re-setup với config mới
    setup_logger()