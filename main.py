import tkinter as tk
from models.action_model import ActionModel
from views.action_list_view import ActionListView
from controllers.action_controller import ActionController
import config as cfg

def main():
     # Tải cấu hình
    cfg.load_config()
    # Create main window
    root = tk.Tk()
    root.title("Tom Sam Autobot")
    root.configure(bg=cfg.LIGHT_BG_COLOR)
    
    # Thiết lập kích thước cửa sổ
    window_width = 800
    window_height = 600
    
    # Tính toán vị trí ở giữa màn hình
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int((screen_width / 2) - (window_width / 2))
    center_y = int((screen_height / 2) - (window_height / 2))
    
    # Đặt kích thước và vị trí cửa sổ
    root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
    
    # Create model
    model = ActionModel()
    
    # Create view
    view = ActionListView(root)
    view.pack(fill=tk.BOTH, expand=True)
    
    # Create controller and set up
    controller = ActionController(root)
    controller.setup(model, view)
    
    # Start application
    root.mainloop()

if __name__ == "__main__":
    main()
