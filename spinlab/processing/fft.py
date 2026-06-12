from warnings import warn
import re
import numpy as _np

__all__ = ["fourier_transform", "inverse_fourier_transform"]


def _convert_to_ppm(freq_coord, frequency):
    return _np.asarray(freq_coord) / (frequency / 1.0e6)


def _get_frequency(data):
    if "frequency" in data.spinlab_attrs:
        return data.spinlab_attrs["frequency"]
    return None


def _coord_spacing(data, dim):
    coord = data.coords[dim]
    if len(coord) < 2:
        raise ValueError(
            "Cannot Fourier transform dim %s. Coordinate must contain at least two points."
            % dim
        )
    return coord[1] - coord[0]


def _rename_ft_dim(dim, old_string, new_string):
    if re.fullmatch("%s[0-9]*" % old_string, dim) is not None:
        dim = dim.replace(old_string, new_string)

    return dim


def fourier_transform(
    data,
    dim="t2",
    zero_fill_factor=1,
    shift=True,
    convert_to_ppm=None,
):
    """Perform Fourier Transform along the dimension (dim) given in proc_parameters

    Args:
        data (SpinData): Data object
        dim (str): Dimension to Fourier Transform. The default is "t2"
        zero_fill_factor (int): Increases the number of points in Fourier transformed dimension by this factor with zero filling. The default is 1
        shift (bool): Apply fftshift to the Fourier transformed data, placing zero frequency at center of dimension
        convert_to_ppm (bool): If true, convert Fourier transformed axis to ppm units by using the "frequency" stored in spinlab_attrs. NMR data always converts to ppm.

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

    dt = _coord_spacing(out, dim)
    n_pts = zero_fill_factor * len(out.coords[dim])
    f = (1.0 / (n_pts * dt)) * _np.r_[0:n_pts]
    if shift == True:
        f -= 1.0 / (2 * dt)

    if out.spinlab_attrs.get("data_type", False) == "NMR":
        convert_to_ppm = True
    elif convert_to_ppm is None:
        convert_to_ppm = False

    proc_parameters["convert_to_ppm"] = (
        convert_to_ppm  # update proc_parameters with the final value of convert_to_ppm
    )

    if convert_to_ppm:
        # linked to topspin.py through special attr "_topspin_procs_offset"
        if out.attrs.get("_topspin_procs_offset", False) is not False:
            # assume that OFFSET gives first ppm value shown by spectrometer
            offset = out.attrs["_topspin_procs_offset"]
            sw = out.attrs["SW"]
            f = (
                _np.arange(0, f.size) * sw / (f.size - 1)
                + offset
                - sw * (f.size - 1) / f.size
            )
        else:
            frequency = _get_frequency(out)
            if frequency is None:
                warn(
                    "Frequency not found. Conversion from Hz to ppm requires the frequency."
                )
            else:
                f = _convert_to_ppm(f, frequency)

    out.values = _np.fft.fft(out.values, n=n_pts, axis=index)

    if shift:
        out.values = _np.fft.fftshift(out.values, axes=index)

    out.coords[dim] = f

    new_dim = _rename_ft_dim(dim, "t", "f")
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
        convert_from_ppm (bool): If true, convert Fourier transformed axis from ppm units to Hz by using the "frequency" stored in spinlab_attrs

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

    df = _coord_spacing(out, dim)
    if convert_from_ppm:
        frequency = _get_frequency(out)
        if frequency is None:
            warn(
                "Frequency not found. Conversion from ppm to Hz requires the frequency."
            )
        else:
            df /= 1 / (frequency / 1.0e6)  # updated

    n_pts = zero_fill_factor * len(out.coords[dim])
    t = (1.0 / (n_pts * df)) * _np.r_[0:n_pts]

    if shift:
        out.values = _np.fft.ifftshift(out.values, axes=index)

    out.values = _np.fft.ifft(out.values, n=n_pts, axis=index)
    out.coords[dim] = t

    new_dim = _rename_ft_dim(dim, "f", "t")
    out.rename(dim, new_dim)

    proc_attr_name = "inverse_fourier_transform"
    out.add_proc_attrs(proc_attr_name, proc_parameters)

    return out


def zero_fill():
    """Zero fill data, Not Implemented"""
    raise NotImplementedError("zero_fill is not implemented")
