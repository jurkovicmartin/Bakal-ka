
import numpy as np
from optic.utils import parameters
from scripts.my_devices import edfa
from optic.utils import dBm2W
import matplotlib.pyplot as plt
# from optic.models.amplification import get_spectrum
from optic.models.devices import basicLaserModel, mzm
import matplotlib.mlab as mlab
from scipy.constants import c

from optic.comm.modulation import modulateGray, GrayMapping
try:
    from optic.dsp.coreGPU import firFilter    
except ImportError:
    from optic.dsp.core import firFilter
from optic.dsp.core import pulseShape, pnorm, signal_power, sigPow
from commpy.utilities  import upsample

def opticalInTime(Ts: int, signal, title: str, type: str):
    """
    Plot optical signal in time showed as magnitude and phase.

    Parameters
    ----
    type: carrier / modulated
    """

    # interval for plot
    interval = np.arange(100,600)
    t = interval*Ts

    magnitude = np.abs(signal[interval]**2)
    phase = np.angle(signal[interval], deg=True)

    if type == "carrier":
        yMin = 0
        yMax = magnitude.max()*2
    # modulated
    else:
        yMin = -1e-6
        yMax = magnitude.max() + 0.05 * magnitude.max()

    # Plotting magnitude and phase in two subplots
    fig, axs = plt.subplots(2, 1, figsize=(8, 4))

    # Plot magnitude
    axs[0].plot(t, magnitude, label="Magnitude", linewidth=2, color="blue")
    axs[0].set_ylabel("Power (p.u.)")
    axs[0].legend(loc="upper left")
    axs[0].set_ylim([yMin, yMax])

    # Plot phase
    axs[1].plot(t, phase, label="Phase", linewidth=2, color="red")
    axs[1].set_ylabel("Phase (°)")
    axs[1].set_xlabel("Time (s)")
    axs[1].legend(loc="upper left")
    axs[1].set_ylim([-180,180])

    plt.suptitle(title)




def opticalSpectrum(signal, Fs: int, Fc: float, title: str):
    """
    Plot optical spectrum with wavelength.

    Parameters:
    -----
    Fs: sampling frequency

    Fc: central frequency
    """
    frequency, spectrum = get_spectrum(signal, Fs, Fc, xunits="Hz")

    # Wavelength
    wavelength = c/frequency
    # To nm
    wavelength = wavelength * 10**9

    # To THz
    frequency = frequency / 10**12

    yMin = spectrum.min()
    yMax = spectrum.max() + 10

    if yMin == -np.inf:
        yMin = -150

    print(yMax)
    print(yMin)

    fig, ax1 = plt.subplots(1)
    ax1.plot( wavelength, frequency)
    ax1.set_ylim([yMin, yMax])   
    ax1.set_xlabel("Wavelength [nm]")
    ax1.set_ylabel("Magnitude [dBm]")

    ax1.minorticks_on()
    ax1.grid(True)


    ax2 = ax1.twiny()

    # Make some room at the top
    fig.subplots_adjust(top=0.8)

    # Plot frequency vs wavelength
    ax2.plot(frequency, spectrum)
    ax2.set_xlabel('Frequency [THz]')
    ax2.minorticks_on()
    ax2.grid(True)

    # Set scattered ticks on the x-axis
    # num_ticks = 5  # Set the number of ticks you want to display
    # tick_indices = np.linspace(0, len(wavelength) - 1, num_ticks, dtype=int)
    # ax.set_xticks(wavelength[tick_indices])
    # ax.set_xticklabels([f"{freq_nm:.3f}" for freq_nm in wavelength[tick_indices]])

    plt.suptitle(title)



def get_spectrum(x, Fs, Fc, xunits = 'm', yunits = 'dBm', window=mlab.window_none, sides="twosided"):
    """
    Calculates the optical spectrum of the signal.

    Parameters
    ----------
    x : np.array
        Signal
    Fs : scalar
        Sampling frequency in Hz.
    Fc : scalar, optional
        Central optical frequency. The default is 193.1e12.

    Returns
    -------
    spectrum : np.array
        Signal's FFT
    frequency: np.array
        Frequency array @ Fc.

    """
    spectrum, frequency = mlab.magnitude_spectrum(
        x, Fs=Fs, window=window, sides=sides
    )
    frequency = c/(frequency + Fc) if (xunits=='m') else frequency + Fc
    spectrum = spectrum*np.conj(spectrum)
    if (yunits=='dBm'):
        spectrum = 10*np.log10(1e3*spectrum)

    return frequency, spectrum



def idealLaser(power: float, length: int) -> np.array:
    """
    Creates ideal optical signal.

    Parameters
    ----
    power: laser power in dBm

    samples: number of samples to be generated
    """
    # length = np.full(samples, 1)
    # length = np.arange(0, samples)

    # carrier = np.sqrt(dBm2W(power)) * np.exp(1j*samples)
    # return np.sqrt(dBm2W(power)) * length
    # return np.sqrt(dBm2W(power)) * np.exp(1j*length)

    # Parameters
    sampling_rate = Fs  # Sampling rate in Hz
    duration = 1  # Duration of the signal in seconds
    frequency = 10  # Frequency of the ideal signal in Hz

    # Time array
    t = np.arange(0, duration, 1/sampling_rate)

    # Generate ideal signal
    ideal_signal = np.sqrt(dBm2W(power)) * np.exp(2j * np.pi * t)


    samples = np.zeros(length)
    samples = np.arange(0, 1, 1/length)
    return np.sqrt(dBm2W(power)) * np.exp(2j * np.pi * samples)



def frequency_spectrum(signal, sample_rate, freq_range=None):
    """
    Compute the frequency spectrum of a signal.

    Parameters:
        signal (array-like): Array of complex values representing the signal.
        sample_rate (float): Sampling rate of the signal.
        freq_range (tuple, optional): Tuple specifying the range of frequencies to consider.
                                       Defaults to None, which means the entire spectrum is computed.

    Returns:
        tuple: A tuple containing:
               - Array of spectrum values
               - Array of corresponding frequency values
    """
    # Compute FFT
    spectrum = np.fft.fft(signal)
    
    # Compute frequency axis
    n = len(signal)
    freq_axis = np.fft.fftfreq(n, d=1/sample_rate)
    
    # Take only positive frequencies
    positive_freq_mask = freq_axis >= 0
    spectrum = spectrum[positive_freq_mask]
    freq_axis = freq_axis[positive_freq_mask]
    
    # If freq_range is specified, filter the spectrum and frequency axis
    if freq_range is not None:
        freq_min, freq_max = freq_range
        freq_mask = (freq_axis >= freq_min) & (freq_axis <= freq_max)
        spectrum = spectrum[freq_mask]
        freq_axis = freq_axis[freq_mask]
    
    return spectrum, freq_axis


def newOpticalSpectrum(signal, Fs: int, Fc: int, title: str, range=None):
    """
    Plot optical spectrum with wavelength.

    Parameters:
    -----
    Fs: sampling frequency

    Fc: central frequency
    """
    frequency, spectrum = frequency_spectrum(signal, Fs, range)

    print(frequency.min())
    print(frequency.max())
    print(spectrum.min())
    print(spectrum.max())

    plt.plot(frequency, np.abs(spectrum))
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.title('Frequency Spectrum')
    plt.show()


"""
Sampling frequency really ovlivni kvalitu (spectrum)
"""


ideal = False
SpS = 8
Rs = 1000000
Fs = SpS * Rs
power = 20
Fc = 134.6 * (10**12)

modulationOrder = 2
modulationFormat = "pam"


# generate pseudo-random bit sequence
bitsTx = np.random.randint(2, size=int(np.log2(modulationOrder)*1e6))
# generate modulated symbol sequence
grayMap = GrayMapping(modulationOrder, modulationFormat)
#print(f"grayMap: {grayMap}")
symbolsTx = modulateGray(bitsTx, modulationOrder, modulationFormat)
#print(f"symbolsTx: {symbolsTx}")
symbolsTx = pnorm(symbolsTx) # power normalization
# upsampling
symbolsUp = upsample(symbolsTx, SpS)
# typical NRZ pulse
pulse = pulseShape("nrz", SpS)
pulse = pulse/max(abs(pulse))
# pulse shaping
information = firFilter(pulse, symbolsUp)





if ideal:
    # carrier = np.full(length, dBm2W(power))
    samples = len(information)

    carrier = idealLaser(power, len(information))

    #np.sqrt(dBm2W(P)) * np.exp(1j * pn) + deltaP
    #carrier = generate_sinusoidal(dBm2W(power), Fc, 1, Fs)
else:
    paramLaser = parameters()
    paramLaser.P = power  # laser power [dBm] [default: 10 dBm]
    paramLaser.lw = 1000 # laser linewidth [Hz] [default: 1 kHz]
    paramLaser.Fs = Fs  # sampling rate [samples/s]
    paramLaser.Ns = len(information)  # number of signal samples [default: 1e3]
    paramLaser.RIN_var = 0

    carrier = basicLaserModel(paramLaser)

spectrumFs = 10**12

opticalSpectrum(carrier, spectrumFs, Fc, "Carrier spectrum")
# opticalInTime(1/Fs, carrier, "carrier", "carrier")
# newOpticalSpectrum(carrier, 10**12, Fc, "New spectrum")

# opticalInTime(1/Fs, carrier, "carrier", "carrier")


# paramMZM = parameters()
# paramMZM.Vpi = 2 # frequency of cosinus
# # paramMZM.Vb = -paramMZM.Vpi/2
# paramMZM.Vb = -1 # phase shift of cosinus

# modulated = mzm(carrier, information, paramMZM)


# opticalSpectrum(modulated, spectrumFs, Fc, "Modulated spectrum")


# paramEDFA = parameters()
# paramEDFA.G = 20   # edfa gain
# paramEDFA.NF = 10 # edfa noise figure 
# paramEDFA.Fc = Fc
# paramEDFA.Fs = Fs

# amplified = edfa(modulated, False, paramEDFA)

# opticalSpectrum(amplified, spectrumFs, Fc, "Amplified spectrum")

plt.show()