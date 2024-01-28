from optic.comm.modulation import modulateGray
from optic.comm.metrics import fastBERcalc, theoryBER
from optic.models.channels import awgn
from optic.dsp.core import pnorm
from optic.plot import pconst
import matplotlib.pyplot as plt
import numpy as np


def simulateConstellation(modulationFormat, modulationOrder, transmissionConditions):
    # ## Define modulation, modulate and demodulate data
    # Run AWGN simulation 
    SNRdB = 25 # SNR 
    M = modulationOrder  # order of the modulation format
    constType = modulationFormat

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
    if transmissionConditions:
        return pconst(symbTx, whiteb=False)
    else:
        return pconst(symbRx, whiteb=False)