from models.action_model import ActionItem

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
            self.move_action
        )
        
        # Load sample data
        self.model.add_sample_actions()
        self.update_view()
        
    def update_view(self):
        self.view.update_listbox(self.model.get_all_actions())
        
    def add_action(self):
        from views.action_dialog_view import ActionDialogView
        dialog = ActionDialogView(self.root)

        # Kết nối sự kiện chọn loại hành động
        dialog.action_type_combo.bind("<<ComboboxSelected>>", lambda e: self.on_action_type_changed(dialog))
    
        # Cấu hình và hiển thị dialog mặc định
        browse_button, select_area_button, select_program_button = self.on_action_type_changed(dialog)
    
        # Đăng ký sự kiện cho các nút
        if browse_button:
            browse_button.config(command=lambda: self.browse_image(dialog))
        if select_area_button:
            select_area_button.config(command=lambda: self.select_screen_area(dialog))
        if select_program_button:
            select_program_button.config(command=lambda: self.browse_program(dialog))
    
        # Đặt hành động khi lưu
        dialog.save_button.config(command=lambda: self.on_dialog_save(dialog))

        # Hiển thị dialog và đợi
        dialog.grab_set()  # Đảm bảo dialog là modal
        self.root.wait_window(dialog)

        # Xử lý kết quả sau khi dialog đóng
        if dialog.result:
            self.model.add_action(dialog.result)
            self.update_view()


    def edit_action(self, index):
        action = self.model.get_action(index)
    
        from views.action_dialog_view import ActionDialogView
        dialog = ActionDialogView(self.root, action)
    
        # Gán callback trực tiếp cho nút Lưu
        dialog.save_button.config(command=lambda: self.on_dialog_save(dialog))
    
        # Kết nối sự kiện chọn loại hành động
        dialog.action_type_combo.bind("<<ComboboxSelected>>", lambda e: self.on_action_type_changed(dialog))
        self.on_action_type_changed(dialog)
    
        # Hiển thị dialog và đợi
        dialog.grab_set()  # Đảm bảo dialog là modal
        self.root.wait_window(dialog)
    
        # Xử lý kết quả sau khi dialog đóng
        if dialog.result:
            self.model.update_action(index, dialog.result)
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
        action_type = dialog.action_type_var.get()
    
        parameters = None
        if dialog.is_edit and dialog.current_action.action_type == action_type:
            parameters = dialog.current_action.parameters
        
        if action_type == "Tìm Hình Ảnh":
            browse_button, select_area_button, select_program_button = dialog.create_image_search_params(parameters)
            browse_button.config(command=lambda: self.browse_image(dialog))
            select_area_button.config(command=lambda: self.select_screen_area(dialog))
            select_program_button.config(command=lambda: self.select_program(dialog))
        elif action_type == "Di Chuyển Chuột":
            dialog.create_mouse_move_params(parameters)

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
            dialog.image_path_var.set(filename)
    
        
    def select_screen_area(self, dialog):
        """Hiển thị trình chọn khu vực màn hình"""
        from views.screen_area_selector import ScreenAreaSelector
    
        def on_area_selected(x, y, width, height):
            # Cập nhật giá trị trong dialog
            dialog.x_var.set(str(int(x)))
            dialog.y_var.set(str(int(y)))
            dialog.width_var.set(str(int(width)))
            dialog.height_var.set(str(int(height)))
            print(f"Đã chọn khu vực: x={x}, y={y}, width={width}, height={height}")
    
        # QUAN TRỌNG: Truyền dialog thay vì self.root
        try:
            selector = ScreenAreaSelector(dialog, callback=on_area_selected)
            selector.show()
        except Exception as e:
            print(f"Lỗi khi hiển thị selector: {e}")

    def select_program(self, dialog):
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Select Program",
            filetypes=(
                ("Executable files", "*.exe"),
                ("All files", "*.*")
            )
        )
        if filename:
            dialog.program_var.set(filename)

    def on_dialog_save(self, dialog):
        print("on_dialog_save được gọi!")
        action_type = dialog.action_type_var.get()
    
        if not action_type:
            dialog.show_message("Lỗi", "Vui lòng chọn một loại hành động")
            return
        
        if action_type == "Tìm Hình Ảnh":
            # Kiểm tra đường dẫn
            path = dialog.image_path_var.get()
            if not path:
                dialog.show_message("Lỗi", "Vui lòng chọn một file hình ảnh")
                return
            
            # Thu thập tất cả tham số
            parameters = {
                "path": path,
                "x": dialog.x_var.get() or "0",
                "y": dialog.y_var.get() or "0",
                "width": dialog.width_var.get() or "0",
                "height": dialog.height_var.get() or "0",
                "accuracy": dialog.accuracy_var.get() or "80", 
                "random_time": dialog.random_time_var.get() or "0",
                "double_click": dialog.double_click_var.get(),
                "random_skip": dialog.random_skip_var.get() or "0",
                "variable": dialog.variable_var.get(),
                "program": dialog.program_var.get(),
                "break_conditions": []
            }
        
            # Thu thập các điều kiện break
            for condition in dialog.break_conditions:
                if condition["variable_var"].get():  # Chỉ thêm nếu biến được chỉ định
                    parameters["break_conditions"].append({
                        "logical_op": condition["logical_op_var"].get(),
                        "variable": condition["variable_var"].get(),
                        "value": condition["value_var"].get()
                    })
                
            dialog.result = ActionItem(action_type, parameters)
            dialog.destroy()
        elif action_type == "Di Chuyển Chuột":
            # Mã xử lý cho hành động di chuyển chuột...
            pass

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

    def on_reorder_actions(self, old_index, new_index):
        """Cập nhật model khi kéo thả"""
        # Di chuyển item trong danh sách actions
        action = self.model.actions.pop(old_index)
        self.model.actions.insert(new_index, action)
    
        # Lưu trạng thái (nếu cần)
        self.model.save_actions()