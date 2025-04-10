from tkinter import ttk, filedialog as fd
from tkinter import Tk, Frame, Menu
from tkinter.messagebox import showinfo
from views.menu_top import MenuTop
from views.frame_actions import FrameActions
from views.frame_list_actions import FrameListActions
import sys

windowApp = Tk()
windowApp.title('Tom Sam Automation')
windowApp.geometry('1000x600')

MenuTop(windowApp)

# row 1
windowApp.frame_list_actions = FrameListActions(windowApp)

# row 0
windowApp.frame_actions = FrameActions(windowApp)

def exit(event):
    windowApp.quit() # if you want to bring it back
    sys.exit() # if you want to exit the entire thing

if __name__ == '__main__':
    windowApp.bind('<Escape>', exit)
    windowApp.mainloop()