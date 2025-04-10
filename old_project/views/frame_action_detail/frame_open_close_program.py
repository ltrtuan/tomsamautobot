from textwrap import fill
from tkinter import ttk, Text
import tkinter as tk
from tkinter.tix import COLUMN
import customtkinter
from views.frame_action_detail.partial_bottom import PartialBottom
from views.frame_action_detail.partial_top import PartialTop
from controllers.crud_frame_fields import CrudFrameFields


class FrameOpenCloseProgram(ttk.LabelFrame):
    def __init__(self, windowPopup, windowApp, dictValues):
        super().__init__()
        self.windowPopup = windowPopup
        self.windowApp = windowApp
        self.dictValues = dictValues
        self.partialTop = PartialTop(windowApp, windowPopup, 0, 0, self, dictValues)
        
        
        ############################## FRAME SELECT IMAGE ###############################
        frameInputText = ttk.LabelFrame(windowPopup, text="Open & Close Program")
        frameInputText.grid(column=0, row=1, sticky='nswe', pady=5,padx=5)        
        
        lbBrowseImages = ttk.Label(frameInputText, text = "Use <VARIABLE>.", justify="left", width=100)
        lbBrowseImages.grid(column=0, row=0, padx=5, pady=5, sticky = 'nswe', columnspan=2) 
        
        btnBrowseFolder = customtkinter.CTkButton(frameInputText, text="Browse Program", text_color="#fff", fg_color="#ffad5e", hover_color="#000", font=('Arial', 15, 'bold'),command=lambda: CrudFrameFields.browse_file(self, ('exe')))
        btnBrowseFolder.grid(column=0, row=1, padx=5, pady=5)
        
        self.txtImagesVar = tk.StringVar()
        self.txtImagesVar.set(dictValues['images'])
        self.txtImages = ttk.Entry(
            frameInputText,
            width=30,
            textvariable=self.txtImagesVar,
            font="Arial"
        )        
        self.txtImages.grid(column=1, row=1, padx=5, pady=5, sticky = 'nwes', columnspan=3)
        
        frameInputText.columnconfigure(1,weight=1)
        
        lbContentFile = ttk.Label(frameInputText, text = "Arguments. Ex: for Firefox: add more # -P 'My Profile' -no-remote #", justify="left", width=100)
        lbContentFile.grid(column=0, row=2, padx=5, pady=5, sticky = 'nswe', columnspan=2) 
        self.txtContentFileVar = tk.StringVar()
        self.txtContentFileVar.set(dictValues['content_file'])
        self.txtContentFile = ttk.Entry(
            frameInputText,
            width=30,
            textvariable=self.txtContentFileVar,
            font="Arial"
        )       
        self.txtContentFile.grid(column=0, row=3, padx=5, pady=5, sticky = 'nwes', columnspan=2)
        
        self.radioSingleClickVar = tk.StringVar()
        self.radioSingleClickVar.set(dictValues['click'] if dictValues['click'] else "1")
        radioSingleClick = customtkinter.CTkRadioButton(master=frameInputText, text="Open Program", variable=self.radioSingleClickVar, value="1")       
        radioSingleClick.grid(column=0, row=4, padx=(5,50), pady=5, sticky = 'nwes')        
        
        radioDoubleClick = customtkinter.CTkRadioButton(master=frameInputText, text="Close Program", variable=self.radioSingleClickVar, value="2")       
        radioDoubleClick.grid(column=1, row=4, padx=(5,50), pady=5, sticky = 'nwes')
        
        fieldsNeedToSave = {}       
      
        
        ######################################################### FIELDS NEED TO SAVE ################################################################
        fieldsNeedToSave.update({'images' : self.txtImagesVar, 'content_file' : self.txtContentFileVar, 'click' : self.radioSingleClickVar})
        PartialBottom(windowApp, windowPopup, 0, 3, self, dictValues, fieldsNeedToSave)