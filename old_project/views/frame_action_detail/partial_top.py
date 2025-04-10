from textwrap import fill
from tkinter import ttk, Text
import tkinter as tk
import customtkinter

class PartialTop(ttk.LabelFrame):
    def __init__(self, windowApp, windowPopup, column, row, formAction, dictValues):
        super().__init__()
        self.windowPopup = windowPopup
        
        framePartial = ttk.LabelFrame(windowPopup)
        framePartial.grid(column=column, row=row, sticky='nswe', pady=5, padx=5)
        
        windowPopup.columnconfigure(column,weight=1)
       
        lbIfCondition = ttk.Label(framePartial, text = "IF Condition A>=2|B<1&C!=RESULT|D=7", justify = "right")
        lbIfCondition.grid(column=0, row=0, padx=5, pady=5, sticky = 'ne')        
        self.txtIfConditionVar = tk.StringVar()
        self.txtIfConditionVar.set(dictValues['if_condition'])
        txtIfCondition = ttk.Entry(
            framePartial,
            width=30,
            textvariable= self.txtIfConditionVar,
            font="Arial"
        )
        txtIfCondition.grid(column=1, row=0, padx=5, pady=5, sticky = 'nwes', columnspan=3)       
        
        framePartial.columnconfigure(1,weight=1)
        
        # btnConfirm = customtkinter.CTkButton(framePartial, text="Confirm", text_color="#fff", fg_color="#FA7F08", hover_color="#000", font=('Arial', 15, 'bold'))
        # btnConfirm.grid(column=0, row=5, padx=5, pady=5, columnspan=2)
        
        # btnCancel = customtkinter.CTkButton(framePartial, text="Cancel", text_color="#fff", fg_color="#ffad5e", hover_color="#000", font=('Arial', 15, 'bold'))
        # btnCancel.grid(column=2, row=5, padx=5, pady=5, columnspan=2)