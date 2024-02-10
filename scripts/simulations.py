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


def simulatePAM(simulationParameters, order, length, amplifier, power=0.01, loss=0.2, dispersion=16):
    """
    Simulation of PAM signal.

    Parameters
    ----
    simulationParameters: list
        [SpS, Rs, Fs, Ts]

        SpS = Samples per symbol

        Rs = Symbol rate

        Fs = Sampling frequency

        Ts = Sampling period

    order: int
        order of modulation

    length: float
        length of fiber [km]
    
    amplifier: bool
        true = included pre amplifier EDFA to match fiber attenuation    

    power: float
        power of laser [W]

    loss: float
        fiber loss [dB/km]

    dispersion: float
        fiber dispersion [ps/nm/km]


    Returns
    -----
    values: list
        simulation values [bitsTx, symbolsTx, modulation signal, modulated signal, recieved signal, detected signal, symbolsRx, bitsRx]
    """
    np.random.seed(seed=123) # fixing the seed to get reproducible results


    # Simulation parameters
    SpS = simulationParameters[0]
    Rs = simulationParameters[1]
    Fs = simulationParameters[2]

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

    # Fiber channel
    recievedSignal = fiberChannel(length, loss, dispersion, amplifier, Fs, modulatedSignal)

    ### DETECTION

    # noisy photodiode (thermal noise + shot noise + bandwidth limitation)
    paramPD = parameters()
    paramPD.ideal = False
    paramPD.B = Rs
    paramPD.Fs = Fs

    detectedSignal = photodiode(recievedSignal, paramPD)

    detectedSignal = detectedSignal/np.std(detectedSignal)

    # capture samples in the middle of signaling intervals
    symbolsRx = detectedSignal[0::SpS]

    # subtract DC level and normalize power
    symbolsRx = symbolsRx - symbolsRx.mean()
    symbolsRx = pnorm(symbolsRx)

    # Demodulate
    bitsRx = demodulate("pam", order, symbolsRx)

    # Output
    values = [bitsTx, symbolsTx, modulationSignal, modulatedSignal, recievedSignal, detectedSignal, symbolsRx, bitsRx]

    return values

def simulatePSK(simulationParameters, order, length, amplifier, power=0.01, loss=0.2, dispersion=16):
    """
    Simulation of PSK signal.

    Parameters
    ----
    simulationParameters: list
        [SpS, Rs, Fs, Ts]

        SpS = Samples per symbol

        Rs = Symbol rate

        Fs = Sampling frequency

        Ts = Sampling period

    order: int
        order of modulation

    length: float
        length of fiber [km]
    
    amplifier: bool
        true = included pre amplifier EDFA to match fiber attenuation    

    power: float
        power of laser [W]

    loss: float
        fiber loss [dB/km]

    dispersion: float
        fiber dispersion [ps/nm/km]

    Returns
    -----
    values: list
        simulation values [bitsTx, symbolsTx, modulation signal, modulated signal, recieved signal, detected signal, symbolsRx, bitsRx]
    """
    np.random.seed(seed=123) # fixing the seed to get reproducible results

    # Simulation parameters
    SpS = simulationParameters[0]
    Rs = simulationParameters[1]
    Fs = simulationParameters[2]

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

    # Fiber channel
    recievedSignal = fiberChannel(length, loss, dispersion, amplifier, Fs, modulatedSignal)

    ### DETECTION

    # noisy photodiode (thermal noise + shot noise + bandwidth limitation)
    paramPD = parameters()
    paramPD.ideal = False
    paramPD.B = Rs
    paramPD.Fs = Fs

    detectedSignal = coherentReceiver(recievedSignal, carrierSignal, paramPD)

    detectedSignal = detectedSignal/np.std(detectedSignal)

    # capture samples in the middle of signaling intervals
    symbolsRx = detectedSignal[0::SpS]

    # subtract DC level and normalize power
    symbolsRx = symbolsRx - symbolsRx.mean()
    symbolsRx = pnorm(symbolsRx)

    # Demodulate
    bitsRx = demodulate("psk", order, symbolsRx)

    # Output
    values = [bitsTx, symbolsTx, modulationSignal, modulatedSignal, recievedSignal, detectedSignal, symbolsRx, bitsRx]
    

    return values

def simulateQAM(simulationParameters, order, length, amplifier, power=0.01, loss=0.2, dispersion=16):
    """
    Simulation of QAM signal.

    Parameters
    ----
    simulationParameters: list
        [SpS, Rs, Fs, Ts]

        SpS = Samples per symbol

        Rs = Symbol rate

        Fs = Sampling frequency

        Ts = Sampling period

    order: int
        order of modulation

    length: float
        length of fiber [km]
    
    amplifier: bool
        true = included pre amplifier EDFA to match fiber loss    

    power: float
        power of laser [W]

    loss: float
        fiber loss [dB/km]

    dispersion: float
        fiber dispersion [ps/nm/km]

    Returns
    -----
    list: list with (Figure, Axes) tuples
        [psd, Tx t, Rx t, Tx eye, Rx eye, Tx con, Rx con]

        tuple with other values
            list: [BER, SER, SNR]

            list: [transmition power [W], transmition power [dB], recieved power [W], recieved power [dB]]
    """
    np.random.seed(seed=123) # fixing the seed to get reproducible results

    # Simulation parameters
    SpS = simulationParameters[0]
    Rs = simulationParameters[1]
    Fs = simulationParameters[2]

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

    modulatedSignal = iqm(carrierSignal, modulationSignal, paramIQM)

    # Fiber channel
    recievedSignal = fiberChannel(length, loss, dispersion, amplifier, Fs, modulatedSignal)

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


def fiberChannel(length, loss, dispersion, amplifier, Fs, signal):
    """
    Simulate signal thru fiber.

    Parameters
    -----
    length: float
        length of fiber [km]

    loss: float
        fiber loss [dB/km]
    
    dispersion: float
        fiber dispersion [ps/nm/km]

    amplifier: bool
        True - include EDFA pre amplifier

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
    paramCh.α = loss        # fiber loss parameter [dB/km]
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


def createPlots(symbolsTx, modulationSignal, modulatedSignal, recievedSignal, detectedSignal, symbolsRx, simulationParameters):
    """
    Create simulation plots of signals.

    Parameters
    -----
    symbolsTx: array
        symbols to transmit

    modulationSiganl: array
        electrical modulation signal

    modulatedSignal: array
        optical modulated signal

    recievedSignal: array
        optical signal after transmition thru channel

    detectedSignal: array
        electrical signal at receiver

    symbolsRx: array
        detected symbols at reciever

    simulationParameters: list
        [SpS, Rs, Fs, Ts]

        SpS = Samples per symbol

        Rs = Symbol rate

        Fs = Sampling frequency

        Ts = Sampling period

    Returns
    -----
    plots: list
        list with tuples (Figure, Axes)
    """

    # Simulation parameters
    SpS = simulationParameters[0]
    Rs = simulationParameters[1]
    Fs = simulationParameters[2]
    Ts = simulationParameters[3]

    plots = [] 
    
    # interval for plots
    interval = np.arange(16*20,16*50)
    t = interval*Ts/1e-9

    # PSD (Tx PSD)
    fig, axs = plt.subplots(figsize=(16,3))
    axs.set_xlim(-3*Rs,3*Rs)
    # axs.set_ylim(-230,-130)
    axs.psd(np.abs(modulatedSignal)**2, Fs=Fs, NFFT = 16*1024, sides="twosided", label = "Optical signal spectrum")
    axs.legend(loc="upper left")
    plt.close()

    plots.append((fig, axs))

    # Modulated signal in time (Tx signal)
    fig, axs = plt.subplots(figsize=(16,3))
    axs.plot(t, np.abs(modulatedSignal[interval])**2, label = "Tx optical modulated signal", linewidth=2)
    axs.set_ylabel("Power (p.u.)")
    axs.set_xlabel("Time (ns)")
    axs.set_xlim(min(t),max(t))
    axs.legend(loc="upper left")
    plt.close()

    plots.append((fig, axs))

    # Channel signal in time (Rx signal)
    fig, axs = plt.subplots(figsize=(16,3))
    axs.plot(t, np.abs(recievedSignal[interval])**2, label = "Rx optical modulated signal", linewidth=2)
    axs.set_ylabel("Power (p.u.)")
    axs.set_xlabel("Time (ns)")
    axs.set_xlim(min(t),max(t))
    axs.legend(loc="upper left")
    plt.close()

    plots.append((fig, axs))

    # Eyediagrams
    discard = 100
    plots.append(eyediagram(modulationSignal[discard:-discard], modulationSignal.size-2*discard, SpS, plotlabel="signal at Tx", ptype="fancy"))
    plots.append(eyediagram(detectedSignal[discard:-discard], detectedSignal.size-2*discard, SpS, plotlabel="signal at Rx", ptype="fancy"))

    # Constellation diagrams
    plots.append(pconst(symbolsTx, whiteb=False))
    plots.append(pconst(symbolsRx, whiteb=False))

    return plots


def calculateValues(format, order, bitsTx, modulatedSignal, recievedSignal, bitsRx):
    """
    Calculate simulation values of signals.

    Parameters
    -----
    format: string
        modulation format 

        pam / psk / qam
    
    order: int
        order of modulation

    bitsTx: array
        bits to transmit

    modulatedSignal: array
        optical modulated signal

    recievedSiganl: array
        optical signal after transmition thru channel

    bitsRx: array
        trasnmited bits after demodulation 

    Returns
    -----
    values: list
        [BER, SER, SNR, transmition power (W), transmition power (dB), recieved power (W), recieved power (dB)]
    """

    # Error values

    values = fastBERcalc(bitsRx, bitsTx, order, format)
    # extract the values from arrays
    values = [array[0] for array in values]

    # Signals power

    # Transmition signal [W]
    values.append(signal_power(modulatedSignal)/1e-3)
    # Transmition signal [dB]
    values.append(10*np.log10(signal_power(modulatedSignal)/1e-3))
    # Recieved signal [W]
    values.append(signal_power(recievedSignal)/1e-3)
    # Recieved signal [dB]
    values.append(10*np.log10(signal_power(recievedSignal)/1e-3))

    return values