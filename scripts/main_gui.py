# Main window

import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from scripts.popup_window import PopupWindow
from scripts.simulation import simulate, getValues, getFigure

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
        self.outputsFrame = ttk.Frame(self.notebookFrame)

        self.optionsFrame.pack()
        self.outputsFrame.pack()

        self.notebookFrame.add(self.optionsFrame, text="Input options")
        self.notebookFrame.add(self.outputsFrame, text="Outputs")

        ### OPTIONS TAB

        # Options tab frames
        self.schemeFrame = tk.Frame(self.optionsFrame)
        self.generalFrame = tk.Frame(self.optionsFrame)

        self.schemeFrame.pack()
        self.generalFrame.pack()

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

        # Simulate button to start simulation
        self.simulateButton = tk.Button(self.optionsFrame, text="Simulate", command=self.startSimulation)
        self.simulateButton.pack()

        ### OUTPUTS TAB

        # Frames

        self.valuesFrame = tk.Frame(self.outputsFrame)
        self.graphsFrame = tk.Frame(self.outputsFrame)

        self.valuesFrame.pack()
        self.graphsFrame.pack()

        # Values frame

        self.powerTxWLabel = tk.Label(self.valuesFrame, text="Tx power:")
        self.powerTxdBmLabel = tk.Label(self.valuesFrame, text="Tx power:")
        self.powerRxWLabel = tk.Label(self.valuesFrame, text="Rx power:")
        self.powerRxdBmLabel = tk.Label(self.valuesFrame, text="Rx power:")

        self.powerTxWLabel.pack()
        self.powerTxdBmLabel.pack()
        self.powerRxWLabel.pack()
        self.powerRxdBmLabel.pack()

        self.berLabel = tk.Label(self.valuesFrame, text="BER:")
        self.serLabel = tk.Label(self.valuesFrame, text="SER:")
        self.snrLabel = tk.Label(self.valuesFrame, text="SNR:")

        self.berLabel.pack()
        self.serLabel.pack()
        self.snrLabel.pack()

        # Graphs frame

        self.psdTxButton = tk.Button(self.graphsFrame, text="Show Tx PSD", command=lambda: self.showGraph(self.psdTxButton))
        self.conTxButton = tk.Button(self.graphsFrame, text="Show Tx constellation diagram", command=lambda: self.showGraph(self.conTxButton))
        self.conRxButton = tk.Button(self.graphsFrame, text="Show Rx constellation diagram", command=lambda: self.showGraph(self.conRxButton))
        self.sigTxButton = tk.Button(self.graphsFrame, text="Show Tx signal in time", command=lambda: self.showGraph(self.sigTxButton))
        self.sigRxButton = tk.Button(self.graphsFrame, text="Show Rx signal in time", command=lambda: self.showGraph(self.sigRxButton))
        self.eyeTxButton = tk.Button(self.graphsFrame, text="Show Tx eyediagram", command=lambda: self.showGraph(self.eyeTxButton))
        self.eyeRxButton = tk.Button(self.graphsFrame, text="Show Rx eyediagram", command=lambda: self.showGraph(self.eyeRxButton))
        
        self.psdTxButton.pack()
        self.conTxButton.pack()
        self.conRxButton.pack()
        self.sigTxButton.pack()
        self.sigRxButton.pack()
        self.eyeTxButton.pack()
        self.eyeRxButton.pack()        

        ### VARIABLES
        
        # For testing default values
        self.sourceParameters = {"Power":0.1, "Frequency":193100000000000, "Linewidth":1000, "RIN":0}
        self.modulatorParameters = {"Type":"MZM"}
        self.channelParameters = {"Length":20, "Attenuation":0.2, "Dispersion":16}
        self.recieverParameters = {"Type":"Photodiode"}
        self.amplifierParameters = {"Gain":4, "Noise":3}

        # Parameters of scheme blocks
        # self.sourceParameters = None
        # self.modulatorParameters = None
        # self.channelParameters = None
        # self.recieverParameters = None
        # self.amplifierParameters = None
        
        # General parameters
        self.generalParameters = {"SpS": 16, "Rs": 10 ** 9}
        self.generalParameters.update({"Fs": self.generalParameters.get("SpS") * self.generalParameters.get("Rs")})
        self.generalParameters.update({"Ts": 1 / self.generalParameters.get("Fs")})

        # Track popup windows to allow only one to be opened
        self.currentPopup = None

        self.root.mainloop()

    def startSimulation(self):
        """
        Start of simulation.
        Main function button.
        """
        if not self.checkSimulationStart(): return

        self.updateGeneralParameters()

        # Simulation
        self.simulationResults = simulate(self.generalParameters, self.sourceParameters, self.modulatorParameters, self.channelParameters, self.recieverParameters, self.amplifierParameters)
        
        # Showing results
        # Values to show
        outputValues = getValues(self.simulationResults, self.generalParameters)
        
        # Actual showing in the app
        self.showValues(outputValues)

        messagebox.showinfo("Simulation status", "Simulation succesfully completed")


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

        # Setting order options for selected modulation format
        if self.mFormatComboBox.get() == "OOK":
            orderOptions = ["2"]
            # Disable modulation order combobox for OOK format
            self.mOrderCombobox.config(state="disabled")
        elif self.mFormatComboBox.get() == "PAM":
            orderOptions = ["2", "4"]
            # Enable modulation order combobox
            self.mOrderCombobox.config(state="readonly")
        elif self.mFormatComboBox.get() == "PSK":
            orderOptions = ["2", "4", "8", "16"]
            # Enable modulation order combobox
            self.mOrderCombobox.config(state="readonly")
        elif self.mFormatComboBox.get() == "QAM":
            orderOptions = ["4", "16", "64"]
            # Enable modulation order combobox
            self.mOrderCombobox.config(state="readonly")
        else: raise Exception("Unexpected error")

        # Sets new options to modulation order combobox
        self.mOrderCombobox.config(values=orderOptions)
        self.mOrderCombobox.set(orderOptions[0])

    def updateGeneralParameters(self):
        """
        Update general parameters with values from editable fields.
        """

        self.generalParameters.update({"Format": self.mFormatComboBox.get().lower(), "Order": int(self.mOrderCombobox.get())})

        # OOK is created same as 2 order PAM
        if self.mFormatComboBox.get() == "OOK":
            self.generalParameters.update({"Format": "pam"})

    
    def showValues(self, outputValues: dict):
        """
        Show values from dictionary in the app.
        """
        self.berLabel.config(text=f"BER: {outputValues.get('BER')}")
        self.serLabel.config(text=f"SER: {outputValues.get('SER')}")
        self.snrLabel.config(text=f"SNR: {outputValues.get('SNR')} dB")

        self.powerTxWLabel.config(text=f"Tx power: {outputValues.get('powerTxW')} W")
        self.powerTxdBmLabel.config(text=f"Tx power: {outputValues.get('powerTxdBm')} dBm")
        self.powerRxWLabel.config(text=f"Rx power: {outputValues.get('powerRxW')} W")
        self.powerRxdBmLabel.config(text=f"Tx power: {outputValues.get('powerRxdBm')} dBm")


    def showGraph(self, clickedButton):
        """
        Show graph in the app. Graph is defined by clickedButton.
        """
        # Trying to show plots without simulation data
        if self.simulationResults is None:
            messagebox.showerror("Showing error", "You must start simulation first.")
            return

        # Define which button was clicked to get rigth plot
        if clickedButton == self.psdTxButton:
            type = "psdTx"
            title = "Tx power spectral density"
        elif clickedButton == self.conTxButton:
            type ="constellationTx"
            title = "Tx constellation diagram"
        elif clickedButton == self.conRxButton:
            type = "constellationRx"
            title = "Rx constellation diagram"
        elif clickedButton == self.sigTxButton:
            type = "signalTx"
            title = "Tx signal in time"
        elif clickedButton == self.sigRxButton:
            type = "signalRx"
            title = "Rx signal in time"
        elif clickedButton == self.eyeTxButton:
            type = "eyediagramTx"
            title = "Tx eyediagram"
        elif clickedButton == self.eyeRxButton:
            type = "eyediagramRx"
            title = "Rx eyediagram"
        else: raise Exception("Unexcpected error")

        figure = getFigure(type, self.simulationResults, self.generalParameters)

        self.popupGraph(title, figure)

    
    def popupGraph(self, title: str, figure):
        """
        Popup window to show the figure.
        """
        # Create window
        popup = tk.Toplevel()
        popup.geometry("1000x600")
        popup.title(title)

        # Show figure
        canvas = FigureCanvasTkAgg(figure, master=popup)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)