import tkinter as tk
from tkinter import ttk

from scripts.popup_window import PopupWindow

class Gui:
    def __init__(self):
        self.root = tk.Tk()

        # self.root.wm_state("zoomed")
        self.root.geometry("1000x600")
        self.root.title("Optical modulaton simulation application")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Notebook tabs frame
        self.notebookFrame = ttk.Notebook(self.root)
        self.notebookFrame.grid(row=0, column=0, sticky="nsew")

        # Tabs
        self.optionsFrame = ttk.Frame(self.notebookFrame)
        self.graphsFrame = ttk.Frame(self.notebookFrame)
        self.valuesFrame = ttk.Frame(self.notebookFrame)

        self.optionsFrame.pack()
        self.graphsFrame.pack()
        self.valuesFrame.pack()

        self.notebookFrame.add(self.optionsFrame, text="Options")
        self.notebookFrame.add(self.graphsFrame, text="Graphs")
        self.notebookFrame.add(self.valuesFrame, text="Values")

        # Communication chain buttons
        self.sourceButton = tk.Button(self.optionsFrame, text="Optical source", command=lambda: self.showPopup(self.sourceButton))
        self.modulatorButton = tk.Button(self.optionsFrame, text="Modulator", command=lambda: self.showPopup(self.modulatorButton))
        self.channelButton = tk.Button(self.optionsFrame, text="Fiber channel", command=lambda: self.showPopup(self.channelButton))
        self.recieverButton = tk.Button(self.optionsFrame, text="Reciever", command=lambda: self.showPopup(self.recieverButton))
        # Aplifier button initially hidden
        self.amplifierButton = tk.Button(self.optionsFrame, text="Pre-amplifier", command=lambda: self.showPopup(self.amplifierButton))

        self.sourceButton.grid(row=0, column=0)
        self.modulatorButton.grid(row=0, column=1)
        self.channelButton.grid(row=0, column=2)
        self.recieverButton.grid(row=0, column=3)

        # Checkbutton for including / excluding channel pre-amplifier
        self.checkVar = tk.BooleanVar()
        self.amplifierCheckbutton = tk.Checkbutton(self.optionsFrame, text="Add channel pre-amplifier", variable=self.checkVar, command=self.amplifierCheckbuttonChange)
        
        self.amplifierCheckbutton.grid(row=1, column=0)

        # Simulate button to start simulation
        self.simulateButton = tk.Button(self.optionsFrame, text="Simulate", command=self.simulate)
        self.simulateButton.grid(row=1, column=1)

        self.currentPopup = None

        self.root.mainloop()

    def simulate(self):
        pass

    def amplifierCheckbuttonChange(self):
        if self.checkVar.get():
            # Show amplifier button
            self.amplifierButton.grid(row=0, column=3)
            self.recieverButton.grid(row=0, column=4)
        else:
            # Remove amplifier button
            self.amplifierButton.grid_forget()
            self.recieverButton.grid(row=0, column=3)

    def showPopup(self, parentButton):
        """
        Show popup window to set parametrs
        """
        # Disable the other buttons when a popup is open
        self.disableButtons()

        # Open a new popup
        if parentButton == self.sourceButton:
            self.currentPopup = PopupWindow(self, parentButton, "source")
        elif parentButton == self.modulatorButton:
            self.currentPopup = PopupWindow(self, parentButton, "modulator")
        elif parentButton == self.channelButton:
            self.currentPopup = PopupWindow(self, parentButton, "channel")
        elif parentButton == self.recieverButton:
            self.currentPopup = PopupWindow(self, parentButton, "reciever")
        elif parentButton == self.amplifierButton:
            self.currentPopup = PopupWindow(self, parentButton, "amplifier")
        else: raise Exception("Unexpected if statement")

        

    def disableButtons(self):
        for button in [self.sourceButton, self.modulatorButton, self.channelButton, self.recieverButton, self.amplifierButton]:
            button.config(state=tk.DISABLED)

    def enableButtons(self):
        for button in [self.sourceButton, self.modulatorButton, self.channelButton, self.recieverButton, self.amplifierButton]:
            button.config(state=tk.NORMAL)

        # Reset the currently open popup
        self.currentPopup = None