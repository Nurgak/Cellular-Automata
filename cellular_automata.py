from tkinter import *
import threading
from math import floor

# http://www.pythonware.com/library/tkinter/introduction/dialog-windows.htm
class StartStateDialog:
    def __init__(self, _parent):
        self.parent = _parent
        top = self.top = Toplevel(self.parent.window)

        self.cells = self.parent.getCells()
        self.state = self.parent.getState()
        
        self.canvas = Canvas(top, width=600, height=50, bg="ivory")
        self.canvas.pack(padx=5, pady=5)
        self.drawState()
        
        self.e_cells = Entry(top, width=10)
        self.e_cells.insert(0, self.cells)
        self.e_cells.pack(side=LEFT, padx=3, pady=3)

        b_setCells = Button(top, text="Set Cells", command=self.setCells)
        b_setCells.pack(side=LEFT, padx=5, pady=5)

        # add reset button to clear all cells
        b_reset = Button(top, text="Reset", command=self.resetState)
        b_reset.pack(side=LEFT, padx=3, pady=3)

        b_ok = Button(top, text="OK", command=self.ok)
        b_ok.pack(side=LEFT, padx=5, pady=5)

        b_cancel = Button(top, text="Cancel", command=self.cancel)
        b_cancel.pack(side=LEFT, padx=5, pady=5)

    def drawState(self):
        # http://stackoverflow.com/questions/2786877/how-do-i-attach-event-bindings-to-items-on-a-canvas-using-tkinter
        size = 600 / self.cells
        for i in range(0, self.cells):
            color = "gray" if self.state[i] else "black"
            self.canvas.create_rectangle(i * size, 0, i * size + size, 50, fill = color)

        self.canvas.bind('<ButtonPress-1>', self.toggleState)

    def toggleState(self, event):
        size = 600 / self.cells
        cellIndex = floor(event.x / size)
        self.state[cellIndex] = not self.state[cellIndex]
        self.drawState()

    def resetState(self):
        self.state = [0 for i in range(self.cells)]
        self.drawState()

    def setCells(self):
        if not self.e_cells.get().isnumeric():
            print("Error: cells must be a number.")
            return
            
        value = int(self.e_cells.get())
        
        if value >= 0:
            self.cells = value
            self.state = [0 for i in range(self.cells)]
            self.drawState()
        else:
            print("Error: cells value can only be bigger or equal to 0.")

    def ok(self):
        self.parent.setCells(self.cells)
        self.parent.setState(self.state)
        self.top.destroy()

    def cancel(self):
        self.top.destroy()

class CellularAutomata:
    __state = 0
    __rule = 30
    __cells = 16
    __thread = 0
    __canvasLine = 0
    
    def __init__(self):
        # set up graphical interface
        self.window = Tk()
        
        self.canvas = Canvas(self.window, width=600, height=600, bg="ivory")
        self.canvas.pack(side=TOP, padx=5, pady=5)
        
        # add button for 1 step
        b_step = Button(self.window, text="Step", command=self.step)
        b_step.pack(side=LEFT, padx=3, pady=3)
        
        # add button for 10 steps
        b_step10 = Button(self.window, text="10 Steps", command=self.step10)
        b_step10.pack(side=LEFT, padx=3, pady=3)
        
        # add run button
        self.b_run = Button(self.window, text="Run", command=self.toggleThread)
        self.b_run.pack(side=LEFT, padx=3, pady=3)

        # add rule input
        self.e_rule = Entry(self.window, width=10)
        self.e_rule.insert(0, self.__rule)
        self.e_rule.pack(side=LEFT, padx=3, pady=3)

        # add button to set rule
        b_rule = Button(self.window, text="Set Rule", command=self.setRuleCallback)
        b_rule.pack(side=LEFT, padx=3, pady=3)

        # add button to set starting state
        b_state = Button(self.window, text="Set State", command=self.setStateCallback)
        b_state.pack(side=LEFT, padx=3, pady=3)

        # add button to clear the canvas
        b_clear = Button(self.window, text="Clear", command=self.clearCanvas)
        b_clear.pack(side=LEFT, padx=3, pady=3)
        
        # set null state
        self.__state = [0 for i in range(self.__cells)]
    
    def start(self):
        self.window.mainloop()

    def setState(self, state):
        self.__state = state

    def getState(self):
        return self.__state

    def setStateCallback(self):
        dialog = StartStateDialog(self)
    
    def setRule(self, rule):
        self.__rule = rule
        
    def setRuleCallback(self):
        if not self.e_rule.get().isnumeric():
            print("Error: rule must be a number.")
            return
            
        value = int(self.e_rule.get())
        
        if value >= 0 and value < 256:
            self.setRule(value)
        else:
            print("Error: rule value can only be between 0 and 255.")
    
    def setCells(self, cells):
        self.__cells = cells

    def getCells(self):
        return self.__cells

    def step(self):
        nextState = []
        for i in range(0, self.__cells):
            # get first condition (use last condition if first cell)
            a = self.__state[(i - 1) % self.__cells]
            # get second condition
            b = self.__state[i]
            # get third condition (use first condition if last cell)
            c = self.__state[(i + 1) % self.__cells]

            # convert condition to binary and bit shift to place
            # ex: (1 << 2) + (0 << 1) + (1 << 0) = 0b101 = 5
            ruleIndex = bin((a << 2) | (b << 1) | c)

            # transform base 2 to base 10 (because of reasons)
            ruleIndex = int(ruleIndex, 2)

            # get rule by bit shifting to left and maskig with 1
            # ex: 0b110011 >> 3 = 0b110 = 6 and 0b110 & 0b001 = 0
            nextState.append((self.__rule >> ruleIndex) & 1)

        self.__state = nextState
        self.updateCanvas()
        
    def step10(self):
        # execute 10 steps
        for i in range(0, 10):
            self.step()

    def toggleThread(self):
        # start or stop the automatic execution of step method
        if self.__thread:
            self.b_run.config(text="Run")
            self.__thread = 0
        else:
            self.b_run.config(text="Stop")
            self.__thread = 1
            self.run()
            
    def run(self):
        # http://stackoverflow.com/questions/2223157/how-to-execute-a-function-asynchronously-every-60-seconds-in-python
        if self.__thread == 0:
            return

        # in case user exits program without stopping the thread
        try:
            # asynchronously call step method, beware of shared resources!
            self.step()
        except Exception as exc:
            # might be called when rule is changed during an automatic run
            print("Error: program doesn exist anymore!", exc)
            return
        
        # start a thread that calls this function in 0.1 seconds
        threading.Timer(0.1, self.run).start()

    def updateCanvas(self):
        # calculate cell size according to window size and cell number
        size = self.canvas.winfo_width() / self.__cells
        for i in range(0, self.__cells):
            color = "gray" if self.__state[i] else "black"
            # draw pixel from x1,y1 to x2,y2
            self.canvas.create_rectangle(i * size, self.__canvasLine * size, i * size + size, self.__canvasLine * size + size, fill = color)

        self.__canvasLine = (self.__canvasLine + 1) % self.__cells

    def clearCanvas(self):
        self.__canvasLine = 0
        self.canvas.delete(ALL)


startState = [0 for i in range(128)]
startState[64] = 1

ca = CellularAutomata()
ca.setCells(128)
ca.setRule(30)
ca.setState(startState)
ca.start()
