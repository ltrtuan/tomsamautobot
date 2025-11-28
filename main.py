import os
import sys
import tkinter as tk
from tkinter import messagebox  # Thêm dòng này
from models.action_model import ActionModel
from views.action_list_view import ActionListView
from controllers.action_controller import ActionController
import config as cfg
from login_window import LoginWindow
import atexit

import sys
import traceback
from helpers.email_notifier import send_email, format_crash_email

import logging
from helpers.logger import setup_logger
logger = logging.getLogger('TomSamAutobot')


from datetime import datetime  # THÊM MỚI - để ghi timestamp crash
import subprocess  # THÊM MỚI - để start watchdog process

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    Catch all uncaught exceptions and send email alert
    This is the LAST line of defense before app crash
    
    NEW: Ghi crash info vào biến môi trường và start watchdog để auto-restart
    """
    # Skip keyboard interrupt (Ctrl+C)
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Log error
    logger.critical("UNCAUGHT EXCEPTION - APP CRASH", exc_info=(exc_type, exc_value, exc_traceback))
    
    # Format crash email
    title, content = format_crash_email(
        exception_type=exc_type.__name__,
        exception_message=str(exc_value),
        traceback_str=traceback.format_exc(),
        context={
            'App': 'TomSamAutobot',
            'Version': cfg.APP_VERSION,
        }
    )
    
    # Send email (non-blocking)
    send_email(
        title=title,
        content=content,
        throttle_seconds=0  # No throttle for crashes (always send)
    )
    
    # ========== AUTO RESTART LOGIC (NEW) ==========
    try:
        # Lấy timestamp hiện tại
        crash_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Ghi crash timestamp vào biến môi trường
        cfg.set_crash_timestamp(crash_time)
        print(f"[CRASH] Crash timestamp recorded: {crash_time}")
        
        # Kiểm tra crash counter để limit max 3 lần/10 phút
        last_reset = cfg.get_last_crash_reset()
        
        if last_reset:
            try:
                last_reset_dt = datetime.strptime(last_reset, "%Y-%m-%d %H:%M:%S")
                elapsed_seconds = (datetime.now() - last_reset_dt).total_seconds()
                
                # Nếu đã quá 20 phút (1200 giây) từ lần reset trước → reset counter
                if elapsed_seconds > 1200:
                    cfg.reset_crash_count()
                    cfg.set_last_crash_reset(crash_time)
                    print("[CRASH] Crash counter reset (10 minutes elapsed)")
            except ValueError:
                # Lỗi parse datetime → reset counter
                cfg.reset_crash_count()
                cfg.set_last_crash_reset(crash_time)
        else:
            # Chưa có last_reset → set lần đầu
            cfg.set_last_crash_reset(crash_time)
        
        # Tăng crash counter
        cfg.increment_crash_count()
        current_crash_count = cfg.get_crash_count()
        print(f"[CRASH] Crash count: {current_crash_count}/3")
        
        # Chỉ start watchdog nếu chưa quá 3 lần crash
        if current_crash_count < 3:
            print("[CRASH] Starting watchdog for auto-restart...")
            start_watchdog_process()
        else:
            print("[CRASH] ⚠ WARNING: Crash limit exceeded (3 times in 10 minutes)")
            print("[CRASH] Auto-restart disabled to prevent crash loop")
            # Clear crash timestamp để không auto-restart
            cfg.clear_crash_timestamp()
            
    except Exception as e:
        print(f"[CRASH] ⚠ Error in auto-restart logic: {e}")
    
    # ========== END AUTO RESTART LOGIC ==========
    
    # Call default exception handler (print to console)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    # ========== FORCE EXIT APP (NEW) ==========
    print("=" * 80)
    print("[CRASH] ⚠ TERMINATING APP PROCESS...")
    print("=" * 80)
    
    # Force exit với exit code = 1 (error)
    # Đảm bảo process bị terminate hoàn toàn
    sys.exit(1)


# ========== INSTALL EXCEPTION HANDLER ==========
sys.excepthook = global_exception_handler


# ========== GLOBAL SELENIUM DRIVER REGISTRY ==========
_active_selenium_drivers = []  # Global list to track all Selenium drivers

def cleanup_all_selenium_drivers():
    """
    Cleanup all active Selenium drivers
    This function is automatically called when Python exits (even if app crashes)
    """
    if not _active_selenium_drivers:
        return
    
    print("[CLEANUP] ========== Cleaning up Selenium drivers ==========")
    cleaned_count = 0
    
    for driver in _active_selenium_drivers:
        try:
            driver.quit()
            cleaned_count += 1
            print(f"[CLEANUP] ✓ ChromeDriver cleaned up")
        except Exception as e:
            print(f"[CLEANUP] ⚠ Cleanup warning: {e}")
    
    _active_selenium_drivers.clear()
    print(f"[CLEANUP] ✓ Total cleaned: {cleaned_count} ChromeDriver process(es)")
    print("[CLEANUP] ========================================")

# Register cleanup function - will run when Python exits
atexit.register(cleanup_all_selenium_drivers)
print("[INIT] ✓ Selenium cleanup handler registered")
# ========== END SELENIUM CLEANUP REGISTRY ==========


# ========== WATCHDOG PROCESS STARTER ========== (THÊM MỚI)
def start_watchdog_process():
    """
    Khởi động watchdog process (detached) để monitor và auto-restart app
    
    Logic:
        - Detect môi trường (development .py hoặc production .exe)
        - Start watchdog_monitor.py/.exe dưới dạng detached process
        - Watchdog sẽ tự động check biến môi trường và restart app khi cần
    """
    try:
        # Flags để tạo detached process trên Windows
        CREATE_NO_WINDOW = 0x08000000
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        
        flags = CREATE_NO_WINDOW | DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        
        # Detect môi trường: frozen (.exe) hay script (.py)
        if getattr(sys, 'frozen', False):
            # === PRODUCTION MODE: App chạy từ .exe ===
            # Tìm watchdog_monitor.exe trong cùng thư mục với app.exe
            app_dir = os.path.dirname(sys.executable)
            watchdog_path = os.path.join(app_dir, 'watchdog_monitor.exe')
            
            if os.path.exists(watchdog_path):
                print(f"[WATCHDOG] Starting watchdog process (production): {watchdog_path}")               
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

                subprocess.Popen(
                    [watchdog_path],
                    startupinfo=startupinfo,
                    creationflags=flags,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    close_fds=True
                )
                print("[WATCHDOG] ✓ Watchdog process started")
            else:
                print(f"[WATCHDOG] ⚠ Warning: watchdog_monitor.exe not found at {watchdog_path}")
        else:
            # === DEVELOPMENT MODE: App chạy từ Python script ===
            script_dir = os.path.dirname(os.path.abspath(__file__))
            watchdog_path = os.path.join(script_dir, 'watchdog_monitor.py')
            
            if os.path.exists(watchdog_path):
                print(f"[WATCHDOG] Starting watchdog process (development): python {watchdog_path}")
                subprocess.Popen(
                    [sys.executable, watchdog_path],
                    creationflags=flags,
                    close_fds=True
                )
                print("[WATCHDOG] ✓ Watchdog process started")
            else:
                print(f"[WATCHDOG] ⚠ Warning: watchdog_monitor.py not found at {watchdog_path}")
                
    except Exception as e:
        print(f"[WATCHDOG] ⚠ Failed to start watchdog: {e}")

# ========== END WATCHDOG PROCESS STARTER ==========


class TomSamAutobot:
    def __init__(self):
        """Khởi tạo ứng dụng TomSamAutobot"""
        # Kiểm tra xác thực trước khi khởi tạo
        if cfg.check_auth_from_env():
            # Đã xác thực, khởi tạo ứng dụng chính
            self.init_main_app()
        else:
            # Chưa xác thực, hiển thị màn hình đăng nhập
            self.login_window = LoginWindow(self.init_main_app)
            self.login_window.show()
            
    def init_main_app(self):
        """Khởi tạo giao diện chính của ứng dụng"""
    
        # Tạo cửa sổ chính nếu chưa tồn tại
        if not hasattr(self, 'root'):
            self.root = tk.Tk()
        else:
            # Nếu đã tồn tại (từ login), sử dụng Toplevel
            self.root = tk.Toplevel()
    
        self.root.title(f"TomSamAutobot {cfg.APP_VERSION}")
        # ===== FIX: Icon path for both .py and .exe (UPDATED) =====
        try:
            # Detect if running as .exe (frozen) or .py (development)
            if getattr(sys, 'frozen', False):
                # Running as .exe - use sys._MEIPASS
                base_path = sys._MEIPASS
            else:
                # Running as .py - use script directory
                base_path = os.path.dirname(os.path.abspath(__file__))
    
            icon_path = os.path.join(base_path, "resources", "tomsamautobot.ico")
    
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
                logger.info(f"[INIT] Icon loaded: {icon_path}")
            else:
                logger.warning(f"[INIT] Icon not found: {icon_path}")
        except Exception as e:
            logger.warning(f"[INIT] Failed to load icon: {e}")
        # ==========================================================


        # ========== WINDOW CLOSE HANDLER (NEW) ==========
        def on_closing():
            """Handle window close event"""
            logger.info("[APP] Window close requested")
            
            # Cancel auto-trigger if active
            if hasattr(self, 'controller') and self.controller:
                if self.controller.auto_trigger_active:
                    logger.info("[APP] Cancelling auto-trigger (user closing app)")
                    self.controller.cancel_auto_trigger()
                    
                    # ===== STOP TRAY ICON (NEW) =====
                    try:
                        self.controller.stop_tray_icon()
                    except:
                        pass
                    # ================================
            
            # Close window
            logger.info("[APP] Closing application")
            self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        logger.info("[INIT] ✓ Window close handler registered")
        # ================================================
    
        # ========== INSTALL TKINTER EXCEPTION HANDLER ==========
        def handle_tkinter_exception(exc, val, tb):
            """
            Handle exceptions in Tkinter callbacks
            Tkinter has its own exception handler that DOES NOT trigger sys.excepthook.
            We need to manually catch and send email for Tkinter exceptions.
            
            NEW: Ghi crash info và start watchdog để auto-restart
            """
            print("=" * 80)
            print("[TKINTER ERROR] Exception in Tkinter event loop:")
            print("=" * 80)
            
            # Format traceback
            tb_str = ''.join(traceback.format_exception(exc, val, tb))
            print(tb_str)
            
            # Log to logger
            logger.critical("TKINTER EXCEPTION - APP CRASH", exc_info=(exc, val, tb))
            
            # Format and send crash email
            title, content = format_crash_email(
                exception_type=exc.__name__,
                exception_message=str(val),
                traceback_str=tb_str,
                context={
                    'App': 'TomSamAutobot',
                    'Source': 'Tkinter Event Loop',
                    'Version': '1.0.0'
                }
            )
            
            print("[EMAIL] Sending crash report...")
            send_email(
                title=title,
                content=content,
                throttle_seconds=0  # No throttle for crashes
            )
            print("[EMAIL] ✓ Crash email sent")
            
            # ========== AUTO RESTART LOGIC (NEW) ==========
            try:
                crash_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cfg.set_crash_timestamp(crash_time)
                print(f"[CRASH] Tkinter crash timestamp recorded: {crash_time}")
                
                # Check và reset crash counter nếu cần
                last_reset = cfg.get_last_crash_reset()
                if last_reset:
                    try:
                        last_reset_dt = datetime.strptime(last_reset, "%Y-%m-%d %H:%M:%S")
                        elapsed_seconds = (datetime.now() - last_reset_dt).total_seconds()
                        if elapsed_seconds > 1200:  # 20 phút
                            cfg.reset_crash_count()
                            cfg.set_last_crash_reset(crash_time)
                    except ValueError:
                        cfg.reset_crash_count()
                        cfg.set_last_crash_reset(crash_time)
                else:
                    cfg.set_last_crash_reset(crash_time)
                
                # Tăng crash counter
                cfg.increment_crash_count()
                current_crash_count = cfg.get_crash_count()
                # ===== THÊM LOG DEBUG (NEW) =====
                logger.critical("=" * 80)
                logger.critical(f"[CRASH DEBUG] Crash count: {current_crash_count}/3")
                logger.critical(f"[CRASH DEBUG] Timestamp: {cfg.get_crash_timestamp()}")
                logger.critical(f"[CRASH DEBUG] Last reset: {cfg.get_last_crash_reset()}")
                logger.critical(f"[CRASH DEBUG] Check: {current_crash_count} <= 3? {current_crash_count <= 3}")
                logger.critical("=" * 80)
                # ================================
                
                if current_crash_count < 3:
                    logger.info("[CRASH] Starting watchdog for auto-restart...")
                    start_watchdog_process()
                    logger.info("[CRASH] ✓ Watchdog started")
                else:
                    logger.warning("[CRASH] ⚠ Crash limit exceeded (3 times in 10 minutes)")
                    logger.warning("[CRASH] Auto-restart disabled to prevent crash loop")
                    cfg.clear_crash_timestamp()
                    logger.info("[CRASH] ✓ Crash timestamp cleared")
                    
            except Exception as e:
                print(f"[CRASH] ⚠ Error in Tkinter auto-restart logic: {e}")
            # ========== END AUTO RESTART LOGIC ==========           
           

            # ========== FORCE EXIT APP (NEW) ==========
            print("=" * 80)
            print("[TKINTER CRASH] ⚠ TERMINATING APP PROCESS...")
            print("=" * 80)
            
            # Cleanup Tkinter
            try:
                if hasattr(self, 'root') and self.root:
                    self.root.quit()  # Stop mainloop
                    self.root.destroy()  # Destroy window
            except:
                pass
            
            # Force exit với exit code = 1 (error)
            sys.exit(1)
            # ==========================================

        # Install Tkinter exception handler
        self.root.report_callback_exception = handle_tkinter_exception
        print("[INIT] ✓ Tkinter exception handler installed")
        # ========================================================
    
        self.root.configure(bg=cfg.LIGHT_BG_COLOR)
    
        # Thiết lập kích thước cửa sổ
        window_width = 800
        window_height = 600
    
        # Tính toán vị trí ở giữa màn hình
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))
    
        # Đặt kích thước và vị trí cửa sổ
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
    
        # Create model
        model = ActionModel()
    
        # Create view
        view = ActionListView(self.root)
        view.pack(fill=tk.BOTH, expand=True)
        
        #Create controller and set up
        self.controller = ActionController(self.root)  # THAY ĐỔI: Lưu vào self.controller
        self.controller.setup(model, view)
        
        # ========== AUTO-START LOGIC (NEW - UPDATED) ==========
        if '--auto-start' in sys.argv:
            logger.info("[AUTO-START] App restarted by watchdog")
            logger.info("[AUTO-START] Starting countdown for auto-trigger...")
            
            # Start countdown (reactive to settings)
            self.controller.start_auto_trigger_countdown()
        # ======================================================
    
        # Start application (blocking)
        self.root.mainloop()


    
    def exit_app(self):
        """Thoát ứng dụng"""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.destroy()
            sys.exit()
            
if __name__ == "__main__":
    # Tải cấu hình
    cfg.load_config()
    # ========== SETUP LOGGER (CHỈ GỌI 1 LẦN) ==========
    logger = setup_logger()
    logger.info("=" * 80)
    logger.info("TomSamAutobot Starting...")
    logger.info(f"Process PID: {os.getpid()}")
    logger.info(f"Arguments: {sys.argv}")
    logger.info("=" * 80)
    # ===================================================
    # Khởi tạo app
    app = TomSamAutobot()
    
   
