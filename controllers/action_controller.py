from models.action_model import ActionItem
import os
import time
import pyautogui
import pystray
from PIL import Image
from constants import ActionType
from views.move_index_dialog import MoveIndexDialog
import json
from tkinter import filedialog, messagebox
import config as cfg  # THÊM MỚI - để quản lý biến môi trường auto-restart
import logging
logger = logging.getLogger('TomSamAutobot')

class ActionController:
    def __init__(self, root):
        self.root = root
        self.model = None
        self.view = None
        self._is_in_nested_execution = False
        self.is_execution_stopped = False
        self._keyboard_listener = None
        self.is_actions_running = False
        
        # ========== AUTO-TRIGGER STATE (NEW) ==========
        self.auto_trigger_remaining = 0
        self.auto_trigger_cancelled = False
        self.auto_trigger_active = False
        

    def create_tray_icon(self):
        """
        Create system tray icon with menu
    
        Features:
        - Double-click: Show window
        - Right-click menu: Show/Stop/Exit
        """
     
        controller_ref = self
        # ===== LOAD ICON FROM RESOURCES FOLDER (NEW) =====
        def load_icon_image():
            """Load app icon from resources folder"""
            import sys
            try:
                # Thử các đường dẫn có thể (runtime và dev mode)
                icon_paths = [
                    os.path.join('resources', 'tomsamautobot.ico'),  # ← Dev mode
                    'resources/tomsamautobot.ico',
                    'tomsamautobot.ico',  # ← Runtime (PyInstaller extracted)
                    os.path.join(sys._MEIPASS, 'resources', 'tomsamautobot.ico') if hasattr(sys, '_MEIPASS') else None,  # ← PyInstaller temp folder
                ]
        
                # Filter out None
                icon_paths = [p for p in icon_paths if p]
        
                for icon_path in icon_paths:
                    if os.path.exists(icon_path):
                        logger.info(f"[TRAY] Loading icon from: {icon_path}")
                        return Image.open(icon_path)
        
                # Nếu không tìm thấy, tạo icon đơn giản
                logger.warning("[TRAY] Icon file not found, creating simple icon")
                return create_simple_icon()

            
            except Exception as e:
                logger.error(f"[TRAY] Error loading icon: {e}")
                return create_simple_icon()
    
        def create_simple_icon():
            """Fallback: Create simple icon if file not found"""
            from PIL import ImageDraw
        
            width = 64
            height = 64
            color_bg = (0, 120, 212)  # Blue
            color_fg = (255, 255, 255)  # White
        
            image = Image.new('RGB', (width, height), color_bg)
            dc = ImageDraw.Draw(image)
            dc.ellipse((8, 8, 56, 56), fill=color_fg)
            dc.ellipse((16, 16, 48, 48), fill=color_bg)
        
            return image
        # =================================================
    
        # Action handlers (giữ nguyên như cũ)
        def show_window_action():
            """Show main window - THREAD SAFE"""
            try:
                self.root.after(0, lambda: self.root.deiconify())
                self.root.after(0, lambda: self.root.lift())
                self.root.after(0, lambda: self.root.focus_force())
                logger.info("[TRAY] Window shown")
            except Exception as e:
                logger.error(f"[TRAY] Show window error: {e}")
    
        def stop_execution_action():
            """Stop execution - THREAD SAFE"""
            try:
                if self.is_actions_running:
                    self.root.after(0, self.stop_execution)
                    logger.info("[TRAY] Stop execution requested")
                else:
                    logger.info("[TRAY] No execution running")
            except Exception as e:
                logger.error(f"[TRAY] Stop error: {e}")
    
        def exit_app_action():
            """Exit application - THREAD SAFE"""
            try:
                logger.info("[TRAY] Exit requested from tray - Force stopping all threads")
        
                # ===== STEP 1: SET STOP FLAG (NEW) =====
                controller_ref.is_execution_stopped = True
                controller_ref.is_actions_running = False
                logger.info("[TRAY] Set execution stop flags")
                # ========================================

                # ===== STEP 1.5: SHUTDOWN THREADPOOLEXECUTOR (NEW) =====
                # Force kill any running executors in background
                import concurrent.futures
        
                # Get all ThreadPoolExecutor instances (hacky but works)
                import gc
                for obj in gc.get_objects():
                    if isinstance(obj, concurrent.futures.ThreadPoolExecutor):
                        try:
                            logger.info(f"[TRAY] Found ThreadPoolExecutor, shutting down...")
                            obj.shutdown(wait=False, cancel_futures=True)  # Cancel all pending futures
                        except Exception as e:
                            logger.error(f"[TRAY] Error shutting executor: {e}")
                # =======================================================
        
                # ===== STEP 2: CANCEL AUTO-TRIGGER (NEW) =====
                if hasattr(controller_ref, 'auto_trigger_active') and controller_ref.auto_trigger_active:
                    try:
                        controller_ref.cancel_auto_trigger()
                        logger.info("[TRAY] Cancelled auto-trigger")
                    except:
                        pass
                # ==============================================
        
                # ===== STEP 3: STOP KEYBOARD LISTENER (NEW) =====
                try:
                    controller_ref.stop_conditional_keyboard_listener()
                    logger.info("[TRAY] Stopped keyboard listener")
                except:
                    pass
                # ================================================
        
                # ===== STEP 4: STOP TRAY ICON =====
                if hasattr(controller_ref, 'tray_icon') and controller_ref.tray_icon:
                    try:
                        controller_ref.tray_icon.stop()
                        logger.info("[TRAY] Tray icon stopped")
                    except Exception as stop_err:
                        logger.error(f"[TRAY] Error stopping tray: {stop_err}")
                # ===================================
        
                # ===== STEP 5: WAIT FOR THREADS CLEANUP (NEW) =====
                logger.info("[TRAY] Waiting 2s for threads to cleanup...")
                time.sleep(2)  # Give threads time to see stop flags and exit
                # ==================================================
                
                # ===== DEBUG: LIST ACTIVE THREADS (NEW) =====
                import threading
                active_threads = threading.enumerate()
                logger.info(f"[TRAY] Active threads before exit: {len(active_threads)}")
                for thread in active_threads:
                    logger.info(f"[TRAY]   - Thread: {thread.name}, daemon={thread.daemon}, alive={thread.is_alive()}")
                # ============================================

        
                # ===== STEP 6: FORCE DESTROY WINDOW =====
                logger.info("[TRAY] Destroying Tkinter window...")
                controller_ref.root.after(0, controller_ref.root.destroy)
                # ========================================
        
                # ===== STEP 7: FORCE EXIT PROCESS (NEW) =====
                # Fallback: If destroy doesn't work, force exit after 3s
                def force_exit():
                    logger.info("[TRAY] Waiting 5s before force exit...")
                    time.sleep(5)
    
                    # Check if still alive
                    import threading
                    active = threading.enumerate()
                    logger.warning(f"[TRAY] FORCE EXIT: Still {len(active)} threads alive")
                    for t in active:
                        logger.warning(f"[TRAY]   - {t.name}: daemon={t.daemon}")
    
                    logger.info("[TRAY] Force killing process with os._exit(0)...")
                    import os
                    os._exit(0)  # ← FORCE KILL PROCESS (không cleanup, kill ngay)
        
                import threading
                exit_thread = threading.Thread(target=force_exit, daemon=True)
                exit_thread.start()
                # ============================================
        
                logger.info("[TRAY] Exit procedure completed")
        
            except Exception as e:
                logger.error(f"[TRAY] Exit error: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
                # Emergency exit
                import sys
                sys.exit(0)

    
        # Wrapper functions for menu
        def on_show(icon, item):
            show_window_action()
    
        def on_stop(icon, item):
            stop_execution_action()
    
        def on_exit(icon, item):
            exit_app_action()
    
        def on_double_click(icon, item):
            """Handle double-click on tray icon"""
            show_window_action()
    
        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem("Show Window", on_show),
            pystray.MenuItem(
                "Stop Execution", 
                on_stop,
                visible=lambda item: self.is_actions_running
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", on_exit)
        )
    
        # Create icon with app icon image
        self.tray_icon = pystray.Icon(
            "TomSamAutobot",
            load_icon_image(),  # ← SỬ DỤNG ICON TỪ FILE
            "TomSamAutobot - Running",
            menu,
            on_activated=on_double_click
        )
    
        logger.info("[TRAY] System tray icon created")


    def start_tray_icon(self):
        """Start tray icon in separate daemon thread"""
        import threading
    
        if not hasattr(self, 'tray_icon') or self.tray_icon is None:
            self.create_tray_icon()
    
        # Check if already running
        if hasattr(self, 'tray_thread') and self.tray_thread and self.tray_thread.is_alive():
            logger.info("[TRAY] Icon already running")
            return
    
        # Run tray icon in daemon thread
        def run_tray():
            try:
                logger.info("[TRAY] Icon thread started")
                self.tray_icon.run()  # Blocking call
                logger.info("[TRAY] Icon thread stopped")
            except Exception as e:
                logger.error(f"[TRAY] Icon thread error: {e}")
    
        self.tray_thread = threading.Thread(target=run_tray, daemon=True)
        self.tray_thread.start()
        logger.info("[TRAY] System tray icon started in background")

    def stop_tray_icon(self):
        """Stop tray icon"""
        if hasattr(self, 'tray_icon') and self.tray_icon is not None:
            try:
                self.tray_icon.stop()
                self.tray_icon = None
                logger.info("[TRAY] System tray icon stopped")
            except Exception as e:
                logger.warning(f"[TRAY] Error stopping icon: {e}")




        
    def setup(self, model, view):
        self.model = model
        self.view = view
        
        # Set up callbacks for UI events
        self.view.set_callbacks(
            self.add_action,
            self.edit_action,
            self.delete_action,
            self.run_sequence,
            self.move_action,
            self.save_actions_to_file,
            self.play_action,
            self.delete_all_actions,
            self.duplicate_action,
            self.show_move_dialog,
            self.load_actions_from_file,
            self.toggle_action_disable
        )
        
        # ✅ KHỞI ĐỘNG LISTENER NGAY KHI APP START
        self.start_conditional_keyboard_listener()
        
        # Load sample data
        self.model.load_actions()
        self.update_view()
        self.setup_close_handler()
        
    def update_view(self):
        # Tính toán cấp độ lồng cho mỗi action
        nesting_levels = self.calculate_nesting_levels()
    
        # Truyền cả actions và nesting_levels vào view
        self.view.update_listbox(self.model.get_all_actions(), nesting_levels)
        
        
    def add_action(self):
        from views.action_dialog_view import ActionDialogView
        dialog = ActionDialogView(self.root)

        # Kết nối sự kiện chọn loại hành động
        dialog.action_type_combo.bind("<<ComboboxSelected>>", lambda e: self.on_action_type_changed(dialog))
    
        # Cấu hình và hiển thị dialog mặc định
        self.on_action_type_changed(dialog)    
      
        # Đặt hành động khi lưu
        dialog.save_button.config(command=lambda: self.on_dialog_save(dialog))

        # Hiển thị dialog và đợi
        dialog.grab_set()  # Đảm bảo dialog là modal
        self.root.wait_window(dialog)

        # Xử lý kết quả sau khi dialog đóng
        if dialog.result:
            self.model.add_action(dialog.result)
            # Thêm dòng này để lưu vào file
            # self.model.save_actions()
            self.update_view()


    def edit_action(self, index):
        action = self.model.get_action(index)
    
        from views.action_dialog_view import ActionDialogView
        dialog = ActionDialogView(self.root, action)
    
        # Gán callback trực tiếp cho nút Lưu
        dialog.save_button.config(command=lambda: self.on_dialog_save(dialog))        
    
        # Kết nối sự kiện chọn loại hành động , edit action không cho chọn lại action nên không cần gọi lại select        
        self.on_action_type_changed(dialog)
    
        # Hiển thị dialog và đợi
        dialog.grab_set()  # Đảm bảo dialog là modal
        self.root.wait_window(dialog)
    
        # Xử lý kết quả sau khi dialog đóng
        if dialog.result:
            self.model.update_action(index, dialog.result)
            # Thêm dòng này để lưu vào file
            # self.model.save_actions()
            self.update_view()   
            
    def delete_action(self, index):
        if self.view.ask_yes_no("Xác nhận", "Bạn có chắc muốn xóa hành động này?"):
            self.model.delete_action(index)
            self.update_view()
            
    def duplicate_action(self, index):
        """Nhân bản một action và đặt nó ngay sau action gốc"""
        original_action = self.model.get_action(index)
        if original_action:
            import copy
            new_parameters = copy.deepcopy(original_action.parameters)
        
            # ← SỬA: Thêm is_disabled parameter
            new_action = ActionItem(
                original_action.action_type, 
                new_parameters,
                original_action.is_disabled  # ← THÊM
            )
        
            self.model.add_action_at(index + 1, new_action)
            self.update_view()

            
                
    def play_action(self, index):
        """Thực thi một hành động cụ thể khi nút play được nhấn"""
    
        # ← ẨN WINDOW NGAY ĐẦU
        print("[EXECUTION] Hiding window to tray...")
        self.root.withdraw()
        
        exception_to_reraise = None  # ← STORE EXCEPTION
    
        try:
            action = self.model.get_action(index)
            action_frame = self.view.action_frames[index] if index < len(self.view.action_frames) else None
            from controllers.actions.action_factory import ActionFactory
            handler = ActionFactory.get_handler(self.root, action, self.view, self.model, self)
        
            print(f"[CONTROLLER DEBUG] play_action called for index {index}")
            print(f"[CONTROLLER DEBUG] Handler created: {handler}")
        
            if handler:
                handler.action_frame = action_frame
                print(f"[CONTROLLER DEBUG] Calling handler.play()...")
            
                # Xử lý đặc biệt cho các loại condition
                if action.action_type == ActionType.IF_CONDITION:
                    result = handler.play()
                    print(f"[CONTROLLER DEBUG] handler.play() result: {result}")
                
                    # Nếu IF sai (result = True), tìm ELSE IF
                    if result:
                        self._find_and_execute_else_if_for_standalone(index)
            
                elif action.action_type == ActionType.ELSE_IF_CONDITION:
                    # Xử lý ELSE_IF khi chạy standalone
                    print(f"[STANDALONE DEBUG] Chạy ELSE_IF tại index {index}")
                    handler.play()
            
                else:
                    handler.play()
    
        except Exception as e:
            # ========== CATCH EXCEPTION (NO EMAIL - WILL BE SENT BY TKINTER HANDLER) ==========
            print("=" * 80)
            print("[PLAY_ACTION ERROR] Exception caught in play_action()")
            print(f"[PLAY_ACTION ERROR] Exception type: {type(e).__name__}")
            print(f"[PLAY_ACTION ERROR] Exception message: {str(e)}")
            print("=" * 80)
        
            import traceback
            tb_str = traceback.format_exc()
            print(tb_str)
        
            # Store exception to re-raise later
            exception_to_reraise = e
        
            print("[PLAY_ACTION] Exception will be re-raised to Tkinter handler")
            # ===================================================================================


    
        finally:
            # ===== STOP TRAY ICON & SHOW WINDOW (NEW) =====
            try:
                self.stop_tray_icon()
            except Exception as tray_err:
                logger.warning(f"[TRAY] Error stopping icon: {tray_err}")
            # ← QUAN TRỌNG: LUÔN SHOW LẠI WINDOW (ngay cả khi có lỗi)
            # print("[EXECUTION] Showing window back...")
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
    
        # ========== RE-RAISE EXCEPTION AFTER CLEANUP ==========
        if exception_to_reraise is not None:
            logger.info("[PLAY_ACTION] Re-raising exception after cleanup...")
            raise exception_to_reraise
        # ======================================================




    def temporarily_disable_esc_listener(self):
        """Tạm thời disable ESC listener (dùng khi Keyboard Action bấm ESC)"""
        self._esc_listener_enabled = False
        logger.info("[KEYBOARD LISTENER] 🔇 ESC listener temporarily disabled")

    def re_enable_esc_listener(self):
        """Bật lại ESC listener"""
        self._esc_listener_enabled = True
        logger.info("[KEYBOARD LISTENER] 🔊 ESC listener re-enabled")

    def press_esc_safely(self):
        """
        Press ESC key without triggering stop execution
    
        Wrapper that temporarily disables listener
        """       
    
        self.temporarily_disable_esc_listener()
    
        try:
            pyautogui.press('esc')
            time.sleep(0.3)
        finally:
            self.re_enable_esc_listener()


    def _find_and_execute_else_if_for_standalone(self, if_index):
        """Tìm và thực thi ELSE IF cho IF độc lập"""
        all_actions = self.model.get_all_actions()
    
        # Tìm ELSE IF đầu tiên cùng cấp với IF này
        i = if_index + 1
        nesting_level = 0
    
        while i < len(all_actions):
            action = all_actions[i]
        
            if action.action_type == ActionType.IF_CONDITION:
                nesting_level += 1
            elif action.action_type == ActionType.END_IF_CONDITION:
                if nesting_level == 0:
                    break  # Hết khối IF, không có ELSE IF
                nesting_level -= 1
            elif action.action_type == ActionType.ELSE_IF_CONDITION and nesting_level == 0:
                # Tìm thấy ELSE IF cùng cấp, thực thi nó
                from controllers.actions.action_factory import ActionFactory
                else_if_handler = ActionFactory.get_handler(self.root, action, self.view, self.model, self)
            
                if else_if_handler:
                    action_frame = self.view.action_frames[i] if i < len(self.view.action_frames) else None
                    if action_frame:
                        else_if_handler.action_frame = action_frame
                    else_if_handler.play()
                return
        
            i += 1

            
    def delete_all_actions(self):
        """Xóa tất cả các hành động"""
        # Gọi phương thức xóa trong model
        self.model.delete_all_actions()
    
        # Cập nhật view sau khi xóa
        self.update_view()
        
    def move_action(self, from_index, to_index):
        # Cập nhật model
        self.model.move_action(from_index, to_index)
    
            
    def on_action_type_changed(self, dialog):       

        action_type_display = dialog.action_type_var.get()
        
        parameters = None
        try:
            # Chuyển đổi từ giá trị hiển thị sang đối tượng enum
            action_type = ActionType.from_display_value(action_type_display)
        except ValueError:
            print(f"Lỗi khi chuyển đổi giá trị: {action_type_display}")
            return None, None, None, None
        
        if dialog.is_edit and dialog.current_action.action_type == action_type_display:
            parameters = dialog.current_action.parameters
        
        # print(f"dialog.current_action.action_type: '{dialog.current_action.action_type}'")
        # print(f"action_type_display: '{action_type_display}'")
        # print(f"Biểu diễn chính xác của dialog.current_action.action_type: {repr(dialog.current_action.action_type)}")
        # print(f"Biểu diễn chính xác của action_type_display: {repr(action_type_display)}")
        #         
        # dialog.current_action.action_type: 'ActionType.TIM_HINH_ANH'
        # action_type_display: 'ActionType.TIM_HINH_ANH'
        # Biểu diễn chính xác của dialog.current_action.action_type: <ActionType.TIM_HINH_ANH: 'Tìm Hình Ảnh'>
        # Biểu diễn chính xác của action_type_display: 'ActionType.TIM_HINH_ANH'

        #Sử dụng factory method để tạo tham số cho loại action
        buttons = dialog.create_params_for_action_type(action_type, parameters)
        
        # Set dialog reference for params that need it
        if hasattr(dialog, 'current_params') and dialog.current_params:
            if hasattr(dialog.current_params, 'set_dialog'):
                dialog.current_params.set_dialog(dialog)
        
        # Mapping giữa button key và command tương ứng
        button_commands = {
            'select_area_button': lambda: self.select_screen_area(dialog),  # SHARED
            'select_program_button': lambda: self.browse_program(dialog)    # SHARED
        }
    
        # Kiểm tra nếu buttons là tuple
        # if isinstance(buttons, tuple):
        #     # Gán các nút dựa vào vị trí trong tuple
        #     button_keys = ['browse_button', 'select_area_button', 'select_program_button', 'screenshot_button']
        #     for i, button in enumerate(buttons):
        #         if i < len(button_keys) and button is not None:
        #             key = button_keys[i]
        #             if key in button_commands:
        #                 button.config(command=button_commands[key])
        # else:
        # Nếu buttons là dictionary, xử lý bình thường
        for button_key, button in buttons.items():
            if button_key in button_commands:
                button.config(command=button_commands[button_key])
    
        return buttons
    
    
    def browse_program(self, dialog):
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Select Program",
            filetypes=(
                ("Executable files", "*.exe"),
                ("All files", "*.*")
            )
        )
        if filename:
            dialog.set_parameter_value("program", filename)
            
    
    def select_screen_area(self, dialog):
        """Hiển thị trình chọn khu vực màn hình"""
        try:
            # Debug
            print("Importing ScreenAreaSelector...")
            from views.screen_area_selector import ScreenAreaSelector
        
            def on_area_selected(x, y, width, height):
                try:
                    # Cập nhật giá trị trong dialog
                    dialog.set_parameter_value("x", str(int(x)))
                    dialog.set_parameter_value("y", str(int(y)))
                    dialog.set_parameter_value("width", str(int(width)))
                    dialog.set_parameter_value("height", str(int(height)))
                    print(f"Đã chọn khu vực: x={x}, y={y}, width={width}, height={height}")
                except Exception as e:
                    print(f"Error updating dialog values: {e}")
        
            # TẠO VÀ HIỂN THỊ SELECTOR Ở NGOÀI HÀM CALLBACK
            print("Creating ScreenAreaSelector instance...")
            selector = ScreenAreaSelector(dialog, callback=on_area_selected)
            print("Showing selector...")
            selector.show()
    
        except Exception as e:
            print(f"Error in select_screen_area: {e}")
            import traceback
            traceback.print_exc()
            # Đảm bảo dialog luôn hiển thị lại
            try:
                dialog.deiconify()
            except:
                print("Could not deiconify dialog")

    def on_dialog_save(self, dialog):
        action_type_display = dialog.action_type_var.get()

        if not action_type_display:
            dialog.show_message("Lỗi", "Vui lòng chọn một loại hành động")
            return
    
        action_type = ActionType.from_display_value(action_type_display)
    
        # Lấy tất cả tham số từ đối tượng tham số hiện tại
        parameters = dialog.get_all_parameters()
        if action_type == ActionType.TIM_HINH_ANH:           
            image_path = parameters.get("image_path", "")
            if not image_path or image_path.strip() == "":
                dialog.show_message("Lỗi", "Vui lòng chọn một file hình ảnh")
                return
        else:
            pass
        print(parameters)
        dialog.result = ActionItem(action_type, parameters)
        dialog.destroy()
    
    def run_sequence(self):
        # ← THÊM: ẨN WINDOW
        # print("[EXECUTION] Hiding window to tray...")
        self.root.withdraw()
        
        # ===== START TRAY ICON (NEW) =====
        try:
            self.start_tray_icon()
        except Exception as tray_err:
            logger.warning(f"[TRAY] Could not start tray icon: {tray_err}")
        # =================================
        
        # ========== CANCEL AUTO-TRIGGER IF ACTIVE (NEW) ==========
        if self.auto_trigger_active:
            logger.info("[RUN_SEQUENCE] Cancelling auto-trigger (manual play)")
            self.cancel_auto_trigger()
        # ==========================================================
        
        from models.global_variables import GlobalVariables
        from constants import ActionType
        from controllers.actions.action_factory import ActionFactory
        
        # 🔄 RESET execution state
        self.is_execution_stopped = False
        self.is_actions_running = True  # ← SET FLAG: ACTIONS BẮT ĐẦU CHẠY
        
        # ========== AUTO-RESTART: SET BIẾN MÔI TRƯỜNG (NEW) ==========
        # Đánh dấu app đã Start (watchdog sẽ check biến này để tự exit)
        cfg.set_app_running(True)
        print("[AUTO-RESTART] ✓ App marked as RUNNING")
    
        # Clear countdown nếu đang có (vì user đã Start thủ công)
        cfg.set_restart_countdown(0)
        print("[AUTO-RESTART] ✓ Restart countdown cleared")    
       
        # ============================================================
    
        # 🎧 BẮT ĐẦU lắng nghe ESC có điều kiện
        self.start_conditional_keyboard_listener()

        try:
            # Lấy danh sách hành động từ model
            actions = self.model.get_all_actions()
    
            # Khởi tạo đối tượng quản lý biến toàn cục
            global_vars = GlobalVariables()
    
            # Khởi tạo stack để theo dõi các If condition lồng nhau
            if_stack = []
    
            # Thêm biến để theo dõi các khối cần bỏ qua
            skip_blocks = []
    
            # Hiển thị thông báo đang thực thi
            # self.view.show_message("Thực thi", "Đang thực thi chuỗi hành động...")
            import time       
            time.sleep(3)
            # Thực thi từng hành động theo thứ tự
            i = 0
            while i < len(actions):
                action = actions[i]
                action_type = action.action_type
        
                # ← THÊM CHECK DISABLED
                if action.is_disabled:
                    logger.info(f"[EXECUTION] ⏭️ Skipping disabled action at index {i}: {action.action_type}")
                    i += 1
                    continue
    
                # Kiểm tra xem action hiện tại có nằm trong khối cần bỏ qua không
                should_skip = False
                for block in skip_blocks:
                    if i >= block['start'] and i < block['end']:
                        should_skip = True
                        break
                
                if should_skip:              
                    i += 1
                    continue
            
                # KHÔNG bỏ qua ELSE_IF khi IF sai - để IfConditionAction tự xử lý
                if if_stack and not if_stack[-1]['condition_met']:
                    # CHỈ bỏ qua action thông thường, KHÔNG bỏ qua ELSE_IF
                    if action_type != ActionType.ELSE_IF_CONDITION and action_type != ActionType.END_IF_CONDITION:                   
                        i += 1
                        continue
            
                # ⚡ CHECK ESC BEFORE EACH ACTION
                if self.is_execution_stopped:
                    logger.info("[EXECUTION CONTROL] 🛑 Breaking due to ESC")
                    break
            
                # Xử lý IF condition
                if action_type == ActionType.IF_CONDITION:
                    # Tạo handler và thực thi condition
                    handler = ActionFactory.get_handler(self.root, action, self.view, self.model, self)
                    if handler:
                        result = handler.play() # Lưu kết quả từ handler.play()
                        condition_result = not result # True nếu điều kiện đúng
        
                        # Tạo một ID duy nhất cho khối IF này
                        import uuid
                        if_id = str(uuid.uuid4())
        
                        # Lưu trạng thái điều kiện IF
                        global_vars.set(f"__if_condition_{if_id}", condition_result)
        
                        # Lưu cấp độ lồng hiện tại
                        current_if_level = len(if_stack)
                        global_vars.set("__if_nesting_level", current_if_level + 1)
                        global_vars.set(f"__if_level_{current_if_level}", if_id)
        
                        # Đẩy thông tin vào stack
                        if_stack.append({
                            'id': if_id,
                            'condition_met': condition_result,
                            'level': current_if_level
                        })
        
                        # THAY ĐỔI: Không tạo skip_blocks, để IfConditionAction tự xử lý
                        if condition_result:
                            # IF đúng: IfConditionAction đã xử lý
                            pass
                        else:
                            # IF sai: IfConditionAction đã tìm và thực thi ELSE IF
                            pass
        
                # Xử lý ELSE IF condition
                elif action_type == ActionType.ELSE_IF_CONDITION:
                    logger.info(f"[CONTROLLER DEBUG] *** BẮT ĐẦU XỬ LÝ ELSE_IF tại index {i} ***")
                    logger.info(f"[CONTROLLER DEBUG] if_stack state: {if_stack}")
    
                    handler = ActionFactory.get_handler(self.root, action, self.view, self.model, self)
                    if handler:
                        action_frame = next((f for f in self.view.action_frames 
                                            if f.action.id == action.id), None)
                        if action_frame:
                            handler.action_frame = action_frame
        
                        logger.info(f"[CONTROLLER DEBUG] Gọi handler.play() cho ELSE_IF")
                        result = handler.play()
                        logger.info(f"[CONTROLLER DEBUG] ELSE_IF trả về: {result}")
                    else:
                        logger.info(f"[CONTROLLER DEBUG] KHÔNG thể tạo handler cho ELSE_IF!")
        
                # Xử lý END IF condition
                elif action_type == ActionType.END_IF_CONDITION:
                    # Xử lý kết thúc if
                    if if_stack:
                        if_stack.pop()
                
                        # Cập nhật cấp độ lồng hiện tại
                        global_vars.set("__if_nesting_level", len(if_stack))
                    
            
                # Xử lý FOR LOOP
                elif action_type == ActionType.FOR_LOOP:
                    import random                    
                  
                    # Import exceptions
                    try:
                        from exceptions.loop_exceptions import LoopBreakException, LoopSkipException
                    except ImportError:
                        print("[CONTROLLER ERROR] Cannot import loop exceptions. Please create exceptions/loop_exceptions.py")
                        i += 1
                        continue
    
                    # Lấy số vòng lặp từ parameters
                    repeat_loop = int(action.parameters.get("repeat_loop", 1))
                    random_repeat_loop = int(action.parameters.get("random_repeat_loop", 0))
    
                    # Sinh số random thêm nếu > 0
                    extra_loop = random.randint(0, random_repeat_loop) if random_repeat_loop > 0 else 0
                    total_loops = repeat_loop + extra_loop
    
                    print(f"[CONTROLLER DEBUG] 🔄 Bắt đầu For Loop với {total_loops} lần")
    
                    # Tìm vị trí End For tương ứng
                    nesting_level = 0
                    end_for_index = i
                    while end_for_index + 1 < len(actions):
                        end_for_index += 1
                        check_action = actions[end_for_index]
                        if check_action.action_type == ActionType.FOR_LOOP:
                            nesting_level += 1
                        elif check_action.action_type == ActionType.END_FOR_LOOP:
                            if nesting_level == 0:
                                break
                            nesting_level -= 1
    
                    # Kiểm tra tính hợp lệ của For Loop
                    if end_for_index >= len(actions) or actions[end_for_index].action_type != ActionType.END_FOR_LOOP:
                        print("[CONTROLLER ERROR] Không tìm thấy End For Loop tương ứng!")
                        i += 1
                        continue
    
                    # Thực thi vòng lặp For với Exception handling - FIXED
                    loop_count = 0
    
                    try:
                        while loop_count < total_loops:
                            # ===== CHECK STOP FLAG AT START (NEW) =====
                            if self.is_execution_stopped:
                                logger.info(f"[FOR LOOP] PAUSE/BREAK detected before iteration {loop_count+1}")
                                i = end_for_index + 1
                                break  # Exit for loop
                            # ==========================================
                            print(f"[CONTROLLER DEBUG] For Loop - Iteration {loop_count}/{total_loops}")
                            for_handler = ActionFactory.get_handler(self.root, action, self.view, self.model, self)
                            if for_handler:
                                for_handler.set_loop_index(loop_count, total_loops)  # 0-based index
                                
                            iteration_completed = False  # ← FLAG để track iteration completion
            
                            try:
                                # Thực thi các action lồng từ i+1 đến end_for_index-1
                                nested_i = i + 1
                
                                while nested_i < end_for_index:
                                    nested_action = actions[nested_i]
                                    nested_action_type = nested_action.action_type
                                    
                                    # ← THÊM CHECK DISABLED CHO NESTED ACTIONS
                                    if nested_action.is_disabled:
                                        print(f"[EXECUTION] ⏭️ Skipping disabled nested action at index {nested_i}: {nested_action.action_type}")
                                        nested_i += 1
                                        continue
                    
                                    # Kiểm tra điều kiện skip từ if_stack
                                    should_skip_nested = False
                                    if if_stack and not if_stack[-1]['condition_met']:
                                        if nested_action_type not in [ActionType.ELSE_IF_CONDITION, ActionType.END_IF_CONDITION]:
                                            should_skip_nested = True
                    
                                    if should_skip_nested:
                                        nested_i += 1
                                        continue
                    
                                    # Xử lý các action lồng
                                    if nested_action_type == ActionType.IF_CONDITION:
                                        handler_nested = ActionFactory.get_handler(self.root, nested_action, self.view, self.model, self)
                                        if handler_nested:
                                            result = handler_nested.play()
                                            condition_result = not result
        
                                            # Cập nhật if_stack cho nested IF
                                            import uuid
                                            nested_if_id = str(uuid.uuid4())
                                            if_stack.append({
                                                'id': nested_if_id,
                                                'condition_met': condition_result,
                                                'level': len(if_stack)
                                            })
        
                                            # ✅ FIX: Skip đến END_IF để tránh thực thi lại actions trong khối IF
                                            if condition_result:  # Nếu IF đúng và đã thực thi
                                                # Tìm END_IF tương ứng và skip đến đó
                                                nesting_level_if = 0
                                                skip_to_end_if = nested_i + 1
                                                while skip_to_end_if < end_for_index:
                                                    skip_action = actions[skip_to_end_if]
                                                    if skip_action.action_type == ActionType.IF_CONDITION:
                                                        nesting_level_if += 1
                                                    elif skip_action.action_type == ActionType.END_IF_CONDITION:
                                                        if nesting_level_if == 0:
                                                            nested_i = skip_to_end_if  # Skip đến END_IF
                                                            break
                                                        nesting_level_if -= 1
                                                    skip_to_end_if += 1
                    
                                    elif nested_action_type == ActionType.ELSE_IF_CONDITION:
                                        handler_nested = ActionFactory.get_handler(self.root, nested_action, self.view, self.model, self)
                                        if handler_nested:
                                            handler_nested.play()
                    
                                    elif nested_action_type == ActionType.END_IF_CONDITION:
                                        if if_stack:
                                            if_stack.pop()
                    
                                    else:
                                        # Thực thi action bình thường - EXCEPTION SẼ ĐƯỢC THROW TẠI ĐÂY
                                        handler_nested = ActionFactory.get_handler(self.root, nested_action, self.view, self.model, self)
                                        if handler_nested:
                                            action_frame = next((f for f in self.view.action_frames
                                                                if f.action.id == nested_action.id), None)
                                            if action_frame:
                                                handler_nested.action_frame = action_frame
                            
                                            # 🚨 CRITICAL: Exception sẽ được throw ngay tại đây
                                            handler_nested.play()
                    
                                    nested_i += 1
                
                                # ✅ QUAN TRỌNG: Chỉ set completed = True khi hoàn thành toàn bộ nested actions
                                iteration_completed = True
                
                            except LoopSkipException as e:
                                print(f"[CONTROLLER DEBUG] ⏭️ LoopSkipException caught: {e}")
                                print(f"[CONTROLLER DEBUG] Skipping iteration {loop_count + 1}")
                                iteration_completed = True  # ← Skip cũng coi là completed
                                
                            # ===== CHECK STOP FLAG AFTER ITERATION (NEW) =====
                            if self.is_execution_stopped:
                                logger.info(f"[FOR LOOP] PAUSE/BREAK detected after iteration {loop_count+1}")
                                i = end_for_index + 1
                                break  # Exit for loop
                            # ================================================
            
                            # ✅ FIXED: Chỉ tăng loop_count MỘT LẦN duy nhất
                            if iteration_completed:
                                loop_count += 1
    
                    except LoopBreakException as e:
                        print(f"[CONTROLLER DEBUG] 🚫 LoopBreakException caught: {e}")
                        print(f"[CONTROLLER DEBUG] For Loop TERMINATED IMMEDIATELY at iteration {loop_count + 1}")
    
                    # Debug thông báo kết thúc For Loop
                    if loop_count >= total_loops:
                        print(f"[CONTROLLER DEBUG] ✅ For Loop completed {total_loops} iterations normally")
                    else:
                        print(f"[CONTROLLER DEBUG] 🛑 For Loop terminated early at iteration {loop_count + 1}")
    
                    # Sau khi hoàn thành vòng lặp, nhảy đến action sau End For
                    i = end_for_index + 1
                    continue


                # Xử lý END FOR LOOP
                elif action_type == ActionType.END_FOR_LOOP:
                    # End For được xử lý trong logic For Loop, chỉ cần bỏ qua
                    print("[CONTROLLER DEBUG] Gặp End For Loop (đã được xử lý trong For Loop)")

                # Xử lý SKIP FOR LOOP
                elif action_type == ActionType.SKIP_FOR_LOOP:
                    handler = ActionFactory.get_handler(self.root, action, self.view, self.model, self)
                    if handler and handler.prepare_play():
                        print(f"[CONTROLLER DEBUG] Skip For được kích hoạt tại index {i}")
                        # Tìm End For tương ứng để skip đến iteration tiếp theo
                        nesting_level = 0
                        skip_to_idx = i + 1
        
                        while skip_to_idx < len(actions):
                            check_action = actions[skip_to_idx]
                            if check_action.action_type == ActionType.FOR_LOOP:
                                nesting_level += 1
                            elif check_action.action_type == ActionType.END_FOR_LOOP:
                                if nesting_level == 0:
                                    # Tìm thấy End For cùng level, skip đến đây để iteration tiếp theo
                                    break
                                nesting_level -= 1
                            skip_to_idx += 1
        
                        # Set flag để báo hiệu skip iteration trong For Loop
                        skip_current_iteration = True
                        break  # Thoát khỏi nested loop hiện tại
                    else:
                        print(f"[CONTROLLER DEBUG] Skip For điều kiện không thỏa, tiếp tục bình thường")

                # Xử lý BREAK FOR LOOP  
                elif action_type == ActionType.BREAK_FOR_LOOP:
                    handler = ActionFactory.get_handler(self.root, action, self.view, self.model, self)
                    if handler and handler.prepare_play():
                        print(f"[CONTROLLER DEBUG] Break For được kích hoạt tại index {i}")
                        # Set flag để báo hiệu break For Loop
                        break_current_loop = True
                        break  # Thoát khỏi nested loop hiện tại
                    else:
                        print(f"[CONTROLLER DEBUG] Break For điều kiện không thỏa, tiếp tục bình thường")


                elif action_type == ActionType.BANPHIM:
                    handler = ActionFactory.get_handler(self.root, action, self.view, self.model, self)
                    if handler:
                        action_frame = next((f for f in self.view.action_frames if f.action.id == action.id), None)
                        if action_frame:
                            handler.action_frame = action_frame
                        handler.play()
                    

                # Xử lý các loại action khác
                else:
                    # Kiểm tra xem có nên bỏ qua action này không
                    should_skip = False
                    # Nếu đang trong if và điều kiện không thỏa mãn thì bỏ qua
                    # NHƯNG KHÔNG bỏ qua ELSE_IF và END_IF
                    if if_stack and not if_stack[-1]['condition_met']:
                        if action_type != ActionType.ELSE_IF_CONDITION and action_type != ActionType.END_IF_CONDITION:
                            should_skip = True
    
                    if not should_skip:
                        # Tạo handler và thực thi
                        handler = ActionFactory.get_handler(self.root, action, self.view, self.model, self)
                        if handler:
                            # Thiết lập action frame
                            action_frame = next((f for f in self.view.action_frames 
                                                if f.action.id == action.id), None)
                            if action_frame:
                                handler.action_frame = action_frame
                            handler.play()
        
                # Di chuyển đến action tiếp theo
                i += 1
    
            # Show completion or stop message
            if self.is_execution_stopped:
                self.view.show_message("đã dừng", "chuỗi hành động đã được dừng (esc)")
            else:
                self.view.show_message("hoàn thành", "chuỗi hành động đã hoàn thành")

        except Exception as e:
            # ========== CATCH EXCEPTION (NO EMAIL - WILL BE SENT BY TKINTER HANDLER) ==========
            print("=" * 80)
            print("[RUN_SEQUENCE ERROR] Exception in sequence execution")
            print("=" * 80)
            
            import traceback
            tb_str = traceback.format_exc()
            print(tb_str)
            
            # Store exception to re-raise (NO EMAIL - will be sent by handle_tkinter_exception)
            exception_to_reraise = e
            
            print("[RUN_SEQUENCE] Exception will be re-raised to Tkinter handler")
            # ===================================================================================
    
        finally:
            # ✅ QUAN TRỌNG: LUÔN RESET FLAGS VÀ DỪNG LISTENER
            self.is_actions_running = False
            self.stop_keyboard_listener()
            print("[EXECUTION CONTROL] 🔄 Reset execution state")
            
            # ========== AUTO-RESTART: CLEAR BIẾN MÔI TRƯỜNG (NEW) ==========
            # Đánh dấu app đã Stop (không còn chạy nữa)
            cfg.set_app_running(False)
            print("[AUTO-RESTART] ✓ App marked as STOPPED")
            # ===============================================================

            print("[EXECUTION] Showing window back...")
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
    
        # ========== RE-RAISE EXCEPTION ==========
        if exception_to_reraise is not None:
            print("[RUN_SEQUENCE] Re-raising exception after cleanup...")
            raise exception_to_reraise
        # ========================================

        
        
    def capture_screen_area(self, dialog):
        """Hiển thị trình chọn khu vực màn hình và chụp ảnh khi bấm ESC"""
        from views.screen_area_selector import ScreenAreaSelector
    
        def update_textboxes(x, y, width, height):
            """Cập nhật textbox với giá trị tọa độ"""
            try:
                dialog.set_parameter_value("x", str(int(x)))
                dialog.set_parameter_value("y", str(int(y)))
                dialog.set_parameter_value("width", str(int(width)))
                dialog.set_parameter_value("height", str(int(height)))
            except Exception as e:
                print(f"Lỗi khi cập nhật giá trị textbox: {e}")
    
        def take_screenshot_after_close(x, y, width, height):
            """Chụp màn hình sau khi dialog đã đóng"""
            try:
                # Lấy đường dẫn lưu từ cài đặt
                save_path = self.get_save_path()
            
                # Tạo tên file với timestamp
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
                full_path = os.path.join(save_path, filename)
            
                # Đảm bảo thư mục tồn tại
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
                # QUAN TRỌNG: Chụp ảnh màn hình độ phân giải cao sau khi dialog đã đóng
                screenshot = pyautogui.screenshot(region=(x, y, width, height))
                screenshot.save(full_path)
            
                # Cập nhật đường dẫn hình ảnh trong dialog
                dialog.set_parameter_value("image_path", full_path)
                print(f"Đã lưu ảnh chụp tại: {full_path}")
            except Exception as e:
                print(f"Lỗi khi chụp màn hình: {e}")
    
        # Tạo và hiển thị selector với cả hai callback
        try:
            selector = ScreenAreaSelector(
                dialog, 
                callback=update_textboxes,
                post_close_callback=take_screenshot_after_close
            )
            selector.show()
        except Exception as e:
            print(f"Lỗi khi hiển thị selector: {e}")
            dialog.deiconify()

    def get_save_path(self):
        """Lấy đường dẫn lưu từ cài đặt, hoặc mặc định là ổ C"""
        try:
            # Thử lấy FILE_PATH từ cài đặt
            from config import get_config
            config = get_config()
            path = config.get("FILE_PATH", "")
        
            if path and os.path.exists(os.path.dirname(path)):
                return os.path.dirname(path)
        except Exception as e:
            print(f"Không thể lấy đường dẫn từ cài đặt: {e}")
    
        # Mặc định lưu vào C:\tomsamautobot
        default_path = "C:\\tomsamautobot"
        os.makedirs(default_path, exist_ok=True)
        return default_path
    
    def check_unsaved_changes(self, callback_function):
        """Kiểm tra thay đổi chưa lưu và hỏi người dùng trước khi tiếp tục"""
        if self.model.is_modified:
            result = self.view.ask_yes_no("Lưu thay đổi", "Bạn chưa lưu actions. Bạn có muốn lưu không?")
            if result:  # Nếu người dùng chọn Yes
                self.model.save_actions()
        # Dù chọn Yes hay No, đều thực hiện callback
        callback_function()

    def setup_close_handler(self):
        """Thiết lập xử lý khi đóng ứng dụng"""
        self.view.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """Xử lý khi đóng ứng dụng"""
        def close_app():
            self.view.master.destroy()
    
        self.check_unsaved_changes(close_app)
        
    def calculate_nesting_levels(self):
        """Tính toán cấp độ lồng cho mỗi action"""
        actions = self.model.get_all_actions()
        nesting_levels = [0] * len(actions)
        current_level = 0
    
        for i, action in enumerate(actions):
            if action.action_type == ActionType.IF_CONDITION:
                # Lưu cấp độ hiện tại cho action IF
                nesting_levels[i] = current_level
                # Tăng cấp độ cho các action sau IF
                current_level += 1
            elif action.action_type == ActionType.FOR_LOOP:
                # For có cùng logic với IF
                nesting_levels[i] = current_level
                current_level += 1
            elif action.action_type == ActionType.ELSE_IF_CONDITION:
                # Else If có cùng cấp độ với If tương ứng
                # Giảm level trước (để cùng level với IF) rồi tăng lại sau
                level_for_else = max(0, current_level - 1)
                nesting_levels[i] = level_for_else
            elif action.action_type == ActionType.END_IF_CONDITION:
                # Giảm cấp độ trước khi gán cho END IF
                current_level = max(0, current_level - 1)
                # Lưu cấp độ hiện tại cho action END IF
                nesting_levels[i] = current_level
            elif action.action_type == ActionType.END_FOR_LOOP:
                # End For có cùng logic với End If
                current_level = max(0, current_level - 1)
                nesting_levels[i] = current_level
            else:
                # Các action thông thường lấy cấp độ hiện tại
                nesting_levels[i] = current_level
    
        return nesting_levels

    def _skip_to_else_if_or_end_if(self, current_if_index, actions, if_stack):
        """Tìm ELSE IF hoặc END IF tương ứng với IF hiện tại"""
        level = 1
        i = current_if_index + 1
    
        while i < len(actions):
            action = actions[i]
        
            if action.action_type == ActionType.IF_CONDITION:
                level += 1
            elif action.action_type == ActionType.ELSE_IF_CONDITION and level == 1:
                # Tìm thấy ELSE IF cùng cấp
                return i
            elif action.action_type == ActionType.END_IF_CONDITION:
                level -= 1
                if level == 0:
                    # Tìm thấy END IF tương ứng
                    return i
        
            i += 1
    
        return len(actions)  # Không tìm thấy, kết thúc sequence

    def show_move_dialog(self):
        """Hiển thị dialog di chuyển hành động"""
        selected_index = self.view.get_selected_index()
    
        if selected_index is None:
            self.view.show_message("Lỗi", "Vui lòng chọn một hành động bằng cách click vào vùng action trước.")
            return
        
        max_index = len(self.model.get_all_actions())
        if max_index <= 1:
            self.view.show_message("Lỗi", "Không đủ hành động để di chuyển.")
            return
    
        dialog = MoveIndexDialog(self.root, selected_index, max_index)
        self.root.wait_window(dialog)
    
        if dialog.result_index is not None:
            target_index = dialog.result_index
            if target_index != selected_index:
                self.move_action(selected_index, target_index)
                self.update_view()
                self.view.set_selected_action(target_index)
                
    def save_actions_to_file(self):
        """Lưu actions vào file được chọn bởi user"""
        # Mở dialog chọn file để save
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Lưu các hành động vào file"
        )
    
        if not file_path:
            messagebox.showinfo("Thông báo", "Bạn chưa chọn file để lưu.")
            return
    
        try:
            # Lưu actions vào file được chọn
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([a.to_dict() for a in self.model.get_all_actions()], f, indent=2)
        
            messagebox.showinfo("Thành công", f"Đã lưu {len(self.model.get_all_actions())} hành động vào:\n{file_path}")
            print(f"Actions saved to: {file_path}")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu file:\n{str(e)}")
            print(f"Error saving actions: {e}")

    def load_actions_from_file(self):
        """Load actions từ file được chọn bởi user"""
        # Kiểm tra nếu có actions hiện tại, hỏi user có muốn tiếp tục không
        current_actions = self.model.get_all_actions()
        if current_actions:
            result = messagebox.askyesno(
                "Xác nhận", 
                f"Hiện tại có {len(current_actions)} hành động.\n"
                "Load file mới sẽ xóa toàn bộ actions hiện tại.\n\n"
                "Bạn có muốn tiếp tục không?"
            )
            if not result:
                return
    
        # Mở dialog chọn file để load
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Chọn file chứa các hành động"
        )
    
        if not file_path:
            messagebox.showinfo("Thông báo", "Bạn chưa chọn file để load.")
            return
    
        try:
            # Đọc file JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                actions_data = json.load(f)
        
            # Validate dữ liệu
            if not isinstance(actions_data, list):
                raise ValueError("File không đúng định dạng actions JSON")
        
            # Xóa toàn bộ actions hiện tại
            self.model.delete_all_actions()
        
            # Load actions từ file
            loaded_count = 0
            for action_data in actions_data:
                try:
                    action_type = action_data.get("action_type")
                    parameters = action_data.get("parameters", {})
                    is_disabled = action_data.get("is_disabled", False)
                    # Convert action_type sang enum nếu cần
                    try:
                        if isinstance(action_type, str):
                            action_enum = ActionType.from_display_value(action_type)
                        else:
                            action_enum = action_type
                    except Exception:
                        action_enum = action_type
                
                    # Tạo ActionItem mới và thêm vào model
                    new_action = ActionItem(action_enum, parameters, is_disabled)
                    self.model.add_action(new_action)
                    loaded_count += 1
                
                except Exception as e:
                    print(f"Warning: Không thể load action: {action_data}, Error: {e}")
                    continue
        
            # Cập nhật view
            self.update_view()
        
            messagebox.showinfo(
                "Thành công", 
                f"Đã load {loaded_count} hành động từ:\n{file_path}"
            )
            print(f"Actions loaded from: {file_path}")
        
        except FileNotFoundError:
            messagebox.showerror("Lỗi", f"Không tìm thấy file:\n{file_path}")
        except json.JSONDecodeError as e:
            messagebox.showerror("Lỗi", f"File JSON không hợp lệ:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể load file:\n{str(e)}")
            print(f"Error loading actions: {e}")

    def start_conditional_keyboard_listener(self):
        """Bắt đầu lắng nghe phím ESC CHỈ KHI actions đang chạy"""
        from pynput import keyboard
    
        # ← THÊM FLAG
        self._esc_listener_enabled = True
        controller_ref = self  # ← CAPTURE self
        def on_key_press(key):
            try:
                if key == keyboard.Key.pause:
                    # ✅ CHỈ XỬ LÝ pause/break KHI ACTIONS ĐANG CHẠY VÀ LISTENER ĐƯỢC BẬT
                    if self.is_actions_running and self._esc_listener_enabled:  # ← THÊM CHECK
                        # ===== PAUSE = EXIT APP (NEW) =====
                        logger.info("[PAUSE DETECTED] 🛑 Người dùng bấm PAUSE/BREAK - Thoát app!")
            
                        # Call exit logic (giống Exit tray icon)
                        self.root.after(0, controller_ref._exit_from_keyboard)  # Schedule on main thread
                        return False  # Stop listener
                    else:
                        # ✅ ACTIONS KHÔNG CHẠY HOẶC LISTENER BỊ DISABLE - IGNORE ESC
                        logger.info("[ESC IGNORED] 🔕 ESC bị ignore")
            except AttributeError:
                pass
    
        # Tạo và start listener
        self._keyboard_listener = keyboard.Listener(on_press=on_key_press)
        self._keyboard_listener.start()
        logger.info("[KEYBOARD LISTENER] 🎧 Đã bắt đầu lắng nghe ESC có điều kiện")
        


    def _exit_from_keyboard(self):
        """Exit app when Pause/Break pressed - Same as tray Exit"""
        try:
            logger.info("[KEYBOARD] Exit requested via PAUSE/BREAK key")
        
            # ===== STEP 1: SET STOP FLAGS =====
            self.is_execution_stopped = True
            self.is_actions_running = False
            logger.info("[KEYBOARD] Set execution stop flags")
            # ==================================
        
            # ===== STEP 2: SHUTDOWN THREADPOOLEXECUTOR =====
            import concurrent.futures
            import gc
            for obj in gc.get_objects():
                if isinstance(obj, concurrent.futures.ThreadPoolExecutor):
                    try:
                        logger.info("[KEYBOARD] Found ThreadPoolExecutor, shutting down...")
                        obj.shutdown(wait=False, cancel_futures=True)
                    except Exception as e:
                        logger.error(f"[KEYBOARD] Error shutting executor: {e}")
            # ===============================================
        
            # ===== STEP 3: CANCEL AUTO-TRIGGER =====
            if hasattr(self, 'auto_trigger_active') and self.auto_trigger_active:
                try:
                    self.cancel_auto_trigger()
                    logger.info("[KEYBOARD] Cancelled auto-trigger")
                except:
                    pass
            # =======================================
        
            # ===== STEP 4: STOP KEYBOARD LISTENER =====
            try:
                self.stop_conditional_keyboard_listener()
                logger.info("[KEYBOARD] Stopped keyboard listener")
            except:
                pass
            # ==========================================
        
            # ===== STEP 5: STOP TRAY ICON =====
            if hasattr(self, 'tray_icon') and self.tray_icon:
                try:
                    self.tray_icon.stop()
                    logger.info("[KEYBOARD] Tray icon stopped")
                except Exception as e:
                    logger.error(f"[KEYBOARD] Error stopping tray: {e}")
            # ==================================
        
            # ===== STEP 6: WAIT FOR CLEANUP =====
            logger.info("[KEYBOARD] Waiting 2s for threads to cleanup...")
            time.sleep(2)
            # ====================================
        
            # ===== STEP 7: DESTROY WINDOW =====
            logger.info("[KEYBOARD] Destroying Tkinter window...")
            self.root.destroy()
            # ==================================
        
            # ===== STEP 8: FORCE EXIT FALLBACK =====
            def force_exit():
                time.sleep(5)
                logger.warning("[KEYBOARD] Force exiting...")
                import os
                os._exit(0)
        
            import threading
            exit_thread = threading.Thread(target=force_exit, daemon=True)
            exit_thread.start()
            # =======================================
        
            logger.info("[KEYBOARD] Exit procedure completed")
        
        except Exception as e:
            logger.error(f"[KEYBOARD] Exit error: {e}")
            import sys
            sys.exit(0)



    def stop_keyboard_listener(self):
        """Dừng lắng nghe keyboard"""
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
            print("[KEYBOARD LISTENER] 🛑 Đã dừng lắng nghe ESC")

    def stop_execution(self):
        """Dừng execution ngay lập tức"""
        self.is_execution_stopped = True
        self.is_actions_running = False  # ← RESET FLAG
        print("[EXECUTION CONTROL] ⏹️ Execution đã được dừng bởi người dùng")
    
        try:
            self.view.show_message("Đã Dừng", "Đã dừng chuỗi hành động theo yêu cầu (PAUSE/BREAK)")
        except:
            pass

    def on_close(self):
        """Xử lý khi đóng ứng dụng"""
        def close_app():
            # ✅ DỪNG LISTENER TRƯỚC KHI ĐÓNG APP
            self.stop_keyboard_listener()
            self.view.master.destroy()
    
        self.check_unsaved_changes(close_app)

    def toggle_action_disable(self, index):
        """Toggle disable/enable state của action"""
        action_frame = self.view.action_frames[index]
        action_frame.toggle_disable()
    
        # Mark model as modified
        self.model.is_modified = True
    
        print(f"[CONTROLLER] Action {index+1} {'disabled' if action_frame.action.is_disabled else 'enabled'}")


    def execute_nested_actions(self, action_items):
        """
        Execute danh sách actions từ script (nested execution)
        Xử lý For loop, If condition đúng logic
    
        Args:
            action_items: List of ActionItem objects
    
        Returns:
            bool: True nếu thành công, False nếu bị stop
        """
        print(f"[NESTED_EXEC] Starting nested execution with {len(action_items)} actions")
    
        # Set flag để các action biết đang trong nested execution
        self._is_in_nested_execution = True
    
        try:
            # SỬ DỤNG LẠI logic execute_actions hiện có
            # Nhưng truyền vào action_items thay vì self.model.actions
        
            # Tạo temporary model với actions từ script
            original_actions = self.model.actions
            self.model.actions = action_items
        
            # Execute như bình thường
            success = self._execute_actions_internal(action_items)
        
            # Restore original actions
            self.model.actions = original_actions
        
            return success
        
        finally:
            self._is_in_nested_execution = False
            print(f"[NESTED_EXEC] Finished nested execution")


    def _execute_actions_internal(self, actions):
        """
        ✅ FIXED: Internal method để execute actions với logic For/If
        Sử dụng helper methods mới: find_matching_end(), execute_for_loop_range(), execute_if_range()
    
        ⚠️ ẢNH HƯỞNG:
        - Không ảnh hưởng run_sequence() (vẫn dùng logic cũ)
        - Chỉ dùng cho execute_nested_actions()
        """
        from controllers.actions.action_factory import ActionFactory
    
        i = 0
        context = {'if_stack': [], 'skip_blocks': []}
    
        while i < len(actions):
            if self.is_execution_stopped:
                return False
        
            action = actions[i]
        
            # Skip nếu disabled
            if action.is_disabled:
                i += 1
                continue
        
            action_type = action.action_type
        
            # ========== XỬ LÝ FOR LOOP ==========
            if action_type == ActionType.FOR_LOOP:
                # ✅ SỬ DỤNG find_matching_end() thay vì _find_matching_end_for()
                end_for_index = self.find_matching_end(
                    actions, i, ActionType.FOR_LOOP, ActionType.END_FOR_LOOP
                )
            
                if end_for_index == -1:
                    print(f"[ERROR] For loop tại index {i} không có End For")
                    return False
            
                # ✅ SỬ DỤNG execute_for_loop_range() 
                success = self.execute_for_loop_range(actions, i, end_for_index, context)
            
                if not success:
                    return False
            
                # Jump qua End For
                i = end_for_index + 1
                continue
        
            # ========== XỬ LÝ IF CONDITION ==========
            elif action_type == ActionType.IF_CONDITION:
                # ✅ SỬ DỤNG find_matching_end() thay vì _find_matching_end_if()
                end_if_index = self.find_matching_end(
                    actions, i, ActionType.IF_CONDITION, ActionType.END_IF_CONDITION
                )
            
                if end_if_index == -1:
                    print(f"[ERROR] If condition tại index {i} không có End If")
                    return False
            
                # ✅ SỬ DỤNG execute_if_range()
                success = self.execute_if_range(actions, i, end_if_index, context)
            
                if not success:
                    return False
            
                # Jump qua End If
                i = end_if_index + 1
                continue
        
            # ========== SKIP CÁC KEYWORD ACTIONS ==========
            elif action_type in [
                ActionType.END_FOR_LOOP,
                ActionType.BREAK_FOR_LOOP,
                ActionType.SKIP_FOR_LOOP,
                ActionType.END_IF_CONDITION,
                ActionType.ELSE_IF_CONDITION
            ]:
                # Những action này được xử lý bởi For/If handler
                i += 1
                continue
        
            # ========== EXECUTE NORMAL ACTION ==========
            else:
                try:
                    handler = ActionFactory.get_handler(
                        self.root, action, self.view, self.model, self
                    )
                
                    if handler:
                        handler.play()
                    
                except Exception as e:
                    print(f"[ERROR] Failed to execute action at index {i}: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
        
            i += 1
    
        return True

    
    # ==================== CONTROL FLOW HELPERS (REFACTORED) ====================
    # Những method này được tách ra để REUSE cho run_sequence() và execute_nested_actions()

    def find_matching_end(self, actions, start_index, start_type, end_type):
        """
        🆕 NEW METHOD - Tìm keyword kết thúc tương ứng (End For, End If)
    
        Args:
            actions: List actions
            start_index: Index của keyword bắt đầu (FOR_LOOP, IF_CONDITION)
            start_type: ActionType của keyword bắt đầu
            end_type: ActionType của keyword kết thúc
    
        Returns:
            int: Index của keyword kết thúc, hoặc -1 nếu không tìm thấy
    
        ⚠️ ẢNH HƯỞNG: Không ảnh hưởng action cũ, chỉ là helper mới
        """
        nesting_level = 0
        i = start_index + 1
    
        while i < len(actions):
            action = actions[i]
        
            if action.action_type == start_type:
                nesting_level += 1  # Nested cùng loại
            elif action.action_type == end_type:
                if nesting_level == 0:
                    return i  # Tìm thấy End cùng cấp
                nesting_level -= 1
        
            i += 1
    
        return -1  # Không tìm thấy


    def execute_action_range(self, actions, start_index, end_index, context=None):
        """
        🆕 NEW METHOD - Execute actions từ start_index+1 đến end_index-1
        Tự động xử lý nested For/If
    
        Args:
            actions: List actions
            start_index: Index bắt đầu (KHÔNG execute action này)
            end_index: Index kết thúc (KHÔNG execute action này)
            context: Dict chứa if_stack, skip_blocks (optional)
    
        Returns:
            bool: True nếu thành công, False nếu stop/error
    
        ⚠️ ẢNH HƯỞNG: Không ảnh hưởng action cũ, chỉ là helper mới
        """
        from controllers.actions.action_factory import ActionFactory
    
        if context is None:
            context = {'if_stack': [], 'skip_blocks': []}
    
        i = start_index + 1
    
        while i < end_index:
            if self.is_execution_stopped:
                return False
        
            action = actions[i]
            # ===== THÊM DEBUG LOG =====
            print(f"[NESTED_EXEC] 📍 Index {i}: {action.action_type}")
            
            # Skip disabled
            if action.is_disabled:
                print(f"[NESTED_EXEC] ⏭️ Skipped (disabled)")
                i += 1
                continue
        
            action_type = action.action_type
        
            # ===== XỬ LÝ NESTED FOR LOOP =====
            if action_type == ActionType.FOR_LOOP:
                end_for = self.find_matching_end(
                    actions, i, ActionType.FOR_LOOP, ActionType.END_FOR_LOOP
                )
            
                if end_for == -1:
                    print(f"[ERROR] For loop at index {i} missing End For")
                    return False
            
                # Execute For loop recursively
                success = self.execute_for_loop_range(actions, i, end_for, context)
                if not success:
                    return False
            
                i = end_for + 1  # Jump qua End For
                continue
        
            # ===== XỬ LÝ NESTED IF CONDITION =====
            elif action_type == ActionType.IF_CONDITION:
                end_if = self.find_matching_end(
                    actions, i, ActionType.IF_CONDITION, ActionType.END_IF_CONDITION
                )
            
                if end_if == -1:
                    print(f"[ERROR] If condition at index {i} missing End If")
                    return False
            
                # Execute If block recursively
                success = self.execute_if_range(actions, i, end_if, context)
                if not success:
                    return False
            
                i = end_if + 1  # Jump qua End If
                continue
        
            # ===== SKIP CONTROL FLOW KEYWORDS =====
            elif action_type in [
                ActionType.END_FOR_LOOP, ActionType.BREAK_FOR_LOOP, ActionType.SKIP_FOR_LOOP,
                ActionType.END_IF_CONDITION, ActionType.ELSE_IF_CONDITION
            ]:
                # Những keyword này được xử lý bởi For/If handler
                i += 1
                continue
        
            # ===== EXECUTE NORMAL ACTION =====
            else:
                handler = ActionFactory.get_handler(
                    self.root, action, self.view, self.model, self
                )
            
                if handler:
                    # Link action frame nếu có
                    action_frame = next(
                        (f for f in self.view.action_frames if f.action.id == action.id),
                        None
                    )
                    if action_frame:
                        handler.action_frame = action_frame
                
                    handler.play()
        
            i += 1
    
        return True


    def execute_for_loop_range(self, actions, for_index, end_for_index, context=None):
        """
        🆕 NEW METHOD - Execute For loop từ for_index đến end_for_index
        Copy từ logic trong run_sequence()
    
        ⚠️ ẢNH HƯỞNG: Không ảnh hưởng action cũ
        """
        from models.global_variables import GlobalVariables
    
        action = actions[for_index]
        params = action.parameters
    
        # Parse iterations
        iterations_str = params.get("iterations", "1")
        if "<" in iterations_str and ">" in iterations_str:
            var_name = iterations_str.strip("<>")
            iterations_str = GlobalVariables().get(var_name, "1")
    
        try:
            iterations = int(iterations_str)
        except:
            iterations = 1
    
        logger.info(f"[FOR LOOP] Starting {iterations} iterations (index {for_index} to {end_for_index})")
    
        # Execute loop
        for iteration in range(iterations):
            if self.is_execution_stopped:
                return False
        
            print(f"[FOR LOOP] Iteration {iteration+1}/{iterations}")
        
            # Set loop index variable
            from controllers.actions.action_factory import ActionFactory
            for_handler = ActionFactory.get_handler(
                self.root, action, self.view, self.model, self
            )
            if hasattr(for_handler, 'set_loop_index'):
                for_handler.set_loop_index(iteration, iterations)
            if for_handler:
                result = for_handler.play()  # ← LƯU RETURN VALUE
    
                # ===== CHECK RESULT (NEW) =====
                if result is False:  # Explicit check for False (not just falsy)
                    logger.warning(f"[ACTION RANGE] execute_for_loop_range stopping")
                    return False
                # ==============================
            # ===== CHECK STOP FLAG BEFORE EXECUTE (NEW) =====
            if self.is_execution_stopped:
                logger.info(f"[FOR LOOP] PAUSE/BREAK detected before executing iteration {iteration+1}")
                return False
            # ================================================
        
            # Execute actions inside loop
            success = self.execute_action_range(actions, for_index, end_for_index, context)
            
            # ===== CHECK STOP FLAG AFTER EXECUTE (NEW) =====
            if self.is_execution_stopped:
                logger.info(f"[FOR LOOP] PAUSE/BREAK detected after iteration {iteration+1} completed")
                return False
            # ===============================================
        
            if not success:
                return False
    
        print(f"[FOR LOOP] Completed {iterations} iterations")
        return True


    def execute_if_range(self, actions, if_index, end_if_index, context=None):
        """
        ✅ FIXED: Execute If block với Else If support
    
        Logic:
        1. Evaluate If condition
        2. Nếu TRUE: Execute actions từ If+1 đến Else If (hoặc End If)
        3. Nếu FALSE: Tìm Else If và execute từ Else If+1 đến End If
    
        ⚠️ ẢNH HƯỞNG: Fix logic If/Else If cho Upload Script
        """
        from controllers.actions.action_factory import ActionFactory
    
        action = actions[if_index]
    
        # ===== EVALUATE CONDITION =====
        handler = ActionFactory.get_handler(
            self.root, action, self.view, self.model, self
        )
    
        if not handler:
            print(f"[IF ERROR] Cannot create handler for If at index {if_index}")
            return False
    
        # Check condition qua should_break_action()
        condition_result = not handler.should_break_action()
    
        print(f"[IF CONDITION] 🔍 Condition at index {if_index} = {condition_result}")
    
        # ===== FIND ELSE IF (NẾU CÓ) =====
        else_if_index = -1
        nesting_level = 0
    
        for i in range(if_index + 1, end_if_index):
            act = actions[i]
        
            # Track nesting
            if act.action_type == ActionType.IF_CONDITION:
                nesting_level += 1
            elif act.action_type == ActionType.END_IF_CONDITION:
                nesting_level -= 1
        
            # Tìm Else If cùng cấp
            elif act.action_type == ActionType.ELSE_IF_CONDITION and nesting_level == 0:
                else_if_index = i
                break
    
        # ===== EXECUTE DỰA VÀO CONDITION =====
        if condition_result:
            # IF TRUE: Execute từ if_index+1 đến else_if_index (hoặc end_if_index)
            execute_end = else_if_index if else_if_index != -1 else end_if_index
        
            print(f"[IF CONDITION] ✅ TRUE → Execute actions [{if_index+1}:{execute_end}]")
        
            return self.execute_action_range(actions, if_index, execute_end, context)
    
        else:
            # IF FALSE: Execute Else If branch (nếu có)
            if else_if_index != -1:
                print(f"[IF CONDITION] ❌ FALSE → Execute Else If actions [{else_if_index+1}:{end_if_index}]")
            
                return self.execute_action_range(actions, else_if_index, end_if_index, context)
            else:
                print(f"[IF CONDITION] ❌ FALSE → No Else If, skip entire block")
                return True
            

    # ========== AUTO-TRIGGER COUNTDOWN METHODS (NEW) ==========
    def start_auto_trigger_countdown(self):
        """
        Start countdown for auto-triggering play after restart
        """
        import logging
        logger = logging.getLogger('TomSamAutobot')
    
        initial_delay = cfg.get_auto_start_delay()
    
        if initial_delay == 0:
            logger.info("[AUTO-TRIGGER] Disabled (delay = 0)")
            self.reset_crash_env_vars()
            return
    
        logger.info(f"[AUTO-TRIGGER] Starting countdown: {initial_delay}s")
        self.auto_trigger_remaining = initial_delay
        self.auto_trigger_cancelled = False
        self.auto_trigger_active = True
    
        # ========== LƯU INITIAL DELAY (FIX) ==========
        self.auto_trigger_initial_delay = initial_delay  # ← THÊM DÒNG NÀY!
        # =============================================
    
        def countdown_loop():
            """Countdown loop - runs every second"""
        
            # Check cancelled
            if self.auto_trigger_cancelled:
                logger.info("[AUTO-TRIGGER] Cancelled by user action")
                self.view.hide_countdown()
                self.auto_trigger_active = False
                return
        
            # Check settings changed
            current_delay = cfg.get_auto_start_delay()
        
            if current_delay == 0:
                # User disabled auto-trigger
                logger.info("[AUTO-TRIGGER] Cancelled (delay set to 0)")
                self.view.hide_countdown()
                self.reset_crash_env_vars()
                self.auto_trigger_active = False
                return
        
            # ========== FIX: SO SÁNH VỚI INITIAL DELAY (FIX) ==========
            if current_delay != self.auto_trigger_initial_delay:
                # Settings changed → Reset countdown
                logger.info(f"[AUTO-TRIGGER] Settings changed: {self.auto_trigger_initial_delay}s → {current_delay}s, resetting countdown")
                self.auto_trigger_remaining = current_delay
                self.auto_trigger_initial_delay = current_delay  # Update initial
            # ==========================================================
        
            # Update UI countdown
            self.view.show_countdown(self.auto_trigger_remaining)
        
            # Check countdown finished
            if self.auto_trigger_remaining <= 0:
                logger.info("[AUTO-TRIGGER] Countdown finished, triggering play...")
                self.view.hide_countdown()
                self.auto_trigger_active = False
            
                # Trigger play
                self.run_sequence()
                return
        
            # Decrement countdown
            self.auto_trigger_remaining -= 1
        
            # Schedule next tick (1 second)
            self.root.after(1000, countdown_loop)
    
        # Start countdown loop
        countdown_loop()

    
    def cancel_auto_trigger(self):
        """Cancel auto-trigger countdown"""
        if self.auto_trigger_active:
            import logging
            logger = logging.getLogger('TomSamAutobot')
            logger.info("[AUTO-TRIGGER] Cancelling countdown...")
            self.auto_trigger_cancelled = True
    
    def reset_crash_env_vars(self):
        """
        Reset all crash-related environment variables
        
        Called when:
        - Auto-trigger completes successfully
        - User manually clicks Play
        - User closes app
        - User disables auto-trigger (delay = 0)
        """
        import logging
        logger = logging.getLogger('TomSamAutobot')
        
        cfg.clear_crash_timestamp()
        logger.info("[AUTO-TRIGGER] ✓ Crash env vars reset")
    # ==========================================================



