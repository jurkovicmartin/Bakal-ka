from scripts.functions import convertNumber
from tkinter import messagebox

class Parameters:
    def __init__(self):
        self.parameters = {}

    def addParameter(self, name, value):
        self.parameters[name] = value

    def getParameter(self, name):
        return self.parameters.get(name, None)

    def getAllParameters(self):
        return self.parameters
    
def checkParameter(parameterName, parameterValue, parentWindow):
        """
        Checks if the parameters has valid values and coverts it to float.

        Parameters
        ----
        parameterName: string
            name of parameter
        
        parameterValue: string
            value to check and covert

        Returns
        -----
        parameter: float
            converted value
            
            None if parameter is not ok
        """

        # Parameters that can be 0
        zeroParameters = ["RIN", "Attenuation", "Dispersion", "Noise"]

        # Check length of fiber
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