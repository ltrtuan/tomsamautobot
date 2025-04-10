from textwrap import fill
from tkinter import ttk, Text
import tkinter as tk
import customtkinter
from views.frame_action_detail.partial_bottom import PartialBottom
from views.frame_action_detail.partial_top import PartialTop

class FrameSleep(ttk.LabelFrame):
    def __init__(self, windowPopup, windowApp, dictValues):
        super().__init__()
        self.windowPopup = windowPopup
        self.windowApp = windowApp
        self.dictValues = dictValues
        
        self.partialTop = PartialTop(windowApp, windowPopup, 0, 0, self, dictValues)
        fieldsNeedToSave = {}
        PartialBottom(windowApp, windowPopup, 0, 3, self, dictValues, fieldsNeedToSave)