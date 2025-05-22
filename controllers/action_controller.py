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
            model.save_actions,
            self.play_action,
            self.delete_all_actions,
            self.duplicate_action
        )
        
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
        # Lấy action cần duplicate
        original_action = self.model.get_action(index)
    
        if original_action:
            # Tạo một bản sao của action
            import copy
            new_parameters = copy.deepcopy(original_action.parameters)
        
            # Tạo action mới với parameters giống hệt action gốc
            new_action = ActionItem(original_action.action_type, new_parameters)
        
            # Thêm action mới vào sau action gốc
            self.model.add_action_at(index + 1, new_action)
        
            # Cập nhật view
            self.update_view()
        
            # Hiển thị thông báo thành công
            action_frame = self.view.action_frames[index + 1] if index + 1 < len(self.view.action_frames) else None
            if action_frame:
                action_frame.show_temporary_notification("Đã nhân bản thành công")

    
    def play_action(self, index):
        """Thực thi một hành động cụ thể khi nút play được nhấn"""
        # Lấy action và frame
        action = self.model.get_action(index)
        action_frame = self.view.action_frames[index] if index < len(self.view.action_frames) else None

        # Tạo handler
        from controllers.actions.action_factory import ActionFactory
        handler = ActionFactory.get_handler(self.root, action, self.view, self.model, self)

        if handler:
            # THÊM: Gọi prepare_play() trước khi play()
            handler.prepare_play()

            # Thiết lập action frame
            handler.action_frame = action_frame

            # Thực thi và lấy kết quả
            result = handler.play()

            # XỬ LÝ ĐẶC BIỆT: Nếu là IF condition và kết quả sai (result=True), tìm ELSE IF
            if action.action_type == ActionType.IF_CONDITION and result:
                # ĐỢI THÔNG BÁO IF HIỂN THỊ (giảm delay để cải thiện UX)
                self.root.after(500, lambda: self.find_and_execute_else_if(handler))  # Thay đổi
        else:
            # Thông báo không hỗ trợ
            if action_frame:
                action_frame.show_temporary_notification(f"Chức năng '{action.action_type}' chưa được hỗ trợ")
            
    def find_and_execute_else_if(self, if_handler):
        """Tìm và thực thi ELSE IF tương ứng cho một IF handler cụ thể."""
        if hasattr(if_handler, 'current_internal_condition_id'):
            if_handler._find_matching_else_if(if_handler.current_internal_condition_id)
        else:
            # Fallback nếu IF handler không có current_internal_condition_id
            # Điều này không nên xảy ra nếu prepare_play của IfConditionAction được gọi đúng
            if_handler._find_matching_else_if() 
            if hasattr(if_handler, 'action_frame') and if_handler.action_frame:
                 if_handler.action_frame.show_temporary_notification("CẢNH BÁO: IF handler thiếu ID nội bộ!")
                
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
        from models.global_variables import GlobalVariables
        from constants import ActionType
        from controllers.actions.action_factory import ActionFactory

        # Lấy danh sách hành động từ model
        actions = self.model.get_all_actions()
    
        # Khởi tạo đối tượng quản lý biến toàn cục
        global_vars = GlobalVariables()
    
        # Khởi tạo stack để theo dõi các If condition lồng nhau
        if_stack = []
    
        # Thêm biến để theo dõi các khối cần bỏ qua
        skip_blocks = []
    
        # Hiển thị thông báo đang thực thi
        self.view.show_message("Thực thi", "Đang thực thi chuỗi hành động...")
    
        # Thực thi từng hành động theo thứ tự
        i = 0
        while i < len(actions):
            action = actions[i]
            action_type = action.action_type
        
            # Kiểm tra xem action hiện tại có nằm trong khối cần bỏ qua không
            should_skip = False
            for block in skip_blocks:
                if i >= block['start'] and i < block['end']:
                    should_skip = True
                    break
                
            if should_skip:
                # Thông báo bỏ qua action này (debug)
                action_frame = next((f for f in self.view.action_frames 
                                   if f.action.id == action.id), None)
                if action_frame:
                    action_frame.show_temporary_notification("Bỏ qua action này")
                i += 1
                continue
            
            # Nếu đang ở trong if stack và điều kiện không thỏa mãn, bỏ qua
            if if_stack and not if_stack[-1]['condition_met']:
                # Thông báo bỏ qua vì if không thỏa mãn (debug)
                action_frame = next((f for f in self.view.action_frames 
                                   if f.action.id == action.id), None)
                if action_frame:
                    action_frame.show_temporary_notification("Bỏ qua vì if điều kiện sai")
                i += 1
                continue
            
            # Xử lý IF condition
            if action_type == ActionType.IF_CONDITION:
                # Tạo handler và thực thi condition
                handler = ActionFactory.get_handler(self.root, action, self.view, self.model, self)
                if handler:
                    result = handler.play()  # Lưu kết quả từ handler.play()
                    condition_result = not result  # True nếu điều kiện đúng
                
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
                
                    # Thêm vào đây: nếu condition false, bỏ qua đến ELSE IF hoặc END IF
                    if not condition_result:
                        # Tìm ELSE_IF hoặc END_IF gần nhất
                        current_level = 1
                        skip_to = -1
                    
                        for j in range(i + 1, len(actions)):
                            if actions[j].action_type == ActionType.IF_CONDITION:
                                current_level += 1
                            elif actions[j].action_type == ActionType.ELSE_IF_CONDITION and current_level == 1:
                                # Tìm thấy ELSE_IF, không skip vượt qua nó
                                break
                            elif actions[j].action_type == ActionType.END_IF_CONDITION:
                                current_level -= 1
                                if current_level == 0:
                                    # Tìm thấy END_IF tương ứng
                                    skip_to = j
                                    break
                    
                        # Nếu không có ELSE_IF, bỏ qua đến END_IF
                        if skip_to > -1:
                            skip_blocks.append({
                                'start': i + 1,  # Start từ action ngay sau if
                                'end': skip_to  # End ở action End If
                            })
        
            # Xử lý ELSE IF condition
            elif action_type == ActionType.ELSE_IF_CONDITION:
                # Kiểm tra xem có nằm trong block if không
                if not if_stack:
                    # Bỏ qua nếu không nằm trong if
                    pass
                else:
                    # Lấy thông tin if gần nhất
                    current_if = if_stack[-1]
        
                    # Kiểm tra riêng và hiển thị rõ lý do bỏ qua
                    if current_if['condition_met']:
                        # Debug: nếu if đã true, bỏ qua else if này
                        action_frame = next((f for f in self.view.action_frames
                                           if f.action.id == action.id), None)
                        if action_frame:
                            action_frame.show_temporary_notification(
                                "Bỏ qua Else If vì If trước đã True"
                            )
                        i += 1
                        continue
            
                    # Chỉ đánh giá nếu các điều kiện trước đó đều không thỏa mãn
                    if not current_if['condition_met']:
                        # Tạo handler và thực thi
                        handler = ActionFactory.get_handler(self.root, action, self.view, self.model, self)
                        if handler:
                            handler.play()
                            condition_result = not handler.should_break_action()
                
                            # Cập nhật trạng thái khối if hiện tại
                            if condition_result:
                                current_if['condition_met'] = True
                                global_vars.set(f"__if_condition_{current_if['id']}", True)
        
            # Xử lý END IF condition
            elif action_type == ActionType.END_IF_CONDITION:
                # Xử lý kết thúc if
                if if_stack:
                    if_stack.pop()
                
                    # Cập nhật cấp độ lồng hiện tại
                    global_vars.set("__if_nesting_level", len(if_stack))
        
            # Xử lý các loại action khác
            else:
                # Kiểm tra xem có nên bỏ qua action này không
                should_skip = False
            
                # Nếu đang trong if và điều kiện không thỏa mãn thì bỏ qua
                if if_stack and not if_stack[-1]['condition_met']:
                    should_skip = True
            
                if not should_skip:
                    # Tạo handler và thực thi
                    handler = ActionFactory.get_handler(self.root, action, self.view, self.model, self)
                    if handler:
                        handler.play()
        
            # Di chuyển đến action tiếp theo
            i += 1
    
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
            else:
                # Các action thông thường lấy cấp độ hiện tại
                nesting_levels[i] = current_level
    
        return nesting_levels

