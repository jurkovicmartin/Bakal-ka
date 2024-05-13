# Simulation functions

import numpy as np
from commpy.utilities  import upsample
from optic.models.devices import mzm, photodiode, basicLaserModel, iqm, coherentReceiver, pm
from optic.models.channels import linearFiberChannel
from optic.comm.modulation import modulateGray, GrayMapping, demodulateGray
from optic.dsp.core import pulseShape, pnorm, signal_power, sigPow
from optic.comm.metrics import fastBERcalc

try:
    from optic.dsp.coreGPU import firFilter    
except ImportError:
    from optic.dsp.core import firFilter
    
from optic.utils import parameters
import matplotlib.pyplot as plt

from scripts.my_devices import edfa, laserSource, idealLaser, myiqm
from scripts.my_plot import eyediagram, constellation, opticalSpectrum, electricalInTime, opticalInTime
from scripts.other_functions import calculateTransSpeed

def simulate(generalParameters: dict, sourceParameters: dict, modulatorParameters: dict, channelParameters: dict, recieverParameters: dict, amplifierParameters: dict, includeAmplifier: bool) -> dict:
    """
    Simulate communication.

    Parameters
    -----
    generalParameters: including modulation format and order for maping

    Returns
    -----
    simulationResults: bitsTx, symbolsTx, modulationSignal, carrierSignal, modulatedSignal, recieverSignal, detectedSignal, symbolsRx, bitsRx

    ! error with detection of amplifier and signal power => recieverSignal is None
    """

    # Each time random numbers
    np.random.seed(seed=123)

    Fs = generalParameters.get("Fs")
    frequency = sourceParameters.get("Frequency")*10**12 # Manage units (THz -> Hz)

    # Output dictionary
    simulationResults = {}
 
    # Adds bitsTx, symbolsTx, modulationSignal
    simulationResults.update(modulationSignal(generalParameters))
    # Adds carrierSignal
    simulationResults.update(carrierSignal(sourceParameters, Fs, simulationResults.get("modulationSignal")))
    # Adds modulatedSignal
    simulationResults.update(modulate(modulatorParameters, simulationResults.get("modulationSignal"), simulationResults.get("carrierSignal"), generalParameters))
    # Adds recieverSignal
    simulationResults.update(fiberTransmition(channelParameters, amplifierParameters, simulationResults.get("modulatedSignal"), Fs, frequency, includeAmplifier))
    
    # Error with amplifier detection (signal is too low)
    if simulationResults.get("recieverSignal") is None:
        return simulationResults
    
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
    if sourceParameters.get("Ideal"):
        power = sourceParameters.get("Power")
        samples = len(modulationSignal)
        return{"carrierSignal":idealLaser(power, samples)}
    
    else:
        # Converts rin (dB/Hz to absolute value)
        rin = 10**(sourceParameters.get("RIN") / 10)

        print(sourceParameters.get("Linewidth"))

        # Laser parameters
        paramLaser = parameters()
        paramLaser.P = sourceParameters.get("Power")   # laser power [dBm] [default: 10 dBm]
        paramLaser.lw = sourceParameters.get("Linewidth")    # laser linewidth [Hz] [default: 1 kHz]
        paramLaser.Fs = Fs  # sampling rate [samples/s]
        paramLaser.Ns = len(modulationSignal)   # number of signal samples [default: 1e3]
        paramLaser.RIN_var = rin # RIN [1e-20]

        return {"carrierSignal":basicLaserModel(paramLaser)}

def modulate(modulatorParameters: dict, modulationSignal, carrierSignal, generalParameters: dict) -> dict:
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

        if generalParameters.get("Format") == "pam" and generalParameters.get("Order") == 4:
            return {"modulatedSignal":mzm(carrierSignal, modulationSignal*0.7, paramMZM)}
        else:
            return {"modulatedSignal":mzm(carrierSignal, modulationSignal, paramMZM)}
    
    elif modulatorParameters.get("Type") == "IQM":
        # IQM parameters
        paramIQM = parameters()
        paramIQM.Vpi = 2
        paramIQM.Vbl = -2
        paramIQM.VbQ = -2
        paramIQM.Vphi = 1

        return {"modulatedSignal":iqm(carrierSignal*np.sqrt(2), modulationSignal, paramIQM)}
    
    else: raise Exception("Unexpected error")

def fiberTransmition(fiberParameters: dict, amplifierParameters: dict, modulatedSignal, Fs: int, frequency: float, includeAmplifier: bool) -> dict:
    """
    Simulates signal thru optical fiber.

    Parameters
    -----
    Fs: sampling frequency

    frequency: central frequency of optical signal [Hz]

    Returns
    -----
    recieverSignal: signal at reciever (dictionary)
    """

    paramCh = parameters()
    paramCh.L = fiberParameters.get("Length")         # total link distance [km]
    paramCh.α = fiberParameters.get("Attenuation")        # fiber loss parameter [dB/km]
    paramCh.D = fiberParameters.get("Dispersion")         # fiber dispersion parameter [ps/nm/km]
    paramCh.Fc = frequency # central optical frequency [Hz]
    paramCh.Fs = Fs        # simulation sampling frequency [samples/second]

    # Channel has amplifier = doesnt has initial 0 gain
    if includeAmplifier:
        recieverSignal = amplifierTransmition(paramCh, amplifierParameters, fiberParameters.get("Ideal"), modulatedSignal, Fs, frequency)
    # Channel without amplifier
    else:
        # Directly pass modulated signal without changes (Ideal channel)
        if fiberParameters.get("Ideal"):
            return {"recieverSignal":modulatedSignal}
        
        recieverSignal = linearFiberChannel(modulatedSignal, paramCh)

    return {"recieverSignal":recieverSignal}


def amplifierTransmition(fiberParameters, amplifierParameters: dict, idealChannel: bool, modulatedSignal, Fs: int, frequency: float) -> np.ndarray | None:
    """
    Simulates signal thru fiber with amplifier.

    Parameters
    -----
    fiberParameters: parameters() object

    Fs: sampling frequency

    frequency: central frequency of optical signal [Hz]

    Returns
    -----
    recieverSignal: signal at reciever (array)

    None: in case there was a error with detection limit of amplifier and signal power
    """

    # Amplifier parameters
    paramEDFA = parameters()
    paramEDFA.G = amplifierParameters.get("Gain")    # edfa gain
    paramEDFA.NF = amplifierParameters.get("Noise")   # edfa noise figure 
    paramEDFA.Fc = frequency
    paramEDFA.Fs = Fs

    detectionLimit = amplifierParameters.get("Detection")
    amplifierPosition = amplifierParameters.get("Position")

    # Ideal channel (= position of amplifier does not matter)
    if idealChannel:
        if amplifierParameters.get("Ideal"):
            recieverSignal = edfa(modulatedSignal, amplifierParameters.get("Ideal"), paramEDFA)
        else:
            if not(checkPower(modulatedSignal, detectionLimit)):
                return
            
            recieverSignal = edfa(modulatedSignal, amplifierParameters.get("Ideal"), paramEDFA)
    
    # Ideal amplifier with real channel
    elif amplifierParameters.get("Ideal") and not(idealChannel):

        if amplifierPosition == "start":
            modulatedSignal = edfa(modulatedSignal, amplifierParameters.get("Ideal"), paramEDFA)

            recieverSignal = linearFiberChannel(modulatedSignal, fiberParameters)

        elif amplifierPosition == "middle":
            # Lenght needs to be halfed
            fiberParameters.L = fiberParameters.L / 2
            # First half
            modulatedSignal = linearFiberChannel(modulatedSignal, fiberParameters)
            # Amplifier
            modulatedSignal = edfa(modulatedSignal, amplifierParameters.get("Ideal"), paramEDFA)
            # Second half
            recieverSignal = linearFiberChannel(modulatedSignal, fiberParameters)

        elif amplifierPosition == "end":
            modulatedSignal = linearFiberChannel(modulatedSignal, fiberParameters)

            recieverSignal = edfa(modulatedSignal, amplifierParameters.get("Ideal"), paramEDFA)
        
        else: raise Exception("Unexpected error")

    # Real amplifier with real channel
    elif not(amplifierParameters.get("Ideal")) and not(idealChannel):
        if amplifierPosition == "start":
            # Signal power is too low
            if not(checkPower(modulatedSignal, detectionLimit)):
                return
            
            modulatedSignal = edfa(modulatedSignal, amplifierParameters.get("Ideal"), paramEDFA)

            recieverSignal = linearFiberChannel(modulatedSignal, fiberParameters)

        elif amplifierPosition == "middle":
            # Lenght needs to be halfed
            fiberParameters.L = fiberParameters.L / 2

            # Signal power is too low
            if not(checkPower(modulatedSignal, detectionLimit)):
                return
            
            # First half
            modulatedSignal = linearFiberChannel(modulatedSignal, fiberParameters)
            # Amplifier
            modulatedSignal = edfa(modulatedSignal, amplifierParameters.get("Ideal"), paramEDFA)
            # Second half
            recieverSignal = linearFiberChannel(modulatedSignal, fiberParameters)

        elif amplifierPosition == "end":
            modulatedSignal = linearFiberChannel(modulatedSignal, fiberParameters)

            # Signal power is too low
            if not(checkPower(modulatedSignal, detectionLimit)):
                return

            recieverSignal = edfa(modulatedSignal, amplifierParameters.get("Ideal"), paramEDFA)
        
        else: raise Exception("Unexpected error")
    else: raise Exception("Unexpected error")

    return recieverSignal


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
            paramPD.R = recieverParameters.get("Resolution")
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
            paramPD.R = recieverParameters.get("Resolution")
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


def getPlot(type: str, title: str, simulationResults: dict, generalParameters: dict, sourceParameters: dict)  -> tuple[plt.Figure, plt.Axes]:
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

    # Frequency to Hz
    centralFrequency = sourceParameters.get("Frequency") * 10**12

    carrierSignal =simulationResults.get("carrierSignal")
    informationSignal = simulationResults.get("modulationSignal")
    modulatedSignal = simulationResults.get("modulatedSignal")
    recieverSignal = simulationResults.get("recieverSignal")
    detectedSignal = simulationResults.get("detectedSignal")
    symbolsTx = simulationResults.get("symbolsTx")
    symbolsRx = simulationResults.get("symbolsRx")

    if type == "electricalTx":
        # Modulation signal
        return electricalInTime(Ts, informationSignal, title)
    elif type == "electricalRx":
        # Detected signal
        return electricalInTime(Ts, detectedSignal, title)
    elif type == "constellationTx":
        # Tx constellation diagram
        return constellation(symbolsTx, whiteb=False, title="Tx symbols")
    elif type == "constellationRx":
        # Rx constellation diagram
        return constellation(symbolsRx, whiteb=False, title="Rx symbols")
    elif type == "spectrumTx":
        # Tx optical spectrum
        return opticalSpectrum(modulatedSignal, 10**12, centralFrequency, title)
        # Rx optical spectrum
    elif type == "spectrumRx":
        return opticalSpectrum(recieverSignal, 10**12, centralFrequency, title)
        # Source signal spectrum
    elif type == "spectrumSc":
        return opticalSpectrum(carrierSignal, 10**12, centralFrequency, title)
    elif type == "opticalTx":
        # Modulated signal in time (Tx signal)
        return opticalInTime(Ts, modulatedSignal, title, "modulated")
    elif type == "opticalRx":
        # Reciever signal in time (Rx signal)
        return opticalInTime(Ts, recieverSignal, title, "modulated")
    elif type == "opticalSc":
        # Source signal in time
        return opticalInTime(Ts, carrierSignal, title, "carrier")
    elif type == "eyeTx":
        # Tx eyediagram
        discard = 100
        return eyediagram(informationSignal[discard:-discard], informationSignal.size-2*discard, SpS, ptype="fancy", title="signal at Tx")
    elif type == "eyeRx":
        # Rx eyediagram
        discard = 100
        return eyediagram(detectedSignal[discard:-discard], detectedSignal.size-2*discard, SpS, ptype="fancy", title="signal at Rx")
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
    symbolsRx = simulationResults.get("symbolsRx")
    modulatedSignal = simulationResults.get("modulatedSignal")
    recieverSignal = simulationResults.get("recieverSignal")

    # Error values

    valuesList = fastBERcalc(symbolsRx, symbolsTx, modulationOrder, modulationFormat)
    # extract the values from arrays
    ber, ser, snr = [array[0] for array in valuesList]
    values = {"BER":ber, "SER":ser, "SNR":snr}

    # Transmission speed
    values.update({"Speed":calculateTransSpeed(Rs, modulationOrder)})

    # Tx power [W]
    power = signal_power(modulatedSignal)
    values.update({"powerTxW":power})
    # Tx power [dBm]
    power = 10*np.log10(power / 1e-3)
    values.update({"powerTxdBm":power})
    # Rx power [W]
    power = signal_power(recieverSignal)
    values.update({"powerRxW":power})
    # Rx power [dBm]
    power = 10*np.log10(power / 1e-3)
    values.update({"powerRxdBm":power})

    return values


def checkPower(signal, limit) -> bool:
        """
        In case of using amplifier checks the signal power and compares it to setted amplifier detection limit.

        Returns
        ----
        True: ok

        False: signal power is too low
        """

        signalPower = 10*np.log10(signal_power(signal) / 1e-3)

        return signalPower >= limit