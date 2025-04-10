from textwrap import fill
from tkinter import ttk, Text
import tkinter as tk
import customtkinter
from views.frame_action_detail.partial_bottom import PartialBottom
from views.frame_action_detail.partial_top import PartialTop
from helpers.select_area import SelectArea
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askopenfilenames
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory

class CrudFrameFields():
    def __init__():
        super().__init__()
        
    def get_area(frameArg, **kwargs):
        SelectArea(frameArg.windowApp, frameArg.windowPopup, **kwargs)
        
    def browse_images(frameArg):
        filenames = askopenfilenames(parent=frameArg.windowPopup,initialdir =  "/", title = "Select Images", filetype = (("png files","*.png"),("all files","*.*")) )
        # text.delete(1.0, tk.END)  # Uncomment if you need to replace text instead of adding
        listfiles = ";".join(filenames)
        frameArg.txtImages.insert(tk.END, listfiles + ";")
        frameArg.txtImagesVar.set(listfiles + ";")
        
    def update_txtimages(frameArg):
        frameArg.txtImagesVar.set(frameArg.txtImages.get('1.0', 'end-1c'))
        
    def update_content_file(frameArg):
        frameArg.txtContentFileVar.set(frameArg.txtContentFile.get('1.0', 'end-1c'))
        
    def browse_folders(frameArg):
        filename = askdirectory(parent=frameArg.windowPopup)
        frameArg.txtImagesVar.set(filename)
        
    def browse_text_file(frameArg):
        filename = askopenfilename(parent=frameArg.windowPopup,initialdir =  "/", title = "Select Text File", filetype = (("text files","*.txt"),("all files","*.*")))
        frameArg.txtImagesVar.set(filename)
        
    def browse_file(frameArg, fileTypes):        
        fileTypeBrowse = ()
        for fileType in fileTypes:
            if fileType == 'txt':
               fileTypeBrowse +=  (("text files","*.txt"),)
            elif fileType == 'csv':
               fileTypeBrowse +=  (("csv files","*.csv"),)
            elif fileType == 'exe':
               fileTypeBrowse +=  (("exe files","*.exe"),)
        fileTypeBrowse += (("all files","*.*"),)
        
        filename = askopenfilename(parent=frameArg.windowPopup,initialdir =  "/", title = "Select File", filetype = fileTypeBrowse )
        frameArg.txtImagesVar.set(filename)