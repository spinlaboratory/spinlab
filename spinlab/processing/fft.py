from warnings import warn
import re
import numpy as _np

__all__ = ["fourier_transform", "inverse_fourier_transform"]


def convert_to_ppm(freq_coord):
    return NotImplemented


def rename_ft_dim(dim, old_string, new_string):
    if re.fullmatch("%s[0-9]*" % old_string, dim) is not None:
        dim = dim.replace(old_string, new_string)

    return dim


def fourier_transform(
    data,
    dim="t2",
    zero_fill_factor=1,
    shift=True,
    convert_to_ppm=True,
):
    """Perform Fourier Transform along the dimension (dim) given in proc_parameters

    Args:
        data (SpinData): Data object
        dim (str): Dimension to Fourier Transform. The default is "t2"
        zero_fill_factor (int): Increases the number of points in Fourier transformed dimension by this factor with zero filling. The default is 1
        shift (bool): Apply fftshift to the Fourier transformed data, placing zero frequency at center of dimension
        convert_to_ppm (bool): If true, convert Fourier transformed axis to ppm units by using the "frequency" stored in attrs

    Returns:
        data (SpinData): Data object after Fourier Transformation

    Examples:

        Fourier transformation of a (NMR) FID stored in a SpinData object

        >>> data = sl.fourier_transform(data)

        Fourier transform along t1 dimension and zero fill to twice the original length

        >>> data = sl.fourier_transform(data, dim = "t1", zero_fill_factor = 2)

    .. Note::

        The fourier_transform function assumes dt = t[1] - t[0]
    """

    out = data.copy()

    # handle zero_fill_factor
    zero_fill_factor = int(zero_fill_factor)
    if zero_fill_factor <= 0:
        zero_fill_factor = 1

    proc_parameters = {
        "dim": dim,
        "zero_fill_factor": zero_fill_factor,
        "shift": shift,
        "convert_to_ppm": convert_to_ppm,
    }

    index = out.dims.index(dim)

    dt = out.coords[dim][1] - out.coords[dim][0]
    n_pts = zero_fill_factor * len(out.coords[dim])
    f = (1.0 / (n_pts * dt)) * _np.r_[0:n_pts]
    if shift == True:
        f -= 1.0 / (2 * dt)

    if convert_to_ppm:
        if ("frequency" not in out.spinlab_attrs.keys()) and (
            "topspin" not in out.attrs.keys()
        ):
            print(
                "NMR frequency not found in the attrs dictionary. Conversion from ppm to Hz requires the NMR frequency."
            )

        # linked to topspin.py through special attr "_topspin_procs_offset"
        elif out.attrs.get("_topspin_procs_offset", False) is not False:
            # assume that OFFSET gives first ppm value shown by spectrometer
            offset = out.attrs["_topspin_procs_offset"]
            sw = out.attrs["SW"]
            f = (
                _np.arange(0, f.size) * sw / (f.size - 1)
                + offset
                - sw * (f.size - 1) / f.size
            )
        else:
            nmr_frequency = out.spinlab_attrs["frequency"]
            f /= nmr_frequency / 1.0e6  # updated

    out.values = _np.fft.fft(out.values, n=n_pts, axis=index)

    if shift:
        out.values = _np.fft.fftshift(out.values, axes=index)

    out.coords[dim] = f

    new_dim = rename_ft_dim(dim, "t", "f")
    out.rename(dim, new_dim)

    proc_attr_name = "fourier_transform"
    out.add_proc_attrs(proc_attr_name, proc_parameters)

    return out


def inverse_fourier_transform(
    data,
    dim="f2",
    zero_fill_factor=1,
    shift=True,
    convert_from_ppm=True,
):
    """Perform an inverse Fourier Transform along the dimension (dim) given in proc_parameters

    Args:
        data (SpinData): Data object
        dim (str): Dimension to inverse Fourier transform. The default is "f2"
        zero_fill_factor (int): Increases the number of points in inverse Fourier transformed dimension by this factor with zero filling. The default is 1
        shift (bool): Apply fftshift to the inverse Fourier transformed data, placing zero frequency at center of dimension
        convert_from_ppm (bool): If true, convert Fourier transformed axis from ppm units to Hz by using the "frequency" stored in attrs

    Returns:
        data (SpinData): Data object after inverse Fourier Transformation

    .. Note::
        Assumes df = f[1] - f[0]
    """

    out = data.copy()

    # handle zero_fill_factor
    zero_fill_factor = int(zero_fill_factor)
    if zero_fill_factor <= 0:
        zero_fill_factor = 1

    proc_parameters = {
        "dim": dim,
        "zero_fill_factor": zero_fill_factor,
        "shift": shift,
        "convert_from_ppm": convert_from_ppm,
    }

    index = out.dims.index(dim)

    df = out.coords[dim][1] - out.coords[dim][0]
    if convert_from_ppm:
        if "nmr_frequency" not in out.attrs.keys():
            warn(
                "NMR frequency not found in the attrs dictionary. Conversion from ppm to Hz requires the NMR frequency."
            )
        else:
            nmr_frequency = out.attrs["nmr_frequency"]
            df /= 1 / (nmr_frequency / 1.0e6)  # updated

    n_pts = zero_fill_factor * len(out.coords[dim])
    t = (1.0 / (n_pts * df)) * _np.r_[0:n_pts]

    if shift:
        out.values = _np.fft.fftshift(out.values, axes=index)

    out.values = _np.fft.ifft(out.values, n=n_pts, axis=index)
    out.coords[dim] = t

    new_dim = rename_ft_dim(dim, "f", "t")
    out.rename(dim, new_dim)

    proc_attr_name = "inverse_fourier_transform"
    out.add_proc_attrs(proc_attr_name, proc_parameters)

    return out


def zero_fill():
    """Zero fill data, Not Implemented"""
    return NotImplemented
