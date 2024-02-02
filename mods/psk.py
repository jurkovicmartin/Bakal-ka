import numpy as np
from commpy.utilities  import upsample
from optic.models.devices import mzm, photodiode, edfa, iqm, hybrid_2x4_90deg, basicLaserModel, coherentReceiver
from optic.models.channels import linearFiberChannel
from optic.comm.modulation import GrayMapping, modulateGray
from optic.dsp.core import pulseShape, lowPassFIR, pnorm, signal_power

try:
    from optic.dsp.coreGPU import firFilter
except ImportError:
    from optic.dsp.core import firFilter

from optic.utils import parameters, dBm2W
from optic.plot import eyediagram, pconst
import matplotlib.pyplot as plt
from scipy.special import erfc
from tqdm import tqdm
import scipy as sp

np.random.seed(seed=123) # fixing the seed to get reproducible results

# ### Intensity modulation (IM) with On-Off Keying (OOK)

# simulation parameters
SpS = 16     # samples per symbol
M = 4        # order of the modulation format
Rs = 5e9    # Symbol rate (for OOK case Rs = Rb)
Fs = Rs*SpS  # Sampling frequency
Ts = 1/Fs    # Sampling period
constType = 'psk'

# Laser power
Pi_dBm = 0         # laser optical power at the input of the MZM in dBm
Pi = dBm2W(Pi_dBm) # convert from dBm to W

# generate pseudo-random bit sequence
bitsTx = np.random.randint(2, size=int(np.log2(M)*1e6))

# generate 2-PAM modulated symbol sequence
symbTx = modulateGray(bitsTx, M, constType)
symbTx = pnorm(symbTx) # power normalization

# upsampling
symbolsUp = upsample(symbTx, SpS)

# typical NRZ pulse
pulse = pulseShape('nrz', SpS)
pulse = pulse/max(abs(pulse))

# pulse shaping
sigTx = firFilter(pulse, symbolsUp)

# Laser parameters
paramLaser = parameters()
paramLaser.P = 10   # laser power [W] [default: 10 dBm]
paramLaser.lw = 1000    # laser linewidth [Hz] [default: 1 kHz]
paramLaser.RIN_var = 1e-20  # variance of the RIN noise [default: 1e-20]
paramLaser.Fs = Fs  # sampling rate [samples/s]
paramLaser.Ns = len(sigTx)   # number of signal samples [default: 1e3]

optical_signal = basicLaserModel(paramLaser)

# IQM parameters
paramIQM = parameters()
paramIQM.Vpi = 2
paramIQM.Vbl = -2
paramIQM.VbQ = -2
paramIQM.Vphi = 1

# optical modulation
Ai = np.sqrt(Pi)
sigTxo = iqm(optical_signal, sigTx, paramIQM)

print('Average power of the modulated optical signal [mW]: %.3f mW'%(signal_power(sigTxo)/1e-3))
print('Average power of the modulated optical signal [dBm]: %.3f dBm'%(10*np.log10(signal_power(sigTxo)/1e-3)))

interval = np.arange(16*20,16*50)
t = interval*Ts/1e-9

fig, axs = plt.subplots(1, 2, figsize=(16,3))
# plot psd
axs[0].set_xlim(-3*Rs,3*Rs)
axs[0].set_ylim(-230,-130)
axs[0].psd(np.abs(sigTxo)**2, Fs=Fs, NFFT = 16*1024, sides='twosided', label = 'Optical signal spectrum')
axs[0].legend(loc='upper left')

axs[1].plot(t, np.abs(sigTxo[interval])**2, label = 'Optical modulated signal', linewidth=2)
axs[1].set_ylabel('Power (p.u.)')
axs[1].set_xlabel('Time (ns)')
axs[1].set_xlim(min(t),max(t))
axs[1].legend(loc='upper left')
axs[1].grid()

# ### Linear fiber channel model (fiber + EDFA opt. amplifier)

# linear optical channel
paramCh = parameters()
paramCh.L = 90         # total link distance [km]
paramCh.α = 0.2        # fiber loss parameter [dB/km]
paramCh.D = 16         # fiber dispersion parameter [ps/nm/km]
paramCh.Fc = 193.1e12  # central optical frequency [Hz]
paramCh.Fs = Fs        # simulation sampling frequency [samples/second]

sigCh = linearFiberChannel(sigTxo, paramCh)

# receiver pre-amplifier
paramEDFA = parameters()
paramEDFA.G = paramCh.α*paramCh.L    # edfa gain
paramEDFA.NF = 4.5   # edfa noise figure 
paramEDFA.Fc = paramCh.Fc
paramEDFA.Fs = Fs

sigCh = edfa(sigCh, paramEDFA)

# I_Rx = hybrid_2x4_90deg(sigCh, optical_signal)
# print(I_Rx)
# print(type(I_Rx))

# noisy photodiode (thermal noise + shot noise + bandwidth limitation)
paramPD = parameters()
paramPD.ideal = False
paramPD.B = Rs
paramPD.Fs = Fs

I_Rx = coherentReceiver(sigCh, optical_signal, paramPD)

fig, axs = plt.subplots(figsize=(16,3))
axs.plot(t, np.abs(I_Rx[interval])**2, label = 'Optical modulated signal', linewidth=2)
axs.set_ylabel('Power (p.u.)')
axs.set_xlabel('Time (ns)')
axs.set_xlim(min(t),max(t))
axs.legend(loc='upper left')
axs.grid()

plt.show()

I_Rx = I_Rx/np.std(I_Rx)

# capture samples in the middle of signaling intervals
symbRx = I_Rx[0::SpS]

# subtract DC level and normalize power
symbRx = symbRx - symbRx.mean()
symbRx = pnorm(symbRx)

pconst(symbTx)
pconst(symbRx)

print("ok")

# print(I_Rx)