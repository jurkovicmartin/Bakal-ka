# Main window

import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from scripts.parameters_window import ParametersWindow
from scripts.simulation import simulate, getValues, getPlot

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
        self.sourceButton = tk.Button(self.schemeFrame, text="Optical source", command=lambda: self.showParametersPopup(self.sourceButton))
        self.modulatorButton = tk.Button(self.schemeFrame, text="Modulator", command=lambda: self.showParametersPopup(self.modulatorButton))
        self.channelButton = tk.Button(self.schemeFrame, text="Fiber channel", command=lambda: self.showParametersPopup(self.channelButton))
        self.recieverButton = tk.Button(self.schemeFrame, text="Reciever", command=lambda: self.showParametersPopup(self.recieverButton))
        # Aplifier button initially hidden
        self.amplifierButton = tk.Button(self.schemeFrame, text="Pre-amplifier", command=lambda: self.showParametersPopup(self.amplifierButton))

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

        # Attention label
        self.attentionLabel = tk.Label(self.optionsFrame, text="")
        self.attentionLabel.pack()

        # Start simulation
        self.simulateButton = tk.Button(self.optionsFrame, text="Simulate", command=self.startSimulation)
        self.simulateButton.pack()

        # Quit
        self.quitButton = tk.Button(self.optionsFrame, text="Quit", command=self.terminateApp)
        self.quitButton.pack()

        ### OUTPUTS TAB

        # Frames

        self.valuesFrame = tk.Frame(self.outputsFrame)
        self.plotsFrame = tk.Frame(self.outputsFrame)

        self.valuesFrame.pack()
        self.plotsFrame.pack()

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

        # plots frame

        self.plotsTxFrame = tk.Frame(self.plotsFrame)
        self.plotsRxFrame = tk.Frame(self.plotsFrame)

        self.plotsTxFrame.grid(row=0, column=0)
        self.plotsRxFrame.grid(row=0, column=1)

        # Tx plots
        self.infTxButton = tk.Button(self.plotsTxFrame, text="Show modulation signal", command=lambda: self.showGraph(self.infTxButton))
        self.conTxButton = tk.Button(self.plotsTxFrame, text="Show Tx constellation diagram", command=lambda: self.showGraph(self.conTxButton))
        self.psdTxButton = tk.Button(self.plotsTxFrame, text="Show Tx PSD", command=lambda: self.showGraph(self.psdTxButton))
        self.sigTxButton = tk.Button(self.plotsTxFrame, text="Show Tx signal in time", command=lambda: self.showGraph(self.sigTxButton))
        self.eyeTxButton = tk.Button(self.plotsTxFrame, text="Show Tx eyediagram", command=lambda: self.showGraph(self.eyeTxButton))
        
        self.infTxButton.pack()
        self.psdTxButton.pack()
        self.conTxButton.pack()
        self.sigTxButton.pack()
        self.eyeTxButton.pack()

        # Rx plots
        self.infRxButton = tk.Button(self.plotsRxFrame, text="Show detected signal", command=lambda: self.showGraph(self.infRxButton))
        self.conRxButton = tk.Button(self.plotsRxFrame, text="Show Rx constellation diagram", command=lambda: self.showGraph(self.conRxButton))
        self.psdRxButton = tk.Button(self.plotsRxFrame, text="Show Rx PSD", command=lambda: self.showGraph(self.psdRxButton))
        self.sigRxButton = tk.Button(self.plotsRxFrame, text="Show Rx signal in time", command=lambda: self.showGraph(self.sigRxButton))
        self.eyeRxButton = tk.Button(self.plotsRxFrame, text="Show Rx eyediagram", command=lambda: self.showGraph(self.eyeRxButton))

        self.infRxButton.pack()
        self.psdRxButton.pack()
        self.conRxButton.pack()
        self.sigRxButton.pack()
        self.eyeRxButton.pack()

        # Close plots button
        self.closeplotsButton = tk.Button(self.plotsFrame, text="Close all showed plots", command=self.closeGraphsWindows)
        self.closeplotsButton.grid(row=1, column=0, columnspan=2)

        # Frames with buttons that will be disabled when doing configuration
        self.buttonFrames = [self.schemeFrame, self.optionsFrame, self.plotsFrame, self.plotsTxFrame, self.plotsRxFrame]
 
        ### VARIABLES
        
        # Testing values
        self.sourceParameters = {"Power":10, "Frequency":193.1, "Linewidth":1000, "RIN":0}
        self.modulatorParameters = {"Type":"MZM"}
        self.channelParameters = {"Length":20, "Attenuation":0.2, "Dispersion":16}
        self.recieverParameters = {"Type":"Photodiode", "Ideal":True}
        self.amplifierParameters = {"Gain":4, "Noise":3}
        self.amplifierParameters = None

        # Parameters of scheme blocks
        # need set values to 0 not None
        # self.sourceParameters = None
        # self.modulatorParameters = None
        # self.channelParameters = None
        # self.recieverParameters = None
        # self.amplifierParameters = None
        
        # General parameters
        # SpS = samples per symbol, Rs = symbol rate, Fs sampling frequency, Ts sampling period
        self.generalParameters = {"SpS": 8, "Rs": 10 ** 3}
        self.generalParameters.update({"Fs": self.generalParameters.get("SpS") * self.generalParameters.get("Rs")})
        self.generalParameters.update({"Ts": 1 / self.generalParameters.get("Fs")})

        # Simulation results variables
        self.plots = {}
        self.simulationResults = None

        self.root.mainloop()



    ### METHODS
    
    def terminateApp(self):
        """
        Terminate the app. Closes main window and all other opened windows.
        """
        # Toplevels windows (graphs)
        self.closeGraphsWindows()
        # Main window
        self.root.destroy()

    def startSimulation(self):
        """
        Start of simulation.
        Main function button.
        """
        # Not all parameters provided
        if not self.checkSimulationStart(): return

        self.updateGeneralParameters()

        self.plots.clear()

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
            
            self.attentionCheck()
        else:
            # Remove amplifier button
            self.amplifierButton.grid_forget()
            self.recieverButton.grid(row=0, column=3)

            self.attentionCheck()


    def showParametersPopup(self, clickedButton):
        """
        Show Toplevel popup window to set parametrs.
        """
        # Disable the other buttons when a popup is open
        self.disableButtons()

        # Open a new popup
        if clickedButton == self.sourceButton:
            ParametersWindow(self, clickedButton, "source", self.getParameters, self.sourceParameters)
        elif clickedButton == self.modulatorButton:
            ParametersWindow(self, clickedButton, "modulator", self.getParameters, self.modulatorParameters)
        elif clickedButton == self.channelButton:
            ParametersWindow(self, clickedButton, "channel", self.getParameters, self.channelParameters)
        elif clickedButton == self.recieverButton:
            ParametersWindow(self, clickedButton, "reciever", self.getParameters, self.recieverParameters)
        elif clickedButton == self.amplifierButton:
            ParametersWindow(self, clickedButton, "amplifier", self.getParameters, self.amplifierParameters)
        else: raise Exception("Unexpected error")

        
    def disableButtons(self):
        """
        Disable buttons when window to set parameters is opened
        """
        for frame in self.buttonFrames:
            for button in frame.winfo_children():
                if isinstance(button, tk.Button):
                    button.config(state="disabled")


    def enableButtons(self):
        """
        Enable buttons when parameters have been set
        """
        for frame in self.buttonFrames:
            for button in frame.winfo_children():
                if isinstance(button, tk.Button):
                    button.config(state="normal")


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
        self.berLabel.config(text=f"BER: {outputValues.get('BER'):.3}")
        self.serLabel.config(text=f"SER: {outputValues.get('SER'):.3}")
        self.snrLabel.config(text=f"SNR: {outputValues.get('SNR'):.3} dB")

        self.powerTxWLabel.config(text=f"Tx power: {outputValues.get('powerTxW'):.3} W")
        self.powerTxdBmLabel.config(text=f"Tx power: {outputValues.get('powerTxdBm'):.3} dBm")
        self.powerRxWLabel.config(text=f"Rx power: {outputValues.get('powerRxW'):.3} W")
        self.powerRxdBmLabel.config(text=f"Tx power: {outputValues.get('powerRxdBm'):.3} dBm")


    def showGraph(self, clickedButton):
        """
        Show graph in the app. Graph is defined by clickedButton.
        """
        # Trying to show plots without simulation data
        if self.simulationResults is None:
            messagebox.showerror("Showing error", "You must start simulation first.")
            return

        # Define which button was clicked to get rigth plot
        if clickedButton == self.infTxButton:
            type = "informationTx"
            title = "Modulation signal"
        elif clickedButton == self.infRxButton:
            type = "informationRx"
            title = "Detected signal"
        elif clickedButton == self.conTxButton:
            type ="constellationTx"
            title = "Tx constellation diagram"
        elif clickedButton == self.conRxButton:
            type = "constellationRx"
            title = "Rx constellation diagram"
        elif clickedButton == self.psdTxButton:
            type = "psdTx"
            title = "Tx power spectral density"
        elif clickedButton == self.psdRxButton:
            type = "psdRx"
            title = "Rx power spectral density"
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

        # Graph was showed once before
        if type in self.plots:
            plot = self.plots.get(type)
            self.displayPlot(plot, title)

        # Graph will be shown for the first time
        else:
            plot = getPlot(type, title,  self.simulationResults, self.generalParameters)
            self.displayPlot(plot, title)
            self.plots.update({type:plot})


    def displayPlot(self, plot, title: str):
        """
        Creates Toplevel popup window to show plot.
        """
        # Creates the window
        popupGraph = tk.Toplevel()
        popupGraph.geometry("1000x600")
        popupGraph.title(title)

        # Shows the plot
        canvas = FigureCanvasTkAgg(plot[0], master=popupGraph)
        canvas.draw()
        canvas.get_tk_widget().pack(side="top", fill="both", expand=1)


    def closeGraphsWindows(self):
        """
        Closes all opened Toplevel windows.
        """
        for window in self.root.winfo_children():
            if isinstance(window, tk.Toplevel):
                window.destroy()

    
    def attentionCheck(self):
        """
        Checks for attention for combination of ideal channel and pre-amplifier. Also updates the attention label.
        """
        if self.channelParameters.get("Ideal") and self.amplifierCheckVar.get():
            self.attentionLabel.config(text="Attention, when using ideal channel the pre-amplifier will be ignored!")
        else:
            self.attentionLabel.config(text="")