import re

def checkNumber(input):
    """
    Checks for numbers and their range.

    Parameters
    ----
    input: string

    Returns
    ----
    converted number: float (also returns 0)

        -1 = input is negative number

        -2 = input is not number

        -3 = input is empty string
    """
    if input:
        # Regular expression to match valid numbers, including negative and decimal numbers
        number_pattern = re.compile(r'^[-+]?\d*\.?\d+$')

        if number_pattern.match(input):
            out = float(input)
            return -1 if out < 0 else out
        else: return -2
    else: return -3