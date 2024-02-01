import re

def checkLength(input_str):
    """
    Inputs string returns float, 
    checks for numbers and their range,
    returns:
    input number (also returns 0),
    -1 = input is negative number,
    -2 = input is not number,
    -3 = input is empty string,
    """
    if input_str:
        # Regular expression to match valid numbers, including negative and decimal numbers
        number_pattern = re.compile(r'^[-+]?\d*\.?\d+$')

        if number_pattern.match(input_str):
            out = float(input_str)
            return -1 if out < 0 else out
        else: return -2
    else: return -3