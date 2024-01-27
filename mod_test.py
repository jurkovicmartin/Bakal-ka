
from optic.comm.modulation import modulateGray
from optic.comm.metrics import fastBERcalc, theoryBER
from optic.models.channels import awgn
from optic.dsp.core import pnorm
from optic.plot import pconst
import matplotlib.pyplot as plt
import numpy as np


# ## Define modulation, modulate and demodulate data
# Run AWGN simulation 
SNRdB = 25 # SNR 
M       = 8  # order of the modulation format
constType = 'psk'

# generate random bits
bits = np.random.randint(2, size = int(np.log2(M)*1e6))

# Map bits to constellation symbols
symbTx = modulateGray(bits, M, constType)

# normalize symbols energy to 1
symbTx = pnorm(symbTx)

# AWGN    
# EbN0dB = SNRdB - 10*np.log10(np.log2(M))
symbRx = awgn(symbTx, SNRdB)
    
# BER calculation (hard demodulation)
# BER, _, SNRest = fastBERcalc(symbRx, symbTx, M, constType)
# print('BER = %.2e'%BER)
# print('SNR = %.2f dB'%SNRdB)
# print('SNR(est) = %.2f dB'%SNRest)
# print('BER(theory) = %.2e'%theoryBER(M, EbN0dB, constType))

a = pconst(symbTx, whiteb=False)
print(type(a))
print(type(a[0]))
pconst(symbRx, whiteb=False)