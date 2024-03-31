from optic.utils import parameters
from optic.models.devices import basicLaserModel
import numpy as np
import matplotlib.pyplot as plt
from optic.models.devices import mzm, pm, iqm, photodiode, coherentReceiver, hybrid_2x4_90deg
from optic.comm.metrics import fastBERcalc

from scripts.my_devices import idealLaserModel

from optic.comm.modulation import modulateGray, GrayMapping, demodulateGray
from optic.dsp.core import pulseShape, pnorm, signal_power
from commpy.utilities  import upsample
try:
    from optic.dsp.coreGPU import firFilter    
except ImportError:
    from optic.dsp.core import firFilter


"""
MODULATOR
For default parameters is ok:

OOK - mzm, iqm
4PAM - iqm

2PSK - mzm, (iqm - img sharp edges), pm (magnitude show)
4PSK - iqm
8PSK - iqm

4QAM - iqm
16QAM - iqm
64QAM - iqm
256QAM - iqm

RECIVER

OOK - photodiode (only with mzm, not iqm)
4PAM

2PSK - photodiode (cut img)
4PSK - coherent
8PSK - coherent

4QAM - coherent
16QAM - coherent
64QAM - coherent
256QAM - coherent
"""


# INFORMATION SIGNAL
SpS = 8 # Samples per symbol
Fs = 8000
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

# PLOT
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



t = np.linspace(0, 1, len(information))

# Define the start and end indices to plot
start_index = 10
end_index = 200  # Choose the end index according to your requirements

# Slice both t and signal arrays
t_slice = t[start_index:end_index]
signal_slice = information[start_index:end_index]

# Calculate magnitude and phase
magnitude = np.abs(signal_slice)
phase = np.angle(signal_slice)

# Plotting magnitude and phase in two subplots
fig, axs = plt.subplots(2, 1, figsize=(8, 8))

# Plot magnitude
axs[0].plot(t_slice, magnitude, label='Magnitude', linewidth=2, color='blue')
axs[0].set_ylabel('Magnitude')
axs[0].legend(loc='upper left')

# Plot phase
axs[1].plot(t_slice, phase, label='Phase', linewidth=2, color='red')
axs[1].set_ylabel('Phase')
axs[1].set_xlabel('Time (s)')  # Adjust the unit based on your data
axs[1].legend(loc='upper left')

plt.suptitle("Information (Magnitude and Phase)")



# CARRIER
# Laser parameters
paramLaser = parameters()
paramLaser.P = 10  # laser power [dBm] [default: 10 dBm]
paramLaser.lw = 1000    # laser linewidth [Hz] [default: 1 kHz]
paramLaser.RIN_var = 0  # variance of the RIN noise [default: 1e-20]
paramLaser.Fs = 8  # sampling rate [samples/s]
paramLaser.Ns = len(information)   # number of signal samples [default: 1e3]

ideal = True

if ideal:

    carrier = idealLaserModel(paramLaser)

else:
    
    carrier = basicLaserModel(paramLaser)

# PLOT
# t = np.linspace(0, 1, len(carrier))
# # Define the start and end indices to plot
# start_index = 10
# end_index = 50  # Choose the end index according to your requirements

# # Slice both t and symbolsTx arrays
# t_slice = t[start_index:end_index]
# signal_slice = carrier[start_index:end_index]

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

# plt.suptitle("Carrier signal")



# MODULATION
modulator = "mzm"

if modulator == "mzm":
    paramMZM = parameters()
    paramMZM.Vpi = 2 # frequency of cosinus
    # paramMZM.Vb = -paramMZM.Vpi/2
    paramMZM.Vb = -1 # phase shift of cosinus
    """
    Vb: -1 ok, +1 protifaze, 0 spicky
    """

    modulated = mzm(carrier, information, paramMZM)

elif modulator == "pm":
    Vpi = 2 # PM’s Vπ voltage

    modulated = pm(carrier, information, Vpi)

elif modulator == "iqm":
    paramIQM = parameters()
    paramIQM.Vpi = 2 # MZM’s Vpi voltage
    paramIQM.VbI = -2 # I-MZM’s bias voltage
    paramIQM.VbQ = -2 # Q-MZM’s bias voltage
    paramIQM.Vphi = 1 # PM bias voltage

    modulated = iqm(carrier, information, paramIQM)

else: pass

# PLOT
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



t = np.linspace(0, 1, len(modulated))

# Define the start and end indices to plot
start_index = 10
end_index = 200  # Choose the end index according to your requirements

# Slice both t and signal arrays
t_slice = t[start_index:end_index]
signal_slice = modulated[start_index:end_index]

# Calculate magnitude and phase
magnitude = np.abs(signal_slice)
phase = np.angle(signal_slice)

# Plotting magnitude and phase in two subplots
fig, axs = plt.subplots(2, 1, figsize=(8, 8))

# Plot magnitude
axs[0].plot(t_slice, magnitude, label='Magnitude', linewidth=2, color='blue')
axs[0].set_ylabel('Magnitude')
axs[0].legend(loc='upper left')

# Plot phase
axs[1].plot(t_slice, phase, label='Phase', linewidth=2, color='red')
axs[1].set_ylabel('Phase')
axs[1].set_xlabel('Time (s)')  # Adjust the unit based on your data
axs[1].legend(loc='upper left')

plt.suptitle("Modulated (Magnitude and Phase)")


# DETECTION
detector = "coherent"

if detector == "photodiode":
    paramPD = parameters()
    paramPD.ideal = True

    detected = photodiode(modulated, paramPD)

elif detector == "coherent":
    paramPD = parameters()
    paramPD.ideal = True

    detected = coherentReceiver(modulated, carrier, paramPD)

else: pass

    


# PLOT
t = np.linspace(0, 1, len(detected))
# Define the start and end indices to plot
start_index = 10
end_index = 200  # Choose the end index according to your requirements

# Slice both t and symbolsTx arrays
t_slice = t[start_index:end_index]
signal_slice = detected[start_index:end_index]

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

plt.suptitle("Detected signal")
    

# RESTORE
detected = detected/np.std(detected)

# capture samples in the middle of signaling intervals
symbolsRx = detected[0::SpS]

# subtract DC level and normalize power
symbolsRx = symbolsRx - symbolsRx.mean()
symbolsRx = pnorm(symbolsRx)

# demodulate symbols to bits with minimum Euclidean distance 
const = GrayMapping(modulationOrder, modulationFormat) # get constellation
Es = signal_power(const) # calculate the average energy per symbol of the constellation

# demodulated bits
bitsRx = demodulateGray(np.sqrt(Es)*symbolsRx, modulationOrder, modulationFormat)


ber = fastBERcalc(bitsRx, bitsTx, modulationOrder, modulationFormat)[0]

print(f"SymbolsTx: {symbolsTx}")
print(f"SymbolsRx: {symbolsRx}")
print(f"Tx bits:{bitsTx}")
print(f"Rx bits:{bitsRx}")
print(f"BER: {ber}")

plt.show()