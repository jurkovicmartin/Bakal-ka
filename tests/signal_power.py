from optic.utils import parameters
from optic.models.devices import basicLaserModel
import numpy as np
import matplotlib.pyplot as plt
from optic.models.devices import mzm

from optic.comm.modulation import modulateGray, GrayMapping
from optic.dsp.core import pulseShape, pnorm, signal_power
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

# Laser parameters
paramLaser = parameters()
paramLaser.P = 20  # laser power [dBm] [default: 10 dBm]
paramLaser.lw = 1000    # laser linewidth [Hz] [default: 1 kHz]
paramLaser.RIN_var = 0  # variance of the RIN noise [default: 1e-20]
paramLaser.Fs = 8  # sampling rate [samples/s]
paramLaser.Ns = len(information)   # number of signal samples [default: 1e3]


carrier = basicLaserModel(paramLaser)

print(f"Carrier: {signal_power(carrier)/1e-3} W")
print(f"Carrier: {10*np.log10(signal_power(carrier)/1e-3)} dBm")


paramMZM = parameters()
paramMZM.Vpi = 2 # frequency of cosinus
# paramMZM.Vb = -paramMZM.Vpi/2
paramMZM.Vb = 1 # phase shift of cosinus


modulated = mzm(carrier, information, paramMZM)

print(f"Modulated: {signal_power(modulated)/1e-3} W")
print(f"Modulated: {10*np.log10(signal_power(modulated)/1e-3)} dBm")