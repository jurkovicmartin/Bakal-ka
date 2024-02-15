# popup_window.py

import tkinter as tk

class PopupWindow:
    def __init__(self, parent_gui, parent_button):
        self.parent_gui = parent_gui
        self.parent_button = parent_button
        self.popup = tk.Toplevel()
        self.popup.title("Popup Window")

        # Entry field
        self.entry = tk.Entry(self.popup)
        self.entry.grid(row=0, column=0)

        # Button to set text in the main button
        set_text_button = tk.Button(self.popup, text="Set Text", command=self.set_text)
        set_text_button.grid(row=1, column=0)

        # Bind the popup window's closing event to the parent's method
        self.popup.protocol("WM_DELETE_WINDOW", self.close_popup)

    def set_text(self):
        text = self.entry.get()
        self.parent_button.config(text=text)
        self.close_popup()

    def close_popup(self):
        # Enable the parent buttons and destroy the popup window
        self.parent_gui.enable_buttons()
        self.popup.destroy()