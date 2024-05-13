# Popup window for setting components parameters

import tkinter as tk
from tkinter import ttk

from scripts.parameters_functions import validateParameters

class ParametersWindow:
    def __init__(self, parentGui, parentButton, buttonType: str, callback, defaultParameters: dict, generalParameters: dict):
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
        self.generalParameters = generalParameters
        self.popupGui()

        # Bind the popup window's closing event to the parent's method
        self.popup.protocol("WM_DELETE_WINDOW", self.closePopup)

    ### METHODS

    def popupGui(self):
        """
        Creates popup gui for setting parameters.
        """
        self.popup = tk.Toplevel()
        self.popup.geometry("800x400")

        if self.type == "source":
            self.popup.title("Parameters of optical source")

            self.titleLabel = tk.Label(self.popup, text="Parameters of optical source")
            self.titleLabel.grid(row=0, column=0, columnspan=2)

            # Setting parameters

            # Power
            self.lengthLabel = tk.Label(self.popup, text="Power [dBm]")
            self.lengthLabel.grid(row=1, column=0)
            self.powerEntry = tk.Entry(self.popup)
            self.powerEntry.grid(row=1, column=1)

            # Frequency
            self.frequencyLabel = tk.Label(self.popup, text="Central frequency [THz]")
            self.frequencyLabel.grid(row=2, column=0)
            self.frequencyEntry = tk.Entry(self.popup)
            self.frequencyEntry.grid(row=2, column=1)

            # Linewidth
            self.linewidthLabel = tk.Label(self.popup, text="Linewidth [Hz]")
            self.linewidthLabel.grid(row=3, column=0)
            self.linewidthEntry = tk.Entry(self.popup)
            self.linewidthEntry.grid(row=3, column=1)
            self.linewidthCombobox = ttk.Combobox(self.popup, values=["Hz", "kHz", "MHz"], state="readonly")
            self.linewidthCombobox.set("Hz")
            self.linewidthCombobox.grid(row=3, column=2)

            # RIN
            self.rinLabel = tk.Label(self.popup, text="RIN [dB/Hz]")
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
        
        elif self.type == "channel":
            self.popup.title("Parameters of fiber channel")

            self.titleLabel = tk.Label(self.popup, text="Parameters of fiber channel")
            self.titleLabel.grid(row=0, column=0, columnspan=2)

            # Setting parameters

            # Length
            self.lengthLabel = tk.Label(self.popup, text="Length [km]")
            self.lengthLabel.grid(row=1, column=0)
            self.lengthEntry = tk.Entry(self.popup)
            self.lengthEntry.grid(row=1, column=1)

            # Attenuation
            self.attenuatinLabel = tk.Label(self.popup, text="Attenuation [dB/km]")
            self.attenuatinLabel.grid(row=2, column=0)
            self.attenuationEntry = tk.Entry(self.popup)
            self.attenuationEntry.grid(row=2, column=1)

            # Dispersion
            self.dispersionLabel = tk.Label(self.popup, text="Chromatic dispersion [ps/nm/km]")
            self.dispersionLabel.grid(row=3, column=0)
            self.dispersionEntry = tk.Entry(self.popup)
            self.dispersionEntry.grid(row=3, column=1)

            # Ideal parameters checkbutton
            self.channelCheckVar = tk.BooleanVar()
            # self.idealCheckbutton = tk.Checkbutton(self.popup, text="Ideal parameters\nNote that ideal channel will ignore amplifier!", variable=self.channelCheckVar, command=self.idealCheckbuttonChange)
            self.idealCheckbutton = tk.Checkbutton(self.popup, text="Ideal parameters", variable=self.channelCheckVar, command=self.idealCheckbuttonChange)
            self.idealCheckbutton.grid(row=4, column=0, columnspan=2)

            # Set button
            self.setButton = tk.Button(self.popup, text="Set parameters", command=self.setParameters)
            self.setButton.grid(row=5, column=0, columnspan=2)

            self.setDefaultParameters()
        
        elif self.type == "reciever":
            self.popup.title("Parameters of reciever")

            self.titleLabel = tk.Label(self.popup, text="Parameters of reciever")
            self.titleLabel.grid(row=0, column=0, columnspan=2)

            # Setting parameters

            # Type
            self.recieverLabel = tk.Label(self.popup, text="Type of reciever")
            self.recieverLabel.grid(row=1, column=0)
            self.recieverCombobox = ttk.Combobox(self.popup, values=["Photodiode", "Coherent"], state="readonly")
            self.recieverCombobox.set("Photodiode")
            self.recieverCombobox.grid(row=1, column=1)
            self.recieverCombobox.bind("<<ComboboxSelected>>", self.receiverChange)
            # Other parameters
            self.receiverChange(event=None)

            # Set button
            self.setButton = tk.Button(self.popup, text="Set parameters", command=self.setParameters)
            self.setButton.grid(row=5, column=0, columnspan=2)

            self.setDefaultParameters()
        
        elif self.type == "amplifier":
            self.popup.title("Parameters of amplifier")

            self.titleLabel = tk.Label(self.popup, text="Parameters of amplifier")
            self.titleLabel.grid(row=0, column=0, columnspan=2)

            # Setting parameters

            # Position
            self.positionLabel = tk.Label(self.popup, text="Position in channel")
            self.positionLabel.grid(row=1, column=0)
            self.positionCombobox = ttk.Combobox(self.popup, values=["start", "middle", "end"], state="readonly")
            self.positionCombobox.set("start")
            self.positionCombobox.grid(row=1, column=1)

            # Gain
            self.gainLabel = tk.Label(self.popup, text="Gain [dB]")
            self.gainLabel.grid(row=2, column=0)
            self.gainEntry = tk.Entry(self.popup)
            self.gainEntry.grid(row=2, column=1)

            # Noise
            self.noiseLabel = tk.Label(self.popup, text="Noise figure [dB]")
            self.noiseLabel.grid(row=3, column=0)
            self.noiseEntry = tk.Entry(self.popup)
            self.noiseEntry.grid(row=3, column=1)

            # Detection
            self.detectionLabel = tk.Label(self.popup, text="Detection limit [dBm]")
            self.detectionLabel.grid(row=4, column=0)
            self.detectionEntry = tk.Entry(self.popup)
            self.detectionEntry.grid(row=4, column=1)

            # Ideal parameters checkbutton
            self.amplifierCheckVar = tk.BooleanVar()
            self.idealCheckbutton = tk.Checkbutton(self.popup, text="Ideal parameters", variable=self.amplifierCheckVar, command=self.idealCheckbuttonChange)
            self.idealCheckbutton.grid(row=5, column=0, columnspan=2)

            # Set button
            self.setButton = tk.Button(self.popup, text="Set parameters", command=self.setParameters)
            self.setButton.grid(row=6, column=0, columnspan=2)

            self.setDefaultParameters()
        
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
            # Getting inserted values
            parameters = {"Power":self.powerEntry.get(), "Frequency":self.frequencyEntry.get(), "Linewidth":self.linewidthEntry.get(), "RIN":self.rinEntry.get()}
            
            parameters.update(self.setIdealParameter(parameters))
            # Validating parameters values
            parameters = validateParameters(self.type, parameters, self.generalParameters, self.popup, self.linewidthCombobox)

            # Return if parameters are not valid
            if parameters is None: return



        elif self.type == "modulator":
            # Getting inserted values
            parameters = {"Type":self.modulatorCombobox.get()}


        elif self.type == "channel":
            # Getting inserted values
            parameters = {"Length":self.lengthEntry.get(), "Attenuation":self.attenuationEntry.get(), "Dispersion":self.dispersionEntry.get()}
            
            parameters.update(self.setIdealParameter(parameters))
            # Validating parameters values
            parameters = validateParameters(self.type, parameters, self.generalParameters, self.popup)

            # Return if parameters are not valid
            if parameters is None: return


        elif self.type == "reciever":
            # Getting inserted values
            parameters = {"Type":self.recieverCombobox.get(), "Bandwidth":self.bandwidthEntry.get(), "Resolution":self.resolutionEntry.get()}
            
            parameters.update(self.setIdealParameter(parameters))
            # Validating parameters values
            parameters = validateParameters(self.type, parameters, self.generalParameters, self.popup, units=self.bandwidthCombobox)


            # Return if parameters are not valid
            if parameters is None: return

        
        elif self.type == "amplifier":
            # Getting inserted values
            parameters = {"Position":self.positionCombobox.get(), "Gain":self.gainEntry.get(), "Noise":self.noiseEntry.get(), "Detection":self.detectionEntry.get()}
            
            parameters.update(self.setIdealParameter(parameters))
            # Validating parameters values
            parameters = validateParameters(self.type, parameters, self.generalParameters, self.popup)

            if parameters is None: return
        
        else: raise Exception("Unexpected error")

        # Return parameters
        self.callback(parameters, self.type)
        # Check for combination of ideal channel + pre-amplifier
        # Only for channel parameters setting, is here because the Ideal state is passed only line above
        # self.parentGui.attentionCheck()

        self.closePopup()


    def idealCheckbuttonChange(self):
        """
        Change parameters to simulate ideal components
        """
        if self.type == "source":
            if self.sourceCheckVar.get():
                self.linewidthEntry.delete(0, tk.END)
                self.linewidthEntry.insert(0, "1")
                self.linewidthEntry.config(state="disabled")
                self.linewidthCombobox.config(state="disabled")

                self.rinEntry.delete(0, tk.END)
                self.rinEntry.insert(0, "0")
                self.rinEntry.config(state="disabled")

            else:
                self.linewidthEntry.config(state="normal")
                self.rinEntry.config(state="normal")
                self.linewidthCombobox.config(state="readonly")
                
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

        elif self.type == "reciever":
            if self.recieverCheckVar.get():
                self.bandwidthEntry.delete(0, tk.END)
                self.bandwidthEntry.insert(0, "inf")
                self.bandwidthEntry.config(state="disabled")
                self.bandwidthCombobox.config(state="disabled")

                self.resolutionEntry.delete(0, tk.END)
                self.resolutionEntry.insert(0, "inf")
                self.resolutionEntry.config(state="disabled")

            else:
                self.bandwidthEntry.config(state="normal")
                self.bandwidthEntry.delete(0, tk.END)
                self.bandwidthEntry.insert(0, "0")
                self.bandwidthCombobox.config(state="readonly")

                self.resolutionEntry.config(state="normal")
                self.resolutionEntry.delete(0, tk.END)
                self.resolutionEntry.insert(0, "0")


        elif self.type == "amplifier":
            if self.amplifierCheckVar.get():
                self.noiseEntry.delete(0, tk.END)
                self.noiseEntry.insert(0, "0")
                self.noiseEntry.config(state="disabled")

                self.detectionEntry.delete(0, tk.END)
                self.detectionEntry.insert(0, "-inf")
                self.detectionEntry.config(state="disabled")
            
            else:
                self.noiseEntry.config(state="normal")
                self.detectionEntry.config(state="normal")
                self.detectionEntry.delete(0, tk.END)
                self.detectionEntry.insert(0, "0")

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
                # Change check button state
                self.idealCheckbutton.invoke() # Trigger command function
            else:
                self.powerEntry.insert(0, str(self.defaultParameters.get("Power")))
                self.frequencyEntry.insert(0, str(self.defaultParameters.get("Frequency")))
                self.setDefaultLinewidth()
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
                # Change check button state
                self.idealCheckbutton.invoke() # Trigger command function
            else:
                self.lengthEntry.insert(0, str(self.defaultParameters.get("Length")))
                self.attenuationEntry.insert(0, str(self.defaultParameters.get("Attenuation")))
                self.dispersionEntry.insert(0, str(self.defaultParameters.get("Dispersion")))

        elif self.type == "reciever":
            # No default parameters
            if self.defaultParameters is None: return

            if self.defaultParameters.get("Ideal"):
                self.recieverCombobox.set(self.defaultParameters.get("Type"))
                # Change check button state
                self.idealCheckbutton.invoke() # Trigger command function
            else:
                self.recieverCombobox.set(self.defaultParameters.get("Type"))
                self.setDefaultBandwidth()
                self.resolutionEntry.insert(0, str(self.defaultParameters.get("Resolution")))

        elif self.type == "amplifier":
            # No default parameters
            if self.defaultParameters is None: return

            if self.defaultParameters.get("Ideal"):
                self.positionCombobox.set(self.defaultParameters.get("Position"))
                self.gainEntry.insert(0, str(self.defaultParameters.get("Gain")))
                # Change check button state
                self.idealCheckbutton.invoke() # Trigger command function
            
            else:
                self.positionCombobox.set(self.defaultParameters.get("Position"))
                self.gainEntry.insert(0, str(self.defaultParameters.get("Gain")))
                self.noiseEntry.insert(0, str(self.defaultParameters.get("Noise")))
                self.detectionEntry.insert(0, str(self.defaultParameters.get("Detection")))
                    
        else: raise Exception("Unexpected error")


    def setIdealParameter(self, parameters: dict) -> dict:
        """
        Set ideal parameter to chain blocks parameters.

        Returns
        ----
        dictionary with "Ideal" key, value pair
        """
        if self.type == "source":
            # Maunaly set ideal parameters
            if parameters.get("Linewidth") == "1" and parameters.get("RIN") == "0":
                return {"Ideal":True}
            # Set value based on the ideal checkbox
            else:
                return {"Ideal":self.sourceCheckVar.get()}
        
        elif self.type == "channel":
            # Maunaly set ideal parameters
            if parameters.get("Attenuation") == "0" and parameters.get("Dispersion") == "0":
                return{"Ideal":True}
            # Set value based on the ideal checkbox
            else:
                return{"Ideal":self.channelCheckVar.get()}
            
        elif self.type == "reciever":
            return {"Ideal":self.recieverCheckVar.get()}

        elif self.type == "amplifier":
            return {"Ideal":self.amplifierCheckVar.get()}
            
    
    def receiverChange(self, event):
        """
        When reciever combobox is changed.
        """
        reciever = self.recieverCombobox.get()

        if reciever == "Photodiode":
            # Bandwidth
            self.bandwidthLabel = tk.Label(self.popup, text="Bandwidth")
            self.bandwidthLabel.grid(row=2, column=0)
            self.bandwidthEntry = tk.Entry(self.popup)
            self.bandwidthEntry.insert(0, "0")
            self.bandwidthEntry.grid(row=2, column=1)
            self.bandwidthCombobox = ttk.Combobox(self.popup, values=["Hz", "kHz", "MHz", "GHz"], state="readonly")
            self.bandwidthCombobox.set("Hz")
            self.bandwidthCombobox.grid(row=2, column=2)

            # Resolution
            self.resolutionLabel = tk.Label(self.popup, text="Resolution [A/W]")
            self.resolutionLabel.grid(row=3, column=0)
            self.resolutionEntry = tk.Entry(self.popup)
            self.resolutionEntry.insert(0, "0")
            self.resolutionEntry.grid(row=3, column=1)
            

            # Ideal parameters checkbutton
            self.recieverCheckVar = tk.BooleanVar()
            self.idealCheckbutton = tk.Checkbutton(self.popup, text="Ideal parameters", variable=self.recieverCheckVar, command=self.idealCheckbuttonChange)
            self.idealCheckbutton.grid(row=4, column=0, columnspan=2)

        elif reciever == "Coherent":
            # Bandwidth
            self.bandwidthLabel = tk.Label(self.popup, text="Bandwidth")
            self.bandwidthLabel.grid(row=2, column=0)
            self.bandwidthEntry = tk.Entry(self.popup)
            self.bandwidthEntry.insert(0, "0")
            self.bandwidthEntry.grid(row=2, column=1)
            self.bandwidthCombobox = ttk.Combobox(self.popup, values=["Hz", "kHz", "MHz", "GHz"], state="readonly")
            self.bandwidthCombobox.set("Hz")
            self.bandwidthCombobox.grid(row=2, column=2)

            # Resolution
            self.resolutionLabel = tk.Label(self.popup, text="Resolution [A/W]")
            self.resolutionLabel.grid(row=3, column=0)
            self.resolutionEntry = tk.Entry(self.popup)
            self.resolutionEntry.insert(0, "0")
            self.resolutionEntry.grid(row=3, column=1)

            # Ideal parameters checkbutton
            self.recieverCheckVar = tk.BooleanVar()
            self.idealCheckbutton = tk.Checkbutton(self.popup, text="Ideal parameters", variable=self.recieverCheckVar, command=self.idealCheckbuttonChange)
            self.idealCheckbutton.grid(row=4, column=0, columnspan=2)

        else: raise Exception("Unexpected error")


    def setDefaultBandwidth(self):
        """
        Sets default value of reciever bandwidth with corresponding units.
        """
        bandwidth = self.defaultParameters.get("Bandwidth")

        if bandwidth >= 10**9:
            self.bandwidthEntry.insert(0, str(bandwidth / 10**9))
            self.bandwidthCombobox.set("GHz")
        elif bandwidth >= 10**6:
            self.bandwidthEntry.insert(0, str(bandwidth / 10**6))
            self.bandwidthCombobox.set("MHz")
        elif bandwidth >= 10**3:
            self.bandwidthEntry.insert(0, str(bandwidth / 10**3))
            self.bandwidthCombobox.set("kHz")
        else:
            self.bandwidthEntry.insert(0, str(bandwidth))
            self.bandwidthCombobox.set("Hz")


    def setDefaultLinewidth(self):
        """
        Sets default value of source linewidth with corresponding units.
        """
        linewidth = self.defaultParameters.get("Linewidth")

        if linewidth >= 10**6:
            self.linewidthEntry.insert(0, str(linewidth / 10**6))
            self.linewidthCombobox.set("MHz")
        elif linewidth >= 10**3:
            self.linewidthEntry.insert(0, str(linewidth / 10**3))
            self.linewidthCombobox.set("kHz")
        else:
            self.linewidthEntry.insert(0, str(linewidth))
            self.linewidthCombobox.set("Hz")