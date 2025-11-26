"""
watchdog_monitor.py - Auto-restart Watchdog Process (SIMPLIFIED)

Nhiệm vụ:
    1. Đợi 60 giây (hardcode)
    2. Restart app với --auto-start flag
    3. Exit
    
Không còn countdown loop, không update env var
Countdown sẽ được xử lý trong app sau khi restart
"""

import os
import sys
import time
import subprocess


def restart_app():
    """
    Restart app với --auto-start flag
    
    Logic:
        1. Clear crash timestamp (để không restart lặp lại)
        2. Detect môi trường (development .py hoặc production .exe)
        3. Khởi động app với argument --auto-start
    """
    print("[WATCHDOG] ========================================")
    print("[WATCHDOG] 🔄 RESTARTING APP...")
    print("[WATCHDOG] ========================================")
    
    # Clear crash timestamp
    import config as cfg
    cfg.clear_crash_timestamp()
    print("[WATCHDOG] ✓ Crash timestamp cleared")
    
    # Detect environment
    is_frozen = getattr(sys, 'frozen', False)
    
    if is_frozen:
        # Production mode: .exe
        print("[WATCHDOG] Mode: Production (.exe)")
        
        app_dir = os.path.dirname(sys.executable)
        app_exe_name = "TomSamAutobot.exe"
        app_exe_path = os.path.join(app_dir, app_exe_name)
        
        if not os.path.exists(app_exe_path):
            print(f"[WATCHDOG] ⚠ ERROR: App executable not found at {app_exe_path}")
            return
        
        print(f"[WATCHDOG] App path: {app_exe_path}")
        
        subprocess.Popen(
            [app_exe_path, '--auto-start'],
            creationflags=0x08000000,  # CREATE_NO_WINDOW
            close_fds=True
        )
        
    else:
        # Development mode: .py
        print("[WATCHDOG] Mode: Development (.py)")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        main_script_path = os.path.join(script_dir, 'main.py')
        
        if not os.path.exists(main_script_path):
            print(f"[WATCHDOG] ⚠ ERROR: main.py not found at {main_script_path}")
            return
        
        print(f"[WATCHDOG] Script path: {main_script_path}")
        print(f"[WATCHDOG] Python: {sys.executable}")
        
        subprocess.Popen(
            [sys.executable, main_script_path, '--auto-start'],
            creationflags=0x08000000,  # CREATE_NO_WINDOW
            close_fds=True
        )
    
    print("[WATCHDOG] ✓ App restarted with --auto-start flag")


def main():
    """
    Main function - Đợi 60 giây và restart app
    """
    print("=" * 60)
    print("[WATCHDOG] 👁 WATCHDOG MONITOR STARTED")
    print("=" * 60)
    
    is_frozen = getattr(sys, 'frozen', False)
    mode = "Production (.exe)" if is_frozen else "Development (.py)"
    print(f"[WATCHDOG] Mode: {mode}")
    print(f"[WATCHDOG] Process ID: {os.getpid()}")
    print("=" * 60)
    
    # ========== WAIT 60 SECONDS (HARDCODE) ==========
    print("[WATCHDOG] Waiting 60 seconds before restart...")
    print("[WATCHDOG] User can close app during this time to cancel restart")
    
    try:
        time.sleep(60)  # Simple blocking sleep
        print("[WATCHDOG] Wait completed!")
        
        # Restart app
        restart_app()
        
    except KeyboardInterrupt:
        print("\n[WATCHDOG] ⚠ Interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"[WATCHDOG] ⚠ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # ================================================
    
    print("=" * 60)
    print("[WATCHDOG] 👁 WATCHDOG MONITOR EXITED")
    print("=" * 60)


if __name__ == "__main__":
    main()
