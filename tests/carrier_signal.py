from optic.utils import parameters
from optic.models.devices import basicLaserModel
import numpy as np
import matplotlib.pyplot as plt
from optic.models.devices import mzm

from scripts.my_devices import idealLaserModel

from optic.comm.modulation import modulateGray, GrayMapping
from optic.dsp.core import pulseShape, pnorm
from commpy.utilities  import upsample
try:
    from optic.dsp.coreGPU import firFilter    
except ImportError:
    from optic.dsp.core import firFilter


# INFORMATION SIGNAL
SpS = 8 # Samples per symbol
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

t = np.linspace(0, 1, len(information))
# Define the start and end indices to plot
start_index = 10
end_index = 200  # Choose the end index according to your requirements

# Slice both t and symbolsTx arrays
t_slice = t[start_index:end_index]
signal_slice = information[start_index:end_index]

# Plotting real and imaginary parts in separate subplots
fig, axs = plt.subplots(2, 1, figsize=(8, 8))

# Plot real part
axs[0].plot(t_slice, signal_slice.real, label='Real Part', linewidth=2, color='blue')
axs[0].set_ylabel('Amplitude (a.u.)')
axs[0].legend(loc='upper left')

# Plot imaginary part
axs[1].plot(t_slice, signal_slice.imag, label='Imaginary Part', linewidth=2, color='red')
axs[1].set_ylabel('Amplitude (a.u.)')
axs[1].set_xlabel('Time (s)')  # Adjust the unit based on your data
axs[1].legend(loc='upper left')

plt.suptitle("Information signal")

# CARRIER SIGNAL

# Laser parameters
paramLaser = parameters()
paramLaser.P = 10  # laser power [dBm] [default: 10 dBm]
paramLaser.lw = 1000    # laser linewidth [Hz] [default: 1 kHz]
paramLaser.RIN_var = 0  # variance of the RIN noise [default: 1e-20]
paramLaser.Fs = 8  # sampling rate [samples/s]
paramLaser.Ns = len(information)   # number of signal samples [default: 1e3]

ideal = True

if ideal:

    signal = idealLaserModel(paramLaser)

    t = np.linspace(0, 1, len(signal))
    # Define the start and end indices to plot
    start_index = 10
    end_index = 50  # Choose the end index according to your requirements

    # Slice both t and symbolsTx arrays
    t_slice = t[start_index:end_index]
    signal_slice = signal[start_index:end_index]

    # Plotting real and imaginary parts in separate subplots
    fig, axs = plt.subplots(2, 1, figsize=(8, 8))

    # Plot real part
    axs[0].plot(t_slice, signal_slice.real, label='Real Part', linewidth=2, color='blue')
    axs[0].set_ylabel('Amplitude (a.u.)')
    axs[0].legend(loc='upper left')

    # Plot imaginary part
    axs[1].plot(t_slice, signal_slice.imag, label='Imaginary Part', linewidth=2, color='red')
    axs[1].set_ylabel('Amplitude (a.u.)')
    axs[1].set_xlabel('Time (s)')  # Adjust the unit based on your data
    axs[1].legend(loc='upper left')

    plt.suptitle("Carrier signal")

else:
    
    signal = basicLaserModel(paramLaser)

    t = np.linspace(0, 1, len(signal))
    # Define the start and end indices to plot
    start_index = 10
    end_index = 50  # Choose the end index according to your requirements

    # Slice both t and symbolsTx arrays
    t_slice = t[start_index:end_index]
    signal_slice = signal[start_index:end_index]

    # Plotting real and imaginary parts in separate subplots
    fig, axs = plt.subplots(2, 1, figsize=(8, 8))

    # Plot real part
    axs[0].plot(t_slice, signal_slice.real, label='Real Part', linewidth=2, color='blue')
    axs[0].set_ylabel('Amplitude (a.u.)')
    axs[0].legend(loc='upper left')

    # Plot imaginary part
    axs[1].plot(t_slice, signal_slice.imag, label='Imaginary Part', linewidth=2, color='red')
    axs[1].set_ylabel('Amplitude (a.u.)')
    axs[1].set_xlabel('Time (s)')  # Adjust the unit based on your data
    axs[1].legend(loc='upper left')

    plt.suptitle("Carrier signal")

# MODULATION

paramMZM = parameters()
paramMZM.Vpi = 2
paramMZM.Vb = -paramMZM.Vpi/2

modulated = mzm(signal, 0.25*information, paramMZM)



t = np.linspace(0, 1, len(modulated))
# Define the start and end indices to plot
start_index = 10
end_index = 200  # Choose the end index according to your requirements

# Slice both t and symbolsTx arrays
t_slice = t[start_index:end_index]
signal_slice = modulated[start_index:end_index]

# Plotting real and imaginary parts in separate subplots
fig, axs = plt.subplots(2, 1, figsize=(8, 8))

# Plot real part
axs[0].plot(t_slice, signal_slice.real, label='Real Part', linewidth=2, color='blue')
axs[0].set_ylabel('Amplitude (a.u.)')
axs[0].legend(loc='upper left')

# Plot imaginary part
axs[1].plot(t_slice, signal_slice.imag, label='Imaginary Part', linewidth=2, color='red')
axs[1].set_ylabel('Amplitude (a.u.)')
axs[1].set_xlabel('Time (s)')  # Adjust the unit based on your data
axs[1].legend(loc='upper left')

plt.suptitle("Modulated signal")

plt.show()