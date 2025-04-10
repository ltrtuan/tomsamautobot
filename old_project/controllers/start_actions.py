from pydoc import Helper
from textwrap import fill
from tkinter import ttk
from tkinter import Tk,Toplevel
import tkinter
from helpers.helpers import Helpers
from helpers.mouse_actions import MouseActions
from helpers.selenium import Selenium
import time
import re
import random
import win32gui, win32con, win32com.client
import os
from python_imagesearch.imagesearch import imagesearcharea
import pyautogui
import mss.tools


class StartActions(ttk.LabelFrame):    
     def __init__(self, tree):
        super().__init__()
        self.tree = tree
        global allVariables
        allVariables = {}
        time.sleep(1)
        for actionItem in tree.get_children():
            valuesItem = tree.item(actionItem, 'values')
            self.executeAction(valuesItem)
                                
     def executeAction(self, valuesItem):
        dataActions = Helpers.convertDataTreeViewToEntry(valuesItem)
        action_key = dataActions['action_key']
        note =  dataActions['note']
        variables =  dataActions['variables']
        x =  int(dataActions['x']) if dataActions['x'] else ''
        y =  int(dataActions['y']) if dataActions['y'] else ''
        width =  int(dataActions['width']) if dataActions['width'] else ''
        height =  int(dataActions['height']) if dataActions['height'] else ''
        width_extra =  int(dataActions['width_extra']) if dataActions['width_extra'] else ''
        height_extra =  int(dataActions['height_extra']) if dataActions['height_extra'] else ''
        if_condition =  dataActions['if_condition']        
        
        name_process =  dataActions['name_process']
        click_if_hand =  dataActions['click_if_hand']
        click =  dataActions['click']
        break_loop =  dataActions['break']
        images =  dataActions['images']
        loop_multiple =  dataActions['loop_multiple']
        content_file =  dataActions['content_file']
        press_key =  dataActions['press_key']
        
        repeat =  int(dataActions['repeat']) if dataActions['repeat'] else 1
        repeat_random =  random.randint(1, int(dataActions['repeat_random'])) if dataActions['repeat_random'] else 0
        totalRepat = repeat + repeat_random        
       
        time_delay =  dataActions['time_delay']
        time_delay_random =  dataActions['time_delay_random']
        
        
        random_skip =  random.randint(1, int(dataActions['random_skip'])) if dataActions['random_skip'] else 1
        #random_skip > 1 will be ignore the action
        if(Helpers.resultIfCondition(if_condition) and random_skip == 1):
            for loopAction in range(totalRepat):
                
                # Switch Process for Current Action
                if(name_process != ""):
                    top_windows = []
                    win32gui.EnumWindows(Helpers.windowEnumerationHandler, top_windows)
                    for i in top_windows:
                        if name_process in i[1].lower():
                            win32gui.ShowWindow(i[0], win32con.SW_MAXIMIZE)
                            win32gui.SetActiveWindow(i[0])
                            win32gui.BringWindowToTop(i[0])
                            win32gui.SetForegroundWindow(i[0])
                            break                        
                
                timeDelayTotalRandom = random.randint(1, int(time_delay_random)) if time_delay_random else 0
                timeDelayTotal = int(time_delay) + timeDelayTotalRandom if time_delay else 0
                time.sleep(int(timeDelayTotal))                
                
                if action_key == 'sleep':
                    pass
                
                #SET VARIABLE
                elif action_key == 'set_variable':
                    if(images):
                        allVariables = Helpers.setVariables(allVariables, images, loop_multiple)
                
                #MOVE MOUSE       
                elif action_key == 'move_mouse':
                    if(x and y and width and height):
                        MouseActions.move_to_area(x, y, width, height)
                        isCursorHand = MouseActions.check_pointer_is_clickable()
                        if(click_if_hand == '1'):
                            if(click and isCursorHand):
                                MouseActions.click(int(click))
                        else:
                            if(click):
                                MouseActions.click(int(click))
                                
                        if(break_loop and isCursorHand):
                            break #Break if Cursor is Hand
                
                #SEARCH IMAGE
                elif action_key == 'search_image':
                    if(width and height):
                        listImages = re.split(r'[;]',images)
                        if(len(listImages)):
                            imageChosen = listImages[0];
                            checkImageExist = os.path.exists(imageChosen)
                            if(checkImageExist):
                                pos = imagesearcharea(imageChosen, 0, 0, width, height)
                                if pos[0] != -1:
                                    width_extra =  random.randint(1, width_extra) if width_extra else 1
                                    height_extra =  random.randint(1, height_extra) if height_extra else 1
                                    time.sleep(0.5)
                                    MouseActions.move_to_area(pos[0], pos[1], width_extra, height_extra)
                                    isCursorHand = MouseActions.check_pointer_is_clickable()
                                    time.sleep(0.5)
                                    if(click_if_hand == '1'):
                                        if(click and isCursorHand):
                                            MouseActions.click(int(click))
                                    else:
                                        if(click):
                                            MouseActions.click(int(click))
                                            

                #CHECK SCREEN PAUSE
                elif action_key == 'check_screen_pause':
                    if(x and y and width and height):
                        with mss.mss() as sct:                        
                            # The screen part to capture
                            monitor = {"top": int(x), "left": int(y), "width": int(width), "height": int(height)}
            
                            # Grab the data
                            sct_img = sct.grab(monitor)
                            
                            firstPixels = list(zip(sct_img.raw[2::4], sct_img.raw[1::4], sct_img.raw[::4]))                            
                            
                        time.sleep(2)
                        
                        with mss.mss() as sct:                        
                            # The screen part to capture
                            monitor = {"top": int(x), "left": int(y), "width": int(width), "height": int(height)}
            
                            # Grab the data
                            sct_img = sct.grab(monitor)
                            
                            lastPixels = list(zip(sct_img.raw[2::4], sct_img.raw[1::4], sct_img.raw[::4]))
                        
                        correct_count = sum(a == b for a, b in zip(firstPixels, lastPixels))
                        overlap = correct_count / len(firstPixels) * 100
                        width_extra = random.randint(0, width)
                        height_extra = random.randint(0, height)
                        if(overlap >= 98):
                            
                            mouse_random_moves = (pyautogui.easeOutCubic, pyautogui.easeOutQuint, pyautogui.easeInQuart, pyautogui.easeInOutBounce, pyautogui.easeInOutBack, pyautogui.easeInCubic)
                            move = random.choice(mouse_random_moves)
                            # pyautogui.moveTo(x, y, duration=0.5, tween=move)   
                            MouseActions.move_to_area(x, y, width_extra, height_extra)
                            if(click):
                                MouseActions.click(int(click))
                                
                #OPEN SELENIUM
                elif action_key == 'open_selenium':
                    Selenium.open()
                    
                #READ COOKIES
                elif action_key == 'read_cookies':
                    Selenium.readCookies()
                    
                #LOAD COOKIES
                elif action_key == 'load_cookies':
                    Selenium.loadCookies()
                    
                #CLEAR COOKIES
                elif action_key == 'clear_cookies':
                    Selenium.clearCookies()