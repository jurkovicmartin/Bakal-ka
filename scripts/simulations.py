import numpy as np
from commpy.utilities  import upsample
from optic.models.devices import mzm, photodiode, edfa, basicLaserModel, iqm, coherentReceiver
from optic.models.channels import linearFiberChannel
from optic.comm.modulation import modulateGray, GrayMapping, demodulateGray
from optic.dsp.core import pulseShape, pnorm, signal_power
from optic.comm.metrics import fastBERcalc

try:
    from optic.dsp.coreGPU import firFilter    
except ImportError:
    from optic.dsp.core import firFilter
    
from optic.utils import parameters
import matplotlib.pyplot as plt

from scripts.plot import eyediagram, pconst


def simulatePAM(order, length, amplifier, power=0.01, dispersion=16):
    """
    Simulation of PAM signal.

    Parameters
    ----
    order: int
        order of modulation

    length: float
        length of fiber [km]
    
    amplifier: bool
        true = included EDFA to match fiber attenuation    

    power: float
        power of laser [W]

    dispersion: float
        fiber dispersion [ps/nm/km]


    Returns
    -----
    list: list with (Figure, Axes) tuples
        [psd, Tx t, Rx t, Tx eye, Rx eye, Tx con, Rx con]

        list with other values

        [BER, SER, SNR]
    """
    np.random.seed(seed=123) # fixing the seed to get reproducible results


    # simulation parameters
    SpS = 16            # samples per symbol
    Rs = 10e9          # Symbol rate
    Fs = SpS*Rs        # Sampling frequency in samples/second
    Ts = 1/Fs          # Sampling period

    outFigures = []

    # Generate signals
    signals = generateSignals("pam", order, power, SpS, Fs)

    bitsTx = signals[0]
    symbolsTx = signals[1]
    modulationSignal = signals[2]
    carrierSignal = signals[3]

    ### MODULATION

    # MZM parameters
    paramMZM = parameters()
    paramMZM.Vpi = 2
    paramMZM.Vb = -paramMZM.Vpi/2

    modulatedSignal = mzm(carrierSignal, 0.25*modulationSignal, paramMZM)

    # interval for plots
    interval = np.arange(16*20,16*50)
    t = interval*Ts/1e-9

    # PSD (Tx PSD)
    fig, axs = plt.subplots(figsize=(16,3))
    axs.set_xlim(-3*Rs,3*Rs)
    axs.set_ylim(-255,-155)
    axs.psd(np.abs(modulatedSignal)**2, Fs=Fs, NFFT = 16*1024, sides="twosided", label = "Optical signal spectrum")
    axs.legend(loc="upper left")
    axs.set_title("Tx power spectral density")
    plt.close()

    outFigures.append((fig, axs))

    # Modulated signal in time (Tx signal)
    fig, axs = plt.subplots(figsize=(16,3))
    axs.plot(t, np.abs(modulatedSignal[interval])**2, label = "Optical modulated signal", linewidth=2)
    axs.set_ylabel("Power (p.u.)")
    axs.set_xlabel("Time (ns)")
    axs.set_xlim(min(t),max(t))
    axs.legend(loc="upper left")
    axs.set_title("Tx signal in time")
    plt.close()

    outFigures.append((fig, axs))

    # Fiber channel
    recievedSignal = fiberChannel(length, dispersion, amplifier, Fs, modulatedSignal)

    # Channel signal in time (Rx signal)
    fig, axs = plt.subplots(figsize=(16,3))
    axs.plot(t, np.abs(recievedSignal[interval])**2, label = "Optical modulated signal", linewidth=2)
    axs.set_ylabel("Power (p.u.)")
    axs.set_xlabel("Time (ns)")
    axs.set_xlim(min(t),max(t))
    axs.legend(loc="upper left")
    axs.set_title("Rx signal in time")
    plt.close()

    outFigures.append((fig, axs))

    ### DETECTION

    # noisy photodiode (thermal noise + shot noise + bandwidth limitation)
    paramPD = parameters()
    paramPD.ideal = False
    paramPD.B = Rs
    paramPD.Fs = Fs

    detectedSignal = photodiode(recievedSignal, paramPD)

    # eyediagrams
    discard = 100
    outFigures.append(eyediagram(modulationSignal[discard:-discard], modulationSignal.size-2*discard, SpS, plotlabel="signal at Tx", ptype="fancy"))
    outFigures.append(eyediagram(detectedSignal[discard:-discard], detectedSignal.size-2*discard, SpS, plotlabel="signal at Rx", ptype="fancy"))

    detectedSignal = detectedSignal/np.std(detectedSignal)

    # capture samples in the middle of signaling intervals
    symbolsRx = detectedSignal[0::SpS]

    # subtract DC level and normalize power
    symbolsRx = symbolsRx - symbolsRx.mean()
    symbolsRx = pnorm(symbolsRx)

    # constellation diagrams
    outFigures.append(pconst(symbolsTx, whiteb=False))
    outFigures.append(pconst(symbolsRx, whiteb=False))

    # Demodulate
    bitsRx = demodulate("pam", order, symbolsRx)

    BER = fastBERcalc(bitsRx, bitsTx, order, "pam")
    # extract the values from arrays
    BER = [array[0] for array in BER]

    return outFigures, BER

def simulatePSK(order, length, amplifier, power=0.01, dispersion=16):
    """
    Simulation of PSK signal.

    Parameters
    ----
    order: int
        order of modulation

    length: float
        length of fiber [km]
    
    amplifier: bool
        true = included EDFA to match fiber attenuation    

    power: float
        power of laser [W]

    dispersion: float
        fiber dispersion [ps/nm/km]

    Returns
    -----
    list: list with (Figure, Axes) tuples
        [psd, Tx t, Rx t, Tx eye, Rx eye, Tx con, Rx con]

        list with other values

        [BER, SER, SNR]
    """
    np.random.seed(seed=123) # fixing the seed to get reproducible results

    # simulation parameters
    SpS = 16     # samples per symbol
    Rs = 10e9    # Symbol rate
    Fs = Rs*SpS  # Sampling frequency
    Ts = 1/Fs    # Sampling period

    outFigures = []

    # Generate signals
    signals = generateSignals("psk", order, power, SpS, Fs)

    bitsTx = signals[0]
    symbolsTx = signals[1]
    modulationSignal = signals[2]
    carrierSignal = signals[3]

    ### MODULATION

    # IQM parameters
    paramIQM = parameters()
    paramIQM.Vpi = 2
    paramIQM.Vbl = -2
    paramIQM.VbQ = -2
    paramIQM.Vphi = 1

    modulatedSignal = iqm(carrierSignal, 0.25*modulationSignal, paramIQM)

    # interval for plots
    interval = np.arange(16*20,16*50)
    t = interval*Ts/1e-9

    # PSD (Tx PSD)
    fig, axs = plt.subplots(figsize=(16,3))
    axs.set_xlim(-3*Rs,3*Rs)
    axs.set_ylim(-230,-130)
    axs.psd(np.abs(modulatedSignal)**2, Fs=Fs, NFFT = 16*1024, sides="twosided", label = "Optical signal spectrum")
    axs.legend(loc="upper left")
    plt.close()

    outFigures.append((fig, axs))

    # Modulated signal in time (Tx signal)
    fig, axs = plt.subplots(figsize=(16,3))
    axs.plot(t, np.abs(modulatedSignal[interval])**2, label = "Optical modulated signal", linewidth=2)
    axs.set_ylabel("Power (p.u.)")
    axs.set_xlabel("Time (ns)")
    axs.set_xlim(min(t),max(t))
    axs.legend(loc="upper left")
    plt.close()

    outFigures.append((fig, axs))

    # Fiber channel
    recievedSignal = fiberChannel(length, dispersion, amplifier, Fs, modulatedSignal)

    # Channel signal in time (Rx signal)
    fig, axs = plt.subplots(figsize=(16,3))
    axs.plot(t, np.abs(recievedSignal[interval])**2, label = "Optical modulated signal", linewidth=2)
    axs.set_ylabel("Power (p.u.)")
    axs.set_xlabel("Time (ns)")
    axs.set_xlim(min(t),max(t))
    axs.legend(loc="upper left")
    plt.close()

    outFigures.append((fig, axs))

    ### DETECTION

    # noisy photodiode (thermal noise + shot noise + bandwidth limitation)
    paramPD = parameters()
    paramPD.ideal = False
    paramPD.B = Rs
    paramPD.Fs = Fs

    detectedSignal = coherentReceiver(recievedSignal, carrierSignal, paramPD)

    # Eyediagrams
    discard = 100
    outFigures.append(eyediagram(modulationSignal[discard:-discard], modulationSignal.size-2*discard, SpS, plotlabel="signal at Tx", ptype="fancy"))
    outFigures.append(eyediagram(detectedSignal[discard:-discard], detectedSignal.size-2*discard, SpS, plotlabel="signal at Rx", ptype="fancy"))

    detectedSignal = detectedSignal/np.std(detectedSignal)

    # capture samples in the middle of signaling intervals
    symbolsRx = detectedSignal[0::SpS]

    # subtract DC level and normalize power
    symbolsRx = symbolsRx - symbolsRx.mean()
    symbolsRx = pnorm(symbolsRx)

    # Constellation diagrams
    outFigures.append(pconst(symbolsTx, whiteb=False))
    outFigures.append(pconst(symbolsRx, whiteb=False))

    # Demodulate
    bitsRx = demodulate("psk", order, symbolsRx)
    
    BER = fastBERcalc(bitsRx, bitsTx, order, "psk")
    # extract the values from arrays
    BER = [array[0] for array in BER]

    

    return outFigures, BER

def simulateQAM(order, length, amplifier, power=0.01, dispersion=16):
    """
    Simulation of QAM signal.

    Parameters
    ----
    order: int
        order of modulation

    length: float
        length of fiber [km]
    
    amplifier: bool
        true = included EDFA to match fiber attenuation    

    power: float
        power of laser [W]

    dispersion: float
        fiber dispersion [ps/nm/km]

    Returns
    -----
    list: list with (Figure, Axes) tuples
        [psd, Tx t, Rx t, Tx eye, Rx eye, Tx con, Rx con]

        list with other values

        [BER, SER, SNR]
    """
    np.random.seed(seed=123) # fixing the seed to get reproducible results

    # simulation parameters
    SpS = 16     # samples per symbol
    Rs = 10e9    # Symbol rate
    Fs = Rs*SpS  # Sampling frequency
    Ts = 1/Fs    # Sampling period

    outFigures = []

    # Generate signals
    signals = generateSignals("psk", order, power, SpS, Fs)

    bitsTx = signals[0]
    symbolsTx = signals[1]
    modulationSignal = signals[2]
    carrierSignal = signals[3]

    ### MODULATION

    # IQM parameters
    paramIQM = parameters()
    paramIQM.Vpi = 2
    paramIQM.Vbl = -2
    paramIQM.VbQ = -2
    paramIQM.Vphi = 1

    # optical modulation
    sigTxo = iqm(carrierSignal, modulationSignal, paramIQM)

    # interval for plots
    interval = np.arange(16*20,16*50)
    t = interval*Ts/1e-9

    # PSD (Tx PSD)
    fig, axs = plt.subplots(figsize=(16,3))
    axs.set_xlim(-3*Rs,3*Rs)
    axs.set_ylim(-230,-130)
    axs.psd(np.abs(sigTxo)**2, Fs=Fs, NFFT = 16*1024, sides="twosided", label = "Optical signal spectrum")
    axs.legend(loc="upper left")
    plt.close()

    outFigures.append((fig, axs))

    # Modulated signal in time (Tx signal)
    fig, axs = plt.subplots(figsize=(16,3))
    axs.plot(t, np.abs(sigTxo[interval])**2, label = "Optical modulated signal", linewidth=2)
    axs.set_ylabel("Power (p.u.)")
    axs.set_xlabel("Time (ns)")
    axs.set_xlim(min(t),max(t))
    axs.legend(loc="upper left")
    plt.close()

    outFigures.append((fig, axs))

    # Fiber channel
    recievedSignal = fiberChannel(length, dispersion, amplifier, Fs)

    # Channel signal in time (Rx signal)
    fig, axs = plt.subplots(figsize=(16,3))
    axs.plot(t, np.abs(recievedSignal[interval])**2, label = "Optical modulated signal", linewidth=2)
    axs.set_ylabel("Power (p.u.)")
    axs.set_xlabel("Time (ns)")
    axs.set_xlim(min(t),max(t))
    axs.legend(loc="upper left")
    plt.close()

    outFigures.append((fig, axs))

    return



def generateSignals(format, order, power, SpS, Fs):
    """
    Generate modulation and optical signal.

    Parameters
    -----
    format: string
        modulation format

        pam / psk / qam
    
    order: int
        order of modulation

    power: float
        power of laser [W]

    SpS: int
        samples per symbol

    Fs: int
        Sampling frequency
    
    Returns
    -----
    signals: tuple
        (bits, symbols, modulation signal, optical signal)
    """

    # generate pseudo-random bit sequence
    bitsTx = np.random.randint(2, size=int(np.log2(order)*1e6))

    # generate PSK modulated symbol sequence
    symbTx = modulateGray(bitsTx, order, format)
    symbTx = pnorm(symbTx) # power normalization

    # upsampling
    symbolsUp = upsample(symbTx, SpS)

    # typical NRZ pulse
    pulse = pulseShape("nrz", SpS)
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

    sigO = basicLaserModel(paramLaser)

    return bitsTx, symbTx, sigTx, sigO

def fiberChannel(length, dispersion, amplifier, Fs, signal):
    """
    Simulate signal thru fiber.

    Parameters
    -----
    length: float
        length of fiber [km]
    
    dispersion: float
        fiber dispersion [ps/nm/km]

    amplifier: bool
        True - include EDFA amplifier

    Fs: int
        Sampling frequency

    signal: array
        input optical signal
    
    Returns
    -----
    signal: array
     optical signal at the end of channel
    """

    # linear optical channel
    paramCh = parameters()
    paramCh.L = length         # total link distance [km]
    paramCh.α = 0.2        # fiber loss parameter [dB/km]
    paramCh.D = dispersion         # fiber dispersion parameter [ps/nm/km]
    paramCh.Fc = 193.1e12  # central optical frequency [Hz]
    paramCh.Fs = Fs        # simulation sampling frequency [samples/second]

    sigCh = linearFiberChannel(signal, paramCh)

    if amplifier:
        # receiver pre-amplifier
        paramEDFA = parameters()
        paramEDFA.G = paramCh.α*paramCh.L    # edfa gain
        paramEDFA.NF = 4.5   # edfa noise figure 
        paramEDFA.Fc = paramCh.Fc
        paramEDFA.Fs = Fs

        sigCh = edfa(sigCh, paramEDFA)
    
    return sigCh

def demodulate(format, order, symbols):
    """
    Demodulate symbols and calculate BER, SER, SNR.

    Parameters
    -----
    format: string
        modulation format

        pam / psk / qam
    
    order: int
        modulation order

    symbols: array
        recieved symbols to demodulate
    
    Returns
    -----
    bits: array
     demodulated bits
    """

    # demodulate symbols to bits with minimum Euclidean distance 
    const = GrayMapping(order, format) # get constellation
    Es = signal_power(const) # calculate the average energy per symbol of the constellation

    # demodulated bits
    bitsRx = demodulateGray(np.sqrt(Es)*symbols, order, format)

    return bitsRx