
# Try modulations

import numpy as np
from commpy.utilities  import upsample
from optic.models.devices import mzm, photodiode, edfa, iqm, hybrid_2x4_90deg
from optic.models.channels import linearFiberChannel
from optic.comm.modulation import GrayMapping, modulateGray
from optic.dsp.core import pulseShape, lowPassFIR, pnorm, signal_power

try:
    from optic.dsp.coreGPU import firFilter
except ImportError:
    from optic.dsp.core import firFilter

from optic.utils import parameters, dBm2W
from optic.plot import eyediagram
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
constType = 'qam'

# Laser power
Pi_dBm = 0         # laser optical power at the input of the MZM in dBm
Pi = dBm2W(Pi_dBm) # convert from dBm to W

# IQM parameters
paramIQM = parameters()
paramIQM.Vpi = 2
paramIQM.Vbl = -2
paramIQM.VbQ = -2
paramIQM.Vphi = 1

# generate pseudo-random bit sequence
bitsTx = np.random.randint(2, size=100000)

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

# optical modulation
Ai = np.sqrt(Pi)
sigTxo = iqm(Ai, sigTx, paramIQM)

print('Average power of the modulated optical signal [mW]: %.3f mW'%(signal_power(sigTxo)/1e-3))
print('Average power of the modulated optical signal [dBm]: %.3f dBm'%(10*np.log10(signal_power(sigTxo)/1e-3)))

fig, axs = plt.subplots(1, 2, figsize=(16,3))
interval = np.arange(16*20,16*50)
t = interval*Ts/1e-9

# plot psd
axs[0].set_xlim(-3*Rs,3*Rs)
axs[0].set_ylim(-180,-80)
axs[0].psd(sigTx,Fs=Fs, NFFT = 16*1024, sides='twosided', label = 'RF signal spectrum')
axs[0].legend(loc='upper left')

axs[1].plot(t, sigTx[interval], label = 'RF binary signal', linewidth=2)
axs[1].set_ylabel('Amplitude (a.u.)')
axs[1].set_xlabel('Time (ns)')
axs[1].set_xlim(min(t),max(t))
axs[1].legend(loc='upper left')
axs[1].grid()

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

# ### Direct-detection (DD) pin receiver model

# # ideal photodiode (noiseless, no bandwidth limitation)
# paramPD = parameters()
# paramPD.ideal = True
# paramPD.Fs = Fs

# I_Tx = photodiode(sigTxo.real, paramPD) # transmitted signal

# # noisy photodiode (thermal noise + shot noise + bandwidth limitation)
# paramPD = parameters()
# paramPD.ideal = False
# paramPD.B = Rs
# paramPD.Fs = Fs

# I_Rx = photodiode(sigCh, paramPD) # received signal after fiber channel and non-ideal PD

I_Rx = hybrid_2x4_90deg(sigCh, sigTx)

discard = 100
# eyediagram(I_Tx[discard:-discard], I_Tx.size-2*discard, SpS, plotlabel='signal at Tx', ptype='fancy')
eyediagram(I_Rx[discard:-discard], I_Rx.size-2*discard, SpS, plotlabel='signal at Rx', ptype='fancy')