import customtkinter as ctk

class Help:
    """
    Help tab gui.
    """
    def __init__(self, mainFrame, exampleFunction):

        generalFont = ("Helvetica", 16, "bold")
        headFont = ("Helvetica", 24, "bold")
        backgroundColor = "#2a2a2a"

        title = ctk.CTkLabel(mainFrame, text="Help", font=headFont)
        title.pack(padx=10, pady=10)


        # Examples chapter
        exampleFrame = ctk.CTkFrame(mainFrame, fg_color=backgroundColor)
        exampleFrame.pack(fill="both", expand=True, padx=10, pady=10)

        exampleTitle = ctk.CTkLabel(exampleFrame, text="Example", font=headFont)
        exampleTitle.grid(row=0, column=0, padx=10, pady=10)

        text = "10 Gb/s OOK"

        exampleText = ctk.CTkLabel(exampleFrame, text=text, font=generalFont)
        exampleText.grid(row=1, column=0, padx=10, pady=10)

        exampleButton = ctk.CTkButton(exampleFrame, text="Set example parameters", command=exampleFunction, font=generalFont)
        exampleButton.grid(row=2, column=0, padx=10, pady=10)


        # Theory
        theoryFrame = ctk.CTkFrame(mainFrame, fg_color=backgroundColor)
        theoryFrame.pack(fill="both", expand=True, padx=10, pady=10)

        theoryTitle = ctk.CTkLabel(theoryFrame, text="Litte of theory", font=headFont)
        theoryTitle.grid(row=0, column=0, padx=10, pady=10)

        text = "Some theory"

        theoryText = ctk.CTkLabel(theoryFrame, text=text, font=generalFont)
        theoryText.grid(row=1, column=0, padx=10, pady=10)

    

