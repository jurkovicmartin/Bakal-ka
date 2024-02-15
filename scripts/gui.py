import tkinter as tk
from tkinter import ttk

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

    def show_popup(self, button):
        popup = tk.Toplevel(self.root)
        popup.title("Popup Window")

        # Entry field
        entry = tk.Entry(popup)
        entry.grid(row=0, column=0)

        # Button to set text in the main button
        set_text_button = tk.Button(popup, text="Set Text", command=lambda: self.set_text(button, entry.get(), popup))
        set_text_button.grid(row=1, column=0)

    def set_text(self, button, text, popup):
        button.config(text=text)
        popup.destroy()

