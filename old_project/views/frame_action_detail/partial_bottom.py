from textwrap import fill
from tkinter import ttk, Text
import tkinter as tk
import customtkinter
from helpers.helpers import Helpers

class PartialBottom(ttk.LabelFrame):
    def __init__(self, windowApp, windowPopup, column, row, formAction, dictValues, fieldsNeedToSave):
        super().__init__()
        self.windowPopup = windowPopup
        self.windowApp = windowApp
        self.formAction = formAction
        self.dictValues = dictValues
        self.fieldsNeedToSave = fieldsNeedToSave
        
        framePartial = ttk.LabelFrame(windowPopup, text="General Settings")
        framePartial.grid(column=column, row=row, sticky='nswe', padx=5, pady=5)
        
        windowPopup.columnconfigure(column,weight=1)
       
        lbTimeDelay = ttk.Label(framePartial, text = "Time Delay (seconds)", justify = "right")
        lbTimeDelay.grid(column=0, row=1, padx=5, pady=5, sticky = 'ne') 
        self.txtTimeDelayVar = tk.StringVar()
        self.txtTimeDelayVar.set(dictValues['time_delay'])
        txtTimeDelay = ttk.Entry(
            framePartial,
            width=30,
            textvariable=self.txtTimeDelayVar,
            font="Arial"
        )
        txtTimeDelay.grid(column=1, row=1, padx=5, pady=5, sticky = 'nwes')
        framePartial.columnconfigure(1,weight=1)
        
        lbTimeDelayRandom = ttk.Label(framePartial, text = "+ Time Delay Random", justify = "right")
        lbTimeDelayRandom.grid(column=2, row=1, padx=5, pady=5, sticky = 'n') 
        self.txtTimeDelayRandomVar = tk.StringVar()
        self.txtTimeDelayRandomVar.set(dictValues['time_delay_random'])
        txtTimeDelayRandom = ttk.Entry(
            framePartial,
            width=30,
            textvariable=self.txtTimeDelayRandomVar,
            font="Arial"
        )
        txtTimeDelayRandom.grid(column=3, row=1, padx=5, pady=5, sticky = 'nwes')   
        
        framePartial.columnconfigure(3,weight=1)
        
        lbRepeat = ttk.Label(framePartial, text = "Repeat", justify = "right")
        lbRepeat.grid(column=0, row=2, padx=5, pady=5, sticky = 'ne') 
        self.txtRepeatVar = tk.StringVar()
        self.txtRepeatVar.set(dictValues['repeat'])
        txtRepeat = ttk.Entry(
            framePartial,
            width=30,
            textvariable=self.txtRepeatVar,
            font="Arial"
        )
        txtRepeat.grid(column=1, row=2, padx=5, pady=5, sticky = 'nwes')   
        
        lbRepeatRandom = ttk.Label(framePartial, text = "+ Random", justify = "right")
        lbRepeatRandom.grid(column=2, row=2, padx=5, pady=5, sticky = 'n') 
        self.txtRepeatRandomVar = tk.StringVar()
        self.txtRepeatRandomVar.set(dictValues['repeat_random'])
        txtRepeatRandom = ttk.Entry(
            framePartial,
            width=30,
            textvariable=self.txtRepeatRandomVar,
            font="Arial"
        )
        txtRepeatRandom.grid(column=3, row=2, padx=5, pady=5, sticky = 'nwes')   

        
        lbRandomSkip = ttk.Label(framePartial, text = "Random Skip Action (!= 1 is skip)", justify = "right")
        lbRandomSkip.grid(column=0, row=3, padx=5, pady=5, sticky = 'ne') 
        self.txtRandomSkipVar = tk.StringVar()
        self.txtRandomSkipVar.set(dictValues['random_skip'])
        txtRandomSkip = ttk.Entry(
            framePartial,
            width=30,
            textvariable=self.txtRandomSkipVar,
            font="Arial"
        )
        txtRandomSkip.grid(column=1, row=3, padx=5, pady=5, sticky = 'nwes')
        
        lbNameProcess = ttk.Label(framePartial, text = "Name Process to Action (use <VARIABLE>)", justify = "right")
        lbNameProcess.grid(column=2, row=3, padx=5, pady=5, sticky = 'ne') 
        self.txtNameProcessVar = tk.StringVar()
        self.txtNameProcessVar.set(dictValues['name_process'])
        txtNameProcess = ttk.Entry(
            framePartial,
            width=30,
            textvariable=self.txtNameProcessVar,
            font="Arial"
        )
        txtNameProcess.grid(column=3, row=3, padx=5, pady=5, sticky = 'nwes')
        
        lbNote = ttk.Label(framePartial, text = "Note", justify = "right")
        lbNote.grid(column=0, row=4, padx=5, pady=5, sticky = 'ne')       
        self.txtNoteVar = tk.StringVar()
        self.txtNoteVar.set(dictValues['note'])
        txtNote = ttk.Entry(
            framePartial,
            width=30,
            textvariable=self.txtNoteVar,
            font="Arial"
        )
        txtNote.grid(column=1, row=4, padx=5, pady=5, sticky = 'nwes', columnspan=3)
        
        btnConfirm = customtkinter.CTkButton(framePartial, text="Confirm", text_color="#fff", fg_color="#FA7F08", hover_color="#000", font=('Arial', 15, 'bold'), command=self.confirm_action)
        btnConfirm.grid(column=0, row=5, padx=5, pady=5, columnspan=4)
        
        # btnCancel = customtkinter.CTkButton(framePartial, text="Cancel", text_color="#fff", fg_color="#ffad5e", hover_color="#000", font=('Arial', 15, 'bold'))
        # btnCancel.grid(column=2, row=5, padx=5, pady=5, columnspan=2)
        

    def confirm_action(self):
        tree = self.windowApp.frame_list_actions.tree
        selected = tree.focus()
        valuesSelected = tree.item(selected, 'values')
        
        valuesDefaultToSave = {"action_key" : valuesSelected[0], 'note' : self.txtNoteVar.get(), 'if_condition' : self.formAction.partialTop.txtIfConditionVar.get(), 'time_delay' : self.txtTimeDelayVar.get(), 'time_delay_random' : self.txtTimeDelayRandomVar.get(), 'repeat' : self.txtRepeatVar.get(), 'repeat_random' : self.txtRepeatRandomVar.get(), 'random_skip' : self.txtRandomSkipVar.get(), 'name_process' : self.txtNameProcessVar.get() }
      
        if(len(self.fieldsNeedToSave)):
            for key in self.fieldsNeedToSave:
                valuesDefaultToSave.update({key : self.fieldsNeedToSave[key].get()})
                
        tupleValues = Helpers.convertDataEntryToInsertTreeView(valuesDefaultToSave)
        tree.item(selected, values = tupleValues)
        self.windowPopup.destroy()
        # tree.insert('', tree.index(selected) + 1 if selected else 'end', iid=None, text=selectedAction, values=(keySelectedAction,''))