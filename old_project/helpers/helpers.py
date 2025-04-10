
import re
import win32gui

class Helpers():
    columns = ('action_key', 'note', 'variables', 'x', 'y', 'width', 'height', 'width_extra', 'height_extra', 'if_condition', 'time_delay', 'time_delay_random', 'repeat', 'repeat_random', 'random_skip', 'name_process', 'click_if_hand', 'click', 'break', 'images','loop_multiple','content_file', 'press_key')
    listActionsDict = {"sleep" : "Sleep", "set_variable" : "Set Variable", "move_mouse" : 'Move Mouse', 'search_image' : 'Search Image', 'check_screen_pause' : 'Check Screen Pause', 'check_screen_full' : 'Check Full Screen', 'capture_screen' : 'Capture Screen', '-' : '------------------', 'search_text' : 'Search Text', 'input_text' : 'Input Text', 'read_file' : 'Read File', 'write_file' : 'Write File', '--' : '------------------', 'open_close_program' : 'Open Close Program', 'show_hide_program' : 'Show Hide Program', 'check_program' : 'Check Program', 'press_key' : 'Press Key', '--' : '------------------', 'open_selenium' : 'Open Selenium', 'read_cookies' : 'Read Cookies', 'load_cookies' : 'Load Cookies', 'clear_cookies' : 'CLEAR Cookies'}
    @staticmethod    
    def convertDataEntryToInsertTreeView(data): 
        dataColumns = []
        for col in Helpers.columns:
            if col in data:
                value = data[col]
            else:
                value = ''
                
            dataColumns.append(value)
       
        return tuple(dataColumns)
    

    @staticmethod
    def convertDataTreeViewToEntry(data):
        dictData = {}
        if len(Helpers.columns) == len(data):
            dictData = dict(zip(Helpers.columns, data))
        return dictData
    
    @staticmethod
    def resultIfCondition(condition):
        if(condition == ''):
            return True
        #A>2||B<4&&C=5&&A=6
        conditionList = re.split(r'([&\\|])',condition)
        conditionList = list(filter(bool, conditionList)) #['A>=2', '|', 'B<1', '&', 'C=2']
        regexConditionDetail = r"([a-zA-Z0-9]*)([^a-zA-Z0-9]*)([a-zA-Z0-9]*)"
        resultIfAll = False
        symbolIf = ''
        for conditionItem in conditionList:
            resultIf = None
            
            if(len(conditionItem) > 1): #mean not | or & symbol
                conditionDetailMatches = re.findall(regexConditionDetail, conditionItem)
                conditionDetailMatches = conditionDetailMatches[0] #('A', '>=', '2')
                leftFormula = conditionDetailMatches[0]
                symbolFormula = conditionDetailMatches[1]
                rightFormula = conditionDetailMatches[2]
                
                if(symbolFormula == '>'):
                    resultIf = leftFormula > rightFormula
                elif(symbolFormula == '>='):
                    resultIf = leftFormula >= rightFormula
                elif(symbolFormula == '='):
                    resultIf = leftFormula == rightFormula
                elif(symbolFormula == '<'):
                    resultIf = leftFormula < rightFormula
                elif(symbolFormula == '<='):
                    resultIf = leftFormula <= rightFormula
                elif(symbolFormula == '!='):
                    resultIf = leftFormula != rightFormula
            else:
                symbolIf = conditionItem

            if(resultIf != None):# in case loop item that has only symbol, so do not need run this code
                if(symbolIf == '|'):
                    resultIfAll = resultIfAll or resultIf
                elif(symbolIf == '&'):
                    resultIfAll = resultIfAll and resultIf
                else:
                    resultIfAll = resultIf
        return resultIfAll
    
    @staticmethod
    def setVariables(allVariables, stringVariables, ignoreMathCalculation):
       #A=4;C=1       
       listVariables = re.split(r'[;]',stringVariables)
       if(len(listVariables)):
           for variableItem in listVariables:
               listVariableItem = re.split(r'[=]',variableItem) #(A, 1)
               if(len(listVariableItem) < 2):
                   return allVariables
               
               # Check the value after = has Math sign
               isMathCalculation = False
               if(int(ignoreMathCalculation) != 1):
                   regexMathSign = r"([+\-%/*])"
                   mathFormula = re.split(regexMathSign, listVariableItem[1]) # [A, +, C] only support 1 math sign
                   if(len(mathFormula) == 3):
                        isMathCalculation = True 
                        mathResult = Helpers.mathCalculation(mathFormula[1], mathFormula[0], mathFormula[2], allVariables)
                        allVariables.update({ listVariableItem[0] : mathResult })
               
               if(isMathCalculation == False):
                   # If value after = is exist in allVariables
                   if listVariableItem[1] in allVariables:
                       allVariables.update({ listVariableItem[0] : allVariables[listVariableItem[1]] })
                   else:
                       allVariables.update({ listVariableItem[0] : listVariableItem[1] })
                   
       return allVariables
   
   
    @staticmethod
    def mathCalculation(mathSign, leftMathSign, rightMathSign, allVariables):
        result = 0
        if leftMathSign in allVariables:                
            leftMathSign = allVariables[leftMathSign]
            
        if rightMathSign in allVariables:                
            rightMathSign = allVariables[rightMathSign]
        
        leftMathSign = int(leftMathSign) if leftMathSign.isnumeric() else 0
        rightMathSign = int(rightMathSign) if rightMathSign.isnumeric() else 0
        
        if(mathSign == '+'):
            result = leftMathSign + rightMathSign
        elif(mathSign == '-'):
            result = leftMathSign + rightMathSign
        elif(mathSign == '*'):
            result = leftMathSign * rightMathSign
        elif(mathSign == '/'):
            result = leftMathSign / rightMathSign
        elif(mathSign == '%'):
            result = leftMathSign % rightMathSign
            
        return result
    
    @staticmethod
    def windowEnumerationHandler(hwnd, top_windows):
        top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))