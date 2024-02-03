import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from scripts.simulations import simulatePAM, simulatePSK
from scripts.functions import checkNumber

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
        self.titleLabel = tk.Label(self.optionsFrame, text="Optical modulaton simulation application")
        self.titleLabel.pack(padx=10, pady=10)

        # Choosing modulation format
        self.mFormatLabel = tk.Label(self.optionsFrame, text="Modulation formats")
        self.mFormatLabel.pack()
        self.mFormatComboBox = ttk.Combobox(self.optionsFrame, values=["PAM", "PSK", "QAM"], state="readonly")
        self.mFormatComboBox.set("PAM")
        self.mFormatComboBox.pack(padx=10, pady=10)
        self.mFormatComboBox.bind("<<ComboboxSelected>>", self.modulationFormatChange)

        # Choosing modulation order
        self.mOrderLabel = tk.Label(self.optionsFrame, text="Order of modulation")
        self.mOrderLabel.pack()
        self.mOrderCombobox = ttk.Combobox(self.optionsFrame, values=["2", "4"], state="readonly")
        self.mOrderCombobox.set("2")
        self.mOrderCombobox.pack(padx=10, pady=10)

        # Simulate button
        self.simulateButton = tk.Button(self.optionsFrame, text="Simulate", command=self.simulate)
        self.simulateButton.pack(padx=10, pady=10)

        ### PARAMETERS

        # Length
        self.lengthLabel = tk.Label(self.optionsFrame, text="Length of fiber [km]")
        self.lengthLabel.pack(pady=10)
        self.lengthEntry = tk.Entry(self.optionsFrame)
        self.lengthEntry.insert(0, "0")
        self.lengthEntry.pack()

        # Power
        self.powerLabel = tk.Label(self.optionsFrame, text="Power of laser [W]")
        self.powerLabel.pack(pady=10)
        self.powerEntry = tk.Entry(self.optionsFrame)
        self.powerEntry.insert(0, "0")
        self.powerEntry.pack()

        ### OUTPUTS
        
        self.berLabel = tk.Label(self.optionsFrame, text="Bit error rate (BER):")
        self.berLabel.pack(pady=10)
        self.serLabel = tk.Label(self.optionsFrame, text="Symbol error rate (SER):")
        self.serLabel.pack(pady=10)
        self.snrLabel = tk.Label(self.optionsFrame, text="Estimated signal-to-noise ratio (SNR):")
        self.snrLabel.pack(pady=10)

        self.root.mainloop()

    ### METHODS
        
    def simulate(self):
        """
        Start simulation
        """
        # Getting simulation parameters        
        fiberLength = self.lengthEntry.get()
        laserPower = self.powerEntry.get()
        
        # Validating parameters
        parameters = self.checkParameters(fiberLength, laserPower)
        if parameters:
            fiberLength = parameters[0]
            laserPower = parameters[1]
        else: return

        # Getting remaining parameters
        modulationFormat = self.mFormatComboBox.get()
        modulationOrder = int(self.mOrderCombobox.get())

        if modulationFormat == "PAM":

            simulation = simulatePAM(modulationOrder, fiberLength, laserPower)
            self.displayPlots(simulation[0])
            self.displayValues(simulation[1])
            messagebox.showinfo("Status of simulation", "Simulation is succesfully completed.")

        elif modulationFormat == "PSK":
            
            simulation = simulatePSK(modulationOrder, fiberLength, laserPower)
            self.displayPlots(simulation[0])
            self.displayValues(simulation[1])
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
            list contains values

            expected order - [BER, SER, SNR]
        """
        self.berLabel["text"] = f"Bit error rate (BER): {values[0]}"
        self.serLabel["text"] = f"Symbol error rate (SER): {values[1]}"
        self.snrLabel["text"] = f"Estimated signal-to-noise ratio (SNR): {values[2]}"

    def checkParameters(self, length, power):
        """
        Checks if the parameters has valid values.

        Parameters
        ----
        length: string
            length of fiber
        
        power: string
            power of laser

        Returns
        -----
        parameters: list: float
            [length, power]
            
            None if parameters are not ok
        """
        parameters = []

        # Check length of fiber
        length = checkNumber(length)

        if length == 0:
            messagebox.showerror("Length input error", "Zero is not valid length!")
            return None
        elif length == -1:
            messagebox.showerror("Length input error", "Length cannot be negative!")
            return None
        elif length == -2:
            messagebox.showerror("Length input error", "Lentgh must be a number!")
            return None
        elif length == -3:
            messagebox.showerror("Length input error", "You must input length!")
            return None
        else:
            parameters.append(length)

        # Check power of laser
        power = checkNumber(power)

        if power == 0:
            messagebox.showerror("Power input error", "Zero is not valid power!")
            return None
        elif power == -1:
            messagebox.showerror("Power input error", "Power cannot be negative!")
            return None
        elif power == -2:
            messagebox.showerror("Power input error", "Power must be a number!")
            return None
        elif power == -3:
            messagebox.showerror("Power input error", "You must input power!")
            return None
        else:
            parameters.append(power)

        return parameters

