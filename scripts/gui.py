import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from scripts.simulations import simulatePAM, simulatePSK, createPlots, calculateValues
from scripts.functions import convertNumber

class Gui:
    def __init__(self):
        self.root = tk.Tk()

        # self.root.wm_state("zoomed")
        self.root.geometry("1000x600")
        self.root.title("Optical modulaton simulation application")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        ### FRAMES
        # Main frame
        self.notebookFrame = ttk.Notebook(self.root)
        self.notebookFrame.grid(row=0, column=0, sticky="nsew")

        # Tabs
        self.optionsFrame = ttk.Frame(self.notebookFrame)
        self.constellationFrame = ttk.Frame(self.notebookFrame)
        self.psdFrame = ttk.Frame(self.notebookFrame)
        self.tSignalFrame = ttk.Frame(self.notebookFrame)
        self.eyeDiagramFrame = ttk.Frame(self.notebookFrame)

        # Configuration to even sizing
        self.optionsFrame.columnconfigure(0, weight=1)
        self.optionsFrame.columnconfigure(1, weight=1)
        self.optionsFrame.rowconfigure(0, weight=1)
        self.optionsFrame.rowconfigure(1, weight=1)

        self.optionsFrame.pack()
        self.constellationFrame.pack()
        self.psdFrame.pack()
        self.tSignalFrame.pack()
        self.eyeDiagramFrame.pack()

        self.notebookFrame.add(self.optionsFrame, text="Options")
        self.notebookFrame.add(self.constellationFrame, text="Constelattion diagram")
        self.notebookFrame.add(self.psdFrame, text="Power spectral density")
        self.notebookFrame.add(self.tSignalFrame, text="Signal in time")
        self.notebookFrame.add(self.eyeDiagramFrame, text="Eye diagram")

        ### OPTIONS
        
        # Frames
        self.modulationFrame = tk.Frame(self.optionsFrame)
        self.parametersFrame = tk.Frame(self.optionsFrame)
        self.outputsFrame = tk.Frame(self.optionsFrame)
        self.buttonsFrame = tk.Frame(self.optionsFrame)

        self.modulationFrame.grid(row=0, column=0, sticky="nsew")
        self.parametersFrame.grid(row=1, column=0, sticky="nsew")
        self.outputsFrame.grid(row=0, column=1, sticky="nsew")
        self.buttonsFrame.grid(row=1, column=1, sticky="nsew")

        ### Modulation
        self.modulationLable = tk.Label(self.modulationFrame, text="Modulation parameters")
        self.modulationLable.pack(pady=10)

        # Choosing modulation format
        self.mFormatLabel = tk.Label(self.modulationFrame, text="Modulation formats")
        self.mFormatLabel.pack(pady=10)
        self.mFormatComboBox = ttk.Combobox(self.modulationFrame, values=["PAM", "PSK", "QAM"], state="readonly")
        self.mFormatComboBox.set("PAM")
        self.mFormatComboBox.pack()
        self.mFormatComboBox.bind("<<ComboboxSelected>>", self.modulationFormatChange)

        # Choosing modulation order
        self.mOrderLabel = tk.Label(self.modulationFrame, text="Order of modulation")
        self.mOrderLabel.pack(pady=10)
        self.mOrderCombobox = ttk.Combobox(self.modulationFrame, values=["2", "4"], state="readonly")
        self.mOrderCombobox.set("2")
        self.mOrderCombobox.pack()

        # Power
        self.powerLabel = tk.Label(self.modulationFrame, text="Power of laser [W]")
        self.powerLabel.pack(pady=10)
        self.powerEntry = tk.Entry(self.modulationFrame)
        self.powerEntry.insert(0, "1")
        self.powerEntry.pack()


        ### Parameters
        self.parametersLabel = tk.Label(self.parametersFrame, text="Channel parameters")
        self.parametersLabel.pack(pady=10)

        # Length
        self.lengthLabel = tk.Label(self.parametersFrame, text="Length of fiber [km]")
        self.lengthLabel.pack(pady=10)
        self.lengthEntry = tk.Entry(self.parametersFrame)
        self.lengthEntry.insert(0, "1")
        self.lengthEntry.pack()

        # Loss
        self.lossLabel = tk.Label(self.parametersFrame, text="Fiber loss [dB/km]")
        self.lossLabel.pack(pady=10)
        self.lossEntry = tk.Entry(self.parametersFrame)
        self.lossEntry.insert(0, "0.2")
        self.lossEntry.pack()

        # Dispersion
        self.dispersionLabel = tk.Label(self.parametersFrame, text="Fiber dispersion [ps/nm/km]")
        self.dispersionLabel.pack(pady=10)
        self.dispersionEntry = tk.Entry(self.parametersFrame)
        self.dispersionEntry.insert(0, "16")
        self.dispersionEntry.pack()

        # Include channel amplifier
        self.checkButtonVar = tk.BooleanVar()
        self.amplifierCheckbutton = tk.Checkbutton(self.parametersFrame, text="Include EDFA pre amplifier to match fiber loss", variable=self.checkButtonVar)
        self.amplifierCheckbutton.pack(pady=10)

        ### Value outputs

        self.powerModWLabel = tk.Label(self.outputsFrame, text="Power of modulated signal:")
        self.powerModWLabel.pack(pady=10)
        self.powerModdBLabel = tk.Label(self.outputsFrame, text="Power of modulated signal:")
        self.powerModdBLabel.pack(pady=10)
        self.powerRecWLabel = tk.Label(self.outputsFrame, text="Power of recieved signal:")
        self.powerRecWLabel.pack(pady=10)
        self.powerRecdBLabel = tk.Label(self.outputsFrame, text="Power of recieved signal:")
        self.powerRecdBLabel.pack(pady=10)
    
        self.berLabel = tk.Label(self.outputsFrame, text="Bit error rate (BER):")
        self.berLabel.pack(pady=10)
        self.serLabel = tk.Label(self.outputsFrame, text="Symbol error rate (SER):")
        self.serLabel.pack(pady=10)
        self.snrLabel = tk.Label(self.outputsFrame, text="Estimated signal-to-noise ratio (SNR):")
        self.snrLabel.pack(pady=10)

        ### Buttons

        self.simulateButton = tk.Button(self.buttonsFrame, text="Simulate", command=self.simulate)
        self.simulateButton.pack(pady=10)
        
        self.root.mainloop()

    ### METHODS
        
    def simulate(self):
        """
        Start simulation
        """

        # Getting simulation parameters        
        laserPower = self.powerEntry.get()
        fiberLength = self.lengthEntry.get()
        fiberLoss = self.lossEntry.get()
        fiberDispersion = self.dispersionEntry.get()        
        
        # Validating parameters
        laserPower = self.checkParameter("Power", laserPower)
        if laserPower is None: return
        fiberLength = self.checkParameter("Length", fiberLength)
        if fiberLength is None: return
        fiberLoss = self.checkParameter("Loss", fiberLoss)
        if fiberLoss is None: return
        fiberDispersion = self.checkParameter("Dispersion", fiberDispersion)
        if fiberDispersion is None: return

        # Getting remaining parameters
        modulationFormat = self.mFormatComboBox.get()
        modulationOrder = int(self.mOrderCombobox.get())
        amplifierBool = self.checkButtonVar.get()

        # Setting general simulation parameters
        SpS = 16     # samples per symbol
        Rs = 10e9    # Symbol rate
        Fs = Rs*SpS  # Sampling frequency
        Ts = 1/Fs    # Sampling period

        simulationParameters = [SpS, Rs, Fs, Ts]

        if modulationFormat == "PAM":

            # [bitsTx, symbolsTx, modulation signal, modulated signal, recieved signal, detected signal, symbolsRx, bitsRx]
            #   0       1           2                   3                   4               5               6          7
            simulation = simulatePAM(simulationParameters, modulationOrder, fiberLength, amplifierBool, laserPower, fiberLoss, fiberDispersion)
            simulationPlots = createPlots(simulation[1], simulation[2], simulation[3], simulation[4], simulation[5], simulation[6], simulationParameters)
            self.displayPlots(simulationPlots)
            simulationValues = calculateValues("pam", modulationOrder, simulation[0], simulation[3], simulation[4], simulation[7])
            self.displayValues(simulationValues)
            messagebox.showinfo("Status of simulation", "Simulation is succesfully completed.")

        elif modulationFormat == "PSK":
            
            # [bitsTx, symbolsTx, modulation signal, modulated signal, recieved signal, detected signal, symbolsRx, bitsRx]
            #   0       1           2                   3                   4               5               6          7
            simulation = simulatePSK(simulationParameters, modulationOrder, fiberLength, amplifierBool, laserPower, fiberLoss, fiberDispersion)
            simulationPlots = createPlots(simulation[1], simulation[2], simulation[3], simulation[4], simulation[5], simulation[6], simulationParameters)
            self.displayPlots(simulationPlots)
            simulationValues = calculateValues("psk", modulationOrder, simulation[0], simulation[3], simulation[4], simulation[7])
            self.displayValues(simulationValues)
            messagebox.showinfo("Status of simulation", "Simulation is succesfully completed.")
            
        elif modulationFormat == "QAM":
            pass
        else: print("Unexpected modulation format error")


    def modulationFormatChange(self, event):
        """
        Change modulation order options when modulation format is changed
        """
        selectedOption = self.mFormatComboBox.get()

        # Setting order options for selected modulation format
        if selectedOption == "PAM":
            orderOptions = ["2", "4"]
        elif selectedOption == "PSK":
            orderOptions = ["2", "4", "8", "16"]
        elif selectedOption == "QAM":
            orderOptions = ["4", "16", "64"]
        else: print("Unexpected modulation choice error")

        # Sets new options to modulation order combobox
        self.mOrderCombobox["values"] = orderOptions
        self.mOrderCombobox.set(orderOptions[0])


    def displayPlots(self, figures):
        """
        Display figures in application.

        Parameters
        -----
        figures: list
            list contains tuples (Figure, Axes)

            expected order - [psd, Tx t, Rx t, Tx eye, Rx eye, Tx con, Rx con]
        """
        # Clearing tabs content
        frames = [self.psdFrame, self.eyeDiagramFrame, self.tSignalFrame, self.constellationFrame]

        for f in frames:
            widgets = f.winfo_children()
            if widgets != []:
                for w in widgets:
                    w.pack_forget()
                widgets.clear()

        figures[5][1].set_title("Tx constellation diagram")
        figures[6][1].set_title("Rx constellation diagram")

        # psd
        canvas = FigureCanvasTkAgg(figures[0][0], master=self.psdFrame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Tx t
        canvas = FigureCanvasTkAgg(figures[1][0], master=self.tSignalFrame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Rx T
        canvas = FigureCanvasTkAgg(figures[2][0], master=self.tSignalFrame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

        # Tx eye
        canvas = FigureCanvasTkAgg(figures[3][0], master=self.eyeDiagramFrame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Rx eye
        canvas = FigureCanvasTkAgg(figures[4][0], master=self.eyeDiagramFrame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

        # Tx con
        canvas = FigureCanvasTkAgg(figures[5][0], master=self.constellationFrame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        
        # Rx con
        canvas = FigureCanvasTkAgg(figures[6][0], master=self.constellationFrame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

    
    def displayValues(self, values):
        """
        Display number values in application.

        Parameters
        -----
        values: list
            [BER, SER, SNR, Tx W, Tx dB, Rx W, Rx dB]
        """
        self.berLabel["text"] = f"Bit error rate (BER): {values[0]}"
        self.serLabel["text"] = f"Symbol error rate (SER): {values[1]}"
        self.snrLabel["text"] = f"Estimated signal-to-noise ratio (SNR): {values[2]} dB"

        self.powerModWLabel["text"] = f"Power of modulated signal: {values[3]} W"
        self.powerModdBLabel["text"] = f"Power of modulated signal: {values[4]} dB"
        self.powerRecWLabel["text"] = f"Power of recieved signal: {values[5]} W"
        self.powerRecdBLabel["text"] = f"Power of recieved signal: {values[6]} dB"


    def checkParameter(self, parameterName, parameterValue):
        """
        Checks if the parameters has valid values and coverts it to float.

        Parameters
        ----
        parameterName: string
            name of parameter
        
        parameterValue: string
            value to check and covert

        Returns
        -----
        parameter: float
            converted value
            
            None if parameter is not ok
        """

        # Parameters that can be 0
        specialParameters = ["Loss", "Dispersion"]

        # Check length of fiber
        value = convertNumber(parameterValue)

        if value == 0 and parameterName in specialParameters:
            return 0
        elif value == 0:
            messagebox.showerror(f"{parameterName} input error", f"Zero is not valid {parameterName}!")
            return None
        elif value == -1:
            messagebox.showerror(f"{parameterName} input error", f"{parameterName} cannot be negative!")
            return None
        elif value == -2:
            messagebox.showerror(f"{parameterName} input error", f"{parameterName} must be a number!")
            return None
        elif value == -3:
            messagebox.showerror(f"{parameterName} input error", f"You must input {parameterName}!")
            return None
        else:
            return value

