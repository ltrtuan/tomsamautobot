from controllers.actions.base_action import BaseAction
import pyautogui
import time

class KeyboardAction(BaseAction):
    """Handler thực thi hành động bàn phím với delay giữa các row."""
    
    def prepare_play(self):
        """Thực hiện nhấn phím theo từng row với delay 1 giây."""
        if self.should_stop():
            return
            
        key_sequence = self.params.get("key_sequence", "")
        if not key_sequence:
            return
        
        # ➊ THÊM: Lưu key_sequence vào variable nếu có
        variable = self.params.get("variable", "")
        if variable:
            from models.global_variables import GlobalVariables
            globals_var = GlobalVariables()
            # ➊ Option 1: Lưu raw string với dấu ;
            # globals_var.set(variable, key_sequence)
    
            # ➋ Option 2: Lưu chỉ chữ cái, bỏ dấu ; và space
            clean_value = key_sequence.replace(";", "").replace(" ", "")
            globals_var.set(variable, clean_value)
            
        # Tách các row bằng dấu ;
        rows = [row.strip() for row in key_sequence.split(";") if row.strip()]        
        
        
        for i, row in enumerate(rows):
            if self.should_stop():
                break                
          
            self._execute_key_combination(row)
            
            # Delay 1 giây giữa các row (trừ row cuối)
            if i < len(rows) - 1:                
                delay = self._get_natural_delay()
                time.sleep(delay)
    
    def _execute_key_combination(self, combination):
        """Thực hiện nhấn tổ hợp phím trong 1 row."""
        keys = [key.strip() for key in combination.split("+") if key.strip()]
        
        if not keys:
            return
            
        # Map phím đặc biệt
        key_mapping = {
            "Window": "win",
            "Ctrl": "ctrl", 
            "Shift": "shift",
            "Alt": "alt",
            "Enter": "enter",
            "Esc": "escape",
            "Del": "delete",
            "BackSpace": "backspace",
            "Space": "space",
            "Up": "up",
            "Down": "down", 
            "Left": "left",
            "Right": "right"
        }
        
        # Convert keys
        pyautogui_keys = []
        for key in keys:
            if key in key_mapping:
                pyautogui_keys.append(key_mapping[key])
            elif key.startswith("F") and len(key) <= 3:  # F1-F12
                pyautogui_keys.append(key.lower())
            else:
                pyautogui_keys.append(key.lower())
                
        # ← THÊM: Kiểm tra nếu có phím ESC
        is_esc_key = "escape" in pyautogui_keys
        try:
            # ← THÊM: Disable listener trước khi bấm ESC
            if is_esc_key:
                print("[KEYBOARD ACTION] 🔇 Tạm dừng ESC listener (đang bấm ESC)")
                if hasattr(self, 'controller') and self.controller:
                    self.controller.temporarily_disable_esc_listener()
        
            if len(pyautogui_keys) == 1:
                # Phím đơn
                print(f"KEYBOARD DEBUG: Nhấn {pyautogui_keys[0]}")
                pyautogui.press(pyautogui_keys[0])
            else:
                # Tổ hợp phím - nhấn đồng thời
                print(f"KEYBOARD DEBUG: Tổ hợp {' + '.join(pyautogui_keys)}")
                pyautogui.hotkey(*pyautogui_keys)
        
            # ← THÊM: Re-enable listener sau khi bấm ESC xong
            if is_esc_key:
                import time
                time.sleep(0.5)  # Đợi 0.5s để ESC được xử lý
                print("[KEYBOARD ACTION] 🔊 Bật lại ESC listener")
                if hasattr(self, 'controller') and self.controller:
                    self.controller.re_enable_esc_listener()
                
        except Exception as e:
            print(f"KEYBOARD ERROR: Lỗi khi nhấn phím {combination}: {e}")


    def _get_natural_delay(self):
        """Tạo delay tự nhiên như người dùng thực sự."""
        import random
    
        # 70% delay ngắn (0.3-0.7s), 30% delay dài (0.8-1.5s) 
        if random.random() < 0.7:
            return random.uniform(0.2, 0.5)  # Typing nhanh
        else:
            return random.uniform(0.6, 0.9)   # Suy nghĩ/pause
        
    @staticmethod
    def press_key_static(key_sequence):
        """
        Static method để press key từ action khác
    
        Args:
            key_sequence: "Enter" hoặc "Ctrl+C" hoặc "Esc;Enter"
        """
        import pyautogui
        import time
        import random
    
        # Map phím
        key_mapping = {
            "Window": "win", "Ctrl": "ctrl", "Shift": "shift", "Alt": "alt",
            "Enter": "enter", "Esc": "escape", "Del": "delete", 
            "BackSpace": "backspace", "Space": "space",
            "Up": "up", "Down": "down", "Left": "left", "Right": "right"
        }
    
        # Tách rows (nếu có dấu ;)
        rows = [row.strip() for row in key_sequence.split(";") if row.strip()]
    
        for i, row in enumerate(rows):
            # Tách keys trong row (nếu có dấu +)
            keys = [key.strip() for key in row.split("+") if key.strip()]
        
            # Convert keys
            pyautogui_keys = []
            for key in keys:
                if key in key_mapping:
                    pyautogui_keys.append(key_mapping[key])
                elif key.startswith("F") and len(key) <= 3:  # F1-F12
                    pyautogui_keys.append(key.lower())
                else:
                    pyautogui_keys.append(key.lower())
        
            # Press keys
            if len(pyautogui_keys) == 1:
                pyautogui.press(pyautogui_keys[0])
            else:
                pyautogui.hotkey(*pyautogui_keys)
        
            # Delay between rows
            if i < len(rows) - 1:
                time.sleep(random.uniform(0.2, 0.5))
