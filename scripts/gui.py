import tkinter as tk
from tkinter import ttk

import modulations as md

class Gui:
    def __init__(self):
        self.root = tk.Tk()

        self.root.title("Optical modulaton simulation application")

        self.titleLabel = tk.Label(self.root, text="Optical modulaton simulation application")
        self.titleLabel.pack(padx=10, pady=10)

        # Choosing modulation format
        self.mFormatLabel = tk.Label(self.root, text="Modulation formats")
        self.mFormatLabel.pack()
        self.mFormatComboBox = ttk.Combobox(self.root, values=["OOK", "PAM", "PSK", "QAM"], state='readonly')
        self.mFormatComboBox.set("OOK")
        self.mFormatComboBox.pack(padx=10, pady=10)

        # Choosing modulation order
        self.mOrderLabel = tk.Label(self.root, text="Order of modulation")
        self.mOrderLabel.pack()
        self.mOrderCombobox = ttk.Combobox(self.root, values=["2", "4", "8", "16", "32", "64"], state='readonly')
        self.mOrderCombobox.set("2")
        self.mOrderCombobox.pack(padx=10, pady=10)

        self.simulateButton = tk.Button(self.root, text="Simulate", command=self.simulate)
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

        print(modulationOrder)

        md.simulateModulation(modulationFormat, modulationOrder)