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


SpS = 8  # Samples per symbol
modulationOrder = 4
modulationFormat = "pam"
Rs = 1000 # Symbol rate
data = 10**6 # bits 10**9 = Gb

# generate pseudo-random bit sequence
bitsTx = np.random.randint(2, size=int(np.log2(modulationOrder)*data))


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

print(len(bitsTx))
print(len(symbolsTx))

transTime = len(symbolsTx)/Rs

transSpeed = len(bitsTx)/transTime

print(f"time: {transTime} s")
print(f"speed: {transSpeed} bps")