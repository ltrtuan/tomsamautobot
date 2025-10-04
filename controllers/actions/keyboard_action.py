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
        
        try:
            if len(pyautogui_keys) == 1:
                # Phím đơn
                print(f"KEYBOARD DEBUG: Nhấn {pyautogui_keys[0]}")
                pyautogui.press(pyautogui_keys[0])
            else:
                # Tổ hợp phím - nhấn đồng thời
                print(f"KEYBOARD DEBUG: Tổ hợp {' + '.join(pyautogui_keys)}")
                pyautogui.hotkey(*pyautogui_keys)
                
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