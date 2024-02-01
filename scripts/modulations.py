
# # Simulate a basic IM-DD PAM transmission system

import numpy as np
from commpy.utilities  import upsample
from optic.models.devices import mzm, photodiode, edfa
from optic.models.channels import linearFiberChannel
from optic.comm.modulation import GrayMapping, modulateGray, demodulateGray
from optic.comm.metrics import  theoryBER
from optic.dsp.core import pulseShape, lowPassFIR, pnorm, signal_power

try:
    from optic.dsp.coreGPU import firFilter    
except ImportError:
    from optic.dsp.core import firFilter
    
from optic.utils import parameters, dBm2W
from plot import eyediagram, pconst
import matplotlib.pyplot as plt
from scipy.special import erfc
from tqdm.notebook import tqdm
import scipy as sp


def PAM(order, length, dispersion=16, power=0):
    """
    order of modulation
    length of fiber
    fiber dispersion
    power of laser
    """
    np.random.seed(seed=123) # fixing the seed to get reproducible results

    # ### Intensity modulation (IM) with Pulse Amplitude Modulation (PAM)

    # M = 2 = ook
    outFigures = []
    # plt.ioff()

    # simulation parameters
    SpS = 16            # samples per symbol
    M = order              # order of the modulation format
    Rs = 10e9          # Symbol rate (for OOK case Rs = Rb)
    Fs = SpS*Rs        # Sampling frequency in samples/second
    Ts = 1/Fs          # Sampling period

    # Laser power
    Pi_dBm = power         # laser optical power at the input of the MZM in dBm
    Pi = dBm2W(Pi_dBm) # convert from dBm to W

    # MZM parameters
    paramMZM = parameters()
    paramMZM.Vpi = 2
    paramMZM.Vb = -paramMZM.Vpi/2

    # generate pseudo-random bit sequence
    bitsTx = np.random.randint(2, size=int(np.log2(M)*1e6))
    print(bitsTx)

    # generate ook modulated symbol sequence
    symbTx = modulateGray(bitsTx, M, "pam")    
    symbTx = pnorm(symbTx) # power normalization

    # upsampling
    symbolsUp = upsample(symbTx, SpS)

    # typical NRZ pulse
    pulse = pulseShape("nrz", SpS)
    pulse = pulse/max(abs(pulse))

    # pulse shaping
    sigTx = firFilter(pulse, symbolsUp)

    # optical modulation
    Ai = np.sqrt(Pi)
    sigTxo = mzm(Ai, 0.25*sigTx, paramMZM)

    print("Average power of the modulated optical signal [mW]: %.3f mW"%(signal_power(sigTxo)/1e-3))
    print("Average power of the modulated optical signal [dBm]: %.3f dBm"%(10*np.log10(signal_power(sigTxo)/1e-3)))

    # interval for plots
    interval = np.arange(16*20,16*50)
    t = interval*Ts/1e-9

    fig, axs = plt.subplots(figsize=(16,3))
    # plot psd
    axs.set_xlim(-3*Rs,3*Rs)
    axs.set_ylim(-255,-155)
    axs.psd(np.abs(sigTxo)**2, Fs=Fs, NFFT = 16*1024, sides="twosided", label = "Optical signal spectrum")
    axs.legend(loc="upper left")
    axs.set_title("Tx power spectral density")

    plt.close()
    outFigures.append((fig, axs))

    fig, axs = plt.subplots(figsize=(16,3))
    # plot signal in t
    axs.plot(t, np.abs(sigTxo[interval])**2, label = "Optical modulated signal", linewidth=2)
    axs.set_ylabel("Power (p.u.)")
    axs.set_xlabel("Time (ns)")
    axs.set_xlim(min(t),max(t))
    axs.legend(loc="upper left")
    axs.set_title("Tx signal in time")
    # axs.grid()

    plt.close()
    outFigures.append((fig, axs))

    # ### Linear fiber channel model (fiber + EDFA opt. amplifier)

    # linear optical channel
    paramCh = parameters()
    paramCh.L = length         # total link distance [km]
    paramCh.α = 0.2        # fiber loss parameter [dB/km]
    paramCh.D = dispersion         # fiber dispersion parameter [ps/nm/km]
    paramCh.Fc = 193.1e12  # central optical frequency [Hz]
    paramCh.Fs = Fs        # simulation sampling frequency [samples/second]

    sigCh = linearFiberChannel(sigTxo, paramCh)

    # receiver pre-amplifier
    paramEDFA = parameters()
    paramEDFA.G = paramCh.α*paramCh.L    # edfa gain
    paramEDFA.NF = 4.5   # edfa noise figure 
    paramEDFA.Fc = paramCh.Fc
    paramEDFA.Fs = Fs

    sigCh = edfa(sigCh, paramEDFA)

    # ### Direct-detection (DD) pin receiver model

    # ideal photodiode (noiseless, no bandwidth limitation)
    paramPD = parameters()
    paramPD.ideal = True
    paramPD.Fs = Fs
    I_Rx_ideal = photodiode(sigTxo.real, paramPD)

    # noisy photodiode (thermal noise + shot noise + bandwidth limitation)
    paramPD = parameters()
    paramPD.ideal = False
    paramPD.B = Rs
    paramPD.Fs = Fs

    I_Rx = photodiode(sigCh, paramPD)

    discard = 100

    outFigures.append(eyediagram(I_Rx_ideal[discard:-discard], I_Rx.size-2*discard, SpS, plotlabel="signal at Tx", ptype="fancy"))
    outFigures.append(eyediagram(I_Rx[discard:-discard], I_Rx.size-2*discard, SpS, plotlabel="signal at Rx", ptype="fancy"))

    # Rx t
    fig, axs = plt.subplots(figsize=(16,3))
    axs.plot(t, np.abs(I_Rx[interval])**2, label = "Optical modulated signal", linewidth=2)
    axs.set_ylabel("Power (p.u.)")
    axs.set_xlabel("Time (ns)")
    axs.set_xlim(min(t),max(t))
    axs.legend(loc="upper left")
    axs.set_title("Rx signal in time")
    # axs.grid()
    plt.close()
    outFigures.append((fig, axs))

    I_Rx = I_Rx/np.std(I_Rx)

    # capture samples in the middle of signaling intervals
    symbRx = I_Rx[0::SpS]

    # subtract DC level and normalize power
    symbRx = symbRx - symbRx.mean()
    symbRx = pnorm(symbRx)

    outFigures.append(pconst(symbTx, whiteb=False))
    outFigures.append(pconst(symbRx, whiteb=False))

    # for index, item in enumerate(outFigures):
    #     print(f"Index: {index}, Item: {item}, Type: {type(item)}")

    return outFigures