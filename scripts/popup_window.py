# Popup window for setting components parameters

import tkinter as tk
from tkinter import ttk

from scripts.parameters_functions import checkParameter

class PopupWindow:
    def __init__(self, parentGui, parentButton, buttonType, callback):
        """
        Class to creates popup window for setting parameters.

        Parameters
        -----
        buttonType: string
            type of button pressed

            "source" / "modulator" / "channel" / "reciever" / "amplifier"

        callback: function to return parameters values to the main gui
        """
        self.parentGui = parentGui
        self.parentButton = parentButton
        self.callback = callback
        self.popup = self.popupGui(buttonType)

        # Bind the popup window's closing event to the parent's method
        self.popup.protocol("WM_DELETE_WINDOW", self.closePopup)

    def popupGui(self, buttonType):
        """
        Creates popup gui for setting parameters.

        Parameters
        -----
        buttonType: string
            type of button pressed

            "source" / "modulator" / "channel" / "reciever" / "amplifier"

        Returns
        -----
        popup window: tkinter Toplevel object
        """

        self.popup = tk.Toplevel()
        self.popup.geometry("400x400")

        if buttonType == "source":
            self.popup.title("Parameters of optical source")

            self.titleLabel = tk.Label(self.popup, text="Parameters of optical source")
            self.titleLabel.grid(row=0, column=0, columnspan=2)

            # Setting parameters

            # Power
            self.lengthLabel = tk.Label(self.popup, text="Power of laser [W]")
            self.lengthLabel.grid(row=1, column=0)
            self.powerEntry = tk.Entry(self.popup)
            self.powerEntry.grid(row=1, column=1)

            # Frequency
            self.frequencyLabel = tk.Label(self.popup, text="Laser frequency [Hz]")
            self.frequencyLabel.grid(row=2, column=0)
            self.frequencyEntry = tk.Entry(self.popup)
            self.frequencyEntry.grid(row=2, column=1)

            # RIN noise
            self.rinLabel = tk.Label(self.popup, text="RIN noise")
            self.rinLabel.grid(row=3, column=0)
            self.rinEntry = tk.Entry(self.popup)
            self.rinEntry.grid(row=3, column=1)

            # Set button
            self.setButton = tk.Button(self.popup, text="Set parameters", command=lambda: self.setParameters(buttonType))
            self.setButton.grid(row=4, column=0, columnspan=2)

            return self.popup
        
        elif buttonType == "modulator":
            self.popup.title("Parameters of modulator")

            self.titleLabel = tk.Label(self.popup, text="Parameters of modulator")
            self.titleLabel.grid(row=0, column=0, columnspan=2)

            # Setting parameters

            # Type
            self.typeLabel = tk.Label(self.popup, text="Type of modulator")
            self.typeLabel.grid(row=1, column=0)
            self.typeCombobox = ttk.Combobox(self.popup, values=["PM", "MZM", "IQM"], state="readonly")
            self.typeCombobox.set("PM")
            self.typeCombobox.grid(row=1, column=1)

            # Set button
            self.setButton = tk.Button(self.popup, text="Set parameters", command=lambda: self.setParameters(buttonType))
            self.setButton.grid(row=2, column=0, columnspan=2)

            return self.popup
        
        elif buttonType == "channel":
            self.popup.title("Parameters of fiber channel")

            self.titleLabel = tk.Label(self.popup, text="Parameters of fiber channel")
            self.titleLabel.grid(row=0, column=0, columnspan=2)

            # Setting parameters

            # Length
            self.lengthLabel = tk.Label(self.popup, text="Length of fiber [km]")
            self.lengthLabel.grid(row=1, column=0)
            self.lengthEntry = tk.Entry(self.popup)
            self.lengthEntry.grid(row=1, column=1)

            # Attenuation
            self.attenuatinLabel = tk.Label(self.popup, text="Attenuation of fiber [dB/km]")
            self.attenuatinLabel.grid(row=2, column=0)
            self.attenuationEntry = tk.Entry(self.popup)
            self.attenuationEntry.grid(row=2, column=1)

            # Dispersion
            self.dispersionLabel = tk.Label(self.popup, text="Dispersion of fiber")
            self.dispersionLabel.grid(row=3, column=0)
            self.dispersionEntry = tk.Entry(self.popup)
            self.dispersionEntry.grid(row=3, column=1)

            # Set button
            self.setButton = tk.Button(self.popup, text="Set parameters", command=lambda: self.setParameters(buttonType))
            self.setButton.grid(row=4, column=0, columnspan=2)

            return self.popup
        
        elif buttonType == "reciever":
            self.popup.title("Parameters of reciever")

            self.titleLabel = tk.Label(self.popup, text="Parameters of reciever")
            self.titleLabel.grid(row=0, column=0, columnspan=2)

            # Setting parameters

            # Type
            self.typeLabel = tk.Label(self.popup, text="Type of reciever")
            self.typeLabel.grid(row=1, column=0)
            self.typeCombobox = ttk.Combobox(self.popup, values=["Diode", "Coherent", "Hybrid"], state="readonly")
            self.typeCombobox.set("Diode")
            self.typeCombobox.grid(row=1, column=1)

            # Set button
            self.setButton = tk.Button(self.popup, text="Set parameters", command=lambda: self.setParameters(buttonType))
            self.setButton.grid(row=2, column=0, columnspan=2)

            return self.popup
        
        elif buttonType == "amplifier":
            self.popup.title("Parameters of amplifier")

            self.titleLabel = tk.Label(self.popup, text="Parameters of amplifier")
            self.titleLabel.grid(row=0, column=0, columnspan=2)

            # Setting parameters

            # Gain
            self.gainLabel = tk.Label(self.popup, text="Gain of amplifier")
            self.gainLabel.grid(row=1, column=0)
            self.gainEntry = tk.Entry(self.popup)
            self.gainEntry.grid(row=1, column=1)

            # Noise
            self.noiseLabel = tk.Label(self.popup, text="Noise of amplifier")
            self.noiseLabel.grid(row=2, column=0)
            self.noiseEntry = tk.Entry(self.popup)
            self.noiseEntry.grid(row=2, column=1)

            # Set button
            self.setButton = tk.Button(self.popup, text="Set parameters", command=lambda: self.setParameters(buttonType))
            self.setButton.grid(row=3, column=0, columnspan=2)

            return self.popup
        
        else: raise Exception("Unexpected if statement")



    def closePopup(self):
        # Enable the parent buttons and destroy the popup window
        self.parentGui.enableButtons()
        self.popup.destroy()


    def setParameters(self, buttonType):
        """
        Set entried parameters.

        Parameters
        -----
        buttonType: string
            type of button pressed

            "source" / "modulator" / "channel" / "reciever" / "amplifier"

        """

        if buttonType == "source":
            # Showing in main gui
            parametersString = f"Laser\n\nPower: {self.powerEntry.get()} W\nFrequency: {self.frequencyEntry.get()} Hz\nRIN: {self.rinEntry.get()}"
            # Getting initial values
            parameters = {"Power":self.powerEntry.get(), "Frequency":self.frequencyEntry.get(), "RIN":self.rinEntry.get()}
            # Validating parameters values
            parameters = self.validateParameters(parameters)

            if parameters is None: return

        elif buttonType == "modulator":
            # Showing in main gui
            parametersString = f"{self.typeCombobox.get()}"

        elif buttonType == "channel":
            # Showing in main gui
            parametersString = f"Fiber channel\n\nLength: {self.lengthEntry.get()} km\nAttenuation: {self.attenuationEntry.get()} dB/km\nDispersion: {self.dispersionEntry.get()}"
            # Getting initial values
            parameters = {"Length":self.lengthEntry.get(), "Attenuation":self.attenuationEntry.get(), "Dispersion":self.dispersionEntry.get()}
            # Validating parameters values
            parameters = self.validateParameters(parameters)

            if parameters is None: return

        elif buttonType == "reciever":
            # Showing in main gui
            parametersString = f"{self.typeCombobox.get()}"
        
        elif buttonType == "amplifier":
            # Showing in main gui
            parametersString = f"Pre-amplifier\n\nGain: {self.gainEntry.get()}\nNoise: {self.noiseEntry.get()}"
            # Getting initial values
            parameters = {"Gain":self.gainEntry.get(), "Noise":self.noiseEntry.get()}
            # Validating parameters values
            parameters = self.validateParameters(parameters)

            if parameters is None: return
        
        else: raise Exception("Unexpected if statement")

        self.parentButton.config(text=parametersString)
        # Return parameters
        self.callback(parameters, buttonType)

        self.closePopup()

    
    def validateParameters(self, parameters):
        """
        Convert string parameters values to float and validate the inputed values.

        Parameters
        -----
        parameters: dictionary
            values are strings

        Returns
        -----
        parameters: dictionary
            values are floats

            None if some parameter is not ok
        """

        for key, value in parameters.items():
            checked = checkParameter(key, value, self.popup)
            if checked is None: return None
            else: parameters.update({key:checked})

        return parameters
  