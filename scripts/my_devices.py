
"""
Script inspired by OpticommPY functions with a little changes.
Also added some more functions.
"""

import numpy as np
import scipy.constants as const
from optic.utils import dBm2W
from optic.dsp.core import gaussianComplexNoise, gaussianNoise

from optic.models.devices import mzm, pm
from optic.utils import parameters

def edfa(Ei, ideal: bool, param=None) -> np.array:
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
    

def idealLaser(power: float, length: int) -> np.array:
    """
    Creates ideal optical signal.

    Parameters
    ----
    power: laser power in dBm

    length: number of samples to be generated
    """
    samples = np.arange(0, 1, 1/length)
    return np.sqrt(dBm2W(power)) * np.exp(2j * np.pi * samples)





def laserSource(param) -> np.array:
    """
    Generates optical carrier signal.

    Parameters:
    ----
    Ns: number of samples of the signal

    phn: phase noise

    pwn: power noise
    """
    P = getattr(param, "P")  # Laser power in dBm
    lw = getattr(param, "lw")  # Linewidth in Hz
    Ns = getattr(param, "Ns")  # Number of samples of the signal
    phn = getattr(param, "phn") # Gaussian phase noise
    pwn = getattr(param, "pwn") # Gaussian power noise

    powerNoise = gaussianNoise(Ns, pwn)
    phaseNoise = gaussianNoise(Ns, phn)

    # return np.sqrt(dBm2W(P)) * np.exp(1j * phaseNoise) + powerNoise
    return dBm2W(P) * np.exp(1j * phaseNoise) + powerNoise
    # return P * np.exp(1j * phaseNoise) + powerNoise


def myiqm(Ai, u, param=None):
    """
    Optical In-Phase/Quadrature Modulator (IQM).

    Parameters
    ----------
    Ai : scalar or np.array
        Amplitude of the optical field at the input of the IQM.
    u : complex-valued np.array
        Modulator's driving signal (complex-valued baseband).
    param : parameter object  (struct)
        Object with physical/simulation parameters of the mzm.

        - param.Vpi: MZM's Vpi voltage [V][default: 2 V]

        - param.VbI: I-MZM's bias voltage [V][default: -2 V]

        - param.VbQ: Q-MZM's bias voltage [V][default: -2 V]

        - param.Vphi: PM bias voltage [V][default: 1 V]

    Returns
    -------
    Ao : complex-valued np.array
        Modulated optical field at the output of the IQM.

    """
    if param is None:
        param = []

    # check input parameters
    Vpi = getattr(param, "Vpi", 2)
    VbI = getattr(param, "VbI", -2)
    VbQ = getattr(param, "VbQ", -2)
    Vphi = getattr(param, "Vphi", 1)

    try:
        u.shape
    except AttributeError:
        u = np.array([u])

    try:
        if Ai.shape == () and u.shape != ():
            Ai = Ai * np.ones(u.shape)
        else:
            assert Ai.shape == u.shape, "Ai and u need to have the same dimensions"
    except AttributeError:
        Ai = Ai * np.ones(u.shape)

    # define parameters for the I-MZM:
    paramI = parameters()
    paramI.Vpi = Vpi
    paramI.Vb = VbI

    # define parameters for the Q-MZM:
    paramQ = parameters()
    paramQ.Vpi = Vpi
    paramQ.Vb = VbQ

    return mzm(Ai, u.real, paramI) + pm(mzm(Ai, u.imag, paramQ), Vphi * np.ones(u.shape), Vpi)
