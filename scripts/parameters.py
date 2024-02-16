class Parameters:
    def __init__(self):
        self.parameters = {}

    def addParameter(self, name, value):
        self.parameters[name] = value

    def getParameter(self, name):
        return self.parameters.get(name, None)

    def getAllParameters(self):
        return self.parameters