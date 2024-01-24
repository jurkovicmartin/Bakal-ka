import tkinter as tk
from tkinter import ttk

import modulations as md

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Gui:
    def __init__(self):
        self.root = tk.Tk()

        self.root.geometry('1000x600')
        self.root.title("Optical modulaton simulation application")

        # Frames
        self.notebookFrame = ttk.Notebook(self.root)
        self.notebookFrame.pack(pady=10, expand=True)

        self.optionsFrame = ttk.Frame(self.notebookFrame)
        self.constellationFrame = ttk.Frame(self.notebookFrame)

        self.constellationFrame.pack(fill='both', expand=True)
        self.optionsFrame.pack(fill='both', expand=True)

        self.notebookFrame.add(self.optionsFrame, text="Options")
        self.notebookFrame.add(self.constellationFrame, text="Constelattion diagram")


        # Options tab widgeds
        self.titleLabel = tk.Label(self.optionsFrame, text="Optical modulaton simulation application")
        self.titleLabel.pack(padx=10, pady=10)

        # Choosing modulation format
        self.mFormatLabel = tk.Label(self.optionsFrame, text="Modulation formats")
        self.mFormatLabel.pack()
        self.mFormatComboBox = ttk.Combobox(self.optionsFrame, values=["OOK", "PAM", "PSK", "QAM"], state='readonly')
        self.mFormatComboBox.set("OOK")
        self.mFormatComboBox.pack(padx=10, pady=10)

        # Choosing modulation order
        self.mOrderLabel = tk.Label(self.optionsFrame, text="Order of modulation")
        self.mOrderLabel.pack()
        self.mOrderCombobox = ttk.Combobox(self.optionsFrame, values=["2", "4", "8", "16", "32", "64"], state='readonly')
        self.mOrderCombobox.set("2")
        self.mOrderCombobox.pack(padx=10, pady=10)

        self.simulateButton = tk.Button(self.optionsFrame, text="Simulate", command=self.simulate)
        self.simulateButton.pack(padx=10, pady=10)

        self.root.mainloop()

    def simulate(self):
        # OptiCommPy takes lowercase modulation formats (in Combobox is uppercase)
        modulationFormat = self.mFormatComboBox.get().lower()
        # get returns string and i need to pass int
        modulationOrder = int(self.mOrderCombobox.get())

        if modulationFormat == 'ook':
            # OOK has only order 2
            modulationOrder = 2

        # Show figure in app
        constelattionFigure = md.simulateConstellation(modulationFormat, modulationOrder)
        canvas = FigureCanvasTkAgg(constelattionFigure[0], master=self.constellationFrame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)