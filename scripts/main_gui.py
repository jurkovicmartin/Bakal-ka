# Main window

import tkinter as tk
from tkinter import ttk, messagebox

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

        # Communication scheme buttons
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

        # Parameters of scheme blocks
        self.sourceParameters = None
        self.modulatorParameters = None
        self.channelParameters = None
        self.recieverParameters = None
        self.amplifierParameters = None

        # Checkbutton for including / excluding channel pre-amplifier
        self.amplifierCheckVar = tk.BooleanVar()
        self.amplifierCheckbutton = tk.Checkbutton(self.optionsFrame, text="Add channel pre-amplifier", variable=self.amplifierCheckVar, command=self.amplifierCheckbuttonChange)
        
        self.amplifierCheckbutton.grid(row=1, column=0)

        # Simulate button to start simulation
        self.simulateButton = tk.Button(self.optionsFrame, text="Simulate", command=self.simulate)
        self.simulateButton.grid(row=1, column=1)

        self.currentPopup = None

        self.root.mainloop()

    def simulate(self):
        """
        Start of simulation.
        Main function button.
        """
        if not self.checkSimulationStart(): return

        print("OK")
        


    def amplifierCheckbuttonChange(self):
        """
        Including / exluding amplifier from the scheme.
        """
        if self.amplifierCheckVar.get():
            # Show amplifier button
            self.amplifierButton.grid(row=0, column=3)
            self.recieverButton.grid(row=0, column=4)
        else:
            # Remove amplifier button
            self.amplifierButton.grid_forget()
            self.recieverButton.grid(row=0, column=3)

    def showPopup(self, clickedButton):
        """
        Show popup window to set parametrs.
        """
        # Disable the other buttons when a popup is open
        self.disableButtons()

        # Open a new popup
        if clickedButton == self.sourceButton:
            self.currentPopup = PopupWindow(self, clickedButton, "source", self.getParameters, self.sourceParameters)
        elif clickedButton == self.modulatorButton:
            self.currentPopup = PopupWindow(self, clickedButton, "modulator", self.getParameters, self.modulatorParameters)
        elif clickedButton == self.channelButton:
            self.currentPopup = PopupWindow(self, clickedButton, "channel", self.getParameters, self.channelParameters)
        elif clickedButton == self.recieverButton:
            self.currentPopup = PopupWindow(self, clickedButton, "reciever", self.getParameters, self.recieverParameters)
        elif clickedButton == self.amplifierButton:
            self.currentPopup = PopupWindow(self, clickedButton, "amplifier", self.getParameters, self.amplifierParameters)
        else: raise Exception("Unexpected if statement")

        

    def disableButtons(self):
        for button in [self.sourceButton, self.modulatorButton, self.channelButton, self.recieverButton, self.amplifierButton]:
            button.config(state=tk.DISABLED)

    def enableButtons(self):
        for button in [self.sourceButton, self.modulatorButton, self.channelButton, self.recieverButton, self.amplifierButton]:
            button.config(state=tk.NORMAL)

        # Reset the currently open popup
        self.currentPopup = None

    def getParameters(self, parameters: dict, buttonType: str):
        """
        Get parameters from popup window.

        Parameters
        -----
        parameters: variable to get

        buttonType: type of button pressed

            "source" / "modulator" / "channel" / "reciever" / "amplifier"
        """
        if buttonType == "source":
            self.sourceParameters = parameters
        elif buttonType == "modulator":
            self.modulatorParameters = parameters
        elif buttonType == "channel":
            self.channelParameters = parameters
        elif buttonType == "reciever":
            self.recieverParameters = parameters
        elif buttonType == "amplifier":
            self.amplifierParameters = parameters
        else: raise Exception("Unexpected error")

    def checkSimulationStart(self) -> bool:
        """
        Checks if all needed parameters are set
        """
        if self.sourceParameters is None:
            messagebox.showerror("Simulation error", "You must set source parameters.")
            return False
        elif self.modulatorParameters is None:
            messagebox.showerror("Simulation error", "You must set modulator parameters.")
            return False
        elif self.channelParameters is None:
            messagebox.showerror("Simulation error", "You must set channel parameters.")
            return False
        elif self.recieverParameters is None:
            messagebox.showerror("Simulation error", "You must set reciever parameters.")
            return False
        # Only if amplifier is included
        elif self.amplifierCheckVar.get() and self.amplifierParameters is None:
            messagebox.showerror("Simulation error", "You must set amplifier parameters.")
            return False
        else: return True