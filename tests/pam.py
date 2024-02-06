
# # Simulate a basic IM-DD PAM transmission system

import numpy as np
from commpy.utilities  import upsample
from optic.models.devices import mzm, photodiode, edfa, basicLaserModel
from optic.models.channels import linearFiberChannel
from optic.comm.modulation import GrayMapping, modulateGray, demodulateGray
from optic.comm.metrics import  theoryBER, fastBERcalc
from optic.dsp.core import pulseShape, lowPassFIR, pnorm, signal_power

try:
    from optic.dsp.coreGPU import firFilter    
except ImportError:
    from optic.dsp.core import firFilter
    
from optic.utils import parameters, dBm2W
from optic.plot import eyediagram, pconst
import matplotlib.pyplot as plt
from scipy.special import erfc
from tqdm.notebook import tqdm
import scipy as sp


np.random.seed(seed=123) # fixing the seed to get reproducible results

# ### Intensity modulation (IM) with Pulse Amplitude Modulation (PAM)

# M = 2 = ook

# simulation parameters
SpS = 16            # samples per symbol
M = 4              # order of the modulation format
Rs = 10e9          # Symbol rate (for OOK case Rs = Rb)
Fs = SpS*Rs        # Sampling frequency in samples/second
Ts = 1/Fs          # Sampling period

# Laser power
Pi_dBm = 0         # laser optical power at the input of the MZM in dBm
Pi = dBm2W(Pi_dBm) # convert from dBm to W

# MZM parameters
paramMZM = parameters()
paramMZM.Vpi = 2
paramMZM.Vb = -paramMZM.Vpi/2

# generate pseudo-random bit sequence
bitsTx = np.random.randint(2, size=int(np.log2(M)*1e6))

# generate ook modulated symbol sequence
symbTx = modulateGray(bitsTx, M, 'pam')    
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
paramLaser.P = 1   # laser power [W] [default: 10 dBm]
paramLaser.lw = 1000    # laser linewidth [Hz] [default: 1 kHz]
paramLaser.RIN_var = 1e-20  # variance of the RIN noise [default: 1e-20]
paramLaser.Fs = Fs  # sampling rate [samples/s]
paramLaser.Ns = len(sigTx)   # number of signal samples [default: 1e3]

optical_signal = basicLaserModel(paramLaser)

# optical modulation
Ai = np.sqrt(Pi)
sigTxo = mzm(optical_signal, sigTx, paramMZM)

print('Average power of the modulated optical signal [mW]: %.3f mW'%(signal_power(sigTxo)/1e-3))
print('Average power of the modulated optical signal [dBm]: %.3f dBm'%(10*np.log10(signal_power(sigTxo)/1e-3)))

# fig, axs = plt.subplots(1, 2, figsize=(16,3))
interval = np.arange(16*20,16*50)
t = interval*Ts/1e-9

# # plot psd
# # RF plot
# axs[0].set_xlim(-3*Rs,3*Rs)
# axs[0].set_ylim(-180,-80)
# axs[0].psd(sigTx,Fs=Fs, NFFT = 16*1024, sides='twosided', label = 'RF signal spectrum')
# axs[0].legend(loc='upper left')

# axs[1].plot(t, sigTx[interval], label = 'RF binary signal', linewidth=2)
# axs[1].set_ylabel('Amplitude (a.u.)')
# axs[1].set_xlabel('Time (ns)')
# axs[1].set_xlim(min(t),max(t))
# axs[1].legend(loc='upper left')
# axs[1].grid()

fig, axs = plt.subplots(figsize=(16,3))
# plot psd
axs.set_xlim(-3*Rs,3*Rs)
axs.set_ylim(-255,-155)
axs.psd(np.abs(sigTxo)**2, Fs=Fs, NFFT = 16*1024, sides='twosided', label = 'Optical signal spectrum')
axs.legend(loc='upper left')

fig, axs = plt.subplots(figsize=(16,3))
# plot signal in t
axs.plot(t, np.abs(sigTxo[interval])**2, label = 'Optical modulated signal', linewidth=2)
axs.set_ylabel('Power (p.u.)')
axs.set_xlabel('Time (ns)')
axs.set_xlim(min(t),max(t))
axs.legend(loc='upper left')
# axs.grid()

# ### Linear fiber channel model (fiber + EDFA opt. amplifier)

# linear optical channel
paramCh = parameters()
paramCh.L = 40         # total link distance [km]
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

# ideal photodiode (noiseless, no bandwidth limitation)
paramPD = parameters()
paramPD.ideal = True
paramPD.Fs = Fs
I_Rx_ideal = photodiode(sigTxo.real, paramPD)

# noisy photodiode (thermal noise + shot noise + bandwidth limitation)
paramPD = parameters()
paramPD.ideal = False
paramPD.B = Rs
paramPD.Fs = Fs

I_Rx = photodiode(sigCh, paramPD)

discard = 100

eyediagram(sigTx[discard:-discard], sigTx.size-2*discard, SpS, plotlabel='signal at Tx', ptype='fancy')
eyediagram(I_Rx[discard:-discard], I_Rx.size-2*discard, SpS, plotlabel='signal at Rx', ptype='fancy')

# fig, axs = plt.subplots(figsize=(16,3))
# # plot psd
# axs[0].set_xlim(-3*Rs,3*Rs)
# axs[0].set_ylim(-355,-155)
# axs[0].psd(np.abs(I_Rx)**2, Fs=Fs, NFFT = 16*1024, sides='twosided', label = 'Optical signal spectrum')
# axs[0].legend(loc='upper left')

# axs.plot(t, np.abs(I_Rx[interval])**2, label = 'Optical modulated signal', linewidth=2)
# axs.set_ylabel('Power (p.u.)')
# axs.set_xlabel('Time (ns)')
# axs.set_xlim(min(t),max(t))
# axs.legend(loc='upper left')
# axs.grid()

fig, axs = plt.subplots(figsize=(16,3))
axs.plot(t, np.abs(sigCh[interval])**2, label = 'Optical modulated signal', linewidth=2)
axs.set_ylabel('Power (p.u.)')
axs.set_xlabel('Time (ns)')
axs.set_xlim(min(t),max(t))
axs.legend(loc='upper left')
axs.grid()

I_Rx = I_Rx/np.std(I_Rx)

# capture samples in the middle of signaling intervals
symbRx = I_Rx[0::SpS]

# subtract DC level and normalize power
symbRx = symbRx - symbRx.mean()
symbRx = pnorm(symbRx)

pconst(symbTx, whiteb=False)
pconst(symbRx, whiteb=False)

# # demodulate symbols to bits with minimum Euclidean distance 
const = GrayMapping(M,'pam') # get PAM constellation
Es = signal_power(const) # calculate the average energy per symbol of the PAM constellation

bitsRx = demodulateGray(np.sqrt(Es)*symbRx, M, 'pam')

discard = 100
err = np.logical_xor(bitsRx[discard:bitsRx.size-discard], bitsTx[discard:bitsTx.size-discard])
BER = np.mean(err)

print(bitsTx[200:221])
print(bitsRx[200:221])
print(BER)

secBER = fastBERcalc(bitsRx, bitsTx, M, 'pam')
print(secBER[0])

# #Pb = 0.5*erfc(Q/np.sqrt(2)) # theoretical error probability
# print('Number of counted errors = %d '%(err.sum()))
# print('BER = %.2e '%(BER))
# #print('Pb = %.2e '%(Pb))

# err = err*1.0
# err[err==0] = np.nan

# plt.plot(err,'o', label = 'bit errors')
# plt.vlines(np.where(err>0), 0, 1)
# plt.xlabel('bit position')
# plt.ylabel('counted error')
# plt.legend()
# plt.grid()
# plt.ylim(0, 1.5)
# plt.xlim(0,err.size)