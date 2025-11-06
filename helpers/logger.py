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
        
        # Tạo thư mục logs nếu chưa có
        os.makedirs(base_dir, exist_ok=True)
        
        # Tìm file log hiện tại hoặc tạo mới
        filename = self._get_current_log_filename()
        
        super().__init__(
            filename=filename,
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding=encoding
        )
    
    def _get_current_log_filename(self):
        """Lấy tên file log hiện tại hoặc tạo tên mới"""
        date_str = self.current_date
        base_name = f"tomsamautobot-log-{date_str}"
        
        # Tìm tất cả log files của ngày hôm nay
        pattern = os.path.join(self.base_dir, f"{base_name}*.log")
        existing_files = glob.glob(pattern)
        
        if not existing_files:
            # Chưa có log file cho ngày hôm nay
            return os.path.join(self.base_dir, f"{base_name}.log")
        
        # Tìm index cao nhất
        max_index = 0
        for filepath in existing_files:
            basename = os.path.basename(filepath)
            # Check format: tomsamautobot-log-{date}-{index}.log
            if basename == f"{base_name}.log":
                max_index = max(max_index, 0)
            else:
                try:
                    # Extract index từ filename
                    index_part = basename.replace(f"{base_name}-", "").replace(".log", "")
                    index = int(index_part)
                    max_index = max(max_index, index)
                except ValueError:
                    pass
        
        # Kiểm tra file hiện tại có còn chỗ không
        if max_index == 0:
            current_file = os.path.join(self.base_dir, f"{base_name}.log")
        else:
            current_file = os.path.join(self.base_dir, f"{base_name}-{max_index}.log")
        
        # Nếu file đã đạt maxBytes, tạo file mới với index tăng
        if os.path.exists(current_file) and os.path.getsize(current_file) >= self.maxBytes:
            max_index += 1
            return os.path.join(self.base_dir, f"{base_name}-{max_index}.log")
        
        return current_file
    
    def shouldRollover(self, record):
        """Override: Kiểm tra xem cần rotate không"""
        # Check nếu đổi ngày mới
        current_date = datetime.now().strftime("%d-%m-%Y")
        if current_date != self.current_date:
            self.current_date = current_date
            # Đổi sang file log ngày mới
            new_filename = self._get_current_log_filename()
            if new_filename != self.baseFilename:
                self.baseFilename = new_filename
                return False  # Không rollover, chỉ switch file
        
        # Check size-based rotation
        if self.maxBytes > 0:
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  # Seek to end
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return True
        return False
    
    def doRollover(self):
        """Override: Tạo file mới khi rotate"""
        if self.stream:
            self.stream.close()
            self.stream = None
        
        # Tạo file log mới với index tăng
        self.baseFilename = self._get_current_log_filename()
        self.mode = 'a'
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
    """
        logger.debug("This is a DEBUG message")
        logger.info("This is an INFO message")
        logger.warning("This is a WARNING message")
        logger.error("This is an ERROR message")
        logger.critical("This is a CRITICAL message")
    """
    logger = logging.getLogger('TomSamAutobot')  # ← Singleton name
    
    # Nếu đã setup rồi, return luôn
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # Lấy log directory
    log_dir = os.path.join(config.FILE_PATH, 'logs') if config.FILE_PATH else 'logs'
    
    # Custom handler
    handler = CustomRotatingFileHandler(
        base_dir=log_dir,
        maxBytes=10*1024*1024,
        backupCount=999,
        encoding='utf-8'
    )
    
    # Formatter
    formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(levelname)s] [%(filename)s] [%(funcName)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
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