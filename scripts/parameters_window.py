# Popup window for setting components parameters

import tkinter as tk
from tkinter import ttk

from scripts.parameters_functions import checkParameter

class ParametersWindow:
    def __init__(self, parentGui, parentButton, buttonType: str, callback, defaultParameters: dict):
        """
        Class to creates popup window for setting parameters.

        Parameters
        -----
        buttonType: type of button pressed

            "source" / "modulator" / "channel" / "reciever" / "amplifier"

        callback: function to return parameters values to the main gui

        defaultParameters: values to input into entry fields

            used when popup window isnt shown for the first time
        """
        self.parentGui = parentGui
        self.parentButton = parentButton
        self.type = buttonType
        self.callback = callback
        self.defaultParameters = defaultParameters
        self.popup = self.popupGui()

        # Bind the popup window's closing event to the parent's method
        self.popup.protocol("WM_DELETE_WINDOW", self.closePopup)

    ### METHODS

    def popupGui(self) -> tk.Toplevel:
        """
        Creates popup gui for setting parameters.

        Returns
        -----
        popup window: tkinter Toplevel object
        """
        self.popup = tk.Toplevel()
        self.popup.geometry("400x400")

        if self.type == "source":
            self.popup.title("Parameters of optical source")

            self.titleLabel = tk.Label(self.popup, text="Parameters of optical source")
            self.titleLabel.grid(row=0, column=0, columnspan=2)

            # Setting parameters

            # Power
            self.lengthLabel = tk.Label(self.popup, text="Power of laser [dBm]")
            self.lengthLabel.grid(row=1, column=0)
            self.powerEntry = tk.Entry(self.popup)
            self.powerEntry.grid(row=1, column=1)

            # Frequency
            self.frequencyLabel = tk.Label(self.popup, text="Laser frequency [THz]")
            self.frequencyLabel.grid(row=2, column=0)
            self.frequencyEntry = tk.Entry(self.popup)
            self.frequencyEntry.grid(row=2, column=1)

            # Linewidth
            self.linewidthLabel = tk.Label(self.popup, text="Linewidth [Hz]")
            self.linewidthLabel.grid(row=3, column=0)
            self.linewidthEntry = tk.Entry(self.popup)
            self.linewidthEntry.grid(row=3, column=1)

            # RIN noise
            self.rinLabel = tk.Label(self.popup, text="RIN noise")
            self.rinLabel.grid(row=4, column=0)
            self.rinEntry = tk.Entry(self.popup)
            self.rinEntry.grid(row=4, column=1)

            # Ideal parameters checkbutton
            self.sourceCheckVar = tk.BooleanVar()
            self.idealCheckbutton = tk.Checkbutton(self.popup, text="Ideal parameters", variable=self.sourceCheckVar, command=self.idealCheckbuttonChange)
            self.idealCheckbutton.grid(row=5, column=0, columnspan=2)
    
            # Set button
            self.setButton = tk.Button(self.popup, text="Set parameters", command=self.setParameters)
            self.setButton.grid(row=6, column=0, columnspan=2)

            self.setDefaultParameters()

            return self.popup
        
        elif self.type == "modulator":
            self.popup.title("Parameters of modulator")

            self.titleLabel = tk.Label(self.popup, text="Parameters of modulator")
            self.titleLabel.grid(row=0, column=0, columnspan=2)

            # Setting parameters

            # Type
            self.modulatorLabel = tk.Label(self.popup, text="Type of modulator")
            self.modulatorLabel.grid(row=1, column=0)
            self.modulatorCombobox = ttk.Combobox(self.popup, values=["PM", "MZM", "IQM"], state="readonly")
            self.modulatorCombobox.set("PM")
            self.modulatorCombobox.grid(row=1, column=1)

            # Set button
            self.setButton = tk.Button(self.popup, text="Set parameters", command=self.setParameters)
            self.setButton.grid(row=2, column=0, columnspan=2)

            self.setDefaultParameters()

            return self.popup
        
        elif self.type == "channel":
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

            # Ideal parameters checkbutton
            self.channelCheckVar = tk.BooleanVar()
            self.idealCheckbutton = tk.Checkbutton(self.popup, text="Ideal parameters", variable=self.channelCheckVar, command=self.idealCheckbuttonChange)
            self.idealCheckbutton.grid(row=4, column=0, columnspan=2)

            # Set button
            self.setButton = tk.Button(self.popup, text="Set parameters", command=self.setParameters)
            self.setButton.grid(row=5, column=0, columnspan=2)

            self.setDefaultParameters()

            return self.popup
        
        elif self.type == "reciever":
            self.popup.title("Parameters of reciever")

            self.titleLabel = tk.Label(self.popup, text="Parameters of reciever")
            self.titleLabel.grid(row=0, column=0, columnspan=2)

            # Setting parameters

            # Type
            self.recieverLabel = tk.Label(self.popup, text="Type of reciever")
            self.recieverLabel.grid(row=1, column=0)
            self.recieverCombobox = ttk.Combobox(self.popup, values=["Photodiode", "Coherent", "Hybrid"], state="readonly")
            self.recieverCombobox.set("Photodiode")
            self.recieverCombobox.grid(row=1, column=1)

            # Set button
            self.setButton = tk.Button(self.popup, text="Set parameters", command=self.setParameters)
            self.setButton.grid(row=2, column=0, columnspan=2)

            self.setDefaultParameters()

            return self.popup
        
        elif self.type == "amplifier":
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
            self.setButton = tk.Button(self.popup, text="Set parameters", command=self.setParameters)
            self.setButton.grid(row=3, column=0, columnspan=2)

            self.setDefaultParameters()

            return self.popup
        
        else: raise Exception("Unexpected if statement")


    def closePopup(self):
        # Enable the parent buttons and destroy the popup window
        self.parentGui.enableButtons()
        self.popup.destroy()


    def setParameters(self):
        """
        Set inserted parameters.
        """
        if self.type == "source":
            # Showing in main gui
            parametersString = f"Laser\n\nPower: {self.powerEntry.get()} W\nFrequency: {self.frequencyEntry.get()} THz\nLinewidth: {self.linewidthEntry.get()} Hz\nRIN: {self.rinEntry.get()}"
            # Getting initial values
            parameters = {"Power":self.powerEntry.get(), "Frequency":self.frequencyEntry.get(), "Linewidth":self.linewidthEntry.get(), "RIN":self.rinEntry.get()}
            # Validating parameters values
            parameters = self.validateParameters(parameters)

            # Return if parameters are not valid
            if parameters is None: return

            if self.sourceCheckVar.get():
                parameters.update({"Ideal":True})
            else:
                parameters.update({"Ideal":False})

        elif self.type == "modulator":
            # Showing in main gui
            parametersString = f"{self.modulatorCombobox.get()}"
            # Getting initial values
            parameters = {"Type":self.modulatorCombobox.get()}

        elif self.type == "channel":
            # Showing in main gui
            parametersString = f"Fiber channel\n\nLength: {self.lengthEntry.get()} km\nAttenuation: {self.attenuationEntry.get()} dB/km\nDispersion: {self.dispersionEntry.get()}"
            # Getting initial values
            parameters = {"Length":self.lengthEntry.get(), "Attenuation":self.attenuationEntry.get(), "Dispersion":self.dispersionEntry.get()}
            # Validating parameters values
            parameters = self.validateParameters(parameters)

            # Return if parameters are not valid
            if parameters is None: return

            if self.channelCheckVar.get():
                parameters.update({"Ideal":True})
            else:
                parameters.update({"Ideal":False})

        elif self.type == "reciever":
            # Showing in main gui
            parametersString = f"{self.recieverCombobox.get()}"
            # Getting initial values
            parameters = {"Type":self.recieverCombobox.get()}
        
        elif self.type == "amplifier":
            # Showing in main gui
            parametersString = f"Pre-amplifier\n\nGain: {self.gainEntry.get()}\nNoise: {self.noiseEntry.get()}"
            # Getting initial values
            parameters = {"Gain":self.gainEntry.get(), "Noise":self.noiseEntry.get()}
            # Validating parameters values
            parameters = self.validateParameters(parameters)

            if parameters is None: return
        
        else: raise Exception("Unexpected error")

        self.parentButton.config(text=parametersString)
        # Return parameters
        self.callback(parameters, self.type)

        self.closePopup()

    
    def validateParameters(self, parameters: dict) -> dict:
        """
        Convert string parameters values to float and validate the inputed values.

        Parameters
        -----
        parameters: values are strings

        Returns
        -----
        parameters: values are floats

            None if some parameters are not ok
        """
        for key, value in parameters.items():
            checked = checkParameter(key, value, self.popup)
            if checked is None: return None
            else: parameters.update({key:checked})

        return parameters
    

    def idealCheckbuttonChange(self):
        """
        Change parameters to simulate ideal components
        """
        if self.type == "source":
            if self.sourceCheckVar.get():
                self.rinEntry.delete(0, tk.END)
                self.rinEntry.insert(0, "0")
                self.rinEntry.config(state="disabled")

                self.linewidthEntry.delete(0, tk.END)
                self.linewidthEntry.insert(0, "1")
                self.linewidthEntry.config(state="disabled")
            else:
                self.rinEntry.config(state="normal")
                self.linewidthEntry.config(state="normal")
                
        elif self.type == "channel":
            if self.channelCheckVar.get():
                self.attenuationEntry.delete(0, tk.END)
                self.attenuationEntry.insert(0, "0")
                self.attenuationEntry.config(state="disabled")

                self.dispersionEntry.delete(0, tk.END)
                self.dispersionEntry.insert(0, "0")
                self.dispersionEntry.config(state="disabled")
            else:
                self.attenuationEntry.config(state="normal")
                self.dispersionEntry.config(state="normal")

        else: raise Exception("Unexpected error")

        
    def setDefaultParameters(self):
        """
        Set default parameters to the entries. If there are any.
        """
        if self.type == "source":
            # No default parameters
            if self.defaultParameters is None: return

            if self.defaultParameters.get("Ideal"):
                self.powerEntry.insert(0, str(self.defaultParameters.get("Power")))
                self.frequencyEntry.insert(0, str(self.defaultParameters.get("Frequency")))
                # Change check button statr
                self.idealCheckbutton.invoke() # Trigger command function
            else:
                self.powerEntry.insert(0, str(self.defaultParameters.get("Power")))
                self.frequencyEntry.insert(0, str(self.defaultParameters.get("Frequency")))
                self.linewidthEntry.insert(0, str(self.defaultParameters.get("Linewidth")))
                self.rinEntry.insert(0, str(self.defaultParameters.get("RIN")))
        
        elif self.type == "modulator":
            # No default parameters
            if self.defaultParameters is None: return
            
            self.modulatorCombobox.set(self.defaultParameters.get("Type"))

        elif self.type == "channel":
            # No default parameters
            if self.defaultParameters is None: return

            if self.defaultParameters.get("Ideal"):
                self.lengthEntry.insert(0, str(self.defaultParameters.get("Length")))
                # Change check button statr
                self.idealCheckbutton.invoke() # Trigger command function
            else:
                self.lengthEntry.insert(0, str(self.defaultParameters.get("Length")))
                self.attenuationEntry.insert(0, str(self.defaultParameters.get("Attenuation")))
                self.dispersionEntry.insert(0, str(self.defaultParameters.get("Dispersion")))

        elif self.type == "reciever":
            # No default parameters
            if self.defaultParameters is None: return

            self.recieverCombobox.set(self.defaultParameters.get("Type"))

        elif self.type == "amplifier":
            # No default parameters
            if self.defaultParameters is None: return

            self.gainEntry.insert(0, str(self.defaultParameters.get("Gain")))
            self.noiseEntry.insert(0, str(self.defaultParameters.get("Noise")))        
        
        else: raise Exception("Unexpected error")