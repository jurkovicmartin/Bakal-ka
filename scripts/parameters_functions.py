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
    

def checkParameter(parameterName: str, parameterValue: str, parentWindow) -> float | None:
        """
        Checks if the parameters has valid values and coverts it to float.

        Parameters
        ----
        parentWindow: object for showing messageboxes

        Returns
        -----
        converted value: None if parameter is not ok
        """
        # Parameters that can be 0
        zeroParameters = ["Power", "RIN", "Attenuation", "Dispersion", "Noise"]

        # Parameters that can be negative
        negativeParameters = ["Power"]

        value, isEmpty = convertNumber(parameterValue)

        if value is None and isEmpty is False:
            messagebox.showerror(f"{parameterName} input error", f"{parameterName} must be a number!", parent=parentWindow)
            return None
        elif value is None and isEmpty is True:
            messagebox.showerror(f"{parameterName} input error", f"You must input {parameterName}!", parent=parentWindow)
            return None
        elif value == 0 and parameterName in zeroParameters:
            return value
        elif value == 0:
            messagebox.showerror(f"{parameterName} input error", f"Zero is not valid {parameterName}!", parent=parentWindow)
            return None
        elif value < 0 and parameterName in negativeParameters:
            return value
        elif value < 0:
            messagebox.showerror(f"{parameterName} input error", f"{parameterName} cannot be negative!", parent=parentWindow)
            return None
        else:
            return value