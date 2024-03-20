# Function to work with parameters values

import re
from tkinter import messagebox
    
def convertNumber(input: str) -> float:
    """
    Converts string to float value. Returns preset values for special cases.

    Returns
    ----
    converted number: float (also returns 0)

        -1 = input is negative number

        -2 = input is not a number

        -3 = input is an empty string
    """
    if input:
        # Regular expression to match valid numbers, including negative and decimal numbers
        number_pattern = re.compile(r'^[-+]?\d*\.?\d+$')

        if number_pattern.match(input):
            out = float(input)
            return -1 if out < 0 else out
        else: return -2
    else: return -3
    

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
        zeroParameters = ["RIN", "Attenuation", "Dispersion", "Noise"]

        value = convertNumber(parameterValue)

        if value == 0 and parameterName in zeroParameters:
            return 0
        elif value == 0:
            messagebox.showerror(f"{parameterName} input error", f"Zero is not valid {parameterName}!", parent=parentWindow)
            return None
        elif value == -1:
            messagebox.showerror(f"{parameterName} input error", f"{parameterName} cannot be negative!", parent=parentWindow)
            return None
        elif value == -2:
            messagebox.showerror(f"{parameterName} input error", f"{parameterName} must be a number!", parent=parentWindow)
            return None
        elif value == -3:
            messagebox.showerror(f"{parameterName} input error", f"You must input {parameterName}!", parent=parentWindow)
            return None
        else:
            return value