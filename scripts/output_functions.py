

def calculateTransSpeed(bits: list, symbols: list, symbolRate: float) -> float:
    """
    Calculates transmission speed in bits/s.

    Parameters
    -----
    bits: list of bits to transmit

    symbols: list of symbols to transmit
    """
    transTime = len(symbols)/symbolRate
    transSpeed = len(bits)/transTime

    return transSpeed