from scipy.signal import savgol_filter as _savgol_filter


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
