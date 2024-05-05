# Popup window to show graphs

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PlotWindow:
    def __init__(self, title: str, plots: tuple):
        """
        Class to creates popup window to show graphical outputs.

        Parameters
        ----
        plots: tuple with figure objects (Tx, RX)
        """
        self.title = title
        self.plots = plots
        self.popupGui()



    def popupGui(self):
        """
        Creates popup gui for setting parameters.
        """
        
        self.popup = tk.Toplevel()
        self.popup.geometry("1000x600")
        self.popup.title(self.title)

        self.titleLabel = tk.Label(self.popup, text=self.title)
        self.titleLabel.grid(row=0, column=0)

       
        # Tx plot
        self.canvasTx = FigureCanvasTkAgg(figure= self.plots[0], master=self.popup)
        self.canvasTx.draw()
        self.canvasTx.get_tk_widget().grid(row=1, column=0)

        # Rx plot
        self.canvasRx = FigureCanvasTkAgg(figure= self.plots[1], master=self.popup)
        self.canvasRx.draw()
        self.canvasRx.get_tk_widget().grid(row=1, column=1)

        self.closeButton = tk.Button(self.popup, text="Close", command=self.closePopup)
        self.closeButton.grid(row=2, column=0)


    def closePopup(self):
        """
        Closes popup window.
        """
        self.popup.destroy()
