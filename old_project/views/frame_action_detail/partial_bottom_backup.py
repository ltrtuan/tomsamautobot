from textwrap import fill
from tkinter import ttk, Text
import tkinter as tk
import customtkinter

class PartialBottom(ttk.LabelFrame):
    def __init__(self, windowPopup, column, row):
        super().__init__()
        self.windowPopup = windowPopup
        
        framePartial = ttk.LabelFrame(windowPopup)
        framePartial.grid(column=column, row=row, sticky='nswe', padx=5, pady=5)
        
        windowPopup.columnconfigure(0,weight=1)
        windowPopup.rowconfigure(0,weight=1)

        lbIfCondition = ttk.Label(framePartial, text = "IF Condition", justify = "right")
        lbIfCondition.grid(column=0, row=0, padx=5, pady=5, sticky = 'ne')      
        txtIfCondition = Text(
            framePartial,
            width=30,
            height=10,
            padx=5,
            pady=5,
            font="Arial"
        )
        txtIfCondition.grid(column=1, row=0, padx=5, pady=5, sticky = 'nwes', columnspan=3)
        
        lbElseCondition = ttk.Label(framePartial, text = "ELSE Condition", justify = "right")
        lbElseCondition.grid(column=0, row=1, padx=5, pady=5, sticky = 'ne')      
        txtElseCondition = Text(
            framePartial,
            width=30,
            height=10,
            padx=5,
            pady=5,
            font="Arial"
        )
        txtElseCondition.grid(column=1, row=1, padx=5, pady=5, sticky = 'nwes', columnspan=3)
        
        framePartial.columnconfigure(1,weight=1)
        
        lbTimeDelay = ttk.Label(framePartial, text = "Time Delay (seconds)", justify = "right")
        lbTimeDelay.grid(column=0, row=2, padx=5, pady=5, sticky = 'ne') 
        txtTimeDelayVar = tk.StringVar()
        txtTimeDelay = ttk.Entry(
            framePartial,
            width=30,
            textvariable=txtTimeDelayVar,
            font="Arial"
        )
        txtTimeDelay.grid(column=1, row=2, padx=5, pady=5, sticky = 'nwes')   
        
        lbTimeDelayRandom = ttk.Label(framePartial, text = "+ Time Delay Random", justify = "right")
        lbTimeDelayRandom.grid(column=2, row=2, padx=5, pady=5, sticky = 'n') 
        txtTimeDelayRandomVar = tk.StringVar()
        txtTimeDelayRandom = ttk.Entry(
            framePartial,
            width=30,
            textvariable=txtTimeDelayRandomVar,
            font="Arial"
        )
        txtTimeDelayRandom.grid(column=3, row=2, padx=5, pady=5, sticky = 'nwes')   
        
        framePartial.columnconfigure(3,weight=1)
        
        lbRepeat = ttk.Label(framePartial, text = "Repeat", justify = "right")
        lbRepeat.grid(column=0, row=3, padx=5, pady=5, sticky = 'ne') 
        txtRepeatVar = tk.StringVar()
        txtRepeat = ttk.Entry(
            framePartial,
            width=30,
            textvariable=txtRepeatVar,
            font="Arial"
        )
        txtRepeat.grid(column=1, row=3, padx=5, pady=5, sticky = 'nwes')   
        
        lbRepeatRandom = ttk.Label(framePartial, text = "+ Random", justify = "right")
        lbRepeatRandom.grid(column=2, row=3, padx=5, pady=5, sticky = 'n') 
        txtRepeatRandomVar = tk.StringVar()
        txtRepeatRandom = ttk.Entry(
            framePartial,
            width=30,
            textvariable=txtRepeatRandomVar,
            font="Arial"
        )
        txtRepeatRandom.grid(column=3, row=3, padx=5, pady=5, sticky = 'nwes')   

        
        lbRandomSkip = ttk.Label(framePartial, text = "Random Skip Action (!= 1 is skip)", justify = "right")
        lbRandomSkip.grid(column=0, row=4, padx=5, pady=5, sticky = 'ne') 
        txtRandomSkipVar = tk.StringVar()
        txtRandomSkip = ttk.Entry(
            framePartial,
            width=30,
            textvariable=txtRandomSkipVar,
            font="Arial"
        )
        txtRandomSkip.grid(column=1, row=4, padx=5, pady=5, sticky = 'nwes')
        
        lbNote = ttk.Label(framePartial, text = "Note", justify = "right")
        lbNote.grid(column=0, row=5, padx=5, pady=5, sticky = 'ne')
        txtNote = Text(
            framePartial,
            width=30,
            height=3,
            padx=5,
            pady=5,
            font="Arial"
        )
        txtNote.grid(column=1, row=5, padx=5, pady=5, sticky = 'nwes', columnspan=3)
        
        btnConfirm = customtkinter.CTkButton(framePartial, text="Confirm", text_color="#fff", fg_color="#FA7F08", hover_color="#000", font=('Arial', 15, 'bold'))
        btnConfirm.grid(column=0, row=6, padx=5, pady=5, columnspan=2)
        
        btnCancel = customtkinter.CTkButton(framePartial, text="Cancel", text_color="#fff", fg_color="#ffad5e", hover_color="#000", font=('Arial', 15, 'bold'))
        btnCancel.grid(column=2, row=6, padx=5, pady=5, columnspan=2)