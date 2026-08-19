"""
The shaped pulses simulation

Author: Timothy Keller

Edit: Yen-Chun Huang
"""

import numpy as np

default_number = 43  # default number for saving pulse shape
resolution = 1.0e-9  # default pulse shape resolution


def _sech(x):
    return 1.0 / np.cosh(x)


def _validate_positive(value, name):
    value = float(value)
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def _validate_nonnegative(value, name):
    value = float(value)
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")
    return value


def _time_axis(tp, resolution):
    tp = _validate_positive(tp, "tp")
    resolution = _validate_positive(resolution, "resolution")
    return np.r_[0.0:tp:resolution]


def save_shape(pulse_shape, filename, num=101):
    """Save a pulse shape in Xepr text shape format.

    Args:
        pulse_shape (array_like): One-dimensional real or complex pulse shape.
        filename (str or path-like): Output filename.
        num (int): Xepr shape number written in the header and footer.

    Returns:
        None

    Examples:
        >>> import numpy as np
        >>> import spinlab as sl
        >>> pulse = np.array([0.0, 0.5, 1.0])
        >>> sl.pulses.save_shape(pulse, "shape.txt", num=7)
    """

    pulse_shape = np.asarray(pulse_shape)
    if pulse_shape.ndim != 1:
        raise ValueError("pulse_shape must be a 1D array")

    with open(filename, "w") as f:
        f.write('begin shape%i "Shape %i"\n' % (int(num), int(num)))

        if np.iscomplexobj(pulse_shape):
            for value in pulse_shape:
                f.write("%0.4f,%0.04f\n" % (np.real(value), np.imag(value)))
        else:
            for value in pulse_shape:
                f.write("%0.4f\n" % value)

        f.write("end shape%i" % (int(num)))


def load_shape(filename):
    """Load a pulse shape from Xepr text shape format.

    Args:
        filename (str or path-like): Path to a pulse shape file.

    Returns:
        ndarray: Complex-valued pulse shape. Real-only files are returned with
        zero imaginary components.

    Examples:
        >>> import spinlab as sl
        >>> pulse = sl.pulses.load_shape("shape.txt")
    """

    with open(filename, "r") as f:
        # Read Preamble
        raw_string = f.read()

    lines = raw_string.strip().split("\n")

    pulse_real = []
    pulse_imag = []

    for line in lines:
        if ("begin" in line) or ("end" in line):
            continue
        if "," in line:
            split_line = line.rsplit(",")
            pulse_real.append(float(split_line[0]))
            pulse_imag.append(float(split_line[1]))
        else:
            pulse_real.append(float(line))
            pulse_imag.append(0.0)

    pulse = np.array(pulse_real) + 1j * np.array(pulse_imag)

    return pulse


def adiabatic(tp, BW, beta, resolution=resolution):
    r"""Generate a complex hyperbolic-secant adiabatic pulse.

    Args:
        tp (float): Pulse length.
        BW (float): Pulse bandwidth.
        beta (float): Dimensionless truncation factor.
        resolution (float): Time resolution of the generated shape.

    Returns:
        tuple: Tuple containing:

            t (ndarray): Time axis.
            pulse (ndarray): Complex pulse shape.

    .. math::

        \mathrm{pulse}(t) =
        \operatorname{sech}\left(\frac{\beta}{t_p}
        \left(t-\frac{t_p}{2}\right)\right)^{1+i\mu}

    with

    .. math::

        \mu = \frac{\pi BW}{\beta/t_p}

    Examples:
        >>> import spinlab as sl
        >>> t, pulse = sl.pulses.adiabatic(tp=1e-6, BW=10e6, beta=5, resolution=1e-9)
    """

    tp = _validate_positive(tp, "tp")
    resolution = _validate_positive(resolution, "resolution")
    beta = _validate_positive(beta, "beta") / tp
    mu = np.pi * BW / beta

    t = _time_axis(tp, resolution)

    pulse = (_sech(beta * (t - 0.5 * tp))) ** (1.0 + 1.0j * mu)

    return t, pulse


def chirp(tp, BW, resolution=resolution):
    r"""Generate a complex quadratic chirp pulse.

    Args:
        tp (float): Pulse length.
        BW (float): Pulse bandwidth.
        resolution (float): Time resolution of the generated shape.

    Returns:
        tuple: Tuple containing:

            t (ndarray): Time axis.
            pulse (ndarray): Complex pulse shape.

    .. math::

        \mathrm{pulse}(t) =
        e^{i 2\pi \frac{k}{2}\left(t-\frac{t_p}{2}\right)^2}

    with

    .. math::

        k = \frac{BW}{t_p}

    Examples:
        >>> import spinlab as sl
        >>> t, pulse = sl.pulses.chirp(tp=1e-6, BW=10e6, resolution=1e-9)
    """
    tp = _validate_positive(tp, "tp")
    resolution = _validate_positive(resolution, "resolution")
    k = BW / tp
    t = _time_axis(tp, resolution)
    pulse = np.exp(1.0j * 2.0 * np.pi * ((k / 2.0) * ((t - tp / 2.0) ** 2.0)))
    return t, pulse


def wurst(tp, N, resolution=resolution):
    r"""Generate a WURST envelope pulse.

    Args:
        tp (float): Pulse length.
        N (float): WURST exponent controlling edge steepness.
        resolution (float): Time resolution of the generated shape.

    Returns:
        tuple: Tuple containing:

            t (ndarray): Time axis.
            pulse (ndarray): Complex-valued WURST envelope.

    .. math::

        \mathrm{pulse}(t) =
        1 - \left|\cos\left(\frac{\pi}{t_p}
        \left(t-\frac{t_p}{2}\right)+\frac{\pi}{2}\right)\right|^N

    Examples:
        >>> import spinlab as sl
        >>> t, pulse = sl.pulses.wurst(tp=1e-6, N=20, resolution=1e-9)
    """
    tp = _validate_positive(tp, "tp")
    resolution = _validate_positive(resolution, "resolution")
    N = _validate_positive(N, "N")
    t = _time_axis(tp, resolution)
    pulse = (1.0 - np.abs(np.cos(np.pi * (t - tp / 2.0) / tp + np.pi / 2.0)) ** N) + 0j

    return t, pulse


def gaussian(tp, sigmas, resolution=resolution):
    r"""Generate a Gaussian envelope pulse.

    Args:
        tp (float): Pulse length.
        sigmas (float): Number of standard deviations from the center to each
            pulse edge.
        resolution (float): Time resolution of the generated shape.

    Returns:
        tuple: Tuple containing:

            t (ndarray): Time axis.
            pulse (ndarray): Complex-valued Gaussian envelope.

    .. math::

        \mathrm{pulse}(t) =
        e^{-\frac{1}{2}\left(\frac{t-t_p/2}{\sigma}\right)^2}

    with

    .. math::

        \sigma = \frac{t_p}{2\,\mathrm{sigmas}}

    Examples:
        >>> import spinlab as sl
        >>> t, pulse = sl.pulses.gaussian(tp=1e-6, sigmas=3, resolution=1e-9)
    """
    tp = _validate_positive(tp, "tp")
    resolution = _validate_positive(resolution, "resolution")
    sigmas = _validate_positive(sigmas, "sigmas")
    sigma = 0.5 * tp / sigmas
    t = _time_axis(tp, resolution)
    pulse = np.exp(-1.0 * (t - tp / 2.0) ** 2.0 / (2.0 * (sigma**2.0))) + 0j
    return t, pulse


def square(tp, t_length=0.0, resolution=resolution):
    """Generate a square pulse.

    If ``t_length`` is greater than ``tp``, the pulse is centered in a longer
    zero-padded time axis. The active pulse interval is half-open:
    ``start <= t < stop``.

    Args:
        tp (float): Pulse length.
        t_length (float): Total length of the time axis. If this is less than
            or equal to ``tp``, the time axis length is ``tp``.
        resolution (float): Time resolution of the generated shape.

    Returns:
        tuple: Tuple containing:

            t (ndarray): Time axis.
            pulse (ndarray): Complex-valued square pulse.

    Examples:
        >>> import spinlab as sl
        >>> t, pulse = sl.pulses.square(tp=1e-6, resolution=1e-9)
        >>> t, pulse = sl.pulses.square(tp=1e-6, t_length=2e-6, resolution=1e-9)
    """
    tp = _validate_positive(tp, "tp")
    resolution = _validate_positive(resolution, "resolution")
    t_length = _validate_nonnegative(t_length, "t_length")
    if t_length > tp:
        t = _time_axis(t_length, resolution)
        pulse = np.zeros_like(t, dtype=complex)
        start = (t_length - tp) / 2.0
        stop = start + tp
        pulse[(t >= start) & (t < stop)] = 1.0
    else:
        t = _time_axis(tp, resolution)
        pulse = np.ones_like(t, dtype=complex)
    return t, pulse


def plane_wave(tp, f, resolution=resolution):
    r"""Generate a complex plane-wave pulse.

    Args:
        tp (float): Pulse length.
        f (float): Plane-wave frequency.
        resolution (float): Time resolution of the generated shape.

    Returns:
        tuple: Tuple containing:

            t (ndarray): Time axis.
            pulse (ndarray): Complex pulse shape.

    .. math::

        \mathrm{pulse}(t) =
        e^{i2\pi f\left(t-\frac{t_p}{2}\right)}

    Examples:
        >>> import spinlab as sl
        >>> t, pulse = sl.pulses.plane_wave(tp=1e-6, f=1e6, resolution=1e-9)
    """
    tp = _validate_positive(tp, "tp")
    resolution = _validate_positive(resolution, "resolution")
    t = _time_axis(tp, resolution)
    pulse = np.exp(1.0j * 2.0 * np.pi * f * (t - tp / 2.0))
    return t, pulse


def sinc(tp, n, resolution=resolution):
    r"""Generate a sinc pulse.

    Args:
        tp (float): Pulse length.
        n (float): Number of sinc lobes. Odd values produce a full symmetric
            sinc shape.
        resolution (float): Time resolution of the generated shape.

    Returns:
        tuple: Tuple containing:

            t (ndarray): Time axis.
            pulse (ndarray): Sinc pulse shape.

    .. math::

        \mathrm{pulse}(t) =
        \frac{\sin\left(\frac{\pi}{2}(n+1)x\right)}{x}

    with

    .. math::

        x = \frac{t-t_p/2}{t_p/2}

    The center point uses the analytic limit
    ``((n + 1) / 2) * pi`` instead of evaluating ``0 / 0``.

    Examples:
        >>> import spinlab as sl
        >>> t, pulse = sl.pulses.sinc(tp=1e-6, n=3, resolution=1e-9)
    """
    tp = _validate_positive(tp, "tp")
    resolution = _validate_positive(resolution, "resolution")
    n = _validate_positive(n, "n")
    t = _time_axis(tp, resolution)
    x = (t - tp / 2.0) / (0.5 * tp)
    scale = ((n + 1.0) / 2.0) * np.pi
    pulse = np.empty_like(x, dtype=float)
    center = np.isclose(x, 0.0)
    pulse[center] = scale
    pulse[~center] = np.sin(scale * x[~center]) / x[~center]

    return t, pulse


if __name__ == "__main__":
    pass
