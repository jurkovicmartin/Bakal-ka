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

        # Options tab frames
        self.schemeFrame = ttk.Frame(self.optionsFrame)
        self.generalFrame = ttk.Frame(self.optionsFrame)
        self.outputsFrame = ttk.Frame(self.optionsFrame)

        self.schemeFrame.pack()
        self.generalFrame.pack()
        self.outputsFrame.pack()

        # Scheme frame

        # Communication scheme buttons
        self.sourceButton = tk.Button(self.schemeFrame, text="Optical source", command=lambda: self.showPopup(self.sourceButton))
        self.modulatorButton = tk.Button(self.schemeFrame, text="Modulator", command=lambda: self.showPopup(self.modulatorButton))
        self.channelButton = tk.Button(self.schemeFrame, text="Fiber channel", command=lambda: self.showPopup(self.channelButton))
        self.recieverButton = tk.Button(self.schemeFrame, text="Reciever", command=lambda: self.showPopup(self.recieverButton))
        # Aplifier button initially hidden
        self.amplifierButton = tk.Button(self.schemeFrame, text="Pre-amplifier", command=lambda: self.showPopup(self.amplifierButton))

        self.sourceButton.grid(row=0, column=0)
        self.modulatorButton.grid(row=0, column=1)
        self.channelButton.grid(row=0, column=2)
        self.recieverButton.grid(row=0, column=3)

        # General frame

        # Checkbutton for including / excluding channel pre-amplifier
        self.amplifierCheckVar = tk.BooleanVar()
        self.amplifierCheckbutton = tk.Checkbutton(self.generalFrame, text="Add channel pre-amplifier", variable=self.amplifierCheckVar, command=self.amplifierCheckbuttonChange)
        self.amplifierCheckbutton.grid(row=0, column=0)

        # Choosing modulation format to map
        self.mFormatLabel = tk.Label(self.generalFrame, text="Modulation formats")
        self.mFormatLabel.grid(row=0, column=1)
        self.mFormatComboBox = ttk.Combobox(self.generalFrame, values=["OOK", "PAM", "PSK", "QAM"], state="readonly")
        self.mFormatComboBox.set("OOK")
        self.mFormatComboBox.grid(row=1, column=1)
        self.mFormatComboBox.bind("<<ComboboxSelected>>", self.modulationFormatChange)

        # Choosing modulation order to map
        self.mOrderLabel = tk.Label(self.generalFrame, text="Order of modulation")
        self.mOrderLabel.grid(row=0, column=2)
        self.mOrderCombobox = ttk.Combobox(self.generalFrame, values=["2"], state="disabled")
        self.mOrderCombobox.set("2")
        self.mOrderCombobox.grid(row=1, column=2)

        # Outputs frame

        # Checkbuttons to choose what outputs to display

        # PSD
        self.psdCheckVar = tk.BooleanVar()
        self.psdCheckbutton = tk.Checkbutton(self.outputsFrame, text="Show Tx PSD", variable=self.psdCheckVar)
        self.psdCheckbutton.grid(row=0, column=0)

        # Tx constellation
        self.conTxCheckVar = tk.BooleanVar()
        self.conTxCheckbutton = tk.Checkbutton(self.outputsFrame, text="Show Tx constellation", variable=self.conTxCheckVar)
        self.conTxCheckbutton.grid(row=0, column=1)

        # Rx constellation
        self.conRxCheckVar = tk.BooleanVar()
        self.conRxCheckbutton = tk.Checkbutton(self.outputsFrame, text="Show Rx constellation", variable=self.conRxCheckVar)
        self.conRxCheckbutton.grid(row=1, column=1)

        # Tx signal in time
        self.signalTxCheckVar = tk.BooleanVar()
        self.signalTxCheckbutton = tk.Checkbutton(self.outputsFrame, text="Show Tx signal in time", variable=self.signalTxCheckVar)
        self.signalTxCheckbutton.grid(row=0, column=2)
      
        # Rx signal in time
        self.signalRxCheckVar = tk.BooleanVar()
        self.signalRxCheckbutton = tk.Checkbutton(self.outputsFrame, text="Show Rx signal in time", variable=self.signalRxCheckVar)
        self.signalRxCheckbutton.grid(row=1, column=2)
        
        # Tx eyediagram
        self.eyeTxCheckVar = tk.BooleanVar()
        self.eyeTxCheckbutton = tk.Checkbutton(self.outputsFrame, text="Show Tx eyediagram", variable=self.eyeTxCheckVar)
        self.eyeTxCheckbutton.grid(row=0, column=3)

        # Rx eyediagram
        self.eyeRxCheckVar = tk.BooleanVar()
        self.eyeRxCheckbutton = tk.Checkbutton(self.outputsFrame, text="Show Rx eyediagram", variable=self.eyeRxCheckVar)
        self.eyeRxCheckbutton.grid(row=1, column=3)

        # Simulate button to start simulation
        self.simulateButton = tk.Button(self.optionsFrame, text="Simulate", command=self.simulate)
        self.simulateButton.pack()

        # Variables

        # Parameters of scheme blocks
        self.sourceParameters = None
        self.modulatorParameters = None
        self.channelParameters = None
        self.recieverParameters = None
        self.amplifierParameters = None
        
        # General parameters
        self.generalParameters = {"SpS": 16, "Rs": 10 ** 9}
        self.generalParameters.update({"Fs": self.generalParameters.get("SpS") * self.generalParameters.get("Rs")})
        self.generalParameters.update({"Ts": 1 / self.generalParameters.get("Fs")})

        # Track popup windows to allow only one to be opened
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
        else: raise Exception("Unexpected error")

        

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

    def modulationFormatChange(self, event):
        """
        Change modulation order options when modulation format is changed
        """
        selectedOption = self.mFormatComboBox.get()

        # Setting order options for selected modulation format
        if selectedOption == "OOK":
            orderOptions = ["2"]
            # Disable modulation order combobox for OOK format
            self.mOrderCombobox.config(state="disabled")
        elif selectedOption == "PAM":
            orderOptions = ["2", "4"]
            # Enable modulation order combobox
            self.mOrderCombobox.config(state="readonly")
        elif selectedOption == "PSK":
            orderOptions = ["2", "4", "8", "16"]
            # Enable modulation order combobox
            self.mOrderCombobox.config(state="readonly")
        elif selectedOption == "QAM":
            orderOptions = ["4", "16", "64"]
            # Enable modulation order combobox
            self.mOrderCombobox.config(state="readonly")
        else: raise Exception("Unexpected error")

        # Sets new options to modulation order combobox
        self.mOrderCombobox.config(values=orderOptions)
        self.mOrderCombobox.set(orderOptions[0])