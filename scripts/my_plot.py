
"""
Script inspired by OpticommPY functions with a little changes.
Also added some more functions.
"""

import matplotlib.pyplot as plt
from matplotlib import cm
import mpl_scatter_density
import numpy as np
import copy
from scipy.interpolate import interp1d
from scipy.ndimage.filters import gaussian_filter

from optic.dsp.core import pnorm, signal_power
from optic.models.amplification import get_spectrum
from optic.plot import constHist
import warnings

warnings.filterwarnings("ignore", r"All-NaN (slice|axis) encountered")

def constellation(x, lim=True, R=1.25, pType="fancy", cmap="turbo", whiteb=True, title="") -> tuple[plt.Figure, plt.Axes]:
    """
    Plot signal constellations.
    
    Parameters
    ----------
    x : complex signals or list of complex signals
        Input signals.
    
    lim : bool, optional
        Flag indicating whether to limit the axes to the radius of the signal. 
        Defaults to True.
    
    R : float, optional
        Scaling factor for the radius of the signal. 
        Defaults to 1.25.
    
    pType : str, optional
        Type of plot. "fancy" for scatter_density plot, "fast" for fast plot.
        Defaults to "fancy".
    
    cmap : str, optional
        Color map for scatter_density plot.
        Defaults to "turbo".
    
    whiteb : bool, optional
        Flag indicating whether to use white background for scatter_density plot.
        Defaults to True.
    
    Returns
    -------
    fig : Figure
        Figure object.
    
    ax : Axes or array of Axes
        Axes object(s).
    
    """
    if type(x) == list:
        for ind, _ in enumerate(x):
            x[ind] = pnorm(x[ind])
        try:
            x[0].shape[1]
        except IndexError:
            x[0] = x[0].reshape(len(x[0]), 1)

        nSubPts = x[0].shape[1]
        radius = R * np.sqrt(signal_power(x[0]))
    else:
        x = pnorm(x)
        try:
            x.shape[1]
        except IndexError:
            x = x.reshape(len(x), 1)

        nSubPts = x.shape[1]
        radius = R * np.sqrt(signal_power(x))

    if nSubPts > 1:
        if nSubPts < 5:
            nCols = nSubPts
            nRows = 1
        elif nSubPts >= 6:
            nCols = int(np.ceil(nSubPts / 2))
            nRows = 2

        # Create a Position index
        Position = range(1, nSubPts + 1)

        fig = plt.figure(figsize=(6,6))

        if type(x) == list:
            for k in range(nSubPts):           

                for ind in range(len(x)):
                    if pType == "fancy":
                        if ind == 0:
                            ax = fig.add_subplot(nRows, nCols, Position[k], projection="scatter_density")
                        ax = constHist(x[ind][:, k], ax, radius, cmap, whiteb)
                    elif pType == "fast":
                        if ind == 0:
                            ax = fig.add_subplot(nRows, nCols, Position[k])
                        ax.plot(x[ind][:, k].real, x[ind][:, k].imag, ".")

                ax.axis("square")
                ax.set_xlabel("In-Phase (I)")
                ax.set_ylabel("Quadrature (Q)")
                # ax.grid()
                ax.set_title(f"mode {str(Position[k] - 1)}")

                if lim:
                    ax.set_xlim(-radius, radius)
                    ax.set_ylim(-radius, radius)

        else:
            for k in range(nSubPts):                
                if pType == "fancy":
                    ax = fig.add_subplot(nRows, nCols, Position[k], projection="scatter_density")
                    ax = constHist(x[:, k], ax, radius, cmap, whiteb)
                elif pType == "fast":
                    ax = fig.add_subplot(nRows, nCols, Position[k])
                    ax.plot(x[:, k].real, x[:, k].imag, ".")

                ax.axis("square")
                ax.set_xlabel("In-Phase (I)")
                ax.set_ylabel("Quadrature (Q)")
                # ax.grid()
                ax.set_title(f"mode {str(Position[k] - 1)}")

                if lim:
                    ax.set_xlim(-radius, radius)
                    ax.set_ylim(-radius, radius)


        fig.tight_layout()

    elif nSubPts == 1:
        fig = plt.figure(figsize=(6,6))
        #ax = plt.gca()
        if pType == "fancy":
            ax = fig.add_subplot(1, 1, 1, projection="scatter_density")
            ax = constHist(x[:, 0], ax, radius, cmap, whiteb)
        elif pType == "fast":
            ax = plt.gca()
            ax.plot(x.real, x.imag, ".")
        plt.axis("square")
        ax.set_xlabel("In-Phase (I)")
        ax.set_ylabel("Quadrature (Q)")
        # plt.grid()

        if lim:
            plt.xlim(-radius - 1, radius + 1)
            plt.ylim(-radius - 1, radius + 1)

    plt.suptitle(title)
    plt.close()

    return fig, ax


def eyediagram(sigIn, Nsamples, SpS, n=3, ptype="fast", plotlabel=None, title="") -> tuple[plt.Figure, plt.Axes]:
    """
    Plot the eye diagram of a modulated signal waveform.

    Parameters
    ----------
    sigIn : array-like
        Input signal waveform.
    Nsamples : int
        Number of samples to be plotted.
    SpS : int
        Samples per symbol.
    n : int, optional
        Number of symbol periods. Defaults to 3.
    ptype : str, optional
        Type of eye diagram. Can be "fast" or "fancy". Defaults to "fast".
    plotlabel : str, optional
        Label for the plot legend. Defaults to None.

    Returns
    -------
    figure : matplotlib.figure.Figure
        The created figure.
    axes : matplotlib.axes._axes.Axes
        The axes of the plot.
    """

    sig = sigIn.copy()

    if not plotlabel:
        plotlabel = " "

    if np.iscomplex(sig).any():
        d = 1
        plotlabel_ = f"{plotlabel} [real]" if plotlabel else "[real]"
    else:
        d = 0
        plotlabel_ = plotlabel

    fig, axes = plt.subplots(figsize=(8,4))

    for ind in range(d + 1):
        if ind == 0:
            y = sig[:Nsamples].real
            x = np.arange(0, y.size, 1) % (n * SpS)
        else:
            y = sig[:Nsamples].imag

            plotlabel_ = f"{plotlabel} [imag]" if plotlabel else "[imag]"

        if ptype == "fancy":
            f = interp1d(np.arange(y.size), y, kind="cubic")

            Nup = 40 * SpS
            tnew = np.arange(y.size) * (1 / Nup)
            y_ = f(tnew)

            taxis = (np.arange(y.size) % (n * SpS * Nup)) * (1 / Nup)
            imRange = np.array(
                [
                    [min(taxis), max(taxis)],
                    [min(y) - 0.1 * np.mean(np.abs(y)), 1.1 * max(y)],
                ]
            )

            H, xedges, yedges = np.histogram2d(
                taxis, y_, bins=350, range=imRange
            )

            H = H.T
            H = gaussian_filter(H, sigma=1.0)

            im = axes.imshow(
                H,
                cmap="turbo",
                origin="lower",
                aspect="auto",
                extent=[0, n, yedges[0], yedges[-1]],
            )

        elif ptype == "fast":
            y[x == n * SpS] = np.nan
            y[x == 0] = np.nan

            im = axes.plot(x / SpS, y, color="blue", alpha=0.8, label=plotlabel_)
            axes.set_xlim(min(x / SpS), max(x / SpS))

            if plotlabel is not None:
                axes.legend(loc="upper left")

    axes.set_xlabel("symbol period (Ts)")
    axes.set_ylabel("amplitude")
    axes.set_title(f"eye diagram {plotlabel_}")
    axes.grid(alpha=0.15)

    plt.suptitle(title)
    plt.close()

    return fig, axes


def signalInTime(Ts: int, signal, title: str, type: str) -> tuple[plt.Figure, plt.Axes]:
    """
    Plot optical / electrical signal in time. Electrical is showed as real and imaginary part, optical as magnitude and phase.

    Parameters
    -----
    type: "optical" / "electrical" signal
    """
    if type == "electrical":
        # interval for plot
        interval = np.arange(100,500)
        t = interval*Ts

        fig, axs = plt.subplots(2, 1, figsize=(8, 4))

        # Real
        axs[0].plot(t, signal[interval].real, label="Real Part", linewidth=2, color="blue")
        axs[0].set_ylabel("Amplitude (a.u.)")
        axs[0].legend(loc="upper left")

        # Imaginary
        axs[1].plot(t, signal[interval].imag, label="Imaginary Part", linewidth=2, color="red")
        axs[1].set_ylabel("Amplitude (a.u.)")
        axs[1].set_xlabel("Time (s)")
        axs[1].legend(loc="upper left")

        plt.suptitle(title)
        plt.close()

        return fig, axs
    
    elif type == "optical":
        # interval for plot
        interval = np.arange(100,250)
        t = interval*Ts

        # Calculate magnitude and phase
        magnitude = np.abs(signal[interval])
        phase = np.angle(signal[interval], deg=True)

        # Plotting magnitude and phase in two subplots
        fig, axs = plt.subplots(2, 1, figsize=(8, 4))

        # Plot magnitude
        axs[0].plot(t, magnitude, label="Magnitude", linewidth=2, color="blue")
        axs[0].set_ylabel("Magnitude (dBm)")
        axs[0].legend(loc="upper left")

        # Plot phase
        axs[1].plot(t, phase, label="Phase", linewidth=2, color="red")
        axs[1].set_ylabel("Phase (°)")
        axs[1].set_xlabel("Time (s)")
        axs[1].legend(loc="upper left")

        plt.suptitle(title)
        plt.close()

        return fig, axs
    
    else: raise Exception("Unexpected error")


def opticalSpectrum(signal, Fs: int, Fc: float, title: str) -> tuple[plt.Figure, plt.Axes]:
    """
    Plot optical spectrum with wavelength.

    Parameters:
    -----
    Fs: sampling frequency

    Fc: central frequency
    """
    wavelength, spectrum = get_spectrum(signal, Fs, Fc, xunits="m")
    # Convert to nm
    wavelength = wavelength * 10**9
    yMin = spectrum.min()
    yMax = spectrum.max() + 10
    fig, ax = plt.subplots(1)
    ax.plot( wavelength, spectrum)
    ax.set_ylim([yMin, yMax])   
    ax.set_xlabel("Wavelength [nm]")
    ax.set_ylabel("Magnitude [dBm]")
    # ax.minorticks_on()
    ax.grid(True)

    # Set scattered ticks on the x-axis
    num_ticks = 5  # Set the number of ticks you want to display
    tick_indices = np.linspace(0, len(wavelength) - 1, num_ticks, dtype=int)
    ax.set_xticks(wavelength[tick_indices])
    ax.set_xticklabels([f"{freq_nm:.6f}" for freq_nm in wavelength[tick_indices]])

    plt.suptitle(title)
    plt.close()

    return fig, ax










def powerSpectralDensity(Rs: int, Fs: int, signal, title: str) -> tuple[plt.Figure, plt.Axes]:
    """
    Plot power spectral density of optical signal.
    """
    fig, axs = plt.subplots(figsize=(8,4))
    axs.set_xlim(-3*Rs,3*Rs)
    # axs.set_ylim(-230,-130)
    axs.psd(np.abs(signal)**2, Fs=Fs, NFFT = 16*1024, sides="twosided", label = "Optical signal spectrum")
    axs.legend(loc="upper left")
    axs.set_title(title)
    plt.close()

    return fig, axs