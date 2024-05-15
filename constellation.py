from optic.utils import parameters
from optic.models.devices import basicLaserModel
import numpy as np
import matplotlib.pyplot as plt
from optic.models.devices import mzm, pm, iqm, photodiode, coherentReceiver, hybrid_2x4_90deg
from optic.comm.metrics import fastBERcalc

from scripts.my_models import idealLaserModel

from optic.comm.modulation import modulateGray, GrayMapping, demodulateGray
from optic.dsp.core import pulseShape, pnorm, signal_power
from optic.plot import pconst
from commpy.utilities  import upsample
try:
    from optic.dsp.coreGPU import firFilter    
except ImportError:
    from optic.dsp.core import firFilter





def plot_constellation(symbolsIdeal, symbols, title, type):
    """
    Plot constellation diagram for transmitted (Tx) or received (Rx) symbols.

    Parameters:
        symbols (array-like): List of complex values representing symbols.
        noise_level (float, optional): Level of noise to add to Tx symbols to generate Rx symbols.
        title (str, optional): Title of the plot.

    Returns:
        None
    """

    if type == "tx":
        fig, ax = plt.subplots()

        ax.scatter(np.real(symbols), np.imag(symbols), c='blue', alpha=0.1, s=5)
        ax.set_title(title)
        ax.set_xlabel('In-phase')
        ax.set_ylabel('Quadrature')
        ax.grid(True)
        plt.show()

    elif type == "rx":
        fig, ax = plt.subplots()

        ax.scatter(np.real(symbols), np.imag(symbols), c='blue', alpha=0.1, s=5)
        # ax.scatter(np.real(symbolsIdeal), np.imag(symbolsIdeal), c='red', s=5, label='Ideal')
        ax.set_title(title)
        ax.set_xlabel('In-phase')
        ax.set_ylabel('Quadrature')
        ax.grid(True)
        ax.legend()
        plt.show()

    # """
    # Plot constellation diagram for transmitted (Tx) or received (Rx) symbols.

    # Parameters:
    #     symbols (array-like): List of complex values representing symbols.
    #     title (str, optional): Title of the plot.

    # Returns:
    #     None
    # """
    # fig, ax = plt.subplots()

    # x = np.real(symbols)
    # y = np.imag(symbols)

    # # Compute 2D histogram to get density
    # hb, xedges, yedges = np.histogram2d(x, y, bins=50, density=True)
    
    # # Find the bin index for each point
    # xidx = np.clip(np.digitize(x, xedges) - 1, 0, len(xedges)-2)
    # yidx = np.clip(np.digitize(y, yedges) - 1, 0, len(yedges)-2)
    
    # # Assign color based on density
    # colors = hb[xidx, yidx]
    
    # # Scatter plot with density-based colors
    # ax.scatter(x, y, c=colors, cmap='coolwarm', alpha=0.7, s=10)

    # ax.set_title(title)
    # ax.set_xlabel('In-phase')
    # ax.set_ylabel('Quadrature')
    # ax.legend()
    # ax.grid(True)
    
    # cb = fig.colorbar(plt.cm.ScalarMappable(cmap='coolwarm'), ax=ax)
    # cb.set_label('Density')

    # plt.show()
    # return






# INFORMATION SIGNAL
SpS = 8 # Samples per symbol
Fs = 8000
modulationOrder = 64  
modulationFormat = "qam"

# generate pseudo-random bit sequence
bitsTx = np.random.randint(2, size=int(np.log2(modulationOrder)*1e3))

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



# CARRIER
# Laser parameters
paramLaser = parameters()
paramLaser.P = 10  # laser power [dBm] [default: 10 dBm]
paramLaser.lw = 1000    # laser linewidth [Hz] [default: 1 kHz]
paramLaser.RIN_var = 1e-20  # variance of the RIN noise [default: 1e-20]
paramLaser.Fs = 8  # sampling rate [samples/s]
paramLaser.Ns = len(information)   # number of signal samples [default: 1e3]


carrier = basicLaserModel(paramLaser)


# MODULATION
modulator = "iqm"

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


# DETECTION
detector = "coherent"

if detector == "photodiode":
    paramPD = parameters()
    paramPD.ideal = False
    paramPD.Fs = Fs
    paramPD.B = 1000

    detected = photodiode(modulated, paramPD)

elif detector == "coherent":
    paramPD = parameters()
    paramPD.ideal = False
    paramPD.Fs = Fs
    paramPD.B = 400

    detected = coherentReceiver(modulated, carrier, paramPD)

else: pass

    


# PLOT
# t = np.linspace(0, 1, len(detected))
# # Define the start and end indices to plot
# start_index = 10
# end_index = 200  # Choose the end index according to your requirements

# # Slice both t and symbolsTx arrays
# t_slice = t[start_index:end_index]
# signal_slice = detected[start_index:end_index]

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

# plt.suptitle("Detected signal")
    

# RESTORE
# detected = detected/np.std(detected)

# capture samples in the middle of signaling intervals
# symbolsRx = detected[0::SpS]

# subtract DC level and normalize power
# symbolsRx = symbolsRx - symbolsRx.mean()
# symbolsRx = pnorm(symbolsRx)

# # demodulate symbols to bits with minimum Euclidean distance 
# const = GrayMapping(modulationOrder, modulationFormat) # get constellation
# Es = signal_power(const) # calculate the average energy per symbol of the constellation

# # demodulated bits
# bitsRx = demodulateGray(np.sqrt(Es)*symbolsRx, modulationOrder, modulationFormat)


# ber = fastBERcalc(bitsRx, bitsTx, modulationOrder, modulationFormat)[0]

# print(f"SymbolsTx: {symbolsTx}")
# print(f"SymbolsRx: {symbolsRx}")
# print(f"Tx bits:{bitsTx}")
# print(f"Rx bits:{bitsRx}")
# print(f"BER: {ber}")

# plot_constellation(symbolsTx, symbolsTx, "Constellation diagram", "tx")
# plot_constellation(symbolsTx, symbolsRx, "Constellation diagram", "rx")

# pconst(symbolsTx)
# pconst(symbolsRx)