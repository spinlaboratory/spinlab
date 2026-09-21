import numpy as np
from scipy.signal import filtfilt, firwin
from scipy.signal import savgol_filter as _savgol_filter


def low_pass(data, cutoff_hz, num_taps=101):
    """Apply a low-pass finite impulse response filter.

    The sampling rate is inferred from the coordinate of the first dimension.

    Args:
        data (SpinData): Data object.
        cutoff_hz (float): Filter cutoff frequency in Hz.
        num_taps (int): Number of FIR filter coefficients.

    Returns:
        SpinData: A filtered copy of the input data.

    Raises:
        ValueError: If the cutoff is outside the interval between zero and the
            Nyquist frequency.
    """
    axis = np.asarray(data.get_coord(data.dims[0]))
    sample_interval = float(np.median(np.diff(axis)))
    sample_rate_hz = 1.0 / sample_interval

    if not 0 < cutoff_hz < sample_rate_hz / 2.0:
        raise ValueError("Cutoff must be between 0 Hz and the Nyquist frequency.")

    coefficients = firwin(
        numtaps=num_taps,
        cutoff=cutoff_hz,
        fs=sample_rate_hz,
        window="hamming",
        pass_zero="lowpass",
    )
    result = data.copy()
    result.values = filtfilt(coefficients, [1.0], np.asarray(data.values))
    return result


def smooth(data, dim="t2", window_length=11, polyorder=3):
    """Apply Savitzky-Golay Smoothing

    This function is a wrapper function for the savgol_filter from the SciPy python package (https://scipy.org/). For a more detailed description see the SciPy help for this function.

    Args:
        data (SpinData): Data object
        dim (str): Dimension to perform smoothing
        window_length (int): Length of window (number of coefficients)
        polyorder (int): Polynomial order to fit samples

    Returns:
        data (SpinData): Data with Savitzky-Golay smoothing applied

    Examples:
        >>> data = sl.load("path/to/data")
        >>> smoothed = sl.smooth(data, dim="t2", window_length=11, polyorder=3)
    """
    out = data.copy()

    proc_parameters = {
        "dim": dim,
        "window_length": window_length,
        "polyorder": polyorder,
    }

    out.unfold(dim)

    out.values = _savgol_filter(out.values, window_length, polyorder, axis=0)

    out.fold()

    proc_attr_name = "smooth"
    out.add_proc_attrs(proc_attr_name, proc_parameters)

    return out
