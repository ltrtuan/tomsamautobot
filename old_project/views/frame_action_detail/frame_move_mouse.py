from textwrap import fill
from tkinter import ttk, Text
import tkinter as tk
import customtkinter
from views.frame_action_detail.partial_bottom import PartialBottom
from views.frame_action_detail.partial_top import PartialTop
from controllers.crud_frame_fields import CrudFrameFields

class FrameMoveMouse(ttk.LabelFrame):
    def __init__(self, windowPopup, windowApp, dictValues):
        super().__init__()
        self.windowPopup = windowPopup
        self.windowApp = windowApp
        self.dictValues = dictValues
        self.partialTop = PartialTop(windowApp, windowPopup, 0, 0, self, dictValues)
        frameMain = ttk.LabelFrame(windowPopup, text="Move Mouse Settings")
        frameMain.grid(column=0, row=1, sticky='nswe', pady=5,padx=5)
        
        windowPopup.columnconfigure(0,weight=1)
        
        lbX = ttk.Label(frameMain, text = "X Coordinate", justify = "right")
        lbX.grid(column=0, row=0, padx=5, pady=5, sticky = 'ne') 
        self.txtXVar = tk.StringVar()
        self.txtXVar.set(dictValues['x'])
        txtX = ttk.Entry(
            frameMain,
            width=30,
            textvariable=self.txtXVar,
            font="Arial"
        )       
        txtX.grid(column=1, row=0, padx=5, pady=5, sticky = 'nwes')
        
        lbY = ttk.Label(frameMain, text = "Y Coordinate", justify = "right")
        lbY.grid(column=2, row=0, padx=5, pady=5, sticky = 'ne')
        self.txtYVar = tk.StringVar()
        self.txtYVar.set(dictValues['y'])
        txtY = ttk.Entry(
            frameMain,
            width=30,
            textvariable=self.txtYVar,
            font="Arial"
        )       
        txtY.grid(column=3, row=0, padx=5, pady=5, sticky = 'nwes')
        
        frameMain.columnconfigure(1,weight=1)
        frameMain.columnconfigure(3,weight=1)
        

        lbWidth = ttk.Label(frameMain, text = "Width Area", justify = "right")
        lbWidth.grid(column=0, row=1, padx=5, pady=5, sticky = 'ne')
        self.txtWidthVar = tk.StringVar()
        self.txtWidthVar.set(dictValues['width'])
        txtWidth = ttk.Entry(
            frameMain,
            width=30,
            textvariable=self.txtWidthVar,
            font="Arial"
        )       
        txtWidth.grid(column=1, row=1, padx=5, pady=5, sticky = 'nwes')
        
        lbHeight = ttk.Label(frameMain, text = "Height Area", justify = "right")
        lbHeight.grid(column=2, row=1, padx=5, pady=5, sticky = 'ne')
        self.txtHeightVar = tk.StringVar()
        self.txtHeightVar.set(dictValues['height'])
        txtHeight = ttk.Entry(
            frameMain,
            width=30,
            textvariable=self.txtHeightVar,
            font="Arial"
        )       
        txtHeight.grid(column=3, row=1, padx=5, pady=5, sticky = 'nwes')
        
        fieldsNeedToSave = {'x' : self.txtXVar, 'y' : self.txtYVar, 'width' : self.txtWidthVar, 'height' : self.txtHeightVar}
        btnGetArea = customtkinter.CTkButton(frameMain, text="Get Area", text_color="#fff", fg_color="#ffad5e", hover_color="#000", font=('Arial', 15, 'bold'),command=lambda: CrudFrameFields.get_area(self, fieldsNeedToSave = fieldsNeedToSave))
        btnGetArea.grid(column=0, row=2, padx=5, pady=5, columnspan=4)
        
        ############################## FRAME CLICK ###############################
        frameClick = ttk.LabelFrame(frameMain, borderwidth=0)
        frameClick.grid(column=0, row=3, sticky='nswe', pady=5,padx=5, columnspan=4)        
        
        self.chkClickIfHandVar = tk.StringVar()
        self.chkClickIfHandVar.set(dictValues['click_if_hand'])
        chkClickIfHand = customtkinter.CTkCheckBox(master=frameClick, text="Click If Hand", variable=self.chkClickIfHandVar, onvalue="1", offvalue="0")       
        chkClickIfHand.grid(column=0, row=0, padx=(5,50), pady=5, sticky = 'nwes')
        
        self.radioSingleClickVar = tk.StringVar()
        self.radioSingleClickVar.set(dictValues['click'])
        radioSingleClick = customtkinter.CTkRadioButton(master=frameClick, text="Single Click", variable=self.radioSingleClickVar, value="1")       
        radioSingleClick.grid(column=1, row=0, padx=(5,50), pady=5, sticky = 'nwes')        
        
        radioDoubleClick = customtkinter.CTkRadioButton(master=frameClick, text="Double Click", variable=self.radioSingleClickVar, value="2")       
        radioDoubleClick.grid(column=2, row=0, padx=(5,50), pady=5, sticky = 'nwes')
        
        self.chkBreakIfHandVar = tk.StringVar()
        self.chkBreakIfHandVar.set(dictValues['break'])
        chkBreakIfHand = customtkinter.CTkCheckBox(master=frameClick, text="Break If Hand", variable=self.chkBreakIfHandVar, onvalue="1", offvalue="0")       
        chkBreakIfHand.grid(column=3, row=0, padx=5, pady=5, sticky = 'nwes')
        ############################## FRAME CLICK ###############################
        
        ######################################################### FIELDS NEED TO SAVE ################################################################
        fieldsNeedToSave.update({'click_if_hand' : self.chkClickIfHandVar, 'click' : self.radioSingleClickVar, 'break' : self.chkBreakIfHandVar})
        PartialBottom(windowApp, windowPopup, 0, 3, self, dictValues, fieldsNeedToSave)