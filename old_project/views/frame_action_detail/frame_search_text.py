from textwrap import fill
from tkinter import ttk, Text
import tkinter as tk
import customtkinter
from views.frame_action_detail.partial_bottom import PartialBottom
from views.frame_action_detail.partial_top import PartialTop
from controllers.crud_frame_fields import CrudFrameFields


class FrameSearchText(ttk.LabelFrame):
    def __init__(self, windowPopup, windowApp, dictValues):
        super().__init__()
        self.windowPopup = windowPopup
        self.windowApp = windowApp
        self.dictValues = dictValues
        self.partialTop = PartialTop(windowApp, windowPopup, 0, 0, self, dictValues)
        
        
        ############################## FRAME SELECT IMAGE ###############################
        frameSelectImage = ttk.LabelFrame(windowPopup, text="Input Text")
        frameSelectImage.grid(column=0, row=1, sticky='nswe', pady=5,padx=5)        
        
        lbBrowseImages = ttk.Label(frameSelectImage, text = "Separate multiple texts by semicolon (;). Use <VARIABLE>", justify="left", width=100)
        lbBrowseImages.grid(column=0, row=0, padx=5, pady=5, sticky = 'nswe', columnspan=3) 
        self.txtImagesVar = tk.StringVar()
        self.txtImagesVar.set(dictValues['images'])
        self.txtImages = Text(
            frameSelectImage,
            width=30,
            height=3,
            padx=5,
            pady=5,
            font="Arial"
        )
        self.txtImages.insert(tk.END, self.txtImagesVar.get())
        self.txtImages.grid(column=0, row=1, padx=5, pady=5, sticky = 'nwes')
        self.txtImages.bind('<KeyRelease>', lambda event:CrudFrameFields.update_txtimages(self))
        frameSelectImage.columnconfigure(0,weight=1)
        
        self.chkLoopMultipleVar = tk.StringVar()
        self.chkLoopMultipleVar.set(dictValues['loop_multiple'])
        chkLoopMultiple = customtkinter.CTkCheckBox(master=frameSelectImage, text="Check if want to loop multiple values (sepa by ;) by themselves", variable=self.chkLoopMultipleVar, onvalue="1", offvalue="0")       
        chkLoopMultiple.grid(column=0, row=2, padx=5, pady=5, sticky = 'nwes')
        
        
        ############################## FRAME SELECT IMAGE ###############################
        
        
        frameMain = ttk.LabelFrame(windowPopup, text="Search Image Settings")
        frameMain.grid(column=0, row=2, sticky='nswe', pady=5,padx=5)
        
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
        # print(type(txtX).__name__)
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
        frameClick.grid(column=0, row=4, sticky='nswe', pady=5,padx=5, columnspan=4)        
        
        self.chkClickIfHandVar = tk.StringVar()
        self.chkClickIfHandVar.set(dictValues['click_if_hand'])
        chkClickIfHand = customtkinter.CTkCheckBox(master=frameClick, text="Click On Area Has Founded Text", variable=self.chkClickIfHandVar, onvalue="1", offvalue="0")       
        chkClickIfHand.grid(column=0, row=0, padx=(5,50), pady=5, sticky = 'nwes')
        
        self.radioSingleClickVar = tk.StringVar()
        self.radioSingleClickVar.set(dictValues['click'])
        radioSingleClick = customtkinter.CTkRadioButton(master=frameClick, text="Single Click", variable=self.radioSingleClickVar, value="1")       
        radioSingleClick.grid(column=1, row=0, padx=(5,50), pady=5, sticky = 'nwes')        
        
        radioDoubleClick = customtkinter.CTkRadioButton(master=frameClick, text="Double Click", variable=self.radioSingleClickVar, value="2")       
        radioDoubleClick.grid(column=2, row=0, padx=(5,50), pady=5, sticky = 'nwes')
       
        ############################## FRAME CLICK ###############################
        
        ######################################################### FIELDS NEED TO SAVE ################################################################
        fieldsNeedToSave.update({'click_if_hand' : self.chkClickIfHandVar, 'click' : self.radioSingleClickVar, 'images' : self.txtImagesVar, 'loop_multiple' : self.chkLoopMultipleVar})
        PartialBottom(windowApp, windowPopup, 0, 3, self, dictValues, fieldsNeedToSave)