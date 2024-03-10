import numpy as np
from optic.comm.modulation import modulateGray, GrayMapping
from optic.dsp.core import pulseShape, pnorm
from commpy.utilities  import upsample
try:
    from optic.dsp.coreGPU import firFilter    
except ImportError:
    from optic.dsp.core import firFilter

import matplotlib.pyplot as plt

SpS = 8 # Samples per symbol
modulationOrder = 4
modulationFormat = "qam"

# generate pseudo-random bit sequence
bitsTx = np.random.randint(2, size=int(np.log2(modulationOrder)*1e6))

# generate modulated symbol sequence
grayMap = GrayMapping(modulationOrder, modulationFormat)
#print(f"grayMap: {grayMap}")

# Plotting
plt.figure(figsize=(8, 8))
plt.scatter(grayMap.real, grayMap.imag, color='blue', marker='o')
# Adding labels and grid
plt.title('Complex Numbers Plot')
plt.xlabel('Real Part')
plt.ylabel('Imaginary Part')
plt.grid(True)

symbolsTx = modulateGray(bitsTx, modulationOrder, modulationFormat)
#print(f"symbolsTx: {symbolsTx}")
symbolsTx = pnorm(symbolsTx) # power normalization

### SHOW SEPARATLY

# Generate a time array with the same length as symbolsTx
# t = np.linspace(0, 1, len(symbolsTx))

# # Define the start and end indices to plot
# start_index = 10
# end_index = 50  # Choose the end index according to your requirements

# # Slice both t and symbolsTx arrays
# t_slice = t[start_index:end_index]
# symbolsTx_slice = symbolsTx[start_index:end_index]

# # Plotting real and imaginary parts separately
# fig, axs = plt.subplots(figsize=(8, 4))
# axs.plot(t_slice, symbolsTx_slice.real, label='Real Part', linewidth=2)
# axs.plot(t_slice, symbolsTx_slice.imag, label='Imaginary Part', linewidth=2)

# axs.set_ylabel('Amplitude (a.u.)')
# axs.set_xlabel('Time (s)')  # Adjust the unit based on your data
# axs.legend(loc='upper left')
# axs.set_title("symbolsTx")


### SHOW IN ONE PLOT
# Generate a time array with the same length as symbolsTx
t = np.linspace(0, 1, len(symbolsTx))

# Define the start and end indices to plot
start_index = 10
end_index = 50  # Choose the end index according to your requirements

# Slice both t and symbolsTx arrays
t_slice = t[start_index:end_index]
symbolsTx_slice = symbolsTx[start_index:end_index]

# Calculate magnitude and phase
magnitude = np.abs(symbolsTx_slice)
phase = np.angle(symbolsTx_slice)

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

plt.suptitle("symbolsTx (Magnitude and Phase)")


# upsampling
symbolsUp = upsample(symbolsTx, SpS)

# typical NRZ pulse
pulse = pulseShape("nrz", SpS)
pulse = pulse/max(abs(pulse))

# pulse shaping
signalTx = firFilter(pulse, symbolsUp)





# Define the start and end indices to plot
start_index = 10
end_index = 200  # Choose the end index according to your requirements

# Slice both t and symbolsTx arrays
t_slice = t[start_index:end_index]
siginalTx_slice = signalTx[start_index:end_index]

# Plotting real and imaginary parts in separate subplots
fig, axs = plt.subplots(2, 1, figsize=(8, 8))

# Plot real part
axs[0].plot(t_slice, siginalTx_slice.real, label='Real Part', linewidth=2, color='blue')
axs[0].set_ylabel('Amplitude (a.u.)')
axs[0].legend(loc='upper left')

# Plot imaginary part
axs[1].plot(t_slice, siginalTx_slice.imag, label='Imaginary Part', linewidth=2, color='red')
axs[1].set_ylabel('Amplitude (a.u.)')
axs[1].set_xlabel('Time (s)')  # Adjust the unit based on your data
axs[1].legend(loc='upper left')

plt.suptitle("symbolsTx (Real and Imaginary Parts)")

# interval = np.arange(16*20,16*50)
# t = interval*(1/8000)/1e-9

# fig, axs = plt.subplots(figsize=(8,4))
# axs.plot(t, signalTx[interval], label = 'RF binary signal', linewidth=2)
# axs.set_ylabel('Amplitude (a.u.)')
# axs.set_xlabel('Time (ns)')
# axs.set_xlim(min(t),max(t))
# axs.legend(loc='upper left')
# axs.set_title("signalTx")
plt.show()

#return {"bitsTx":bitsTx, "symbolsTx":symbolsTx, "modulationSignal":signalTx}