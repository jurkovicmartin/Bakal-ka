
import numpy as np
from optic.utils import parameters
from scripts.my_devices import edfa
from optic.utils import dBm2W
import matplotlib.pyplot as plt
# from optic.models.amplification import get_spectrum
from optic.models.devices import basicLaserModel
import matplotlib.mlab as mlab
from scipy.constants import c


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

    plt.suptitle(title)




def generate_sinusoidal(amplitude, frequency, duration, sampling_freq):
    # Compute the number of samples
    N = int(duration * sampling_freq)
    
    # Time vector
    t = np.arange(N) / sampling_freq
    
    # Generate sinusoidal signal
    x = amplitude * np.sin(2 * np.pi * frequency * t)
    
    return x



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
    print(wavelength.min())
    print(wavelength.max())

    fig, ax1 = plt.subplots(1)
    ax1.plot( wavelength, spectrum)
    ax1.set_ylim([yMin, yMax])   
    ax1.set_xlabel("Wavelength [nm]")
    ax1.set_ylabel("Magnitude [dBm]")

    # ax.minorticks_on()
    ax1.grid(True)


    ax2 = ax1.twiny()

    # Make some room at the top
    fig.subplots_adjust(top=0.8)

    # Plot frequency vs wavelength
    ax2.plot(frequency, wavelength, color='red')
    ax2.set_xlabel('Frequency [THz]')

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


"""
Sampling frequency really ovlivni kvalitu (spectrum)
"""


ideal = False
Fs = 8000000
power = 20
length = 2000000

if ideal:
    Fc = 193.1 * (10**12)
    # carrier = np.full(length, dBm2W(power))
    samples = np.full(length, 1)
    # carrier = np.sqrt(dBm2W(power)) * np.exp(1j*samples)
    carrier = np.sqrt(dBm2W(power)) * samples

    #np.sqrt(dBm2W(P)) * np.exp(1j * pn) + deltaP
    #carrier = generate_sinusoidal(dBm2W(power), Fc, 1, Fs)
else:
    paramLaser = parameters()
    paramLaser.P = power  # laser power [dBm] [default: 10 dBm]
    paramLaser.lw = 1 # laser linewidth [Hz] [default: 1 kHz]
    paramLaser.Fs = Fs  # sampling rate [samples/s]
    paramLaser.Ns = length  # number of signal samples [default: 1e3]
    paramLaser.RIN_var = 1e-20
    Fc = 193.1 * (10**12)

    carrier = basicLaserModel(paramLaser)



opticalSpectrum(carrier, 1000000000000, Fc, "spectrum")

# opticalInTime(1/Fs, carrier, "carrier", "carrier")

plt.show()





paramEDFA = parameters()
paramEDFA.G = 20   # edfa gain
paramEDFA.NF = 4 # edfa noise figure 
paramEDFA.Fc = 193.1e12
paramEDFA.Fs = Fs

amplified = edfa(carrier, False, paramEDFA)