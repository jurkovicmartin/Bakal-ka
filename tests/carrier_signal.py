from optic.utils import parameters
from optic.models.devices import basicLaserModel
import numpy as np
import matplotlib.pyplot as plt

# Laser parameters
paramLaser = parameters()
paramLaser.P = 10  # laser power [dBm] [default: 10 dBm]
paramLaser.lw = 1000    # laser linewidth [Hz] [default: 1 kHz]
paramLaser.RIN_var = 0  # variance of the RIN noise [default: 1e-20]
paramLaser.Fs = 8  # sampling rate [samples/s]
paramLaser.Ns = 1000   # number of signal samples [default: 1e3]

signal = basicLaserModel(paramLaser)

print(signal)



# Extract real and imaginary parts
real_parts = [num.real for num in signal]
imaginary_parts = [num.imag for num in signal]

# Plot the complex numbers on the complex plane
plt.scatter(real_parts, imaginary_parts, color='blue', marker='o')
plt.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
plt.axvline(x=0, color='black', linestyle='--', linewidth=0.8)

# Set labels and title
plt.xlabel('Real Part')
plt.ylabel('Imaginary Part')
plt.title('Complex Number Plot')

# Show the plot
plt.grid(True)
plt.show()



t = np.linspace(0, 1, len(signal))
# Define the start and end indices to plot
start_index = 10
end_index = 50  # Choose the end index according to your requirements

# Slice both t and symbolsTx arrays
t_slice = t[start_index:end_index]
signal_slice = signal[start_index:end_index]

# # Calculate magnitude and phase
# magnitude = np.abs(signal_slice)
# phase = np.angle(signal_slice)

# # Plotting magnitude and phase in two subplots
# fig, axs = plt.subplots(2, 1, figsize=(8, 8))

# # Plot magnitude
# axs[0].plot(t_slice, magnitude, label='Magnitude', linewidth=2, color='blue')
# axs[0].set_ylabel('Magnitude')
# axs[0].legend(loc='upper left')

# # Plot phase
# axs[1].plot(t_slice, phase, label='Phase', linewidth=2, color='red')
# axs[1].set_ylabel('Phase')
# axs[1].set_xlabel('Time (s)')  # Adjust the unit based on your data
# axs[1].legend(loc='upper left')

# plt.suptitle("symbolsTx (Magnitude and Phase)")

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

plt.suptitle("symbolsTx (Real and Imaginary Parts)")

plt.show()