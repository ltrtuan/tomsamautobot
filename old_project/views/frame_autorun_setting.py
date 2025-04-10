from tkinter import ttk, filedialog as fd
import tkinter as tk

class FrameAutoRunSettings():
     def __init__(self, frmSettingAutoRunWindow):
        super().__init__()
        
        # Tkinter LabelFrame
        frameActions = ttk.LabelFrame(frmSettingAutoRunWindow, text='Actions')
        frameActions.grid(column=0, row=0, sticky='we', padx=5, pady=5)

        showErrorVar = tk.StringVar()
        def showError_changed():
            tk.messagebox.showinfo(title='Show Error',
                                message=showErrorVar.get())
        chkShowError = ttk.Checkbutton(frameActions,
                        text='Show Error',
                        command=showError_changed,
                        variable=showErrorVar,
                        onvalue='1',
                        offvalue='0')
        chkShowError.grid(column=0, row=0, padx=5, pady=5)


        autorunVar = tk.StringVar()
        def autorun_changed():
            tk.messagebox.showinfo(title='Show Error',
                                message=autorunVar.get())
        chkAutoRun = ttk.Checkbutton(frameActions,
                        text='Auto Run',
                        command=autorun_changed,
                        variable=autorunVar,
                        onvalue='1',
                        offvalue='0')
        chkAutoRun.grid(column=1, row=0, padx=5, pady=5)


        def getPathLogFile():
            filetypes = (
                ('Txt files', '*.txt'),
                ('All files', '*.*')
            )

            filename = fd.askopenfilename(
                title='Open a file',
                initialdir='/',
                filetypes=filetypes,
                parent=frmSettingAutoRunWindow)
            txtLogPathVar.set(filename);
    
        btnLogPath = ttk.Button(
           frameActions, 
           text="Log File",
           command=getPathLogFile
        )
        btnLogPath.grid(column=0, row=1, padx=5, pady=5)

        txtLogPathVar = tk.StringVar()
        txtLogPath = ttk.Entry(
            frameActions,   
            width=20,
            textvariable=txtLogPathVar
        )
        txtLogPath.grid(column=1, row=1, padx=5, pady=5)


        def getAutoRunFile():
            filetypes = (
                ('Tom files', '*.tom'),
                ('All files', '*.*')
            )

            filename = fd.askopenfilename(
                title='Open a file',
                initialdir='/',
                filetypes=filetypes,
                parent=frmSettingAutoRunWindow)
            txtAutoRunPathVar.set(filename);
    
        btnAutoRunPath = ttk.Button(
           frameActions, 
           text="Auto Run File",
           command=getAutoRunFile
        )
        btnAutoRunPath.grid(column=0, row=2, padx=5, pady=5)

        txtAutoRunPathVar = tk.StringVar()
        txtAutoRunPath = ttk.Entry(
            frameActions,   
            width=20,
            textvariable=txtAutoRunPathVar
        )
        txtAutoRunPath.grid(column=1, row=2, padx=5, pady=5)