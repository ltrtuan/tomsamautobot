from textwrap import fill
from tkinter import ttk, Text
import tkinter as tk
import customtkinter
from views.frame_action_detail.partial_bottom import PartialBottom
from views.frame_action_detail.partial_top import PartialTop
from controllers.crud_frame_fields import CrudFrameFields


class FrameReadFile(ttk.LabelFrame):
    def __init__(self, windowPopup, windowApp, dictValues):
        super().__init__()
        self.windowPopup = windowPopup
        self.windowApp = windowApp
        self.dictValues = dictValues
        self.partialTop = PartialTop(windowApp, windowPopup, 0, 0, self, dictValues)
        
        
        ############################## FRAME SELECT IMAGE ###############################
        frameInputText = ttk.LabelFrame(windowPopup, text="Get Line In File")
        frameInputText.grid(column=0, row=1, sticky='nswe', pady=5,padx=5)        
        
        lbBrowseImages = ttk.Label(frameInputText, text = "Use <VARIABLE>. Support files: txt, csv.", justify="left", width=100)
        lbBrowseImages.grid(column=0, row=0, padx=5, pady=5, sticky = 'nswe', columnspan=2) 
        
        btnBrowseFolder = customtkinter.CTkButton(frameInputText, text="Browse File", text_color="#fff", fg_color="#ffad5e", hover_color="#000", font=('Arial', 15, 'bold'),command=lambda: CrudFrameFields.browse_file(self,('txt','csv')))
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
        
        fieldsNeedToSave = {}       
        
        ############################## FRAME CLICK ###############################      

        frameClick = ttk.LabelFrame(windowPopup, borderwidth=0)
        frameClick.grid(column=0, row=2, sticky='nswe', pady=5,padx=5, columnspan=3)        
        
        self.chkClickIfHandVar = tk.StringVar()
        self.chkClickIfHandVar.set(dictValues['click_if_hand'])
        chkClickIfHand = customtkinter.CTkCheckBox(master=frameClick, text="Check if want to random Press and Copy text", variable=self.chkClickIfHandVar, onvalue="1", offvalue="0")       
        chkClickIfHand.grid(column=0, row=0, padx=(5,50), pady=5, sticky = 'nwes', columnspan=3)
        
        self.chkLoopMultipleVar = tk.StringVar()
        self.chkLoopMultipleVar.set(dictValues['loop_multiple'])
        chkLoopMultiple = customtkinter.CTkCheckBox(master=frameClick, text="Remove selected line (only for rotate lines option)", variable=self.chkLoopMultipleVar, onvalue="1", offvalue="0")       
        chkLoopMultiple.grid(column=0, row=1, padx=5, pady=5, sticky = 'nwes', columnspan=3)
        
       
        self.radioSingleClickVar = tk.StringVar()
        self.radioSingleClickVar.set(dictValues['click'] if dictValues['click'] else "1")
        radioNormal = customtkinter.CTkRadioButton(master=frameClick, text="Normal", variable=self.radioSingleClickVar, value="1")       
        radioNormal.grid(column=0, row=2, padx=(5,50), pady=5, sticky = 'nwes')        
        
        radioRotateLines = customtkinter.CTkRadioButton(master=frameClick, text="Rotate Lines", variable=self.radioSingleClickVar, value="2")       
        radioRotateLines.grid(column=1, row=2, padx=(5,50), pady=5, sticky = 'nwes')
        
        radioRandomLines = customtkinter.CTkRadioButton(master=frameClick, text="Random Lines", variable=self.radioSingleClickVar, value="3")       
        radioRandomLines.grid(column=2, row=2, padx=(5,50), pady=5, sticky = 'nwes')
       
        ############################## FRAME CLICK ###############################
        
        ######################################################### FIELDS NEED TO SAVE ################################################################
        fieldsNeedToSave.update({'click_if_hand' : self.chkClickIfHandVar, 'images' : self.txtImagesVar, 'loop_multiple' : self.chkLoopMultipleVar, 'click' : self.radioSingleClickVar})
        PartialBottom(windowApp, windowPopup, 0, 3, self, dictValues, fieldsNeedToSave)