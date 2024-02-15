import tkinter as tk
from tkinter import ttk

from scripts.popup_window import PopupWindow

class Gui:
    def __init__(self):
        self.root = tk.Tk()

        # self.root.wm_state("zoomed")
        self.root.geometry("1000x600")
        self.root.title("Optical modulaton simulation application")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.notebookFrame = ttk.Notebook(self.root)
        self.notebookFrame.grid(row=0, column=0, sticky="nsew")

        # Tabs
        self.optionsFrame = ttk.Frame(self.notebookFrame)
        self.graphsFrame = ttk.Frame(self.notebookFrame)
        self.valuesFrame = ttk.Frame(self.notebookFrame)

        self.optionsFrame.pack()
        self.graphsFrame.pack()
        self.valuesFrame.pack()

        self.notebookFrame.add(self.optionsFrame, text="Options")
        self.notebookFrame.add(self.graphsFrame, text="Graphs")
        self.notebookFrame.add(self.valuesFrame, text="Values")

        # Create buttons 1-4
        self.button_1 = tk.Button(self.optionsFrame, text="1", command=lambda: self.show_popup(self.button_1))
        self.button_2 = tk.Button(self.optionsFrame, text="2", command=lambda: self.show_popup(self.button_2))
        self.button_3 = tk.Button(self.optionsFrame, text="3", command=lambda: self.show_popup(self.button_3))
        self.button_4 = tk.Button(self.optionsFrame, text="4", command=lambda: self.show_popup(self.button_4))

        # Create button 5 initially hidden
        self.button_5 = tk.Button(self.optionsFrame, text="5", command=lambda: self.show_popup(self.button_5))

        # Create a checkbutton and set its command to toggle_button_5
        self.check_var = tk.BooleanVar()
        self.checkbutton = tk.Checkbutton(self.optionsFrame, text="Add Button 5", variable=self.check_var, command=self.toggle_button_5)

        # Place buttons and checkbutton on the grid
        self.button_1.grid(row=0, column=0)
        self.button_2.grid(row=0, column=1)
        self.button_3.grid(row=0, column=2)
        self.button_4.grid(row=0, column=3)
        self.checkbutton.grid(row=1, column=0, columnspan=4)

        self.current_popup = None

        self.root.mainloop()

    def toggle_button_5(self):
        if self.check_var.get():
            # If the checkbutton is checked, display button_5
            self.button_5.grid(row=0, column=3)
            self.button_4.grid(row=0, column=4)
        else:
            # If the checkbutton is unchecked, hide button_5 and restore the original order
            self.button_5.grid_forget()
            self.button_4.grid(row=0, column=3)

    def show_popup(self, parent_button):
        # Disable the other buttons when a popup is open
        self.disable_buttons()

        # Open a new popup
        self.current_popup = PopupWindow(self, parent_button)

    def disable_buttons(self):
        # Disable all buttons except the currently open popup's parent button
        for button in [self.button_1, self.button_2, self.button_3, self.button_4, self.button_5]:
            button.config(state=tk.DISABLED)

    def enable_buttons(self):
        # Enable all buttons
        for button in [self.button_1, self.button_2, self.button_3, self.button_4, self.button_5]:
            button.config(state=tk.NORMAL)

        # Reset the currently open popup to None
        self.current_popup = None

