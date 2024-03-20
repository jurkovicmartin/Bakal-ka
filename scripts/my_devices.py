
"""
Script inspired by OpticommPY functions with a little changes.
Also added some more functions.
"""

import numpy as np
from optic.utils import dBm2W

def idealLaserModel(param) -> np.array:
    """
    Laser model without any noise.

    Parameters
    -----
    param: parameters of laser
    """
    P = getattr(param, "P", 10)  # Laser power in dBm
    Ns = getattr(param, "Ns", 1000)  # Number of samples of the signal

    # Return optical signal
    return np.full(Ns, np.sqrt(dBm2W(P)))