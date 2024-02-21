# Simulation functions

import numpy as np
from commpy.utilities  import upsample
from optic.models.devices import mzm, photodiode, edfa, basicLaserModel, iqm, coherentReceiver, pm
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

from scripts.plot import eyediagram, pconst, powerSpectralDensity, signalInTime

def simulate(generalParameters: dict, sourceParameters: dict, modulatorParameters: dict, channelParameters: dict, recieverParameters: dict, amplifierParameters: dict) -> dict:
    """
    Simulate communication.

    Parameters
    -----
    generalParameters: including modulation format and order for maping

    Returns
    -----
    simulationResults: bitsTx, symbolsTx, modulationSignal, carrierSignal, modulatedSignal, recieverSignal, detectedSignal, symbolsRx, bitsRx
    """

    np.random.seed(seed=123) # fixing the seed to get reproducible results

    # Not returning values
    Fs = generalParameters.get("Fs")
    Rs = generalParameters.get("Rs")
    frequency = sourceParameters.get("Frequency")

    # Output dictionary
    simulationResults = {}

    # Adds bitsTx, symbolsTx, modulationSignal
    simulationResults.update(modulationSignal(generalParameters))
    # Adds carrierSignal
    simulationResults.update(carrierSignal(sourceParameters, Fs, simulationResults.get("modulationSignal")))
    # Adds modulatedSignal
    simulationResults.update(modulate(modulatorParameters, simulationResults.get("modulationSignal"), simulationResults.get("carrierSignal")))
    # Adds recieverSignal
    simulationResults.update(fiberTransmition(channelParameters, amplifierParameters, simulationResults.get("modulatedSignal"), Fs, frequency))
    # Adds detectedSignal
    simulationResults.update(detection(recieverParameters, simulationResults.get("recieverSignal"), simulationResults.get("carrierSignal"), Rs, Fs))
    # Adds symbolsRx, bitsRx
    simulationResults.update(restoreInformation(simulationResults.get("detectedSignal"), generalParameters))

    return simulationResults

def modulationSignal(generalParameters: dict) -> dict:
    """
    Generate electrical modulation signal.

    Returns
    -----
        bitsTx, symbolsTx, modulationSignal
    """

    SpS = generalParameters.get("SpS")  # Samples per symbol
    modulationOrder = generalParameters.get("Order")
    modulationFormat = generalParameters.get("Format")
    
    # generate pseudo-random bit sequence
    bitsTx = np.random.randint(2, size=int(np.log2(modulationOrder)*1e6))

    # generate modulated symbol sequence
    symbolsTx = modulateGray(bitsTx, modulationOrder, modulationFormat)
    symbolsTx = pnorm(symbolsTx) # power normalization

    # upsampling
    symbolsUp = upsample(symbolsTx, SpS)

    # typical NRZ pulse
    pulse = pulseShape("nrz", SpS)
    pulse = pulse/max(abs(pulse))

    # pulse shaping
    signalTx = firFilter(pulse, symbolsUp)

    return {"bitsTx":bitsTx, "symbolsTx":symbolsTx, "modulationSignal":signalTx}

def carrierSignal(sourceParameters: dict, Fs: int, modulationSignal) -> dict:
    """
    Generate optical carrier signal.

    Parameters
    -----
    Fs: sample frequency

    modulationSignal: to match both signals lengths

    Returns
    -----
    carrierSignal
    """

    # Laser parameters
    paramLaser = parameters()
    paramLaser.P = sourceParameters.get("Power")   # laser power [W] [default: 10 dBm]
    paramLaser.lw = sourceParameters.get("Linewidth")    # laser linewidth [Hz] [default: 1 kHz]
    paramLaser.RIN_var = sourceParameters.get("RIN")  # variance of the RIN noise [default: 1e-20]
    paramLaser.Fs = Fs  # sampling rate [samples/s]
    paramLaser.Ns = len(modulationSignal)   # number of signal samples [default: 1e3]

    return {"carrierSignal":basicLaserModel(paramLaser)}

def modulate(modulatorParameters: dict, modulationSignal, carrierSignal) -> dict:
    """
    Modulates carrier signal.

    Returns
    -----
    modulatedSignal
    """

    if modulatorParameters.get("Type") == "PM":

        return {"modulatedSignal":pm(carrierSignal, 0.25*modulationSignal, 5)}
    
    elif modulatorParameters.get("Type") == "MZM":
        # MZM parameters
        paramMZM = parameters()
        paramMZM.Vpi = 2
        paramMZM.Vb = -paramMZM.Vpi/2

        return {"modulatedSignal":mzm(carrierSignal, 0.25*modulationSignal, paramMZM)}
    
    elif modulatorParameters.get("Type") == "IQM":
        # IQM parameters
        paramIQM = parameters()
        paramIQM.Vpi = 2
        paramIQM.Vbl = -2
        paramIQM.VbQ = -2
        paramIQM.Vphi = 1

        return {"modulatedSignal":iqm(carrierSignal, 0.25*modulationSignal, paramIQM)}
    
    else: raise Exception("Unexpected error")

def fiberTransmition(fiberParameters: dict, amplifierParameters: dict, modulatedSignal, Fs: int, frequency: float) -> dict:
    """
    Simulates signal thru optical fiber.

    Parameters
    -----
    Fs: sampling frequency

    frequency: central frequency of optical signal

    Returns
    -----
    recieverSignal: signal at the end of fiber
    """

    # linear optical channel
    paramCh = parameters()
    paramCh.L = fiberParameters.get("Length")         # total link distance [km]
    paramCh.α = fiberParameters.get("Attenuation")        # fiber loss parameter [dB/km]
    paramCh.D = fiberParameters.get("Dispersion")         # fiber dispersion parameter [ps/nm/km]
    paramCh.Fc = frequency  # central optical frequency [Hz]
    paramCh.Fs = Fs        # simulation sampling frequency [samples/second]

    recieverSignal = linearFiberChannel(modulatedSignal, paramCh)

    # Channel has amplifier
    if amplifierParameters is not None:
        # receiver pre-amplifier
        paramEDFA = parameters()
        paramEDFA.G = amplifierParameters.get("Gain")    # edfa gain
        paramEDFA.NF = amplifierParameters.get("Noise")   # edfa noise figure 
        paramEDFA.Fc = frequency
        paramEDFA.Fs = Fs

        recieverSignal = edfa(recieverSignal, paramEDFA)

    return {"recieverSignal":recieverSignal}

def detection(recieverParameters: dict, recieverSignal, referentSignal, Rs: int, Fs: int) -> dict:
    """
    Convert optical signal back to electrical

    Parameters
    ----
    referentSginal: optical signal as a signal from local oscilator for coherent detection

    Rs: symbol rate

    Fs: sampling frequency

    Returns
    -----
    detectedSignal
    """

    if recieverParameters.get("Type") == "Photodiode":
        # noisy photodiode (thermal noise + shot noise + bandwidth limitation)
        paramPD = parameters()
        paramPD.ideal = False
        paramPD.B = Rs
        paramPD.Fs = Fs

        return {"detectedSignal":photodiode(recieverSignal, paramPD)}
    
    elif recieverParameters.get("Type") == "Coherent":
        # noisy photodiode (thermal noise + shot noise + bandwidth limitation)
        paramPD = parameters()
        paramPD.ideal = False
        paramPD.B = Rs
        paramPD.Fs = Fs

        return {"detectedSignal":coherentReceiver(recieverSignal, referentSignal, paramPD)}

    elif recieverParameters.get("Type") == "Hybrid":
        pass

    else: raise Exception("Unexpected error")



def restoreInformation(detectedSignal, generalParameters: dict) -> dict:
    """
    Gets bits information from detected signal.

    Returns
    -----
    symbolsRx, bitsRx
    """

    SpS = generalParameters.get("SpS")
    modulationFormat = generalParameters.get("Format")
    modulationOrder = generalParameters.get("Order")

    detectedSignal = detectedSignal/np.std(detectedSignal)

    # capture samples in the middle of signaling intervals
    symbolsRx = detectedSignal[0::SpS]

    # subtract DC level and normalize power
    symbolsRx = symbolsRx - symbolsRx.mean()
    symbolsRx = pnorm(symbolsRx)

    # demodulate symbols to bits with minimum Euclidean distance 
    const = GrayMapping(modulationOrder, modulationFormat) # get constellation
    Es = signal_power(const) # calculate the average energy per symbol of the constellation

    # demodulated bits
    bitsRx = demodulateGray(np.sqrt(Es)*symbolsRx, modulationOrder, modulationFormat)

    return {"symbolsRx":symbolsRx, "bitsRx":bitsRx}


def getFigure(type: str, simulationResults: dict, generalParameters: dict):
    """
    Shows graph in separate window and returns (Figure, Axes) tuple

    Parameters
    -----
    type: specify which plot will be returned
    """

    Ts = generalParameters.get("Ts")
    Rs = generalParameters.get("Rs")
    Fs = generalParameters.get("Fs")
    SpS = generalParameters.get("SpS")

    informationSignal = simulationResults.get("modulationSignal")
    modulatedSignal = simulationResults.get("modulatedSignal")
    recieverSignal = simulationResults.get("recieverSignal")
    detectedSignal = simulationResults.get("detectedSignal")
    symbolsTx = simulationResults.get("symbolsTx")
    symbolsRx = simulationResults.get("symbolsRx")

    if type == "psdTx":
        # Tx PSD
        psd = powerSpectralDensity(Rs, Fs, modulatedSignal, "Tx power spectral density")

        return psd[0]
    
    elif type == "signalTx":
        # Modulated signal in time (Tx signal)
        sig = signalInTime(Ts, modulatedSignal, "Tx optical signal")

        return sig[0]

    elif type == "signalRx":
        # Reciever signal in time (Rx signal)
        sig = signalInTime(Ts, recieverSignal, "Rx optical signal")

        return sig[0]
    
    elif type == "eyediagramTx":
        # Tx eyediagram
        discard = 100
        eye = eyediagram(informationSignal[discard:-discard], informationSignal.size-2*discard, SpS, plotlabel="signal at Tx", ptype="fancy")
        
        return eye[0]
    
    elif type == "eyediagramRx":
        # Rx eyediagram
        discard = 100
        eye = eyediagram(detectedSignal[discard:-discard], detectedSignal.size-2*discard, SpS, plotlabel="signal at Rx", ptype="fancy")

        return eye[0]
    
    elif type == "constellationTx":
        # Tx constellation diagram
        con = pconst(symbolsTx, whiteb=False)
        
        return con[0]
    
    elif type == "constellationRx":
        # Rx constellation diagram
        con = pconst(symbolsRx, whiteb=False)

        return con[0]

    else: raise Exception("Unexpected error")


def getValues(simulationResults: dict, generalParameters: dict) -> dict:
    """
    Calculates simulation values from simulation results.

    Returns
    -----
    BER, SER, SNR, powerTxdBm, powerTxW, powerRxdBm, powerRxW
    """
    
    modulationFormat = generalParameters.get("Format")
    modulationOrder = generalParameters.get("Order")

    bitsTx = simulationResults.get("bitsTx")
    bitsRx = simulationResults.get("bitsRx")
    modulatedSignal = simulationResults.get("modulatedSignal")
    recieverSignal = simulationResults.get("recieverSignal")

    # Error values

    valuesList = fastBERcalc(bitsRx, bitsTx, modulationOrder, modulationFormat)
    # extract the values from arrays
    ber, ser, snr = [array[0] for array in valuesList]

    values = {"BER":ber, "SER":ser, "SNR":snr}

    # Tx power [W]
    power = signal_power(modulatedSignal)/1e-3
    values.update({"powerTxW":power})
    # Tx power [dBm]
    power = 10*np.log10(power)
    values.update({"powerTxdBm":power})
    # Rx power [W]
    power = signal_power(recieverSignal)/1e-3
    values.update({"powerRxW":power})
    # Rx power [dBm]
    power = 10*np.log10(power)
    values.update({"powerRxdBm":power})

    return values

