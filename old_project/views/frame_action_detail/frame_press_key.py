from textwrap import fill
from tkinter import ttk, Text
import tkinter as tk
import customtkinter
from views.frame_action_detail.partial_bottom import PartialBottom
from views.frame_action_detail.partial_top import PartialTop
from controllers.crud_frame_fields import CrudFrameFields


class FramePressKey(ttk.LabelFrame):
    def __init__(self, windowPopup, windowApp, dictValues):
        super().__init__()
        self.windowPopup = windowPopup
        self.windowApp = windowApp
        self.dictValues = dictValues
        self.partialTop = PartialTop(windowApp, windowPopup, 0, 0, self, dictValues)
        
        
        ############################## FRAME SELECT IMAGE ###############################
        frameInputText = ttk.LabelFrame(windowPopup, text="Press Key")
        frameInputText.grid(column=0, row=1, sticky='nswe', pady=5,padx=5)        
        
        self.radioKeyVar = tk.StringVar()
        self.radioKeyVar.set(dictValues['click'])
        ctrlKey = customtkinter.CTkRadioButton(master=frameInputText, text="CTRL", variable=self.radioKeyVar, value="1")       
        ctrlKey.grid(column=0, row=0, padx=(5,50), pady=5, sticky = 'nwes')        
        
        altKey = customtkinter.CTkRadioButton(master=frameInputText, text="ALT", variable=self.radioKeyVar, value="2")       
        altKey.grid(column=1, row=0, padx=(5,50), pady=5, sticky = 'nwes')
        
        winKey = customtkinter.CTkRadioButton(master=frameInputText, text="WIN", variable=self.radioKeyVar, value="3")       
        winKey.grid(column=2, row=0, padx=(5,50), pady=5, sticky = 'nwes')        
        
        
        self.radioKey2Var = tk.StringVar()
        self.radioKey2Var.set(dictValues['press_key'])
        
        labelSeparator = ttk.Label(frameInputText, text = "----------------------------------------------------------------------------------------", justify="left", width=100)
        labelSeparator.grid(column=0, row=1, padx=5, pady=5, sticky = 'nswe', columnspan=6) 
        
        aKey = customtkinter.CTkRadioButton(master=frameInputText, text="A", variable=self.radioKey2Var, value="1")       
        aKey.grid(column=0, row=2, padx=(5,10), pady=5, sticky = 'nwes')
        
        cKey = customtkinter.CTkRadioButton(master=frameInputText, text="C", variable=self.radioKey2Var, value="2")       
        cKey.grid(column=1, row=2, padx=(5,10), pady=5, sticky = 'nwes')
        
        vKey = customtkinter.CTkRadioButton(master=frameInputText, text="V", variable=self.radioKey2Var, value="3")       
        vKey.grid(column=2, row=2, padx=(5,10), pady=5, sticky = 'nwes')
        
        wKey = customtkinter.CTkRadioButton(master=frameInputText, text="W", variable=self.radioKey2Var, value="4")       
        wKey.grid(column=3, row=2, padx=(5,10), pady=5, sticky = 'nwes')
        
        tKey = customtkinter.CTkRadioButton(master=frameInputText, text="T", variable=self.radioKey2Var, value="5")       
        tKey.grid(column=4, row=2, padx=(5,10), pady=5, sticky = 'nwes')
        
        tKey = customtkinter.CTkRadioButton(master=frameInputText, text="D", variable=self.radioKey2Var, value="6")       
        tKey.grid(column=5, row=2, padx=(5,10), pady=5, sticky = 'nwes')

        
        #######################################################################################################################
        
        tabKey = customtkinter.CTkRadioButton(master=frameInputText, text="TAB", variable=self.radioKey2Var, value="7")       
        tabKey.grid(column=0, row=3, padx=(5,10), pady=5, sticky = 'nwes') 
        
        enterKey = customtkinter.CTkRadioButton(master=frameInputText, text="ENTER", variable=self.radioKey2Var, value="8")       
        enterKey.grid(column=1, row=3, padx=(5,10), pady=5, sticky = 'nwes')
        
        deleteKey = customtkinter.CTkRadioButton(master=frameInputText, text="DEL", variable=self.radioKey2Var, value="9")       
        deleteKey.grid(column=2, row=3, padx=(5,10), pady=5, sticky = 'nwes')
        
        f4Key = customtkinter.CTkRadioButton(master=frameInputText, text="F4", variable=self.radioKey2Var, value="10")       
        f4Key.grid(column=3, row=3, padx=(5,10), pady=5, sticky = 'nwes')
        
        ######################################################################################################################
        
        arrowUpKey = customtkinter.CTkRadioButton(master=frameInputText, text="Arrow Up", variable=self.radioKey2Var, value="11")       
        arrowUpKey.grid(column=0, row=4, padx=(5,10), pady=5, sticky = 'nwes')
        
        arrowDownKey = customtkinter.CTkRadioButton(master=frameInputText, text="Arrow Down", variable=self.radioKey2Var, value="12")       
        arrowDownKey.grid(column=1, row=4, padx=(5,10), pady=5, sticky = 'nwes')
        
        arrowLeftKey = customtkinter.CTkRadioButton(master=frameInputText, text="Arrow Left", variable=self.radioKey2Var, value="13")       
        arrowLeftKey.grid(column=2, row=4, padx=(5,10), pady=5, sticky = 'nwes')
        
        arrowRightKey = customtkinter.CTkRadioButton(master=frameInputText, text="Arrow Right", variable=self.radioKey2Var, value="14")       
        arrowRightKey.grid(column=3, row=4, padx=(5,10), pady=5, sticky = 'nwes')
        
        fieldsNeedToSave = {}
       
        
        ######################################################### FIELDS NEED TO SAVE ################################################################
        fieldsNeedToSave.update({'click' : self.radioKeyVar, 'press_key' : self.radioKey2Var})
        PartialBottom(windowApp, windowPopup, 0, 3, self, dictValues, fieldsNeedToSave)