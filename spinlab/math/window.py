import numpy as _np
from ..constants import constants as _const


def _handle_array(x):
    """Handle array or integer input argument for window functions.

    Args:
        x (array_like, int): array or integer

    Returns:
        int: length of array or integer input
    """
    if isinstance(x, int):
        N = x
    else:
        N = len(x)

    return N


def exponential(x, lw, shift=0.0):
    r"""Calculate exponential window function.

    The window maximum is at ``shift`` (default 0) and decays symmetrically
    on both sides. For data starting at 0 this reproduces the classic
    one-sided exponential decay.

    Args:
        x (array_like): Vector of points (e.g. time axis).
        lw (int or float): Linewidth in Hz.
        shift (float): Position of the window maximum (default: 0).

    Returns:
        ndarray: Exponential window function.

    .. math::
        \mathrm{exponential} = e^{-\pi \, |x - \mathrm{shift}| \, lw}
    """
    return _np.exp(-_const.pi * _np.abs(x - shift) * lw)


def gaussian(x, lw, shift=0.0):
    r"""Calculate gaussian window function.

    Args:
        x (array_like): Vector of points (e.g. time axis).
        lw (float): Full width at half maximum (FWHM) of the Gaussian.
        shift (float): Position of the window maximum (default: 0).

    Returns:
        ndarray: Gaussian window function.

    .. math::
        \mathrm{gaussian} = e^{-2\pi^{2} \sigma^{2} (x - \mathrm{shift})^{2}}
    """
    sigma = lw / (2.0 * _np.sqrt(2.0 * _np.log(2.0)))
    return _np.exp(-2.0 * _const.pi**2 * sigma**2 * (x - shift) ** 2)


def hann(x, shift=0.0):
    r"""Calculate Hann window function.

    Args:
        x (array_like): Vector of points (e.g. time axis).
        shift (float): Position of the window maximum (default: 0).

    Returns:
        ndarray: Hann window function.

    .. math::
        \mathrm{hann} = 0.5 + 0.5\cos\left(\pi \frac{x - \mathrm{shift}}{x_{\max}}\right)
    """
    x = _np.asarray(x)
    x_max = _np.max(_np.abs(x - shift))
    if x_max == 0:
        return _np.ones_like(x)
    return 0.5 + 0.5 * _np.cos(_const.pi * (x - shift) / x_max)


def traf(x, lw, shift=0.0):
    r"""Calculate TRAF (Trafficante) window function.

    Args:
        x (array_like): Vector of points (e.g. time axis).
        lw (float): Linewidth in Hz.
        shift (float): Position of the window maximum (default: 0).

    Returns:
        ndarray: TRAF window function.

    .. math::
        \mathrm{traf}  &=  \frac{f_1 (f_1 + f_2)}{f_1^{2} + f_2^{2}} \\
        f_1(t) &=  \exp(-|t - \mathrm{shift}| \, \pi \, lw) \\
        f_2(t) &=  \exp(-(T_{\max} - |t - \mathrm{shift}|) \, \pi \, lw)
    """
    t_abs = _np.abs(x - shift)
    T = _np.max(t_abs)
    T2 = 1.0 / (_const.pi * lw)
    E = _np.exp(-t_abs / T2)
    e = _np.exp(-(T - t_abs) / T2)
    return E * (E + e) / (E**2 + e**2)


def hamming(x, shift=0.0):
    r"""Calculate Hamming window function.

    Args:
        x (array_like): Vector of points (e.g. time axis).
        shift (float): Position of the window maximum (default: 0).

    Returns:
        ndarray: Hamming window function.

    .. math::
        \mathrm{hamming} = 0.53836 + 0.46164\cos\left(\pi \frac{x - \mathrm{shift}}{x_{\max}}\right)
    """
    x = _np.asarray(x)
    x_max = _np.max(_np.abs(x - shift))
    if x_max == 0:
        return _np.ones_like(x)
    return 0.53836 + 0.46164 * _np.cos(_const.pi * (x - shift) / x_max)


def lorentz_gauss(x, lw, gauss_lw, shift=0.0):
    r"""Calculate Lorentz-to-Gauss transformation window function.

    Args:
        x (array_like): Vector of points (e.g. time axis).
        lw (float): Lorentzian linewidth in Hz (line narrowing component).
        gauss_lw (float): Gaussian linewidth in Hz (target line shape).
        shift (float): Position of the window maximum (default: 0).

    Returns:
        ndarray: Lorentz-Gauss window function.

    .. math::
        \mathrm{lorentz\_gauss} = \exp\left(\pi \, lw \, |t| - \frac{(\pi \, gauss\_lw \, t)^{2}}{4 \ln 2}\right)

    where :math:`t = x - \mathrm{shift}`.
    """
    t = x - shift
    sigma = gauss_lw / (2.0 * _np.sqrt(2.0 * _np.log(2.0)))
    expo = _const.pi * _np.abs(t) * lw
    gaus = 2.0 * _const.pi**2 * sigma**2 * t**2
    return _np.exp(expo - gaus)


def sin2(x, shift=0.0):
    r"""Calculate sin-squared window function.

    Args:
        x (array_like): Vector of points (e.g. time axis).
        shift (float): Position of the window maximum (default: 0).

    Returns:
        ndarray: Sin-squared window function.

    .. math::
        \sin^{2} = \cos\left(\frac{\pi}{2} \frac{x - \mathrm{shift}}{x_{\max}}\right)^{2}
    """
    x = _np.asarray(x)
    x_max = _np.max(_np.abs(x - shift))
    if x_max == 0:
        return _np.ones_like(x)
    return _np.cos(0.5 * _const.pi * (x - shift) / x_max) ** 2
