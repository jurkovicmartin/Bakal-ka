
# Constellation

from optic.comm.modulation import modulateGray, demodulateGray, GrayMapping
from optic.comm.metrics import fastBERcalc, theoryBER
from optic.models.channels import awgn
from optic.dsp.core import pnorm, signal_power
from optic.plot import pconst
import matplotlib.pyplot as plt
import numpy as np

# %load_ext autoreload
# %autoreload 2

# ## Define modulation, modulate and demodulate data

# Run AWGN simulation 
SNRdB = 25 # SNR 
M      = 16  # order of the modulation format
constType = 'qam' # 'qam', 'psk', 'pam' or 'ook'

# generate random bits
bits = np.random.randint(2, size = int(np.log2(M)*1e6))

# Map bits to constellation symbols
symbTx = modulateGray(bits, M, constType)

# normalize symbols energy to 1
symbTx = pnorm(symbTx)

# AWGN    
EbN0dB = SNRdB - 10*np.log10(np.log2(M))
symbRx = awgn(symbTx, SNRdB)
    
# BER calculation (hard demodulation)
BER, _, SNRest = fastBERcalc(symbRx, symbTx, M, constType)
print('BER = %.2e'%BER)
print('SNR = %.2f dB'%SNRdB)
print('SNR(est) = %.2f dB'%SNRest)
print('BER(theory) = %.2e'%theoryBER(M, EbN0dB, constType))

# plt.figure(figsize=(4,4))
# plt.plot(symbRx.real, symbRx.imag,'.', label='Rx')
# plt.plot(symbTx.real, symbTx.imag,'.', label='Tx')
# plt.axis('square')
# plt.xlabel('In-Phase (I)')
# plt.ylabel('Quadrature (Q)')
# plt.legend(loc='upper right')
# plt.grid()


# # plot modulation bit-to-symbol mapping
# constSymb = GrayMapping(M, constType)             # Gray constellation mapping
# bitMap = demodulateGray(constSymb, M, constType)  # bit mapping
# bitMap = bitMap.reshape(-1, int(np.log2(M)))
# Es = signal_power(constSymb)                      # mean symbol energy

# for ind, symb in enumerate(constSymb/np.sqrt(Es)):
#     bitMap[ind,:]
#     plt.annotate(str(bitMap[ind,:])[1:-1:2], xy = (symb.real, symb.imag))

pconst(symbTx)
pconst(symbRx)

#pconst(symbRx, whiteb=False)