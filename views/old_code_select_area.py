from re import S
from textwrap import fill
from time import sleep
from tkinter import ttk, Text,Toplevel
import tkinter as tk
import customtkinter
import time
from pynput.mouse import Listener
import mss.tools
from tkinter.filedialog import asksaveasfilename

class SelectArea():
    start_x = None
    start_y = None
    end_x = None
    end_y = None
    #fieldsNeedToSave : only 4 variables: width, height, width, height
    def __init__(self, windowApp, windowPopup, **kwargs):
        super().__init__()
        ########################## Set Variables ##########################
        self.windowApp = windowApp
        self.windowPopup = windowPopup
        
        if 'fieldsNeedToSave' in kwargs:
            fieldsNeedToSave = kwargs['fieldsNeedToSave']
            self.txtXVar = fieldsNeedToSave['x']
            self.txtYVar = fieldsNeedToSave['y']
            self.txtWidthVar = fieldsNeedToSave['width']
            self.txtHeightVar = fieldsNeedToSave['height']
         
        self.captureImage = False
        if 'captureImage' in kwargs:
            self.captureImage = kwargs['captureImage']
            
        FrameGetArea = Toplevel(self.windowPopup)
        #Get the current screen width and height
        screen_width = windowPopup.winfo_screenwidth()
        screen_height = windowPopup.winfo_screenheight()

        root_geometry = str(screen_width) + 'x' + str(screen_height) #Creates a geometric string argument
        FrameGetArea.geometry(root_geometry) #Sets the geometry string value
       
        FrameGetArea.overrideredirect(True)
        FrameGetArea.overrideredirect(False)
        FrameGetArea.attributes("-fullscreen", True)
        FrameGetArea.wait_visibility(FrameGetArea)
        FrameGetArea.wm_attributes("-alpha", 0.25)#Set windows transparent
        FrameGetArea.attributes('-topmost', 'true')
        windowPopup.withdraw()
        windowApp.withdraw()

        self.isClick = False
        self.rects = []
        self.canvas = tk.Canvas(FrameGetArea, width=screen_width, height=screen_height)#Crate canvas
        self.canvas.config(cursor="cross")#Change mouse pointer to cross       
        self.canvas.grid(column=0, row=0)
        FrameGetArea.columnconfigure(0,weight=1)
        FrameGetArea.rowconfigure(0,weight=1)
        self.FrameGetArea = FrameGetArea
        # Collect events until released
        time.sleep( 0.5 )
        # with Listener(on_move=self.on_move, on_click=self.on_click) as listener:
        #     windowPopup.mainloop()#Start tkinter window
        #     listener.join()
        self.listener = Listener(
            on_click=self.on_click,
            on_move=self.on_move
            )
        self.listener.start()
        
        FrameGetArea.bind('<Escape>', self.exit)
        
    def exit(self, event):
        global start_x,start_y,end_x,end_y
        if(self.captureImage == True):   
            time.sleep(0.5)           
            self.FrameGetArea.wm_attributes("-alpha", 0)
            with mss.mss() as sct:                        
                # The screen part to capture
                monitor = {"top": int(start_y), "left": int(start_x), "width": int(end_x - start_x), "height": int(end_y - start_y)}
            
                # Grab the data
                sct_img = sct.grab(monitor)

                # Save to the picture file
                data = [("PNG Files", "*.png")] # look up only PNG and JPG files
                filename = asksaveasfilename(parent=self.windowPopup, filetypes=data, defaultextension=data)
                if filename:
                    mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)
            time.sleep(0.5)
            
        self.windowPopup.deiconify()
        self.windowApp.deiconify()
        
        if(self.captureImage == False):
            self.txtXVar.set(start_x)
            self.txtYVar.set(start_y)
            self.txtWidthVar.set(end_x - start_x)
            self.txtHeightVar.set(end_y - start_y)
        
        self.listener.stop()
        self.FrameGetArea.destroy() # if you want to bring it back
          
    #Get and print coordinates
    def on_move(self, x, y):       
        if(self.isClick):
            if len(self.rects) > 0 and self.canvas.find_all():
                self.canvas.delete(self.rects.pop())
            self.rects.append(self.canvas.create_rectangle(start_x, start_y, x, y, outline="red", width = 2))#Draw a rectangle.
        
    #Start and End mouse position
    def on_click(self, x, y, button, pressed):    
        global start_x,start_y,end_x,end_y
        btn = button.name
        if len(self.rects) > 0 and self.canvas.find_all():
            self.canvas.delete(self.rects.pop())
        if btn == "left":
            #Left button pressed then continue
            if pressed:
                start_x = x
                start_y = y
                self.isClick = True
            else:
                if len(self.rects) > 0 and self.canvas.find_all():
                    self.canvas.delete(self.rects.pop())
                self.rects.append(self.canvas.create_rectangle(start_x, start_y, x, y, outline="red", width = 2))#Draw a rectangle.
                end_x = x
                end_y = y
                self.isClick = False