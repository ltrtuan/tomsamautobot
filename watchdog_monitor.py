"""
watchdog_monitor.py - Auto-restart Watchdog Process (SIMPLIFIED)

Nhiệm vụ:
1. Đợi 60 giây (hardcode)
2. Restart app với --auto-start flag
3. Exit

Không cần countdown loop, không update env var
Countdown sẽ được xử lý trong app sau khi restart
"""
import os
import sys
import time
import subprocess

# ========== THÊM LOGGER (NEW) ==========
import logging
from helpers.logger import setup_logger

# Setup logger cho watchdog
logger = setup_logger()
logger = logging.getLogger("TomSamAutobot.Watchdog")  # Sub-logger
# ========================================

def restart_app():
    """
    Restart app với --auto-start flag
    
    Logic:
    1. Clear crash timestamp (không restart lặp lại)
    2. Detect môi trường: development (.py) hoặc production (.exe)
    3. Khởi động app với argument --auto-start
    """
    logger.info("=" * 60)
    logger.info("[WATCHDOG] RESTARTING APP...")
    logger.info("=" * 60)
    
    # Clear crash timestamp
    import config as cfg
    cfg.clear_crash_timestamp()
    logger.info("[WATCHDOG] Crash timestamp cleared")
    
    # Detect environment
    is_frozen = getattr(sys, 'frozen', False)
    
    if is_frozen:
        # Production mode (.exe)
        logger.info("[WATCHDOG] Mode: Production (.exe)")
        app_dir = os.path.dirname(sys.executable)
        app_exe_name = "TomSamAutobot.exe"
        app_exe_path = os.path.join(app_dir, app_exe_name)
        
        if not os.path.exists(app_exe_path):
            logger.error(f"[WATCHDOG] ERROR: App executable not found at {app_exe_path}")
            return
        
        logger.info(f"[WATCHDOG] App path: {app_exe_path}")
        subprocess.Popen(
            [app_exe_path, "--auto-start"],
            creationflags=0x08000000,  # CREATE_NO_WINDOW
            close_fds=True
        )
    else:
        # Development mode (.py)
        logger.info("[WATCHDOG] Mode: Development (.py)")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        main_script_path = os.path.join(script_dir, "main.py")
        
        if not os.path.exists(main_script_path):
            logger.error(f"[WATCHDOG] ERROR: main.py not found at {main_script_path}")
            return
        
        logger.info(f"[WATCHDOG] Script path: {main_script_path}")
        logger.info(f"[WATCHDOG] Python: {sys.executable}")
        subprocess.Popen(
            [sys.executable, main_script_path, "--auto-start"],
            creationflags=0x08000000,  # CREATE_NO_WINDOW
            close_fds=True
        )
    
    logger.info("[WATCHDOG] App restarted with --auto-start flag")


def main():
    """Main function - đợi 60 giây và restart app"""
    logger.info("=" * 60)
    logger.info("[WATCHDOG] WATCHDOG MONITOR STARTED")
    logger.info("=" * 60)
    
    is_frozen = getattr(sys, 'frozen', False)
    mode = "Production (.exe)" if is_frozen else "Development (.py)"
    logger.info(f"[WATCHDOG] Mode: {mode}")
    logger.info(f"[WATCHDOG] Process ID: {os.getpid()}")
    logger.info("=" * 60)
    
    # ========== WAIT 60 SECONDS (HARDCODE) ==========
    logger.info("[WATCHDOG] Waiting 60 seconds before restart...")
    logger.info("[WATCHDOG] User can close app during this time to cancel restart")
    
    try:
        time.sleep(60)  # Simple blocking sleep
        logger.info("[WATCHDOG] Wait completed!")
        
        # Restart app
        restart_app()
        
    except KeyboardInterrupt:
        logger.warning("[WATCHDOG] Interrupted by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"[WATCHDOG] ERROR: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    logger.info("=" * 60)
    logger.info("[WATCHDOG] WATCHDOG MONITOR EXITED")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
