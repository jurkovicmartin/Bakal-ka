
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from PIL import Image
from sys import platform
import winsound
import time

class MessageWindow:
    def __init__(self, master, type: str, title: str, message: str):
        """
        Show popup messages.

        Parameters
        -----
        type: succes / error
        """
        self.window = tk.Toplevel(master=master, bg="#1f1f1f")
        self.window.geometry("450x150")
        self.window.resizable(False, False)
        self.window.title(title)
        self.set_dark_theme()

        font = ("Helvetica", 16, "bold")

        if type == "succes":
            image = ctk.CTkImage(light_image=Image.open("img/ok_ico.png"), dark_image=Image.open("img/ok_ico.png"))
            self.window.iconbitmap("img/ok_ico.ico")
        elif type == "error":
            image = ctk.CTkImage(light_image=Image.open("img/not_ico.png"), dark_image=Image.open("img/not_ico.png"), size=(80, 80))
            self.window.iconbitmap("img/not_ico.ico")
        else:
            raise Exception("Unexpected error")
        
        self.imageLabel = ctk.CTkLabel(self.window, image=image, text="")
        self.imageLabel.pack(side= "left", padx=10, pady=10)

        self.messageLabel = ctk.CTkLabel(self.window, text=message, font=font)
        self.messageLabel.pack(side="right", padx=10, pady=10)

        # System is windows
        if platform == "win32":
            # Play alert sound
            time.sleep(1)
            winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS)
        else:
            pass

        #self.window.after(200, self.window.lift)


        # Create a dark-themed style for the Toplevel window
    def set_dark_theme(self):
        style = ttk.Style(self.window)
        style.theme_use('clam')  # Use an existing theme as base
        style.configure('.', background='#333', foreground='white')  # Set background and foreground colors
        style.map('.', background=[('disabled', '#333'), ('active', '#666')])  # Map disabled and active background colors
        # Add more configurations for specific widgets as needed




