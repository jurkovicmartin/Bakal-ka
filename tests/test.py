import numpy as np


from optic.comm.modulation import modulateGray, GrayMapping
from optic.dsp.core import pulseShape, pnorm
from commpy.utilities  import upsample
try:
    from optic.dsp.coreGPU import firFilter    
except ImportError:
    from optic.dsp.core import firFilter

# print(2*10**3)

# number = complex(2,3)
# modul = np.sqrt(number.real**2 + number.imag**2)

# print(number.real)
# print(number.imag)
# print(modul)


# Ai = 0.01
# u = 1
# Vπ = 0.01
# π = np.pi

# print(Ai * np.exp(1j * (u / Vπ) * π))


SpS = 2 # Samples per symbol
Rs = 1
Fs = SpS * Rs
Ts = 1/Fs
modulationOrder = 4 
modulationFormat = "qam"
bits = 8


# generate pseudo-random bit sequence
bitsTx = np.random.randint(2, size=bits)
print(f"bitsTx: {bitsTx}")

# generate modulated symbol sequence
grayMap = GrayMapping(modulationOrder, modulationFormat)
print(f"grayMap: {grayMap}")

symbolsTx = modulateGray(bitsTx, modulationOrder, modulationFormat)
print(f"symbolsTx: {symbolsTx}")
symbolsTx = pnorm(symbolsTx) # power normalization
print(f"norm symbolsTx: {symbolsTx}")

# upsampling
symbolsUp = upsample(symbolsTx, SpS)
print(f"symbolsUp: {symbolsUp}")

# typical NRZ pulse
pulse = pulseShape("nrz", SpS, Ts=Ts)
print(f"pulse: {pulse}")
pulse = pulse/max(abs(pulse))
print(f"2 pulse: {pulse}")

# pulse shaping
information = firFilter(pulse, symbolsUp)
print(f"infromation: {information}")