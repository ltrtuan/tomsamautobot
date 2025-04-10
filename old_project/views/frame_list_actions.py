from textwrap import fill
from tkinter import ttk
from tkinter import Tk,Toplevel
import tkinter
from views.frame_action_detail.frame_sleep import FrameSleep
from views.frame_action_detail.frame_set_variable import FrameSetVariable
from views.frame_action_detail.frame_move_mouse import FrameMoveMouse
from views.frame_action_detail.frame_search_image import FrameSearchImage
from views.frame_action_detail.frame_check_screen_pause import FrameCheckScreenPause
from views.frame_action_detail.frame_capture_screen import FrameCaptureScreen
from views.frame_action_detail.frame_search_text import FrameSearchText
from views.frame_action_detail.frame_input_text import FrameInputText
from views.frame_action_detail.frame_read_file import FrameReadFile
from views.frame_action_detail.frame_write_file import FrameWriteFile
from views.frame_action_detail.frame_open_close_program import FrameOpenCloseProgram
from views.frame_action_detail.frame_show_hide_program import FrameShowHideProgram
from views.frame_action_detail.frame_check_program import FrameCheckProgram
from views.frame_action_detail.frame_press_key import FramePressKey
from helpers.helpers import Helpers

class FrameListActions(ttk.LabelFrame):
     def __init__(self, windowApp):
        super().__init__()
        self.windowApp = windowApp
        
        s=ttk.Style()
        s.theme_use('clam')
        s.configure('Treeview', rowheight=35, indent=20, borderwidth = 1, background = "#fff",foreground = "#000", fieldbackground="#fff", font=("Arial", 15))
        
        s.map('Treeview', background = [('selected', '#348888')])
        frameListActions = ttk.LabelFrame(windowApp)
        frameListActions.grid(row=1, column=0, columnspan=6, padx=5, sticky='nsew')
        windowApp.rowconfigure(1, weight = 1) # configure the root grid rows
        
        vScrollbar = ttk.Scrollbar(frameListActions, orient="vertical")
        hScrollbar = ttk.Scrollbar(frameListActions, orient="horizontal")
        
        # define columns
        columns = Helpers.columns
        self.tree = ttk.Treeview(frameListActions, columns=columns, 
                    selectmode='none',
                    xscrollcommand=hScrollbar.set,
                    yscrollcommand=vScrollbar.set,
                    show='tree headings',
                    cursor="hand2"
                    )
       
        # define headings
        self.tree.heading('action_key', text='Action key')
        self.tree.heading('note', text='Note')
        self.tree["displaycolumns"]=("note")
        
        hScrollbar["command"] = self.tree.xview
        hScrollbar.grid(row=1, column=0, sticky='ew')
        vScrollbar["command"] = self.tree.yview
        vScrollbar.grid(row=0, column=1, sticky='ns')
        
        
        # generate sample data
        # contacts = []
        # for n in range(1, 100):
        #     contacts.append((f'first {n}', f'last {n}', f'email{n}@example.com'))
        
        # for index, contact in enumerate(contacts):
        #     self.tree.insert('', 'end', text='Tuan '+str(index), values=contact)
       
       
        self.tree.grid(row=0, column=0, padx=5, sticky='nsew')
        self.tree.bind("<ButtonPress-1>",self.bDown)
        self.tree.bind("<ButtonRelease-1>",self.bUp, add='+')
        self.tree.bind("<B1-Motion>",self.bMove, add='+')
        self.tree.bind("<Shift-ButtonPress-1>",self.bDown_Shift, add='+')
        self.tree.bind("<Shift-ButtonRelease-1>",self.bUp_Shift, add='+')
        self.tree.bind('<Control-c>', self.copy)
        self.tree.bind('<Control-x>', self.cut)
        self.tree.bind('<Control-v>', self.paste)
        self.tree.bind('<Control-a>', lambda *args: self.tree.selection_add(self.tree.get_children()))
        self.tree.bind('<Control-ButtonPress-1>', self.bDown_Ctrl)
        self.tree.bind('<Control-ButtonRelease-1>', self.bUp_Ctrl)
        self.tree.bind("<Double-1>", self.OnDoubleClick)
        frameListActions.columnconfigure(0, weight=1)
        frameListActions.rowconfigure(0, weight=1)
        # frameListActions.columnconfigure(1, weight=1)
        # frameListActions.rowconfigure(1, weight=1)

        
     def bDown_Shift(self, event):
        tv = event.widget
        select = [tv.index(s) for s in tv.selection()]
        item_iid = tv.selection()[0]
        parent_iid = tv.parent(item_iid)
        current_parent_iid = tv.parent(tv.identify_row(event.y))
        if(parent_iid == current_parent_iid): 
            select.append(tv.index(tv.identify_row(event.y)))
       
        for i in range(select[0],select[-1]+1,1):
            if(parent_iid != ''):
                tv.selection_add(tv.get_children(parent_iid)[i])
            else:
                tv.selection_add(tv.get_children()[i])

     def bDown(self, event):
        tv = event.widget        
        if tv.identify_row(event.y) not in tv.selection():
            tv.selection_set(tv.identify_row(event.y))        

     def bUp(self, event):
        tv = event.widget
        if tv.identify_row(event.y) in tv.selection():
            tv.selection_set(tv.identify_row(event.y))    

     def bUp_Shift(self, event):
        pass

     def bMove(self, event):
        tv = event.widget
        if(tv.identify_row(event.y) not in tv.selection()):
            current_parent_iid = tv.parent(tv.identify_row(event.y))
            moveto = tv.index(tv.identify_row(event.y))  
            select = tv.selection()
            try:
              for s in select:
                tv.move(s, current_parent_iid, moveto)
            except:
              print("An exception occurred")
            
     def copy(self, event):
        tree = event.widget
        sel = tree.selection() # get selected items
        self.windowApp.clipboard_clear()  # clear clipboard      
       
        for item in sel:
            # retrieve the values of the row
            values = [tree.item(item, 'text')]
            values.extend(tree.item(item, 'values'))
            valueStr = ",".join(values)            # append the values separated by \t to the clipboard
            self.windowApp.clipboard_append("\n"+valueStr)
      
     def cut(self, event):
        tree = event.widget        
        self.copy(event)
        sel = tree.selection() # get selected items
        tree.delete(*sel)
        
     def paste(self, event):
        tv = event.widget
        try:
            contentCopy = self.windowApp.clipboard_get()
        except tkinter.TclError:
            contentCopy = ''
        
        if(contentCopy != ''):
            listRows = contentCopy.split("\n")
            copyTo = tv.index(tv.identify_row(event.y))  
            for row in listRows:
                values = row.split(",")                
                if(len(values) >= 3):
                    text = values[0]
                    values.pop(0)                    
                    tv.insert(parent=tv.identify_row(event.y), index=copyTo+1, iid=None, open=True, text=text, values=values)
        
     def bDown_Ctrl(self, event):
        tv = event.widget
        if tv.identify_row(event.y) not in tv.selection():            
            select = list(tv.selection())
            select.append(tv.identify_row(event.y))
            select.sort()
            for i in select:
                tv.selection_add(i)
        else:
            tv.selection_remove(tv.identify_row(event.y))

     def bUp_Ctrl(self, event):
         pass
     
     def OnDoubleClick(self, event):
         tv = event.widget
         item = tv.identify_row(event.y)
         values = tv.item(item, 'values')
         action_key = None                 
         if len(values) > 0:
            action_key = values[0]        
         
         if action_key != '' and action_key != None and action_key.find("-") == -1 :
             FrameSetting = Toplevel(self.windowApp)
             FrameSetting.geometry("800x700")         
             FrameSetting.attributes('-topmost', 'true')
             data = Helpers.convertDataTreeViewToEntry(values)
             if action_key == 'sleep':     
                FrameSetting.title("Sleep Setting")
                FrameSleep(FrameSetting, self.windowApp, data)
                
             elif action_key == 'set_variable':              
                FrameSetting.title("Set Variable Setting")
                FrameSetVariable(FrameSetting, self.windowApp, data)
                
             elif action_key == 'move_mouse':              
                FrameSetting.title("Move Mouse Setting")
                FrameMoveMouse(FrameSetting, self.windowApp, data)
                
             elif action_key == 'search_image':              
                FrameSetting.title("Search Image Setting")
                FrameSearchImage(FrameSetting, self.windowApp, data)
                
             elif action_key == 'check_screen_pause':              
                FrameSetting.title("Check Screen Pause Setting")
                FrameCheckScreenPause(FrameSetting, self.windowApp, data)
                
             elif action_key == 'capture_screen':              
                FrameSetting.title("Capture Screen Setting")
                FrameCaptureScreen(FrameSetting, self.windowApp, data)
                
             elif action_key == 'search_text':              
                FrameSetting.title("Search Text Setting")
                FrameSearchText(FrameSetting, self.windowApp, data)
                
             elif action_key == 'input_text':              
                FrameSetting.title("Input Text Setting")
                FrameInputText(FrameSetting, self.windowApp, data)
                
             elif action_key == 'read_file':              
                FrameSetting.title("Read File Setting")
                FrameReadFile(FrameSetting, self.windowApp, data)
                
             elif action_key == 'write_file':              
                FrameSetting.title("Write File Setting")
                FrameWriteFile(FrameSetting, self.windowApp, data)
                
             elif action_key == 'open_close_program':              
                FrameSetting.title("Open & Close Program Setting")
                FrameOpenCloseProgram(FrameSetting, self.windowApp, data)
                
             elif action_key == 'show_hide_program':              
                FrameSetting.title("Show & Hide Program Setting")
                FrameShowHideProgram(FrameSetting, self.windowApp, data)
                
             elif action_key == 'check_program':              
                FrameSetting.title("Check Program Setting")
                FrameCheckProgram(FrameSetting, self.windowApp, data)
                
             elif action_key == 'press_key':              
                FrameSetting.title("Press Key Setting")
                FramePressKey(FrameSetting, self.windowApp, data)
             
             else:
                pass