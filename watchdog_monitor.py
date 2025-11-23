"""
watchdog_monitor.py - Auto-restart Watchdog Process

Process giám sát độc lập, detached từ main app
Nhiệm vụ:
    1. Check biến môi trường mỗi 5 giây
    2. Countdown và restart app khi cần
    3. Tự động exit khi:
       - User set auto_restart_minutes = 0 (cancel)
       - User bấm Start thủ công
       - Đã restart app thành công
       
Hoạt động trong cả Development (.py) và Production (.exe) mode
"""

import os
import sys
import time
import subprocess
from datetime import datetime, timedelta

# Import config để đọc biến môi trường
import config as cfg


def should_restart():
    """
    Kiểm tra xem có nên restart app không
    
    Returns:
        tuple: (should_restart: bool, minutes_remaining: int)
        
    Logic:
        1. Đọc TOMSAM_AUTO_RESTART_MINUTES (số phút setting)
        2. Nếu = 0 → user đã cancel → return (False, 0)
        3. Đọc TOMSAM_CRASH_TIMESTAMP (thời điểm crash)
        4. Nếu không có crash timestamp → return (False, 0)
        5. Tính thời gian đã trôi qua từ lúc crash
        6. Nếu đã đủ thời gian → return (True, 0)
        7. Nếu chưa đủ → return (False, số phút còn lại)
    """
    # ===== BƯỚC 1: Đọc setting số phút restart =====
    restart_minutes = cfg.get_auto_restart_minutes()
    
    # Nếu user đã set = 0 → cancel auto-restart
    if restart_minutes == 0:
        print("[WATCHDOG] Auto-restart disabled (setting = 0)")
        return False, 0
    
    # ===== BƯỚC 2: Check xem có crash timestamp không =====
    crash_timestamp_str = cfg.get_crash_timestamp()
    
    # Nếu không có crash timestamp → không cần restart
    if not crash_timestamp_str or crash_timestamp_str == "":
        return False, 0
    
    # ===== BƯỚC 3: Parse crash timestamp =====
    try:
        crash_time = datetime.strptime(crash_timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        print(f"[WATCHDOG] ⚠ Invalid crash timestamp format: {crash_timestamp_str}")
        print(f"[WATCHDOG] Error: {e}")
        return False, 0
    
    # ===== BƯỚC 4: Tính thời gian đã trôi qua (phút) =====
    elapsed_seconds = (datetime.now() - crash_time).total_seconds()
    elapsed_minutes = elapsed_seconds / 60.0
    
    # ===== BƯỚC 5: Tính số phút còn lại =====
    remaining_minutes = restart_minutes - elapsed_minutes
    
    # ===== BƯỚC 6: Quyết định có restart không =====
    if remaining_minutes <= 0:
        # Đã đủ thời gian → nên restart
        print(f"[WATCHDOG] ✓ Countdown finished! ({restart_minutes} minutes elapsed)")
        return True, 0
    else:
        # Chưa đủ thời gian → chờ tiếp
        remaining_int = int(remaining_minutes) + 1  # Làm tròn lên
        return False, remaining_int


def restart_app():
    """
    Restart app và trigger Start button tự động
    
    Logic:
        1. Clear crash timestamp (để không restart lặp lại)
        2. Detect môi trường (development .py hoặc production .exe)
        3. Khởi động app với argument --auto-start
        4. App sẽ tự động gọi controller.runsequence() khi load xong
    """
    print("[WATCHDOG] ========================================")
    print("[WATCHDOG] 🔄 RESTARTING APP...")
    print("[WATCHDOG] ========================================")
    
    # ===== BƯỚC 1: Clear crash timestamp =====
    cfg.clear_crash_timestamp()
    print("[WATCHDOG] ✓ Crash timestamp cleared")
    
    # ===== BƯỚC 2: Detect môi trường =====
    is_frozen = getattr(sys, 'frozen', False)
    
    if is_frozen:
        # ===== PRODUCTION MODE: App chạy từ .exe =====
        print("[WATCHDOG] Mode: Production (.exe)")
        
        # Tìm file .exe chính (TomSamAutobot.exe)
        app_dir = os.path.dirname(sys.executable)
        
        # Giả sử file exe có tên TomSamAutobot.exe
        # Nếu khác, cần điều chỉnh tên
        app_exe_name = "TomSamAutobot.exe"
        app_exe_path = os.path.join(app_dir, app_exe_name)
        
        if not os.path.exists(app_exe_path):
            print(f"[WATCHDOG] ⚠ ERROR: App executable not found at {app_exe_path}")
            print("[WATCHDOG] Please check the .exe filename")
            return
        
        print(f"[WATCHDOG] App path: {app_exe_path}")
        
        # Start app với --auto-start flag
        subprocess.Popen(
            [app_exe_path, '--auto-start'],
            creationflags=0x08000000,  # CREATE_NO_WINDOW
            close_fds=True
        )
        
    else:
        # ===== DEVELOPMENT MODE: App chạy từ Python script =====
        print("[WATCHDOG] Mode: Development (.py)")
        
        # Tìm main.py trong thư mục hiện tại
        script_dir = os.path.dirname(os.path.abspath(__file__))
        main_script_path = os.path.join(script_dir, 'main.py')
        
        if not os.path.exists(main_script_path):
            print(f"[WATCHDOG] ⚠ ERROR: main.py not found at {main_script_path}")
            return
        
        print(f"[WATCHDOG] Script path: {main_script_path}")
        print(f"[WATCHDOG] Python: {sys.executable}")
        
        # Start app với Python và --auto-start flag
        subprocess.Popen(
            [sys.executable, main_script_path, '--auto-start'],
            creationflags=0x08000000,  # CREATE_NO_WINDOW
            close_fds=True
        )
    
    print("[WATCHDOG] ✓ App restarted with --auto-start flag")
    print("[WATCHDOG] App will trigger Start button automatically after 2 seconds")


def main():
    """
    Main loop của watchdog - chạy vô hạn đến khi thỏa exit condition
    
    Exit conditions:
        1. User set auto_restart_minutes = 0 (cancel)
        2. User bấm Start thủ công (app_is_running = True)
        3. Đã restart app thành công
        4. KeyboardInterrupt (Ctrl+C)
    
    Loop logic (mỗi 5 giây):
        1. Check auto_restart_minutes
        2. Check crash_timestamp
        3. Tính countdown
        4. Ghi countdown vào biến môi trường (để UI hiển thị)
        5. Check app_is_running
        6. Nếu đến lúc restart → restart và exit
    """
    print("=" * 60)
    print("[WATCHDOG] 👁 WATCHDOG MONITOR STARTED")
    print("=" * 60)
    
    # Hiển thị thông tin môi trường
    is_frozen = getattr(sys, 'frozen', False)
    mode = "Production (.exe)" if is_frozen else "Development (.py)"
    print(f"[WATCHDOG] Mode: {mode}")
    print(f"[WATCHDOG] Process ID: {os.getpid()}")
    print(f"[WATCHDOG] Checking interval: 5 seconds")
    print("=" * 60)
    
    # ===== MAIN LOOP - Check mỗi 5 giây =====
    while True:
        try:
            # ===== CHECK 1: Auto-restart có bị disable không? =====
            restart_minutes = cfg.get_auto_restart_minutes()
            
            if restart_minutes == 0:
                print("[WATCHDOG] ⚠ Auto-restart disabled (setting = 0)")
                print("[WATCHDOG] Clearing countdown and exiting...")
                cfg.set_restart_countdown(0)
                break  # Exit watchdog
            
            # ===== CHECK 2: Có cần restart không? =====
            should_restart_flag, remaining = should_restart()
            
            # ===== GÀNH COUNTDOWN VÀO BIẾN MÔI TRƯỜNG =====
            # (để ActionListView đọc và hiển thị realtime)
            cfg.set_restart_countdown(remaining)
            
            if remaining > 0:
                print(f"[WATCHDOG] ⏳ Countdown: {remaining} phút còn lại...")
            
            # ===== CHECK 3: Đã đến lúc restart? =====
            if should_restart_flag:
                print("[WATCHDOG] ✓ It's time to restart!")
                restart_app()
                print("[WATCHDOG] Watchdog exiting after restart...")
                break  # Exit watchdog sau khi restart
            
            # ===== CHECK 4: User đã Start thủ công? =====
            if cfg.is_app_running():
                print("[WATCHDOG] ✓ App is running (user pressed Start)")
                print("[WATCHDOG] Clearing countdown and exiting...")
                cfg.set_restart_countdown(0)
                break  # Exit watchdog
            
            # ===== ĐỢI 5 GIÂY TRƯỚC KHI CHECK LẠI =====
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n[WATCHDOG] ⚠ Interrupted by user (Ctrl+C)")
            cfg.set_restart_countdown(0)
            break
            
        except Exception as e:
            print(f"[WATCHDOG] ⚠ ERROR: {e}")
            import traceback
            traceback.print_exc()
            # Không exit, tiếp tục loop
            time.sleep(5)
    
    # ===== WATCHDOG EXITED =====
    print("=" * 60)
    print("[WATCHDOG] 👁 WATCHDOG MONITOR EXITED")
    print("=" * 60)


if __name__ == "__main__":
    """
    Entry point của watchdog
    
    Usage:
        Development: python watchdog_monitor.py
        Production: watchdog_monitor.exe (tự động start bởi main app khi crash)
    """
    main()
