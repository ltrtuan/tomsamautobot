from tkinter import Tk, Menu, Toplevel
from tkinter import filedialog as fd
from views.frame_smtp_setting import FrameSMTPSetting
from views.frame_autorun_setting import FrameAutoRunSettings
class MenuTop():   
    def __init__(self, windowApp):
        super().__init__()
        self.windowApp = windowApp
        menuBar = Menu(windowApp)
        windowApp.config(menu=menuBar)
       
        self.create_menu_file(menuBar)
        self.create_menu_setting(menuBar)        
        
    def select_file(self):
        filetypes = (
            ('Tom files', '*.tom'),
            ('All files', '*.*')
        )
        tree = self.windowApp.frame_list_actions.tree
        filename = fd.askopenfilename(
            parent=self.windowApp, 
            title='Open a file',
            initialdir='/',
            filetypes=filetypes)
        if(filename):
            with open(filename, 'r', encoding='utf8') as f:
                lines = f.readlines()                
                if(lines):                          
                    for line in lines:                         
                        values = line.split(",")                
                        if(len(values) >= 3):
                            text = values[0]
                            values.pop(0)                    
                            tree.insert(parent='', index='end', iid=None, open=True, text=text, values=values)
                            
        
    def save_as_file(self):       
        data = [("Tom Files", "*.tom")]
        filename = fd.asksaveasfilename(parent=self.windowApp, filetypes=data, defaultextension=data)
        tree = self.windowApp.frame_list_actions.tree
        if(filename):
            with open(filename, 'w', encoding='utf8') as f:
                for item in tree.get_children():
                    values = [tree.item(item, 'text')]
                    values.extend(tree.item(item, 'values'))
                    valueStr = ",".join(values)
                    f.write(valueStr)
                    f.write('\n')
    
    def create_menu_file(self, menuBar):
         # create the file_menu
        fileMENU = Menu(
            menuBar,
            tearoff=0
        )
        # add the File menu to the menubar
        menuBar.add_cascade(
            label="File",
            menu=fileMENU
        )

        # add menu items to the File menu
        fileMENU.add_command(label='Open...',command=self.select_file)
        fileMENU.add_command(label='Save As',command=self.save_as_file)
    
    def create_menu_setting(self, menuBar):
        # create the Setting Menu
        settingMENU = Menu(
            menuBar,
            tearoff=0
        )
        menuBar.add_cascade(
            label="Settings",
            menu=settingMENU
        )
        settingMENU.add_command(label='SMTP & Email',command=self.open_settings_smtp) 
        settingMENU.add_command(label='Autorun & Error',command=self.open_settings_autorun)

    def open_settings_smtp(self):
        frmSettingSMTP = Toplevel(self.windowApp)
        frmSettingSMTP.geometry("600x150")
        frmSettingSMTP.resizable(False, False);
        frmSettingSMTP.title("Setting SMTP & Email")
        frmSettingSMTP.attributes('-topmost', 'true')
        FrameSMTPSetting(frmSettingSMTP)
    
    def open_settings_autorun(self):
        frmSettingAutoRun = Toplevel(self.windowApp)
        frmSettingAutoRun.geometry("300x150")
        frmSettingAutoRun.resizable(False, False);
        frmSettingAutoRun.title("Setting Autorun & Error")
        frmSettingAutoRun.attributes('-topmost', 'true')
        FrameAutoRunSettings(frmSettingAutoRun)