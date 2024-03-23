
"""
Script inspired by OpticommPY functions with a little changes.
Also added some more functions.
"""

import numpy as np
import scipy.constants as const
from optic.utils import dBm2W
from optic.dsp.core import gaussianComplexNoise

def idealLaserModel(param) -> np.array:
    """
    Laser model without any noise.

    Parameters
    -----
    param: parameters of laser
    """
    P = getattr(param, "P")  # Laser power in dBm
    Ns = getattr(param, "Ns")  # Number of samples of the signal

    # Return optical signal
    return np.full(Ns, np.sqrt(dBm2W(P)))


def edfa(Ei, ideal: bool, param=None):
    """
    Implement simple EDFA model.

    Parameters
    ----------
    Ei : np.array
        Input signal field.
        
    ideal: with / without noise

    param : parameter object (struct)
        Parameters of the edfa.

        - param.G : amplifier gain in dB. The default is 20.
        - param.NF : EDFA noise figure in dB. The default is 4.5.
        - param.Fc : central optical frequency. The default is 193.1e12.
        - param.Fs : sampling frequency in samples/second.

    Returns
    -------
    Eo : np.array
        Amplified noisy optical signal.

    """
    # Input parameters
    G = getattr(param, "G")
    NF = getattr(param, "NF")
    Fc = getattr(param, "Fc")
    Fs = getattr(param, "Fs")

    if ideal:
        G_lin = 10 ** (G / 10)

        return Ei * np.sqrt(G_lin)
    else:
        NF_lin = 10 ** (NF / 10)
        G_lin = 10 ** (G / 10)
        nsp = (G_lin * NF_lin - 1) / (2 * (G_lin - 1))

        N_ase = (G_lin - 1) * nsp * const.h * Fc
        p_noise = N_ase * Fs

        noise = gaussianComplexNoise(Ei.shape, p_noise)

        return Ei * np.sqrt(G_lin) + noise