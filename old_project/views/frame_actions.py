from tkinter import ttk, filedialog as fd
import tkinter as tk
import customtkinter
from tkinter.messagebox import askyesno
from helpers.helpers import Helpers
from controllers.start_actions import StartActions

class FrameActions(ttk.LabelFrame):
     def __init__(self, windowApp):
        super().__init__()       
        # Tkinter LabelFrame
        frameActions = ttk.LabelFrame(windowApp)
        frameActions.grid(column=0, row=0, sticky='we', padx=5, pady=(50, 20))
        self.windowApp = windowApp
        
        
        btnStart = customtkinter.CTkButton(windowApp, text="Start", text_color="#fff", fg_color="#FA7F08", hover_color="#000", font=('Arial', 15, 'bold'), command=lambda: StartActions(tree = self.windowApp.frame_list_actions.tree))
        btnStart.grid(column=0, row=0, padx=5, pady=5, sticky='we')
        
        btnDelete = customtkinter.CTkButton(windowApp, text="Delete", text_color="#fff", fg_color="#ffad5e", hover_color="#000", font=('Arial', 15, 'bold'), command=self.delete_row_actions)
        btnDelete.grid(column=1, row=0, padx=5, pady=5, sticky='we')
        
        btnDeleteAll = customtkinter.CTkButton(windowApp, text="Delete All", text_color="#fff", fg_color="#ffad5e", hover_color="#000", font=('Arial', 15, 'bold'),command=self.delete_all_row_actions)
        btnDeleteAll.grid(column=2, row=0, padx=5, pady=5, sticky='we')
        
        btnStop = customtkinter.CTkButton(windowApp, text="Stop", text_color="#fff", fg_color="#ffad5e", hover_color="#000", font=('Arial', 15, 'bold'))
        btnStop.grid(column=3, row=0, padx=5, pady=5, sticky='we')
        
        self.cbActions_var = tk.StringVar()       
        listActionsDict = Helpers.listActionsDict
        self.actionValues = list(listActionsDict.values())
        self.actionKeys = list(listActionsDict.keys())
        cbActions = customtkinter.CTkComboBox(windowApp, values=self.actionValues, variable = self.cbActions_var)
        cbActions.grid(column=4, row=0, padx=5, pady=5, sticky='we')
        
        btnAddAction = customtkinter.CTkButton(windowApp, text="Add Actions", text_color="#fff", fg_color="#F24405", hover_color="#000", font=('Arial', 15, 'bold'), command=self.add_row_actions)
        btnAddAction.grid(column=5, row=0, padx=5, pady=5, sticky='we')
        
        windowApp.columnconfigure(0,weight=1)
        windowApp.columnconfigure(1,weight=2)
        windowApp.columnconfigure(2,weight=1)
        windowApp.columnconfigure(3,weight=1)
        windowApp.columnconfigure(4,weight=1)
        windowApp.columnconfigure(5,weight=1)
        
     def add_row_actions(self):
         selectedAction = self.cbActions_var.get()
         if(selectedAction != ''):
             position = self.actionValues.index(selectedAction)
             keySelectedAction = self.actionKeys[position]
             tree = self.windowApp.frame_list_actions.tree
             selected = tree.focus()
             tupleValues = Helpers.convertDataEntryToInsertTreeView({"action_key" : keySelectedAction})
             tree.insert('', tree.index(selected) + 1 if selected else 'end', iid=None, text=selectedAction, values=tupleValues)
        
     def delete_row_actions(self):
        answer = askyesno(title='Confirm to Delete', message='Are you sure that you want to delete?')
        if answer:
            tree = self.windowApp.frame_list_actions.tree
            for s in tree.selection():
                if tree.exists(s)==True:
                    tree.delete(s)
         
     def delete_all_row_actions(self):
        answer = askyesno(title='Confirm to Delete', message='Are you sure that you want to delete?')
        if answer:
            tree = self.windowApp.frame_list_actions.tree
            for row in tree.get_children():
                tree.delete(row)