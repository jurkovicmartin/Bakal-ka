# Main window

# SpS = samples per symbol, Rs = symbol rate, Fs sampling frequency, Ts sampling period

import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from scripts.parameters_window import ParametersWindow
from scripts.simulation import simulate, getValues, getPlot
from scripts.parameters_functions import convertNumber

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
        self.generalFrame = tk.Frame(self.optionsFrame)
        self.schemeFrame = tk.Frame(self.optionsFrame)

        self.generalFrame.pack(pady=10)
        self.schemeFrame.pack(pady=10)

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

        # Choosing modulation format to map
        self.mFormatLabel = tk.Label(self.generalFrame, text="Modulation formats")
        self.mFormatComboBox = ttk.Combobox(self.generalFrame, values=["OOK", "PAM", "PSK", "QAM"], state="readonly")
        self.mFormatComboBox.set("OOK")
        self.mFormatComboBox.bind("<<ComboboxSelected>>", self.modulationFormatChange)
        self.mFormatLabel.grid(row=0, column=0)
        self.mFormatComboBox.grid(row=1, column=0)

        # Choosing modulation order to map
        self.mOrderLabel = tk.Label(self.generalFrame, text="Order of modulation")
        self.mOrderCombobox = ttk.Combobox(self.generalFrame, values=["2"], state="disabled")
        self.mOrderCombobox.set("2")
        self.mOrderLabel.grid(row=0, column=1)
        self.mOrderCombobox.grid(row=1, column=1)

        # Symbol rate
        self.symbolRateLabel = tk.Label(self.generalFrame, text="Symbol rate [symbols/s]")
        self.symbolRateEntry = tk.Entry(self.generalFrame)
        self.symbolRateEntry.insert(0, "1000")
        self.symbolRateLabel.grid(row=0, column=3)
        self.symbolRateEntry.grid(row=1, column=3)

        # Checkbutton for including / excluding channel pre-amplifier
        self.amplifierCheckVar = tk.BooleanVar()
        self.amplifierCheckbutton = tk.Checkbutton(self.generalFrame, text="Add channel pre-amplifier", variable=self.amplifierCheckVar, command=self.amplifierCheckbuttonChange)
        self.amplifierCheckbutton.grid(row=2, column=0)

        # Attention label for adding pre-amplifier
        self.attentionLabel = tk.Label(self.generalFrame, text="")
        self.attentionLabel.grid(row=2, column=1, columnspan=2)

        # Other

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
        self.powerTxWLabel.grid(row=0, column=0)
        self.powerTxdBmLabel.grid(row=0, column=1)
        self.powerRxWLabel.grid(row=1, column=0)
        self.powerRxdBmLabel.grid(row=1, column=1)

        self.transSpeedLabel = tk.Label(self.valuesFrame, text="Transmission speed:")
        self.snrLabel = tk.Label(self.valuesFrame, text="SNR:")
        self.berLabel = tk.Label(self.valuesFrame, text="BER:")
        self.serLabel = tk.Label(self.valuesFrame, text="SER:")
        self.transSpeedLabel.grid(row=2, column=0)
        self.snrLabel.grid(row=2, column=1)
        self.berLabel.grid(row=3, column=0)
        self.serLabel.grid(row=3, column=1)

        # plots frame

        self.plotsTxFrame = tk.Frame(self.plotsFrame)
        self.plotsRxFrame = tk.Frame(self.plotsFrame)

        self.plotsTxFrame.grid(row=0, column=0)
        self.plotsRxFrame.grid(row=0, column=1)

        # Tx plots
        self.infTxButton = tk.Button(self.plotsTxFrame, text="Show modulation signal", command=lambda: self.showGraph(self.infTxButton))
        self.conTxButton = tk.Button(self.plotsTxFrame, text="Show Tx constellation diagram", command=lambda: self.showGraph(self.conTxButton))
        self.spectrumTxButton = tk.Button(self.plotsTxFrame, text="Show Tx spectrum", command=lambda: self.showGraph(self.spectrumTxButton))
        self.sigTxButton = tk.Button(self.plotsTxFrame, text="Show Tx signal in time", command=lambda: self.showGraph(self.sigTxButton))
        self.eyeTxButton = tk.Button(self.plotsTxFrame, text="Show Tx eyediagram", command=lambda: self.showGraph(self.eyeTxButton))
        
        self.infTxButton.pack()
        self.spectrumTxButton.pack()
        self.conTxButton.pack()
        self.sigTxButton.pack()
        self.eyeTxButton.pack()

        # Rx plots
        self.infRxButton = tk.Button(self.plotsRxFrame, text="Show detected signal", command=lambda: self.showGraph(self.infRxButton))
        self.conRxButton = tk.Button(self.plotsRxFrame, text="Show Rx constellation diagram", command=lambda: self.showGraph(self.conRxButton))
        self.spectrumRxButton = tk.Button(self.plotsRxFrame, text="Show Rx spectrum", command=lambda: self.showGraph(self.spectrumRxButton))
        self.sigRxButton = tk.Button(self.plotsRxFrame, text="Show Rx signal in time", command=lambda: self.showGraph(self.sigRxButton))
        self.eyeRxButton = tk.Button(self.plotsRxFrame, text="Show Rx eyediagram", command=lambda: self.showGraph(self.eyeRxButton))

        self.infRxButton.pack()
        self.spectrumRxButton.pack()
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
        # self.sourceParameters = {"Power":10, "Frequency":193.1, "Ideal":True}
        # self.modulatorParameters = {"Type":"MZM"}
        # self.channelParameters = {"Length":20, "Ideal":True}
        # self.recieverParameters = {"Type":"Photodiode", "Bandwidth":1000, "Resolution":1, "Ideal":False}
        # self.amplifierParameters = None

        # self.generalParameters = {"SpS": 8, "Rs": 10 ** 3}

        # Inicial parameters
        self.sourceParameters = {"Power": 0, "Frequency": 0, "Linewidth": 0, "PowerNoise": 0, "PhaseNoise": 0, "Ideal": False}
        self.modulatorParameters = {"Type": "MZM"}
        self.channelParameters = {"Length": 0, "Attenuation": 0, "Dispersion": 0, "Ideal": False}
        self.recieverParameters = {"Type": "Photodiode", "Bandwidth": 0, "Resolution": 0, "Ideal": False}
        self.amplifierParameters = {"Gain": 0, "Noise": 0, "Ideal": False}
        # Store initial parameters to check for simulation start
        self.initialParameters = {"Source": self.sourceParameters, "Modulator": self.modulatorParameters, 
                                  "Channel": self.channelParameters, "Reciever": self.recieverParameters, "Amplifier": self.amplifierParameters}

        self.generalParameters = {"SpS":8}

        # Default parameters (testing)
        self.sourceParameters = {"Power": 10, "Frequency": 191.7, "Linewidth": 1, "PowerNoise": 0, "PhaseNoise": 0, "Ideal": True}
        self.modulatorParameters = {"Type": "MZM"}
        self.channelParameters = {"Length": 40, "Attenuation": 0, "Dispersion": 0, "Ideal": True}
        self.recieverParameters = {"Type": "Photodiode", "Bandwidth": 1000, "Resolution": 0.5, "Ideal": False}
        self.amplifierParameters = {"Gain": 0, "Noise": 0, "Ideal": False}



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
        # Get values of general parameters
        self.updateGeneralParameters()

        # Not all parameters provided
        if not self.checkSimulationStart(): return
        
        # Clear plots for new simulation (othervise old graphs would be shown)
        self.plots.clear()

        # Simulation
        self.simulationResults = simulate(self.generalParameters, self.sourceParameters, self.modulatorParameters,
                                           self.channelParameters, self.recieverParameters, self.amplifierParameters)
        
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
        # Some general parameter was not ok
        if not self.updateGeneralParameters():
            return

        # Disable the other buttons when a popup is open
        self.disableButtons()

        # Open a new popup
        if clickedButton == self.sourceButton:
            ParametersWindow(self, clickedButton, "source", self.getParameters, self.sourceParameters, self.generalParameters)
        elif clickedButton == self.modulatorButton:
            ParametersWindow(self, clickedButton, "modulator", self.getParameters, self.modulatorParameters, self.generalParameters)
        elif clickedButton == self.channelButton:
            ParametersWindow(self, clickedButton, "channel", self.getParameters, self.channelParameters, self.generalParameters)
        elif clickedButton == self.recieverButton:
            ParametersWindow(self, clickedButton, "reciever", self.getParameters, self.recieverParameters, self.generalParameters)
        elif clickedButton == self.amplifierButton:
            ParametersWindow(self, clickedButton, "amplifier", self.getParameters, self.amplifierParameters, self.generalParameters)
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
        # There is only 1 general paramete (Fs), means some problem with setting other parameters
        if len(self.generalParameters) == 1:
            return False
        # Source parameters are same as initial
        elif self.sourceParameters == self.initialParameters.get("Source"):
            messagebox.showerror("Simulation error", "You must set source parameters.")
            return False
        # elif self.modulatorParameters == self.initialParameters.get("Modulator"):
        #     messagebox.showerror("Simulation error", "You must set modulator parameters.")
        #     return False
        elif self.channelParameters == self.initialParameters.get("Channel"):
            messagebox.showerror("Simulation error", "You must set channel parameters.")
            return False
        elif self.recieverParameters == self.initialParameters.get("Reciever"):
            messagebox.showerror("Simulation error", "You must set reciever parameters.")
            return False
        # Only if amplifier is included
        elif self.amplifierCheckVar.get() and self.amplifierParameters == self.initialParameters.get("Amplifier"):
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
            orderOptions = ["4"]
            # Enable modulation order combobox
            self.mOrderCombobox.config(state="readonly")
        elif self.mFormatComboBox.get() == "PSK":
            orderOptions = ["2", "4", "8", "16"]
            # Enable modulation order combobox
            self.mOrderCombobox.config(state="readonly")
        elif self.mFormatComboBox.get() == "QAM":
            orderOptions = ["4", "16", "64", "256"]
            # Enable modulation order combobox
            self.mOrderCombobox.config(state="readonly")
        else: raise Exception("Unexpected error")

        # Sets new options to modulation order combobox
        self.mOrderCombobox.config(values=orderOptions)
        self.mOrderCombobox.set(orderOptions[0])


    def updateGeneralParameters(self) -> bool:
        """
        Update general parameters with values from editable fields.

        Returns
        ----
        False: some parameter was not ok

        True: all general parameters are ok
        """
        # Modulation format and order
        self.generalParameters.update({"Format": self.mFormatComboBox.get().lower(), "Order": int(self.mOrderCombobox.get())})

        # OOK is created same as 2 order PAM
        if self.mFormatComboBox.get() == "OOK":
            self.generalParameters.update({"Format": "pam"})

        # Check symbol rate
        Rs, isEmpty = convertNumber(self.symbolRateEntry.get())
        if Rs is None and isEmpty:
            messagebox.showerror("Symbol rate input error", "You must input symbol rate!")
            return False
        elif Rs is None and not isEmpty:
            messagebox.showerror("Symbol rate input error", "Symbol rate must be a number!")
            return False
        elif Rs != int(Rs):
            messagebox.showerror("Symbol rate input error", "Symbol rate must whole number!")
            return False
        elif Rs < 1000:
            messagebox.showerror("Symbol rate input error", "Symbol rate must be atleast 1000")
            return False
        # Rs is ok
        else:
            self.generalParameters.update({"Rs":Rs})
        
        self.generalParameters.update({"Fs":self.generalParameters.get("SpS") * self.generalParameters.get("Rs")})
        self.generalParameters.update({"Ts":1 / self.generalParameters.get("Fs")})

        return True

    
    def showValues(self, outputValues: dict):
        """
        Show values from dictionary in the app.
        """
        # ' ' insted of " " because of f-string 
        self.powerTxWLabel.config(text=f"Tx power: {outputValues.get('powerTxW'):.3} W")
        self.powerTxdBmLabel.config(text=f"Tx power: {outputValues.get('powerTxdBm'):.3} dBm")
        self.powerRxWLabel.config(text=f"Rx power: {outputValues.get('powerRxW'):.3} W")
        self.powerRxdBmLabel.config(text=f"Tx power: {outputValues.get('powerRxdBm'):.3} dBm")
        
        self.showTransSpeed(outputValues.get("Speed"))
        self.snrLabel.config(text=f"SNR: {outputValues.get('SNR'):.3} dB")
        self.berLabel.config(text=f"BER: {outputValues.get('BER'):.3}")
        self.serLabel.config(text=f"SER: {outputValues.get('SER'):.3}")


    def showTransSpeed(self, transmissionSpeed: float):
        """
        Shows transmission speed in the app with reasonable units
        """
        if transmissionSpeed >= 10**9:
            self.transSpeedLabel.config(text=f"Transmission speed: {transmissionSpeed / 10**9} Gb/s")
        elif transmissionSpeed >= 10**6:
            self.transSpeedLabel.config(text=f"Transmission speed: {transmissionSpeed / 10**6} Mb/s")
        elif transmissionSpeed >= 10**3:
            self.transSpeedLabel.config(text=f"Transmission speed: {transmissionSpeed / 10**3} kb/s")
        # Should not happen
        else:
            self.transSpeedLabel.config(text=f"Transmission speed: {transmissionSpeed} b/s")


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
        elif clickedButton == self.spectrumTxButton:
            type = "spectrumTx"
            title = "Tx optical spectrum"
        elif clickedButton == self.spectrumRxButton:
            type = "spectrumRx"
            title = "Rx optical spectrum"
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
            plot = getPlot(type, title,  self.simulationResults, self.generalParameters, self.sourceParameters)
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