# Simulation functions

import numpy as np
from commpy.utilities  import upsample
from optic.models.devices import mzm, photodiode, basicLaserModel, iqm, coherentReceiver, pm
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

from scripts.my_devices import idealLaserModel, edfa
from scripts.my_plot import eyediagram, pconst, powerSpectralDensity, signalInTime
from scripts.output_functions import calculateTransSpeed

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
    frequency = sourceParameters.get("Frequency")*10**12 # Manage units (THz -> Hz)

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
    simulationResults.update(detection(recieverParameters, simulationResults.get("recieverSignal"), simulationResults.get("carrierSignal"), generalParameters))
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
    data = convertDataQuantity(generalParameters.get("Data"))
    
    # generate pseudo-random bit sequence
    bitsTx = np.random.randint(2, size=int(np.log2(modulationOrder)*data))

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
    paramLaser.P = sourceParameters.get("Power")   # laser power [dBm] [default: 10 dBm]
    paramLaser.lw = sourceParameters.get("Linewidth")    # laser linewidth [Hz] [default: 1 kHz]
    paramLaser.RIN_var = sourceParameters.get("RIN")  # variance of the RIN noise [default: 1e-20]
    paramLaser.Fs = Fs  # sampling rate [samples/s]
    paramLaser.Ns = len(modulationSignal)   # number of signal samples [default: 1e3]

    if sourceParameters.get("Ideal"):
        return {"carrierSignal":idealLaserModel(paramLaser)}
    else:
        return {"carrierSignal":basicLaserModel(paramLaser)}

def modulate(modulatorParameters: dict, modulationSignal, carrierSignal) -> dict:
    """
    Modulates carrier signal.

    Returns
    -----
    modulatedSignal
    """

    if modulatorParameters.get("Type") == "PM":

        return {"modulatedSignal":pm(carrierSignal, modulationSignal, 2)}
    
    elif modulatorParameters.get("Type") == "MZM":
        # MZM parameters
        paramMZM = parameters()
        paramMZM.Vpi = 2
        paramMZM.Vb = -1

        return {"modulatedSignal":mzm(carrierSignal, modulationSignal, paramMZM)}
    
    elif modulatorParameters.get("Type") == "IQM":
        # IQM parameters
        paramIQM = parameters()
        paramIQM.Vpi = 2
        paramIQM.Vbl = -2
        paramIQM.VbQ = -2
        paramIQM.Vphi = 1

        return {"modulatedSignal":iqm(carrierSignal, modulationSignal, paramIQM)}
    
    else: raise Exception("Unexpected error")

def fiberTransmition(fiberParameters: dict, amplifierParameters: dict, modulatedSignal, Fs: int, frequency: float) -> dict:
    """
    Simulates signal thru optical fiber.

    Parameters
    -----
    Fs: sampling frequency

    frequency: central frequency of optical signal [Hz]

    Returns
    -----
    recieverSignal: signal at the end of fiber
    """
    # Directly pass modulated signal without changes (Ideal channel)
    if fiberParameters.get("Ideal"):
        return {"recieverSignal":modulatedSignal}
    
    # Linear optical channel
    paramCh = parameters()
    paramCh.L = fiberParameters.get("Length")         # total link distance [km]
    paramCh.α = fiberParameters.get("Attenuation")        # fiber loss parameter [dB/km]
    paramCh.D = fiberParameters.get("Dispersion")         # fiber dispersion parameter [ps/nm/km]
    paramCh.Fc = frequency # central optical frequency [Hz]
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

        recieverSignal = edfa(recieverSignal, amplifierParameters.get("Ideal"), paramEDFA)

    return {"recieverSignal":recieverSignal}

def detection(recieverParameters: dict, recieverSignal, referentSignal, generalParameters: dict) -> dict:
    """
    Convert optical signal back to electrical

    Parameters
    ----
    referentSginal: optical signal as a signal from local oscilator for coherent detection

    Returns
    -----
    detectedSignal
    """
    Fs = generalParameters.get("Fs")
    Rs = generalParameters.get("Rs")

    if recieverParameters.get("Type") == "Photodiode":
        # Ideal photodiode
        if recieverParameters.get("Ideal"):
            paramPD = parameters
            paramPD.idel = True
        else:
            # noisy photodiode (thermal noise + shot noise + bandwidth limitation)
            paramPD = parameters()
            paramPD.ideal = False
            paramPD.B = recieverParameters.get("Bandwidth")
            paramPD.Fs = Fs

        return {"detectedSignal":photodiode(recieverSignal, paramPD)}
    
    elif recieverParameters.get("Type") == "Coherent":
        # Ideal photodiode
        if recieverParameters.get("Ideal"):
            paramPD = parameters
            paramPD.idel = True
        else:
            # noisy photodiode (thermal noise + shot noise + bandwidth limitation)
            paramPD = parameters()
            paramPD.ideal = False
            paramPD.B = recieverParameters.get("Bandwidth")
            paramPD.Fs = Fs

        return {"detectedSignal":coherentReceiver(recieverSignal, referentSignal, paramPD)}

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


def getPlot(type: str, title: str, simulationResults: dict, generalParameters: dict)  -> tuple[plt.Figure, plt.Axes]:
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

    if type == "informationTx":
        # Modulation signal
        return signalInTime(Ts, informationSignal, title, "electrical")
    elif type == "informationRx":
        # Detected signal
        return signalInTime(Ts, detectedSignal, title, "electrical")
    elif type == "constellationTx":
        # Tx constellation diagram
        return pconst(symbolsTx, whiteb=False)
    elif type == "constellationRx":
        # Rx constellation diagram
        return pconst(symbolsRx, whiteb=False)
    elif type == "psdTx":
        # Tx PSD
        return powerSpectralDensity(Rs, Fs, modulatedSignal, title)
    elif type == "psdRx":
        return powerSpectralDensity(Rs, Fs, recieverSignal, title)
    elif type == "signalTx":
        # Modulated signal in time (Tx signal)
        return signalInTime(Ts, modulatedSignal, title, "optical")
    elif type == "signalRx":
        # Reciever signal in time (Rx signal)
        return signalInTime(Ts, recieverSignal, title, "optical")
    elif type == "eyediagramTx":
        # Tx eyediagram
        discard = 100
        return eyediagram(informationSignal[discard:-discard], informationSignal.size-2*discard, SpS, plotlabel="signal at Tx", ptype="fancy")
    elif type == "eyediagramRx":
        # Rx eyediagram
        discard = 100
        return eyediagram(detectedSignal[discard:-discard], detectedSignal.size-2*discard, SpS, plotlabel="signal at Rx", ptype="fancy")
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
    Rs = generalParameters.get("Rs")

    bitsTx = simulationResults.get("bitsTx")
    bitsRx = simulationResults.get("bitsRx")
    symbolsTx = simulationResults.get("symbolsTx")
    modulatedSignal = simulationResults.get("modulatedSignal")
    recieverSignal = simulationResults.get("recieverSignal")

    # Error values

    valuesList = fastBERcalc(bitsRx, bitsTx, modulationOrder, modulationFormat)
    # extract the values from arrays
    ber, ser, snr = [array[0] for array in valuesList]
    values = {"BER":ber, "SER":ser, "SNR":snr}

    # Transmission speed
    values.update({"Speed":calculateTransSpeed(bitsTx, symbolsTx, Rs)})

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

def convertDataQuantity(data: str) -> int:
    """
    Converts string "kb" / "Mb" / "Gb" to int number
    """
    if data == "kb":
        return 10**3
    elif data == "Mb":
        return 10**6
    elif data == "Gb":
        return 10**9