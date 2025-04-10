from textwrap import fill
from tkinter import ttk, Text
import tkinter as tk
import customtkinter
from views.frame_action_detail.partial_bottom import PartialBottom
from views.frame_action_detail.partial_top import PartialTop
from controllers.crud_frame_fields import CrudFrameFields


class FrameCheckProgram(ttk.LabelFrame):
    def __init__(self, windowPopup, windowApp, dictValues):
        super().__init__()
        self.windowPopup = windowPopup
        self.windowApp = windowApp
        self.dictValues = dictValues
        self.partialTop = PartialTop(windowApp, windowPopup, 0, 0, self, dictValues)
        
        
        ############################## FRAME SELECT IMAGE ###############################
        frameInputText = ttk.LabelFrame(windowPopup, text="Check Exist, Current Program")
        frameInputText.grid(column=0, row=1, sticky='nswe', pady=5,padx=5)        
        
        lbBrowseImages = ttk.Label(frameInputText, text = "Separate multiple texts by semicolon (;). Use <VARIABLE>.", justify="left", width=100)
        lbBrowseImages.grid(column=0, row=0, padx=5, pady=5, sticky = 'nswe', columnspan=3) 
        self.txtImagesVar = tk.StringVar()
        self.txtImagesVar.set(dictValues['images'])
        self.txtImages = Text(
            frameInputText,
            width=30,
            height=3,
            padx=5,
            pady=5,
            font="Arial"
        )
        self.txtImages.insert(tk.END, self.txtImagesVar.get())
        self.txtImages.grid(column=0, row=1, padx=5, pady=5, sticky = 'nwes')
        self.txtImages.bind('<KeyRelease>', lambda event:CrudFrameFields.update_txtimages(self))
        frameInputText.columnconfigure(0,weight=1)
        
        self.chkLoopMultipleVar = tk.StringVar()
        self.chkLoopMultipleVar.set(dictValues['loop_multiple'])
        chkLoopMultiple = customtkinter.CTkCheckBox(master=frameInputText, text="Check if want to loop multiple values (sepa by ;) by themselves", variable=self.chkLoopMultipleVar, onvalue="1", offvalue="0")       
        chkLoopMultiple.grid(column=0, row=2, padx=5, pady=5, sticky = 'nwes', columnspan=3)        
       
        
        fieldsNeedToSave = {}
       
        
        ######################################################### FIELDS NEED TO SAVE ################################################################
        fieldsNeedToSave.update({'images' : self.txtImagesVar, 'loop_multiple' : self.chkLoopMultipleVar})
        PartialBottom(windowApp, windowPopup, 0, 3, self, dictValues, fieldsNeedToSave)