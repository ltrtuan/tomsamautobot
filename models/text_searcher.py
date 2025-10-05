# models/text_searcher.py
import pyautogui
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("[TEXT_SEARCHER] Warning: pytesseract not installed. Text search will not work.")

class TextSearcher:
    """Class để tìm kiếm text trên màn hình sử dụng OCR"""
    
    def __init__(self, search_text, region=None):
        """
        Args:
            search_text: Text cần tìm
            region: Tuple (x, y, width, height) hoặc None để tìm toàn màn hình
        """
        self.search_text = search_text
        self.region = region
    
    def search(self):
        """
        Tìm kiếm text trên màn hình
        
        Returns:
            tuple: (found, location) 
                - found: True nếu tìm thấy, False nếu không
                - location: (x, y) vị trí trung tâm của text tìm thấy
        """
        if not TESSERACT_AVAILABLE:
            print("[TEXT_SEARCHER] pytesseract not available")
            return False, None
        
        try:
            # Chụp màn hình
            if self.region:
                screenshot = pyautogui.screenshot(region=self.region)
                offset_x, offset_y = self.region[0], self.region[1]
            else:
                screenshot = pyautogui.screenshot()
                offset_x, offset_y = 0, 0
            
            # Sử dụng pytesseract để OCR
            # Lấy vị trí của từng từ
            data = pytesseract.image_to_data(
                screenshot, 
                output_type=pytesseract.Output.DICT,
                lang='eng+vie'
            )
            
            # Tìm text trong kết quả OCR
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                text = data['text'][i].strip()
                
                # So sánh text (không phân biệt hoa thường)
                if text.lower() == self.search_text.lower():
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    
                    # Tính vị trí trung tâm
                    center_x = offset_x + x + w // 2
                    center_y = offset_y + y + h // 2
                    
                    print(f"[TEXT_SEARCHER] Found text '{self.search_text}' at ({center_x}, {center_y})")
                    return True, (center_x, center_y)
            
            print(f"[TEXT_SEARCHER] Text '{self.search_text}' not found")
            return False, None
            
        except Exception as e:
            print(f"[TEXT_SEARCHER] Error during search: {e}")
            return False, None
