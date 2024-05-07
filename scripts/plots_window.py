# Popup window to show graphs

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PlotWindow:
    def __init__(self, type: str, title: str, plots: tuple):
        """
        Class to creates popup window to show graphical outputs.

        Parameters
        ----
        type: type of output (electrical / optical / spectrum / ...)

        plots: tuple with figure objects (Tx, RX)
        """
        self.type = type
        self.title = title
        self.plots = plots
        self.popupGui()



    def popupGui(self):
        """
        Creates popup gui for setting parameters.
        """
        
        self.popup = tk.Toplevel()
        #self.popup.geometry("1000x600")
        self.popup.wm_state("zoomed")
        self.popup.title(self.title)

        self.titleLabel = tk.Label(self.popup, text=self.title)
        self.titleLabel.grid(row=0, column=0)

        # Create a canvas to contain the frame with plots
        self.canvas = tk.Canvas(self.popup, width=1000, height=600)
        self.canvas.grid(row=1, column=0)

        # Create a frame to contain the plots
        self.plotFrame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.plotFrame, anchor='nw')

        # Show 3 plots
        if self.type == "optical" or self.type == "spectrum":
            # Source plot
            self.canvasTx = FigureCanvasTkAgg(figure= self.plots[2], master=self.plotFrame)
            self.canvasTx.draw()
            self.canvasTx.get_tk_widget().pack()

            # Tx plot
            self.canvasTx = FigureCanvasTkAgg(figure= self.plots[0], master=self.plotFrame)
            self.canvasTx.draw()
            self.canvasTx.get_tk_widget().pack()

            # Rx plot
            self.canvasRx = FigureCanvasTkAgg(figure= self.plots[1], master=self.plotFrame)
            self.canvasRx.draw()
            self.canvasRx.get_tk_widget().pack()

        # Show 2 plots
        else:
            # Tx plot
            self.canvasTx = FigureCanvasTkAgg(figure= self.plots[0], master=self.plotFrame)
            self.canvasTx.draw()
            self.canvasTx.get_tk_widget().pack()

            # Rx plot
            self.canvasRx = FigureCanvasTkAgg(figure= self.plots[1], master=self.plotFrame)
            self.canvasRx.draw()
            self.canvasRx.get_tk_widget().pack()

        self.closeButton = tk.Button(self.popup, text="Close", command=self.closePopup)
        self.closeButton.grid(row=2, column=0)

         # Add a scrollbar
        self.scrollbar = ttk.Scrollbar(self.popup, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Bind scroll event to canvas
        self.plotFrame.bind("<Configure>", self.on_configure)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)

    def on_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")


    def closePopup(self):
        """
        Closes popup window.
        """
        self.popup.destroy()
