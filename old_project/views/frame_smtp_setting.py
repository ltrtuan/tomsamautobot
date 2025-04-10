from tkinter import ttk
import tkinter as tk

class FrameSMTPSetting():
    def __init__(self, frmSettingSMTPWindow):
        super().__init__()
        # Tkinter LabelFrame
        frameSMTPSetting = ttk.LabelFrame(frmSettingSMTPWindow, text='STMP Settings')
        frameSMTPSetting.grid(column=0, row=0, sticky='we', padx=5, pady=5)


        lbSMTPUrl = ttk.Label(frameSMTPSetting, text = "SMTP Url")
        lbSMTPUrl.grid(column=0, row=0, padx=5, pady=5, sticky = 'w')
        txtSMTPUrlVar = tk.StringVar()
        txtSMTPUrl = ttk.Entry(
            frameSMTPSetting,
            width=30,
            textvariable=txtSMTPUrlVar
        )
        txtSMTPUrl.grid(column=1, row=0, padx=5, pady=5, sticky = 'we')

        lbPort = ttk.Label(frameSMTPSetting, text = "Port")
        lbPort.grid(column=0, row=1, padx=5, pady=5, sticky = 'w')
        txtPortVar = tk.StringVar()
        txtPort = ttk.Entry(
            frameSMTPSetting,
            width=30,
            textvariable=txtPortVar
        )
        txtPort.grid(column=1, row=1, padx=5, pady=5, sticky = 'we')

        lbUserName = ttk.Label(frameSMTPSetting, text = "Username")
        lbUserName.grid(column=0, row=2, padx=5, pady=5, sticky = 'w')
        txtUserNameVar = tk.StringVar()
        txtUserName = ttk.Entry(
            frameSMTPSetting,
            width=30,
            textvariable=txtUserNameVar
        )
        txtUserName.grid(column=1, row=2, padx=5, pady=5, sticky = 'we')

        lbPassword = ttk.Label(frameSMTPSetting, text = "Password")
        lbPassword.grid(column=0, row=3, padx=5, pady=5, sticky = 'w')
        txtPasswordVar = tk.StringVar()
        txtPassword = ttk.Entry(
            frameSMTPSetting,
            width=30,
            textvariable=txtPasswordVar
        )
        txtPassword.grid(column=1, row=3, padx=5, pady=5, sticky = 'we')

        frameSMTPSetting.columnconfigure(0,weight=1)
        frameSMTPSetting.columnconfigure(1,weight=9)


        # Tkinter LabelFrame
        frameEmailSetting = ttk.LabelFrame(frmSettingSMTPWindow, text='Email Settings')
        frameEmailSetting.grid(column=1, row=0, sticky='we', padx=5, pady=5)

        lbEmailFrom = ttk.Label(frameEmailSetting, text = "Email From")
        lbEmailFrom.grid(column=0, row=0, padx=5, pady=5, sticky = 'w')
        txtEmailFromVar = tk.StringVar()
        txtEmailFrom = ttk.Entry(
            frameEmailSetting,
            width=30,
            textvariable=txtEmailFromVar
        )
        txtEmailFrom.grid(column=1, row=0, padx=5, pady=5, sticky = 'we')

        lbEmailTo = ttk.Label(frameEmailSetting, text = "Email To")
        lbEmailTo.grid(column=0, row=1, padx=5, pady=5, sticky = 'w')
        txtEmailToVar = tk.StringVar()
        txtEmailTo = ttk.Entry(
            frameEmailSetting,
            width=30,
            textvariable=txtEmailToVar
        )
        txtEmailTo.grid(column=1, row=1, padx=5, pady=5, sticky = 'we')

        lbTitleEmail = ttk.Label(frameEmailSetting, text = "Title")
        lbTitleEmail.grid(column=0, row=2, padx=5, pady=5, sticky = 'w')
        txtTitleEmailVar = tk.StringVar()
        txtTitleEmail = ttk.Entry(
            frameEmailSetting,
            width=30,
            textvariable=txtTitleEmailVar
        )
        txtTitleEmail.grid(column=1, row=2, padx=5, pady=5, sticky = 'we')

        lbMessEmail = ttk.Label(frameEmailSetting, text = "Message")
        lbMessEmail.grid(column=0, row=3, padx=5, pady=5, sticky = 'w')
        txtMessEmailVar = tk.StringVar()
        txtMessEmail = ttk.Entry(
            frameEmailSetting,
            width=30,
            textvariable=txtMessEmailVar
        )
        txtMessEmail.grid(column=1, row=3, padx=5, pady=5, sticky = 'we')
        
        frameEmailSetting.columnconfigure(0,weight=1)
        frameEmailSetting.columnconfigure(1,weight=9)
        
        frmSettingSMTPWindow.columnconfigure(0,weight=1)
        frmSettingSMTPWindow.columnconfigure(1,weight=1)

        frmSettingSMTPWindow.rowconfigure(0, weight=1) 
        frmSettingSMTPWindow.rowconfigure(1, weight=1)

        