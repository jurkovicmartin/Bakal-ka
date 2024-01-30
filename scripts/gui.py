import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import modulations as md

class Gui:
    def __init__(self):
        self.root = tk.Tk()

        self.root.geometry("1000x600")
        self.root.title("Optical modulaton simulation application")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Frames
        self.notebookFrame = ttk.Notebook(self.root)
        self.notebookFrame.grid(row=0, column=0, sticky="nsew")

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


        # Options tab widgets
        self.titleLabel = tk.Label(self.optionsFrame, text="Optical modulaton simulation application")
        self.titleLabel.pack(padx=10, pady=10)

        # Choosing modulation format
        self.mFormatLabel = tk.Label(self.optionsFrame, text="Modulation formats")
        self.mFormatLabel.pack()
        self.mFormatComboBox = ttk.Combobox(self.optionsFrame, values=["OOK", "PAM", "PSK", "QAM"], state="readonly")
        self.mFormatComboBox.set("OOK")
        self.mFormatComboBox.pack(padx=10, pady=10)
        self.mFormatComboBox.bind("<<ComboboxSelected>>", self.modulationFormatChange)

        # Choosing modulation order
        self.mOrderLabel = tk.Label(self.optionsFrame, text="Order of modulation")
        self.mOrderLabel.pack()
        self.mOrderCombobox = ttk.Combobox(self.optionsFrame, values=["2"], state="readonly")
        self.mOrderCombobox.set("2")
        self.mOrderCombobox.pack(padx=10, pady=10)

        # Ideal / not ideal transmission
        self.tCheckbuttonState = tk.BooleanVar(value=True)
        self.transmissionCheckbutton = tk.Checkbutton(self.optionsFrame, text="Ideal transmission", variable=self.tCheckbuttonState)
        self.transmissionCheckbutton.pack(padx=10, pady=10)

        # Simulate button
        self.simulateButton = tk.Button(self.optionsFrame, text="Simulate", command=self.simulate)
        self.simulateButton.pack(padx=10, pady=10)

        self.root.mainloop()

    # FUNCTIONS

    def simulate(self):
        # Need to pass lowercase modulation formats
        modulationFormat = self.mFormatComboBox.get().lower()
        # Need to pass int
        modulationOrder = int(self.mOrderCombobox.get())
        transmissionConditions = self.tCheckbuttonState.get()

        # Showing one figure at the time
        cFrameWidgets = self.constellationFrame.winfo_children()
        if cFrameWidgets != []:
            # Hiding last shown canvas
            lastCanvas = cFrameWidgets[0]
            lastCanvas.pack_forget()
            cFrameWidgets.clear()

        # Show figure in app tab
        constelattionFigure = md.simulateConstellation(modulationFormat, modulationOrder, transmissionConditions)
        canvas = FigureCanvasTkAgg(constelattionFigure[0], master=self.constellationFrame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


    def modulationFormatChange(self, event):
        selectedOption = self.mFormatComboBox.get()

        # Setting order options for selected modulation format
        if selectedOption == "OOK":
            orderOptions = ["2"]
        elif selectedOption == "PAM":
            orderOptions = ["2", "4"]
        elif selectedOption == "PSK":
            orderOptions = ["2", "4", "8", "16"]
        elif selectedOption == "QAM":
            orderOptions = ["4", "16", "64"]
        else: print("Unexpected error of modulation choice")

        # Sets new options to modulation order combobox
        self.mOrderCombobox["values"] = orderOptions
        self.mOrderCombobox.set(orderOptions[0])
        