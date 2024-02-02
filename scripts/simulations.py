import numpy as np
from commpy.utilities  import upsample
from optic.models.devices import mzm, photodiode, edfa, basicLaserModel, iqm, coherentReceiver
from optic.models.channels import linearFiberChannel
from optic.comm.modulation import modulateGray
from optic.dsp.core import pulseShape, pnorm, signal_power

try:
    from optic.dsp.coreGPU import firFilter    
except ImportError:
    from optic.dsp.core import firFilter
    
from optic.utils import parameters
import matplotlib.pyplot as plt

from scripts.plot import eyediagram, pconst


def simulatePAM(order, length, dispersion=16, power=0.01):
    """
    Simulation of PAM signal.

    Parameters
    ----
    order: int
        order of modulation

    length: float
        length of fiber [km]

    dispersion: float
        fiber dispersion [ps/nm/km]

    power: float
        power of laser [W]

    Returns
    -----
    list: with (Figure, Axes) tuples
        order of figures: [psd, Tx t, Rx t, Tx eye, Rx eye, Tx con, Rx con]
    """
    np.random.seed(seed=123) # fixing the seed to get reproducible results

    outFigures = []

    # simulation parameters
    SpS = 16            # samples per symbol
    M = order              # order of the modulation format
    Rs = 10e9          # Symbol rate (for OOK case Rs = Rb)
    Fs = SpS*Rs        # Sampling frequency in samples/second
    Ts = 1/Fs          # Sampling period

    ### MODULATION

    # Laser power
    Pi = power

    # MZM parameters
    paramMZM = parameters()
    paramMZM.Vpi = 2
    paramMZM.Vb = -paramMZM.Vpi/2

    # generate pseudo-random bit sequence
    bitsTx = np.random.randint(2, size=int(np.log2(M)*1e6))

    # generate PAM modulated symbol sequence
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

    # print("Average power of the modulated optical signal [mW]: %.3f mW"%(signal_power(sigTxo)/1e-3))
    # print("Average power of the modulated optical signal [dBm]: %.3f dBm"%(10*np.log10(signal_power(sigTxo)/1e-3)))

    # interval for plots
    interval = np.arange(16*20,16*50)
    t = interval*Ts/1e-9

    # plot psd
    fig, axs = plt.subplots(figsize=(16,3))
    axs.set_xlim(-3*Rs,3*Rs)
    axs.set_ylim(-255,-155)
    axs.psd(np.abs(sigTxo)**2, Fs=Fs, NFFT = 16*1024, sides="twosided", label = "Optical signal spectrum")
    axs.legend(loc="upper left")
    axs.set_title("Tx power spectral density")
    plt.close()

    outFigures.append((fig, axs))

    # plot signal in t
    fig, axs = plt.subplots(figsize=(16,3))
    axs.plot(t, np.abs(sigTxo[interval])**2, label = "Optical modulated signal", linewidth=2)
    axs.set_ylabel("Power (p.u.)")
    axs.set_xlabel("Time (ns)")
    axs.set_xlim(min(t),max(t))
    axs.legend(loc="upper left")
    axs.set_title("Tx signal in time")
    plt.close()

    outFigures.append((fig, axs))

    ### FIBER CHANNEL

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

    ### DETECTION

    # noisy photodiode (thermal noise + shot noise + bandwidth limitation)
    paramPD = parameters()
    paramPD.ideal = False
    paramPD.B = Rs
    paramPD.Fs = Fs

    I_Rx = photodiode(sigCh, paramPD)

    # Rx t
    fig, axs = plt.subplots(figsize=(16,3))
    axs.plot(t, np.abs(I_Rx[interval])**2, label = "Optical modulated signal", linewidth=2)
    axs.set_ylabel("Power (p.u.)")
    axs.set_xlabel("Time (ns)")
    axs.set_xlim(min(t),max(t))
    axs.legend(loc="upper left")
    axs.set_title("Rx signal in time")
    plt.close()

    outFigures.append((fig, axs))

    # eyediagrams
    discard = 100
    outFigures.append(eyediagram(sigTxo[discard:-discard], I_Rx.size-2*discard, SpS, plotlabel="signal at Tx", ptype="fancy"))
    outFigures.append(eyediagram(I_Rx[discard:-discard], I_Rx.size-2*discard, SpS, plotlabel="signal at Rx", ptype="fancy"))

    I_Rx = I_Rx/np.std(I_Rx)

    # capture samples in the middle of signaling intervals
    symbRx = I_Rx[0::SpS]

    # subtract DC level and normalize power
    symbRx = symbRx - symbRx.mean()
    symbRx = pnorm(symbRx)

    # constellation diagrams
    outFigures.append(pconst(symbTx, whiteb=False))
    outFigures.append(pconst(symbRx, whiteb=False))

    return outFigures

def simulatePSK(order, length, dispersion=16, power=0.01):
    """
    Simulation of PSK signal.

    Parameters
    ----
    order: int
        order of modulation

    length: float
        length of fiber [km]

    dispersion: float
        fiber dispersion [ps/nm/km]

    power: float
        power of laser [dBm]

    Returns
    -----
    list: with (Figure, Axes) tuples
        order of figures: [psd, Tx t, Rx t, Tx eye, Rx eye, Tx con, Rx con]
    """
    np.random.seed(seed=123) # fixing the seed to get reproducible results

    # simulation parameters
    SpS = 16     # samples per symbol
    M = order        # order of the modulation format
    Rs = 10e9    # Symbol rate (for OOK case Rs = Rb)
    Fs = Rs*SpS  # Sampling frequency
    Ts = 1/Fs    # Sampling period

    outFigures = []

    # generate pseudo-random bit sequence
    bitsTx = np.random.randint(2, size=int(np.log2(M)*1e6))

    # generate PSK modulated symbol sequence
    symbTx = modulateGray(bitsTx, M, "psk")
    symbTx = pnorm(symbTx) # power normalization

    # upsampling
    symbolsUp = upsample(symbTx, SpS)

    # typical NRZ pulse
    pulse = pulseShape('nrz', SpS)
    pulse = pulse/max(abs(pulse))

    # pulse shaping
    sigTx = firFilter(pulse, symbolsUp)

    # Laser parameters
    paramLaser = parameters()
    paramLaser.P = power   # laser power [W] [default: 10 dBm]
    paramLaser.lw = 1000    # laser linewidth [Hz] [default: 1 kHz]
    paramLaser.RIN_var = 1e-20  # variance of the RIN noise [default: 1e-20]
    paramLaser.Fs = Fs  # sampling rate [samples/s]
    paramLaser.Ns = len(sigTx)   # number of signal samples [default: 1e3]

    optical_signal = basicLaserModel(paramLaser)

    # IQM parameters
    paramIQM = parameters()
    paramIQM.Vpi = 2
    paramIQM.Vbl = -2
    paramIQM.VbQ = -2
    paramIQM.Vphi = 1

    # optical modulation
    sigTxo = iqm(optical_signal, 0.25*sigTx, paramIQM)

    # print('Average power of the modulated optical signal [mW]: %.3f mW'%(signal_power(sigTxo)/1e-3))
    # print('Average power of the modulated optical signal [dBm]: %.3f dBm'%(10*np.log10(signal_power(sigTxo)/1e-3)))

    interval = np.arange(16*20,16*50)
    t = interval*Ts/1e-9

    # plot psd
    fig, axs = plt.subplots(figsize=(16,3))
    axs.set_xlim(-3*Rs,3*Rs)
    axs.set_ylim(-230,-130)
    axs.psd(np.abs(sigTxo)**2, Fs=Fs, NFFT = 16*1024, sides='twosided', label = 'Optical signal spectrum')
    axs.legend(loc='upper left')
    plt.close()

    outFigures.append((fig, axs))

    # plot signal in time
    fig, axs = plt.subplots(figsize=(16,3))
    axs.plot(t, np.abs(sigTxo[interval])**2, label = 'Optical modulated signal', linewidth=2)
    axs.set_ylabel('Power (p.u.)')
    axs.set_xlabel('Time (ns)')
    axs.set_xlim(min(t),max(t))
    axs.legend(loc='upper left')
    plt.close()

    outFigures.append((fig, axs))

    ### FIBER CHANNEL

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

    ### DETECTION

    # noisy photodiode (thermal noise + shot noise + bandwidth limitation)
    paramPD = parameters()
    paramPD.ideal = False
    paramPD.B = Rs
    paramPD.Fs = Fs

    I_Rx = coherentReceiver(sigCh, optical_signal, paramPD)

    # Rx t
    fig, axs = plt.subplots(figsize=(16,3))
    axs.plot(t, np.abs(I_Rx[interval])**2, label = 'Optical modulated signal', linewidth=2)
    axs.set_ylabel('Power (p.u.)')
    axs.set_xlabel('Time (ns)')
    axs.set_xlim(min(t),max(t))
    axs.legend(loc='upper left')
    plt.close()

    outFigures.append((fig, axs))

    # eyediagrams
    discard = 100
    outFigures.append(eyediagram(sigTxo[discard:-discard], I_Rx.size-2*discard, SpS, plotlabel="signal at Tx", ptype="fancy"))
    outFigures.append(eyediagram(I_Rx[discard:-discard], I_Rx.size-2*discard, SpS, plotlabel="signal at Rx", ptype="fancy"))

    I_Rx = I_Rx/np.std(I_Rx)

    # capture samples in the middle of signaling intervals
    symbRx = I_Rx[0::SpS]

    # subtract DC level and normalize power
    symbRx = symbRx - symbRx.mean()
    symbRx = pnorm(symbRx)

    # constellation diagrams
    outFigures.append(pconst(symbTx, whiteb=False))
    outFigures.append(pconst(symbRx, whiteb=False))

    return outFigures