class BaseFlowAction:
    def __init__(self, driver):
        self.driver = driver

    def get_element_viewport_coordinates(self, element):
        """
        Trả về tọa độ (x, y), chiều dài, chiều cao, right, bottom của element relative to viewport hiện tại.
        Kết quả: dict {x, y, width, height, right, bottom}
        """
        try:
            rect = self.driver.execute_script("""
                var rect = arguments[0].getBoundingClientRect();
                return {
                    'x': rect.left,
                    'y': rect.top,
                    'width': rect.width,
                    'height': rect.height,
                    'right': rect.right,
                    'bottom': rect.bottom
                };
            """, element)
            return rect
        except Exception as e:
            print(f"[BaseFlowAction] Get viewport coordinates error: {e}")
            return None

    def is_element_in_viewport(self, element):
        """
        Kiểm tra xem element có nằm trong vùng nhìn thấy của user trên màn hình browser chưa.
        """
        try:
            return self.driver.execute_script("""
                var rect = arguments[0].getBoundingClientRect();
                return (
                    rect.top >= 0 &&
                    rect.left >= 0 &&
                    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                );
            """, element)
        except Exception as e:
            print(f"[BaseFlowAction] Check viewport error: {e}")
            return False
