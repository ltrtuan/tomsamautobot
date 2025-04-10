import pyautogui
import os, subprocess
from time import sleep
from random import choices, randint, choice, sample, uniform
from math import ceil
from multiprocessing import Process
import win32gui

#Ref https://github.com/vincentbavitz/bezmouse/blob/master/mouse.py
class MouseActions():
    
    @staticmethod
    def click(type_click = 1):   
        '''This function clicks the mouse with realistic errors:
            occasional accidental right click
            occasional double click
            occasional no click
        '''
        if type_click == 1:
            sleep(93 / randint(83,201))
            pyautogui.click()
        else:
            pyautogui.click()
            sleep(randint(43, 113) / 1000)
            pyautogui.click()
            # pyautogui.click(button = 'right')
    
    @staticmethod
    def move_to_area(x, y, width, height, deviation = 30):
        '''
        Arguments same as pyautogui.locateAllOnScreen format: x and y are top left corner
    
        This advanced function saves the xdotool commands to a temporary file
        'mouse.sh' in ./tmp/ then executes them from the shell to give clean curves
        '''
    
        init_pos = pyautogui.position()
    
        x_coord = x + randint(0, width)
        y_coord = y + randint(0, height)
        speed = randint(1, 2)
        deviation = randint(1, int(deviation))
        MouseActions.move(x_coord, y_coord, MouseActions.mouse_bez(init_pos, (x_coord, y_coord), deviation, speed))
        

    @staticmethod
    def pascal_row(n):
        # This returns the nth row of Pascal's Triangle
        result = [1]
        x, numerator = 1, n
        for denominator in range(1, n//2+1):
            # print(numerator,denominator,x)
            x *= numerator
            x /= denominator
            result.append(x)
            numerator -= 1
        if n&1 == 0:
            # n is even
            result.extend(reversed(result[:-1]))
        else:
            result.extend(reversed(result)) 
        return result
    
    @staticmethod
    def make_bezier(xys):

        # xys should be a sequence of 2-tuples (Bezier control points)
        n = len(xys)
        combinations = MouseActions.pascal_row(n - 1)
        def bezier(ts):
            # This uses the generalized formula for bezier curves
            # http://en.wikipedia.org/wiki/B%C3%A9zier_curve#Generalization
            result = []
            for t in ts:
                tpowers = (t**i for i in range(n))
                upowers = reversed([(1-t)**i for i in range(n)])
                coefs = [c*a*b for c, a, b in zip(combinations, tpowers, upowers)]
                result.append(
                    list(sum([coef*p for coef, p in zip(coefs, ps)]) for ps in zip(*xys)))
            return result
        return bezier
    

    @staticmethod
    def mouse_bez(init_pos, fin_pos, deviation, speed):
        '''
        GENERATE BEZIER CURVE POINTS
        Takes init_pos and fin_pos as a 2-tuple representing xy coordinates
            variation is a 2-tuple representing the
            max distance from fin_pos of control point for x and y respectively
            speed is an int multiplier for speed. The lower, the faster. 1 is fastest.
            
        '''

        #time parameter
        randTime = randint(2,30)
        ts = [t/(speed * float(randTime)) for t in range(speed * (randTime + 1))]
        #bezier centre control points between (deviation / 2) and (deviaion) of travel distance, plus or minus at random
        control_1 = (init_pos[0] + choice((-1, 1)) * abs(ceil(fin_pos[0]) - ceil(init_pos[0])) * 0.01 * randint(deviation // 2, deviation),
                    init_pos[1] + choice((-1, 1)) * abs(ceil(fin_pos[1]) - ceil(init_pos[1])) * 0.01 * randint(deviation // 2, deviation)
                        )
        control_2 = (init_pos[0] + choice((-1, 1)) * abs(ceil(fin_pos[0]) - ceil(init_pos[0])) * 0.01 * randint(deviation // 2, deviation),
                    init_pos[1] + choice((-1, 1)) * abs(ceil(fin_pos[1]) - ceil(init_pos[1])) * 0.01 * randint(deviation // 2, deviation)
                        )
        
        xys = [init_pos, control_1, control_2, fin_pos]
        bezier = MouseActions.make_bezier(xys)
        points = bezier(ts)

        return points
    

    @staticmethod
    def connected_bez(coord_list, deviation, speed):
        '''
        Connects all the coords in coord_list with bezier curve
        and returns all the points in new curve
    
        ARGUMENT: DEVIATION (INT)
            deviation controls how straight the lines drawn my the cursor
            are. Zero deviation gives straight lines
            Accuracy is a percentage of the displacement of the mouse from point A to
            B, which is given as maximum control point deviation.
            Naturally, deviation of 10 (10%) gives maximum control point deviation
            of 10% of magnitude of displacement of mouse from point A to B, 
            and a minimum of 5% (deviation / 2)
        '''
    
        i = 1
        points = []
    
        while i < len(coord_list):
            points += MouseActions.mouse_bez(coord_list[i - 1], coord_list[i], deviation, speed)
            i += 1
    
        return points
    

    @staticmethod
    def move(x_coord, y_coord, mouse_points, draw = False, rand_err = True):
        '''
        Moves mouse in accordance with a list of points (continuous curve)
        Input these as a list of points (2-tuple or another list)
    
        Generates file (mouse.sh) in ./tmp/ and runs it as bash file
    
        If you want a click at a particular point, write 'click' for that point in
        mouse_points
    
        This advanced function saves the xdotool commands to a temporary file
        'mouse.sh' in ./tmp/ then executes them from the shell to give clean curves
    
        You may wish to generate smooth bezier curve points to input into this
        function. In this case, take mouse_bez(init_pos, fin_pos, deviation, speed)
        as the argument.
    
        PARAMETERS:
            mouse_points
                list of 2-tuples or lists of ints or floats representing xy coords
            draw
                a boolean deciding whether or not to draw the curve the mouse makes
                to a file in /tmp/
        '''         
        mouse_points = [[round(v) for v in x] if type(x) is not str else x for x in mouse_points]
        mouse_random_moves = (pyautogui.easeOutCubic, pyautogui.easeOutQuint, pyautogui.easeInQuart, pyautogui.easeInOutBounce, pyautogui.easeInOutBack, pyautogui.easeInCubic)
        move = choice(mouse_random_moves)
        mouse_pointsr = sample(mouse_points, randint(3,7 if len(mouse_points) > 7 else len(mouse_points)))
        for coord in mouse_pointsr:
            pyautogui.moveTo(coord[0], coord[1])
        pyautogui.moveTo(x_coord, y_coord, duration=0.5, tween=move)   
    @staticmethod
    def check_pointer_is_clickable():
        try:
            e = win32gui.GetIconInfo(win32gui.GetCursorInfo()[1]) # GetCursorInfo()[1] to get "HCURSOR",GetIconInfo to get the info about the cursor.
            # print(e)           
            if e[1] == 6:
                return True
            else:
                return False
        except:
            return False