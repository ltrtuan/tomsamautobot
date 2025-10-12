# helpers/selenium_actions.py

"""
Selenium Human-like Actions
Các hành động mô phỏng người dùng thật khi lướt web với chuyển động chuột human-like
"""

import random
import time
import math
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, 
    TimeoutException, 
    ElementClickInterceptedException,
    StaleElementReferenceException
)

# ============================================================
# HUMAN-LIKE MOUSE MOVEMENT (FROM human_like_movement.py)
# ============================================================

class HumanMouseMovement:
    """Class chứa các thuật toán di chuyển chuột human-like với Bezier curves"""
    
    @staticmethod
    def _bezier_curve(t, p0, p1, p2, p3):
        """Tính điểm trên đường cong Bezier bậc 3"""
        return (
            (1-t)**3 * p0 +
            3 * (1-t)**2 * t * p1 +
            3 * (1-t) * t**2 * p2 +
            t**3 * p3
        )
    
    @staticmethod
    def bezier_path(start, end):
        """Đường cong Bezier mượt mà"""
        path = []
        distance = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        steps = random.randint(15, 25)
        
        offset_x = random.uniform(-0.3, 0.3) * distance
        offset_y = random.uniform(-0.3, 0.3) * distance
        
        p0 = start
        p3 = end
        p1 = (start[0] + distance/3 + offset_x, start[1] + offset_y)
        p2 = (end[0] - distance/3 + offset_x, end[1] + offset_y)
        
        for i in range(steps + 1):
            t = i / steps
            x = HumanMouseMovement._bezier_curve(t, p0[0], p1[0], p2[0], p3[0])
            y = HumanMouseMovement._bezier_curve(t, p0[1], p1[1], p2[1], p3[1])
            
            if i < steps * 0.2 or i > steps * 0.8:
                pause = random.uniform(0.001, 0.003)
            else:
                pause = random.uniform(0.0005, 0.002)
            
            path.append((x, y, pause))
        
        return path
    
    @staticmethod
    def zigzag_path(start, end):
        """Đi zigzag từ A đến B"""
        path = []
        segments = random.randint(4, 7)
        amplitude = random.uniform(20, 50)
        
        dx = (end[0] - start[0]) / segments
        dy = (end[1] - start[1]) / segments
        
        for i in range(segments + 1):
            if i == 0:
                x, y = start
            elif i == segments:
                x, y = end
            else:
                x = start[0] + dx * i
                offset = amplitude if i % 2 == 0 else -amplitude
                y = start[1] + dy * i + offset
            
            pause = random.uniform(0.005, 0.015)
            path.append((x, y, pause))
        
        return path
    
    @staticmethod
    def random_waypoints_path(start, end):
        """Đi qua nhiều waypoint ngẫu nhiên"""
        path = []
        waypoints = random.randint(3, 6)
        
        path.append((start[0], start[1], random.uniform(0.001, 0.003)))
        
        for _ in range(waypoints):
            x = random.uniform(min(start[0], end[0]) - 50, max(start[0], end[0]) + 50)
            y = random.uniform(min(start[1], end[1]) - 50, max(start[1], end[1]) + 50)
            pause = random.uniform(0.005, 0.02)
            path.append((x, y, pause))
        
        path.append((end[0], end[1], random.uniform(0.001, 0.003)))
        
        return path
    
    @staticmethod
    def get_random_path(start, end):
        """Random chọn 1 trong 3 styles phổ biến nhất"""
        styles = [
            HumanMouseMovement.bezier_path,
            HumanMouseMovement.zigzag_path,
            HumanMouseMovement.random_waypoints_path,
        ]
        
        style_func = random.choice(styles)
        return style_func(start, end)


# ============================================================
# SELENIUM HUMAN ACTIONS
# ============================================================

class SeleniumHumanActions:
    """Class chứa các hành động human-like cho Selenium với mouse movement erratic"""
    
    def __init__(self, driver):
        """
        Initialize with Selenium WebDriver
        :param driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.actions = ActionChains(driver)
    
    # ============================================================
    # 1. MOVE MOUSE TO ELEMENT (HUMAN-LIKE)
    # ============================================================
    def move_mouse_to_element(self, element=None, duration=0.5):
        """
        Di chuyển chuột đến element với đường đi erratic như người thật
        :param element: WebElement hoặc None (random element)
        :param duration: Thời gian di chuyển (giây)
        :return: True nếu thành công
        """
        try:
            if element is None:
                # Random chọn element trên page
                elements = self.driver.find_elements(By.XPATH, "//*[@href or @onclick]")
                if not elements:
                    return False
                element = random.choice(elements)
            
            # Get current mouse position (giả sử từ center màn hình)
            viewport_width = self.driver.execute_script("return window.innerWidth")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            start = (viewport_width / 2, viewport_height / 2)
            
            # Get element position
            location = element.location
            size = element.size
            end = (location['x'] + size['width'] / 2, location['y'] + size['height'] / 2)
            
            # Generate human-like path
            path = HumanMouseMovement.get_random_path(start, end)
            
            # Execute movement
            for x, y, pause in path:
                # Di chuyển bằng JavaScript (vì ActionChains không support intermediate points)
                self.driver.execute_script(
                    "var event = new MouseEvent('mousemove', {clientX: arguments[0], clientY: arguments[1]}); "
                    "document.elementFromPoint(arguments[0], arguments[1])?.dispatchEvent(event);",
                    x, y
                )
                time.sleep(pause)
            
            # Finally move to element using ActionChains
            self.actions.move_to_element(element).perform()
            time.sleep(duration * 0.2)
            
            return True
        except Exception as e:
            print(f"[SELENIUM] move_mouse_to_element error: {e}")
            return False
    
    # ============================================================
    # 2. CLICK ELEMENT (WITH HUMAN-LIKE MOVEMENT)
    # ============================================================
    def click_element(self, element=None, delay_before=0.3, delay_after=0.5):
        """
        Click vào element với delay và mouse movement human-like
        :param element: WebElement hoặc None (random clickable)
        :param delay_before: Delay trước khi click
        :param delay_after: Delay sau khi click
        :return: True nếu thành công
        """
        try:
            time.sleep(delay_before)
            
            if element is None:
                # Random chọn clickable element
                clickable = self.driver.find_elements(By.XPATH, "//a[@href] | //button")
                if not clickable:
                    return False
                element = random.choice(clickable)
            
            # Scroll element vào view trước
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
            time.sleep(0.3)
            
            # Move mouse to element with human-like path
            self.move_mouse_to_element(element, duration=random.uniform(0.3, 0.7))
            
            # Hover một chút trước khi click (human behavior)
            time.sleep(random.uniform(0.1, 0.3))
            
            # Click
            element.click()
            time.sleep(delay_after)
            return True
        except Exception as e:
            print(f"[SELENIUM] click_element error: {e}")
            return False
    
    # ============================================================
    # 3. CLICK RANDOM LINK
    # ============================================================
    def click_random_link(self, max_attempts=3):
        """
        Click vào link ngẫu nhiên trên page
        :param max_attempts: Số lần thử tối đa
        :return: True nếu thành công
        """
        for _ in range(max_attempts):
            try:
                links = self.driver.find_elements(By.TAG_NAME, "a")
                valid_links = [link for link in links if link.get_attribute("href") and link.is_displayed()]
                
                if not valid_links:
                    return False
                
                link = random.choice(valid_links)
                return self.click_element(link, delay_before=0.5, delay_after=1.0)
            except:
                continue
        return False
    
    # ============================================================
    # 4. SCROLL PAGE SMOOTHLY
    # ============================================================
    def scroll_page(self, direction="down", distance=300, duration=1.0):
        """
        Scroll trang smooth như người dùng thật
        :param direction: "up" hoặc "down"
        :param distance: Khoảng cách scroll (pixels)
        :param duration: Thời gian scroll
        :return: True
        """
        try:
            scroll_amount = distance if direction == "down" else -distance
            steps = int(duration * 10)  # 10 steps per second
            step_distance = scroll_amount / steps
            
            for _ in range(steps):
                self.driver.execute_script(f"window.scrollBy(0, {step_distance});")
                time.sleep(duration / steps)
            
            return True
        except Exception as e:
            print(f"[SELENIUM] scroll_page error: {e}")
            return False
    
    # ============================================================
    # 5. SCROLL TO RANDOM POSITION
    # ============================================================
    def scroll_to_random_position(self):
        """
        Scroll đến vị trí ngẫu nhiên trong page
        :return: True
        """
        try:
            page_height = self.driver.execute_script("return document.body.scrollHeight")
            random_position = random.randint(0, page_height)
            
            self.driver.execute_script(f"window.scrollTo({{top: {random_position}, behavior: 'smooth'}});")
            time.sleep(random.uniform(0.5, 1.5))
            return True
        except Exception as e:
            print(f"[SELENIUM] scroll_to_random_position error: {e}")
            return False
    
    # ============================================================
    # 6. HOVER OVER ELEMENT (HUMAN-LIKE)
    # ============================================================
    def hover_element(self, element=None, duration=1.0):
        """
        Hover chuột lên element với mouse path erratic
        :param element: WebElement hoặc None (random)
        :param duration: Thời gian hover
        :return: True nếu thành công
        """
        try:
            if element is None:
                elements = self.driver.find_elements(By.XPATH, "//*[@href or @onclick or @onmouseover]")
                if not elements:
                    return False
                element = random.choice(elements)
            
            # Move with human-like path
            self.move_mouse_to_element(element, duration=duration * 0.5)
            
            # Hover and pause
            self.actions.move_to_element(element).pause(duration * 0.5).perform()
            return True
        except Exception as e:
            print(f"[SELENIUM] hover_element error: {e}")
            return False
    
    # ============================================================
    # 7. TYPE TEXT WITH HUMAN SPEED
    # ============================================================
    def type_text(self, element, text, typing_speed=0.1):
        """
        Gõ text với tốc độ như người thật
        :param element: Input element
        :param text: Text cần gõ
        :param typing_speed: Tốc độ gõ (giây/ký tự)
        :return: True nếu thành công
        """
        try:
            element.clear()
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(typing_speed * 0.5, typing_speed * 1.5))
            return True
        except Exception as e:
            print(f"[SELENIUM] type_text error: {e}")
            return False
    
    # ============================================================
    # 8. RANDOM MOUSE MOVEMENT (ERRATIC)
    # ============================================================
    def random_mouse_movement(self, num_moves=3):
        """
        Di chuyển chuột ngẫu nhiên với path erratic để mô phỏng user đang đọc
        :param num_moves: Số lần di chuyển
        :return: True
        """
        try:
            viewport_width = self.driver.execute_script("return window.innerWidth")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            current_x = viewport_width / 2
            current_y = viewport_height / 2
            
            for _ in range(num_moves):
                # Random target position
                target_x = random.randint(100, viewport_width - 100)
                target_y = random.randint(100, viewport_height - 100)
                
                # Generate human-like path
                path = HumanMouseMovement.bezier_path((current_x, current_y), (target_x, target_y))
                
                # Execute movement
                for x, y, pause in path:
                    self.driver.execute_script(
                        "var event = new MouseEvent('mousemove', {clientX: arguments[0], clientY: arguments[1]}); "
                        "document.elementFromPoint(arguments[0], arguments[1])?.dispatchEvent(event);",
                        x, y
                    )
                    time.sleep(pause)
                
                current_x, current_y = target_x, target_y
                time.sleep(random.uniform(0.3, 0.8))
            
            return True
        except Exception as e:
            print(f"[SELENIUM] random_mouse_movement error: {e}")
            return False
    
    # ============================================================
    # 9-20: GIỮ NGUYÊN CÁC METHODS KHÁC (KHÔNG LIÊN QUAN MOUSE)
    # ============================================================
    
    def read_page(self, min_seconds=3, max_seconds=10):
        """Dừng lại như đang đọc nội dung"""
        duration = random.uniform(min_seconds, max_seconds)
        print(f"[SELENIUM] Reading page for {duration:.1f}s...")
        time.sleep(duration)
        return True
    
    def scroll_to_bottom(self, num_pauses=3):
        """Scroll từ từ xuống cuối trang"""
        try:
            page_height = self.driver.execute_script("return document.body.scrollHeight")
            current_position = 0
            step = page_height / (num_pauses + 1)
            
            for i in range(num_pauses + 1):
                target = int(step * (i + 1))
                distance = target - current_position
                
                self.scroll_page("down", distance, duration=random.uniform(1.0, 2.0))
                current_position = target
                
                # Pause để đọc
                time.sleep(random.uniform(1.5, 3.5))
            
            return True
        except Exception as e:
            print(f"[SELENIUM] scroll_to_bottom error: {e}")
            return False
    
    def go_back(self, delay=1.0):
        """Quay lại trang trước"""
        try:
            self.driver.back()
            time.sleep(delay)
            return True
        except Exception as e:
            print(f"[SELENIUM] go_back error: {e}")
            return False
    
    def go_forward(self, delay=1.0):
        """Tiến tới trang sau"""
        try:
            self.driver.forward()
            time.sleep(delay)
            return True
        except Exception as e:
            print(f"[SELENIUM] go_forward error: {e}")
            return False
    
    def refresh_page(self, delay=2.0):
        """Refresh trang hiện tại"""
        try:
            self.driver.refresh()
            time.sleep(delay)
            return True
        except Exception as e:
            print(f"[SELENIUM] refresh_page error: {e}")
            return False
    
    def switch_to_tab(self, tab_index=None):
        """Chuyển sang tab khác"""
        try:
            tabs = self.driver.window_handles
            if len(tabs) <= 1:
                return False
            
            if tab_index is None:
                tab_index = random.randint(0, len(tabs) - 1)
            
            self.driver.switch_to.window(tabs[tab_index])
            time.sleep(random.uniform(0.5, 1.5))
            return True
        except Exception as e:
            print(f"[SELENIUM] switch_to_tab error: {e}")
            return False
    
    def open_new_tab(self, url=None):
        """Mở tab mới"""
        try:
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            if url:
                self.driver.get(url)
                time.sleep(random.uniform(1.0, 2.0))
            
            return True
        except Exception as e:
            print(f"[SELENIUM] open_new_tab error: {e}")
            return False
    
    def close_current_tab(self):
        """Đóng tab hiện tại"""
        try:
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                time.sleep(random.uniform(0.5, 1.0))
                return True
            return False
        except Exception as e:
            print(f"[SELENIUM] close_current_tab error: {e}")
            return False
    
    def zoom_page(self, zoom_level=1.0):
        """Zoom trang web"""
        try:
            self.driver.execute_script(f"document.body.style.zoom='{zoom_level}'")
            time.sleep(0.5)
            return True
        except Exception as e:
            print(f"[SELENIUM] zoom_page error: {e}")
            return False
    
    def right_click(self, element=None):
        """Click chuột phải vào element"""
        try:
            if element is None:
                elements = self.driver.find_elements(By.XPATH, "//*[not(self::script)]")
                if not elements:
                    return False
                element = random.choice(elements[:20])
            
            self.actions.context_click(element).perform()
            time.sleep(random.uniform(0.5, 1.0))
            
            # Press ESC để đóng context menu
            self.actions.send_keys(Keys.ESCAPE).perform()
            return True
        except Exception as e:
            print(f"[SELENIUM] right_click error: {e}")
            return False
    
    def drag_and_drop(self, source_element, target_element):
        """Drag element từ source đến target"""
        try:
            self.actions.drag_and_drop(source_element, target_element).perform()
            time.sleep(random.uniform(0.5, 1.5))
            return True
        except Exception as e:
            print(f"[SELENIUM] drag_and_drop error: {e}")
            return False
    
    def wait_and_click(self, by, value, timeout=10):
        """Đợi element xuất hiện rồi click"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            time.sleep(random.uniform(0.3, 0.8))
            return self.click_element(element)
        except TimeoutException:
            print(f"[SELENIUM] Timeout waiting for element: {value}")
            return False
        except Exception as e:
            print(f"[SELENIUM] wait_and_click error: {e}")
            return False
    
    # ============================================================
    # BONUS: EXECUTE RANDOM ACTION
    # ============================================================
    def execute_random_action(self):
        """
        Thực thi 1 hành động ngẫu nhiên từ danh sách
        :return: Action name
        """
        actions = [
            ("scroll", lambda: self.scroll_page("down", random.randint(200, 500))),
            ("read", lambda: self.read_page(2, 5)),
            ("move_mouse", lambda: self.random_mouse_movement(2)),
            ("hover", lambda: self.hover_element()),
            ("click_link", lambda: self.click_random_link()),
            ("scroll_to_random", lambda: self.scroll_to_random_position()),
        ]
        
        action_name, action_func = random.choice(actions)
        try:
            action_func()
            return action_name
        except:
            return "failed"
