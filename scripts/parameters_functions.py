# Function to work with parameters values

import re
from tkinter import messagebox
    
def convertNumber(input: str) -> tuple[float, bool]:
    """
    Converts string to float value. Bool value indicates empty input string.

    Returns

    (float, False) = converted float number
    
    (None, False) = input string has character in it

    (None, True) = input string is empty
    ----
    """
    if input:
        # Regular expression to match valid numbers, including negative and decimal numbers
        number_pattern = re.compile(r'^[-+]?\d*\.?\d+$')

        if number_pattern.match(input):
            return float(input), False
        else:
            return None, False
    else:
        return None, True
    

def validateParameters(type: str, parameters: dict, generalParameters: dict, parentWindow) -> dict | None:
    """
    Checks if the parameters has valid values and coverts numbers into float.

    Parameters
    ----
    type: type of block

    parameters: parameters to check

    generalParameters: for some parameters limits

    parentWindow: object for showing messageboxes

    Returns
    -----
    valid parameters

    None if some parameters are not ok
    """
    # Removes ideal (bool) value from dictionary
    ideal = parameters.pop("Ideal")

    # Remove valid string values
    if type == "modulator" or type == "reciever":
        numberParameters, stringParameters = removeStringValues(parameters, type, ideal)
    else:
        numberParameters = parameters
        stringParameters = {}

    # Conevert to floats
    for key, value in numberParameters.items():
        checked = checkNumber(key, value, parentWindow)
        # Some number parameters was not inputed correctly
        if checked is None:
            return None
        else:
            numberParameters.update({key:checked})

    # Check the limits

    for key, value in numberParameters.items():
        checked = checkLimit(key, value, generalParameters, parentWindow)
        # Off limit parameter
        if not checked:
            return None
    
    # Merge all the removed values back together
    numberParameters.update(stringParameters)
    numberParameters.update({"Ideal":ideal})

    return numberParameters


    

def checkNumber(parameterName: str, parameterValue: str, parentWindow) -> float | None:
    """
    Converts string number to float.

    Checks for:
        empty string
        string with characters

    Show error message if parameter is not ok and returns None.

    Parameters
    -----
    parentWindow: object for showing messageboxes
    """

    value, isEmpty = convertNumber(parameterValue)

    if value is None and isEmpty is False:
        messagebox.showerror(f"{parameterName} input error", f"{parameterName} must be a number!", parent=parentWindow)
        return None
    elif value is None and isEmpty is True:
        messagebox.showerror(f"{parameterName} input error", f"You must input {parameterName}!", parent=parentWindow)
        return None
    else: return value
        

def checkLimit(parameterName: str, parameterValue: float, generalParameters: dict, parentWindow) -> bool:
    """
    Checks the limit of parameter.

    Parameters
    -----
    parentWindow: object for showing messageboxes

    Returns
    ----
    True: parameter is ok

    False: parameters is off limit
    """
    # Parameter set too low
    if not checkDownLimit(parameterName, parameterValue, parentWindow):
        return False
    
    # Parameter set too high
    if not checkUpLimit(parameterName, parameterValue, generalParameters, parentWindow):
        return False
    
    return True



def checkDownLimit(parameterName: str, parameterValue: float, parentWindow) -> bool:
    """
    Checks down limit of parameter.

    Returns
    ----
    True: limit ok

    False: limit not ok
    """
    # tuple (bool, value)
    # True = parameter can be equal or greater
    # False = parameter must be greater
    downLimits = {
        # Source
        "Power":(True , -50), # -50 dBm
        "Frequency":(True, 170), # ~ 1760 nm
        "Linewidth":(True, 1), # 1 Hz
        "PowerNoise":(True, 0), # 0
        "PhaseNoise":(True, 0), # 0
        # Modulator

        # Channel
        "Length":(False, 0), # > 0 km
        "Attenuation":(True, 0), # 0 dBm/km
        "Dispersion":(True, 0), # 0 ps/nm/km
        # Reciever
        "Bandwidth":(False, 0), # > 0 Hz
        "Resolution":(False, 0), # > 0 A/W
        # Amplifier
        "Gain":(False, 0), # > 0 dB
        "Noise":(True, 0), # 0 dB
    }

    limitComp, limitValue = downLimits.get(parameterName)

    # Can be equal
    if limitComp:
        if parameterValue < limitValue:
            messagebox.showerror(f"{parameterName} input error", f"{parameterName} must be greater or equal to {limitValue}!", parent=parentWindow)
            return False
        else:
            return True
    else:
        if parameterValue < limitValue:
            messagebox.showerror(f"{parameterName} input error", f"{parameterName} must be greater than {limitValue}!", parent=parentWindow)
            return False
        elif parameterValue == limitValue:
            messagebox.showerror(f"{parameterName} input error", f"{parameterName} must be greater than {limitValue}!", parent=parentWindow)
            return False
        else:
            return True
        

def checkUpLimit(parameterName: str, parameterValue: float, generalParameters: dict, parentWindow) -> bool:
    """
    Checks up limit of parameter.

    Returns
    ----
    True: limit ok

    False: limit not ok
    """
    # tuple (bool, value)
    # True = parameter can be equal or lower
    # False = parameter must be lower
    upLimits = {
        # Source
        "Power":(True , 50), # 50 dBm
        "Frequency":(True, 250), # <= ~ 1200 nm
        "Linewidth":(True, 10**10), # 10 GHz
        "PowerNoise":(True, 1), # 1
        "PhaseNoise":(True, 1), # 1
        # Modulator

        # Channel
        "Length":(True, 1000), # 1000 km
        "Attenuation":(True, 1), # 1 dB/km
        "Dispersion":(True, 100), # ps/nm/km
        # Reciever
        "Bandwidth":(True, generalParameters.get("Fs") / 2), # <= Fs/2
        "Resolution":(True, 100), # 100 A/W 
        # Amplifier
        "Gain":(True, 50), # 50 dB
        "Noise":(True, 0), # 20 dB
    }

    limitComp, limitValue = upLimits.get(parameterName)

    # Can be equal
    if limitComp:
        if parameterValue > limitValue:
            messagebox.showerror(f"{parameterName} input error", f"{parameterName} must be lower or equal to {limitValue}!", parent=parentWindow)
            return False
        else:
            return True
    else:
        if parameterValue < limitValue:
            messagebox.showerror(f"{parameterName} input error", f"{parameterName} must be lower than {limitValue}!", parent=parentWindow)
            return False
        elif parameterValue == limitValue:
            messagebox.showerror(f"{parameterName} input error", f"{parameterName} must be lower than {limitValue}!", parent=parentWindow)
            return False
        else:
            return True 


def removeStringValues(parameters: dict, type: str, ideal: bool) -> tuple[dict, dict]:
    """
    Separates valid string parameters from number parameters.

    Returns
    -----
    tuple (dictionary with number parameters, dictionary with string parameters)
    """

    if type == "modulator":
        pass
    elif type == "reciever":
        # Type of reciever
        stringDict = {"Type":parameters.pop("Type")}

        # Some parameters has as ideal value "inf"
        if ideal:
            stringDict.update({"Bandwidth":parameters.pop("Bandwidth"), "Resolution":parameters.pop("Resolution")})
        

        return parameters, stringDict
        
    else: raise Exception("Unexpected error")     
    