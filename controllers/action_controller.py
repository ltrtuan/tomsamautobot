from models.action_model import ActionItem
import os
import time
import pyautogui
from PIL import Image
from constants import ActionType

class ActionController:
    def __init__(self, root):
        self.root = root
        self.model = None
        self.view = None
        
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
            model.save_actions
        )
        
        # Load sample data
        self.model.load_actions()
        self.update_view()
        self.setup_close_handler()
        
    def update_view(self):
        self.view.update_listbox(self.model.get_all_actions())
        
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
            
    def move_action(self, from_index, to_index):
        # Cập nhật model
        self.model.move_action(from_index, to_index)
    
        # Cập nhật view
        self.update_view()
            
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
        
        # Mapping giữa button key và command tương ứng
        button_commands = {
            'browse_button': lambda: self.browse_image(dialog),
            'select_area_button': lambda: self.select_screen_area(dialog),
            'select_program_button': lambda: self.browse_program(dialog),
            'screenshot_button': lambda: self.capture_screen_area(dialog)
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

    def browse_image(self, dialog):
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Chọn một hình ảnh",
            filetypes=(
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("All files", "*.*")
            )
        )
        if filename:
            dialog.set_parameter_value("image_path", filename)
        
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

    def on_dialog_save(self, dialog):
        print("on_dialog_save được gọi!")
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
        
            # Thu thập tất cả tham số
            # parameters = {
            #     "path": path,
            #     "x": dialog.x_var.get() or "0",
            #     "y": dialog.y_var.get() or "0",
            #     "width": dialog.width_var.get() or "0",
            #     "height": dialog.height_var.get() or "0",
            #     "accuracy": dialog.accuracy_var.get() or "80", 
            #     "random_time": dialog.random_time_var.get() or "0",
            #     "double_click": dialog.double_click_var.get(),
            #     "random_skip": dialog.random_skip_var.get() or "0",
            #     "variable": dialog.variable_var.get(),
            #     "program": dialog.program_var.get(),
            #     "break_conditions": []
            # }
    
            # # Thu thập các điều kiện break
            # for condition in dialog.break_conditions:
            #     if condition["variable_var"].get():  # Chỉ thêm nếu biến được chỉ định
            #         parameters["break_conditions"].append({
            #             "logical_op": condition["logical_op_var"].get(),
            #             "variable": condition["variable_var"].get(),
            #             "value": condition["value_var"].get()
            #         })
            
            # dialog.result = ActionItem(action_type_display, parameters)
            # dialog.destroy()
        elif action_type == ActionType.DI_CHUYEN_CHUOT:
            # Thu thập tham số cho hành động di chuyển chuột
            # parameters = {
            #     "x": dialog.x_var.get() or "0",
            #     "y": dialog.y_var.get() or "0",
            #     "duration": dialog.duration_var.get() or "0.5"
            # }
            # dialog.result = ActionItem(action_type_display, parameters)
            # dialog.destroy()
            pass
        else:
            dialog.show_message("Lỗi", f"Loại hành động không được hỗ trợ: {action_type_display}")

        dialog.result = ActionItem(action_type, parameters)
        dialog.destroy()
        

    def run_sequence(self):
        
        from models.image_action import ImageAction
        from models.global_variables import GlobalVariables
    
        # Lấy danh sách hành động từ model
        actions = self.model.get_all_actions()
        # Lấy đối tượng quản lý biến toàn cục
        variables = GlobalVariables()
    
        # Hiển thị thông báo đang thực thi
        self.view.show_message("Thực thi", "Đang thực thi chuỗi hành động...")
    
        # Thực thi từng hành động theo thứ tự
        for i, action in enumerate(actions):
            action_type = action.action_type
            parameters = action.parameters
        
            print(f"Đang thực hiện hành động {i+1}: {action_type}")
        
            if action_type == "Tìm Hình Ảnh":
                # Khởi tạo và thực thi hành động tìm hình ảnh
                image_action = ImageAction(parameters)
                result = image_action.execute()
            
                if not result:
                    print(f"Hành động {i+1}: Tìm hình ảnh thất bại hoặc điều kiện dừng được đáp ứng")
                else:
                    print(f"Hành động {i+1}: Tìm hình ảnh thành công")
                
            elif action_type == "Di Chuyển Chuột":
                # Xử lý hành động di chuyển chuột
                print(f"Hành động {i+1}: Di chuyển chuột (chưa được triển khai)")
            
            # Thêm các loại hành động khác...
    
        # Hiển thị thông báo hoàn thành
        self.view.show_message("Hoàn Thành", "Chuỗi hành động đã được thực hiện")    
        
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