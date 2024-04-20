from optic.utils import parameters
from optic.models.devices import basicLaserModel
import numpy as np
import matplotlib.pyplot as plt
from optic.models.devices import mzm, pm

from optic.comm.modulation import modulateGray, GrayMapping
from optic.dsp.core import pulseShape, pnorm
from commpy.utilities  import upsample
try:
    from optic.dsp.coreGPU import firFilter    
except ImportError:
    from optic.dsp.core import firFilter

from optic.utils import parameters, dBm2W
from optic.dsp.core import gaussianComplexNoise, gaussianNoise

from optic.plot import plotPSD
from optic.models.amplification import OSA, get_spectrum

from scripts.my_plot import opticalSpectrum



def laser(param):

    P = getattr(param, "P", 10)  # Laser power in dBm
    lw = getattr(param, "lw", 1e3)  # Linewidth in Hz
    RIN_var = getattr(param, "RIN_var", 1e-20)  # RIN variance
    Ns = getattr(param, "Ns", 1000)  # Number of samples of the signal
    pn = getattr(param, "pn", 0)

    # deltaP = gaussianComplexNoise(Ns, RIN_var)
    deltaP = gaussianNoise(Ns, RIN_var)

    deltaPn = gaussianNoise(Ns, pn)

    # Return optical signal
    return np.sqrt(dBm2W(P)) * np.exp(1j * deltaPn) + deltaP



def mOSA(x, Fs, Fc=193.1e12):
    """
    Plot the optical spectrum of the signal in X and Y polarizations.

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
    plot

    """
    freqs, ZX = get_spectrum(x, Fs, Fc, xunits="m")
    yMin = -70
    yMax = ZX.max() + 10
    _,ax = plt.subplots(1)
    ax.plot( 1e9*freqs, ZX, label="X Pol.")
    # if (np.shape(x)[1] == 2):
    #     freqs, ZY = get_spectrum(x[:,1], Fs, Fc)
    #     ax.plot( 1e9*freqs, ZY, label="Y Pol.", alpha=0.5)
    #     yMax = np.array([ZX.max(), ZY.max()]).max() + 10
    #     ax.legend()
    ax.set_ylim([yMin, yMax])   
    ax.set_xlabel("Wavelength [nm]")
    ax.set_ylabel("Magnitude [dBm]")
    ax.minorticks_on()
    ax.grid(True)
    
    return ax


# INFORMATION SIGNAL
SpS = 8 # Samples per symbol
Rs = 10e9
Fs = SpS * Rs
modulationOrder = 2
modulationFormat = "pam"

# generate pseudo-random bit sequence
bitsTx = np.random.randint(2, size=int(np.log2(modulationOrder)*1e3))

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

# t = np.linspace(0, 1, len(information))
# # Define the start and end indices to plot
# start_index = 10
# end_index = 200  # Choose the end index according to your requirements

# # Slice both t and symbolsTx arrays
# t_slice = t[start_index:end_index]
# signal_slice = information[start_index:end_index]

# # Plotting real and imaginary parts in separate subplots
# fig, axs = plt.subplots(2, 1, figsize=(8, 8))

# # Plot real part
# axs[0].plot(t_slice, signal_slice.real, label='Real Part', linewidth=2, color='blue')
# axs[0].set_ylabel('Amplitude (a.u.)')
# axs[0].legend(loc='upper left')

# # Plot imaginary part
# axs[1].plot(t_slice, signal_slice.imag, label='Imaginary Part', linewidth=2, color='red')
# axs[1].set_ylabel('Amplitude (a.u.)')
# axs[1].set_xlabel('Time (s)')  # Adjust the unit based on your data
# axs[1].legend(loc='upper left')

# plt.suptitle("Information signal")

# CARRIER SIGNAL

# Laser parameters
paramLaser = parameters()
paramLaser.P = 10  # laser power [dBm] [default: 10 dBm]
paramLaser.lw = 1000    # laser linewidth [Hz] [default: 1 kHz]
paramLaser.RIN_var = 1e-20  # variance of the RIN noise [default: 1e-20]
paramLaser.Fs = 8  # sampling rate [samples/s]
paramLaser.Ns = len(information)   # number of signal samples [default: 1e3]

Fc = 191.7 * 10**12

paramLaser.pn = 1e-2
    
# signal = basicLaserModel(paramLaser)
signal = laser(paramLaser)


# t = np.linspace(0, 1, len(modulated))
interval = np.arange(100,500)
t = interval*(1/Fs)


# Calculate magnitude and phase
magnitude = np.abs(signal[interval])
phase = np.angle(signal[interval], deg=True)

# Plotting magnitude and phase in two subplots
fig, axs = plt.subplots(2, 1, figsize=(8, 8))

# Plot magnitude
axs[0].plot(t, magnitude, label='Magnitude', linewidth=2, color='blue')
axs[0].set_ylabel('Magnitude')
axs[0].legend(loc='upper left')

# Plot phase
axs[1].plot(t, phase, label='Phase', linewidth=2, color='red')
axs[1].set_ylabel('Phase (°)')
axs[1].set_xlabel('Time (s)')  # Adjust the unit based on your data
axs[1].legend(loc='upper left')

plt.suptitle("Carrier (Magnitude and Phase)")




# MODULATION

paramMZM = parameters()
paramMZM.Vpi = 2
paramMZM.Vb = -paramMZM.Vpi/2

modulated = mzm(signal, information, paramMZM)


# Vpi = 2 # PM’s Vπ voltage

# modulated = pm(signal, information, Vpi)

# t = np.linspace(0, 1, len(modulated))
interval = np.arange(100,500)
t = interval*(1/Fs)


# Calculate magnitude and phase
magnitude = np.abs(modulated[interval])
phase = np.angle(modulated[interval], deg=True)

# Plotting magnitude and phase in two subplots
fig, axs = plt.subplots(2, 1, figsize=(8, 8))

# Plot magnitude
axs[0].plot(t, magnitude, label='Magnitude', linewidth=2, color='blue')
axs[0].set_ylabel('Magnitude')
axs[0].legend(loc='upper left')

# Plot phase
axs[1].plot(t, phase, label='Phase', linewidth=2, color='red')
axs[1].set_ylabel('Phase (°)')
axs[1].set_xlabel('Time (s)')  # Adjust the unit based on your data
axs[1].legend(loc='upper left')

plt.suptitle("Modulated (Magnitude and Phase)")




# fig, axs = plt.subplots(figsize=(8,4))
# # axs.set_xlim(-3*Rs,3*Rs)
# # axs.set_ylim(-230,-130)
# axs.psd(np.abs(signal)**2, Fs=Fs, Fc=Fc, NFFT = 16*1024, sides="twosided", label = "Optical signal spectrum")
# axs.legend(loc="upper left")
# axs.set_title("PSD")

# plotPSD(modulated, Fs, Fc, label="PSD")

mOSA(modulated, Fs, Fc)

# opticalSpectrum(modulated, Fs, Fc, "From my lib")

plt.show()