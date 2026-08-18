import numpy as _np
from scipy.special import erf as _erf
from scipy.special import jv as _jv

from ..core.data import SpinData


def combine_harmonics(data, dim="X", new_dim="harmonic", coord=None):
    """Combine sequential real/imaginary trace pairs into complex harmonic spectra

    Bruker multi-harmonic (dual detection) BES3T files store each harmonic as two
    consecutive traces along a dimension (e.g. "X"): the first trace holds the
    real part of the harmonic's complex spectrum and the second holds the
    corresponding imaginary part. This function pairs up sequential traces along
    ``dim``, combines each pair into one complex value, and collapses ``dim`` to
    half its original length.

    Only the real part of the input values is used for each trace (any existing
    imaginary component, e.g. residual crosstalk picked up by the ADC, is
    discarded).

    Args:
        data (SpinData): SpinData input object, e.g. as returned by sl.load() for a
            multi-harmonic BES3T dataset
        dim (String): Dimension containing the sequential real/imag trace pairs, must have even length. default="X"
        new_dim (String): Name for the resulting dimension, default="harmonic"
        coord (array, None): Coordinate values for new_dim, default is 1, 2, 3, ...

    Returns:
        data (SpinData): New SpinData object with dim collapsed to half its length and combined into complex values

    Examples:
        In this example a multi-harmonic Bruker BES3T dataset with 5 harmonics
        (10 sequential traces along the "X" dimension) is imported and combined
        into 5 complex harmonic spectra.

        .. code-block:: python

            data = sl.load("path/to/multi_harmonic_data.DTA")
            harmonics = sl.combine_harmonics(data)

    """
    if dim not in data.dims:
        raise KeyError(
            "dim {} not in dims of SpinData object, available dims are: {}".format(
                dim, data.dims
            )
        )

    axis = data.dims.index(dim)
    n_points = data.shape[axis]
    if n_points % 2 != 0:
        raise ValueError(
            "dim {} has length {}, must be even to pair into real/imag".format(
                dim, n_points
            )
        )

    values = _np.real(data.values)
    real_part = _np.take(values, _np.arange(0, n_points, 2), axis=axis)
    imag_part = _np.take(values, _np.arange(1, n_points, 2), axis=axis)
    new_values = real_part + 1j * imag_part

    if coord is None:
        coord = _np.arange(1, n_points // 2 + 1)
    else:
        coord = _np.asarray(coord)
        if len(coord) != n_points // 2:
            raise ValueError(
                "coord must have length {} to match the {} combined harmonics".format(
                    n_points // 2, n_points // 2
                )
            )

    dims = data.dims.copy()
    dims[axis] = new_dim

    coords = list(data.coords)
    coords[axis] = coord

    out = SpinData(new_values, dims, coords, dict(data.attrs))

    proc_parameters = {"dim": dim, "new_dim": new_dim}
    out.add_proc_attrs("combine_harmonics", proc_parameters)

    return out


def label_harmonics(data, dim="X", new_dim="harmonic", coord=None):
    """Relabel a dimension of sequential single-phase harmonic traces as harmonic order

    Some multi-harmonic BES3T files record only in-phase (0 deg) harmonics, with
    no imaginary/quadrature (90 deg) channel -- each trace is a plain real
    amplitude, one per harmonic order, e.g. ``IKKF REAL,REAL,REAL,REAL,REAL`` for
    5 harmonics. There is nothing to pair into complex values here, unlike
    :func:`combine_harmonics` (which is for dual-phase 0/90 deg data): this
    function simply relabels ``dim`` as the harmonic-order dimension expected by
    :func:`reconstruct_harmonics`, without changing or pairing the values.

    Args:
        data (SpinData): SpinData input object, e.g. as returned by sl.load() for a
            single-phase multi-harmonic BES3T dataset
        dim (String): Dimension containing the sequential harmonic traces, default="X"
        new_dim (String): Name for the resulting dimension, default="harmonic"
        coord (array, None): Coordinate values for new_dim, default is 1, 2, 3, ...

    Returns:
        data (SpinData): New SpinData object with dim renamed to new_dim

    Examples:
        In this example a single-phase multi-harmonic Bruker BES3T dataset with 5
        harmonics (5 sequential traces along the "X" dimension, no 90 deg
        channel) is imported and relabeled for use with reconstruct_harmonics.

        .. code-block:: python

            data = sl.load("path/to/single_phase_multi_harmonic_data.DTA")
            harmonics = sl.label_harmonics(data)

    """
    if dim not in data.dims:
        raise KeyError(
            "dim {} not in dims of SpinData object, available dims are: {}".format(
                dim, data.dims
            )
        )

    axis = data.dims.index(dim)
    n_points = data.shape[axis]

    if coord is None:
        coord = _np.arange(1, n_points + 1)
    else:
        coord = _np.asarray(coord)
        if len(coord) != n_points:
            raise ValueError(
                "coord must have length {} to match the {} harmonics".format(
                    n_points, n_points
                )
            )

    dims = data.dims.copy()
    dims[axis] = new_dim

    coords = list(data.coords)
    coords[axis] = coord

    out = SpinData(data.values, dims, coords, dict(data.attrs))

    proc_parameters = {"dim": dim, "new_dim": new_dim}
    out.add_proc_attrs("label_harmonics", proc_parameters)

    return out


def _harmonic_filter(u, n, modulation_amplitude):
    """Bessel-function filter D_n(u) relating harmonic n to the 1st-derivative spectrum

    D_n(u) = (h_m / 4n) * j^(n-1) * [J_(n-1)(h_m*u/2) + J_(n+1)(h_m*u/2)]

    Eq. (4) in Tseitlin, Eaton, Eaton, J. Magn. Reson. 209 (2011) 277-281,
    derived from Eq. (1)-(2) therein: S_n(u) = j^n J_n(h_m*u/2) G(u), and
    G(u) = F(u)/(ju) = j^(n-1)/u * J_n(h_m*u/2) * F(u).
    """
    z = modulation_amplitude * u / 2.0
    return (
        (modulation_amplitude / (4.0 * n))
        * (1j ** (n - 1))
        * (_jv(n - 1, z) + _jv(n + 1, z))
    )


def _lowpass_filter(u, cutoff, filter_width):
    """Smooth (Gaussian-edged) low-pass filter in the u domain

    Equivalent to the convolution of a rectangular passband [-cutoff, cutoff]
    with a Gaussian of the given width, as described in Yu, Tseytlin, Eaton,
    Eaton, J. Magn. Reson. 254 (2015) 86-92.
    """
    return 0.5 * (
        _erf((u + cutoff) / (_np.sqrt(2) * filter_width))
        - _erf((u - cutoff) / (_np.sqrt(2) * filter_width))
    )


def reconstruct_harmonics(
    data,
    modulation_amplitude,
    dim="B0",
    harmonic_dim="harmonic",
    cutoff=None,
    filter_width=None,
):
    """Reconstruct the minimally-broadened 1st-derivative EPR line from multiple harmonics

    Implements the multi-harmonic reconstruction method of Tseitlin, Eaton, and
    Eaton (J. Magn. Reson. 209 (2011) 277-281) and Yu, Tseytlin, Eaton, and Eaton
    (J. Magn. Reson. 254 (2015) 86-92). Combining multiple harmonics of an
    over-modulated field-swept CW EPR signal allows the 1st-derivative lineshape
    to be recovered with the S/N benefit of over-modulation, but without the
    associated line broadening.

    Each harmonic spectrum s_n(B) is related to the Fourier transform F(u) of the
    true 1st-derivative line f(B) by an analytical filter D_n(u) that depends only
    on the modulation amplitude and the harmonic order n:

        S_n(u) = D_n(u) * F(u)

    D_n(u) has an oscillatory behavior with zeros at different positions for each
    n, so information about F(u) lost in one harmonic's zeros is preserved by
    other harmonics. F(u) is recovered as the combination of all harmonics that
    minimizes noise amplification, assuming similar noise levels for all
    harmonics:

        F(u) = sum_n( conj(D_n(u)) * S_n(u) ) / sum_n( |D_n(u)|^2 ) * LPF(u)

    f(B) is obtained by inverse Fourier transform of F(u). This method assumes the
    adiabatic approximation (magnetization instantaneously follows the modulation
    field), so it is not applicable in the rapid-scan regime.

    Args:
        data (SpinData): SpinData object with a dimension indexing harmonic order
            (see harmonic_dim) and an evenly spaced field-swept dimension (see
            dim). Values along harmonic_dim are expected to be complex, with the
            real part holding one phase-sensitive-detection channel (e.g. 0 deg)
            and the imaginary part the orthogonal channel (e.g. 90 deg) for each
            harmonic -- the format produced by combine_harmonics(). The two channels
            are reconstructed independently and recombined into the real and
            imaginary parts of the output.
        modulation_amplitude (float): Peak-to-peak field modulation amplitude,
            h_m, in the same units as the coordinate of dim
        dim (String): Field-swept dimension, default="B0"
        harmonic_dim (String): Dimension indexing harmonic order n = 1, 2, 3, ...,
            default="harmonic"
        cutoff (float, None): Cutoff frequency of the low-pass filter applied in
            the Fourier-conjugate domain, in units of 1/[dim units]. Default None
            applies no low-pass filtering.
        filter_width (float, None): Width of the Gaussian used to smooth the edge
            of the low-pass filter, in units of 1/[dim units]. Required if cutoff
            is given, ignored otherwise.

    Returns:
        data (SpinData): New SpinData object with harmonic_dim collapsed,
            containing the reconstructed 1st-derivative EPR line f(B)

    Examples:
        .. code-block:: python

            data = sl.load("path/to/multi_harmonic_data.DTA")
            harmonics = sl.combine_harmonics(data)
            f = sl.reconstruct_harmonics(harmonics, modulation_amplitude=1.0)

            # with a low-pass filter to suppress high-frequency noise
            f = sl.reconstruct_harmonics(
                harmonics, modulation_amplitude=1.0, cutoff=2.0, filter_width=0.2
            )

    """
    if dim not in data.dims:
        raise KeyError(
            "dim {} not in dims of SpinData object, available dims are: {}".format(
                dim, data.dims
            )
        )
    if harmonic_dim not in data.dims:
        raise KeyError(
            "harmonic_dim {} not in dims of SpinData object, available dims are: {}".format(
                harmonic_dim, data.dims
            )
        )
    if cutoff is not None and filter_width is None:
        raise ValueError("filter_width must be given when cutoff is specified")

    field_axis = data.dims.index(dim)
    harmonic_axis = data.dims.index(harmonic_dim)

    field_coord = data.coords[dim]
    n_field = len(field_coord)
    d_field = field_coord[1] - field_coord[0]
    if not _np.allclose(_np.diff(field_coord), d_field):
        raise ValueError("dim {} coordinates must be evenly spaced".format(dim))

    harmonic_orders = _np.asarray(data.coords[harmonic_dim])
    if _np.any(harmonic_orders <= 0):
        raise ValueError("harmonic_dim coordinates must be positive integers")

    u = 2 * _np.pi * _np.fft.fftfreq(n_field, d=d_field)

    values = _np.moveaxis(data.values, harmonic_axis, 0)
    field_axis_in_slice = field_axis - (1 if harmonic_axis < field_axis else 0)

    slice_shape = values.shape[1:]
    broadcast_shape = [1] * len(slice_shape)
    broadcast_shape[field_axis_in_slice] = n_field

    numerator_real = _np.zeros(slice_shape, dtype=complex)
    numerator_imag = _np.zeros(slice_shape, dtype=complex)
    denominator = _np.zeros(n_field, dtype=float)

    for i, n in enumerate(harmonic_orders):
        n = int(round(n))
        harmonic_slice = values[i]

        Dn = _harmonic_filter(u, n, modulation_amplitude)
        Dn_bcast = Dn.reshape(broadcast_shape)

        Sn_real = _np.fft.fft(_np.real(harmonic_slice), axis=field_axis_in_slice)
        Sn_imag = _np.fft.fft(_np.imag(harmonic_slice), axis=field_axis_in_slice)

        numerator_real += _np.conj(Dn_bcast) * Sn_real
        numerator_imag += _np.conj(Dn_bcast) * Sn_imag
        denominator += _np.abs(Dn) ** 2

    denominator_bcast = denominator.reshape(broadcast_shape)
    denominator_safe = _np.where(denominator_bcast == 0, _np.inf, denominator_bcast)

    F_real = numerator_real / denominator_safe
    F_imag = numerator_imag / denominator_safe

    if cutoff is not None:
        lpf = _lowpass_filter(u, cutoff, filter_width).reshape(broadcast_shape)
        F_real = F_real * lpf
        F_imag = F_imag * lpf

    f_real = _np.real(_np.fft.ifft(F_real, axis=field_axis_in_slice))
    f_imag = _np.real(_np.fft.ifft(F_imag, axis=field_axis_in_slice))

    new_values = f_real + 1j * f_imag

    dims = [d for d in data.dims if d != harmonic_dim]
    coords = [data.coords[d] for d in dims]

    out = SpinData(new_values, dims, coords, dict(data.attrs))

    proc_parameters = {
        "dim": dim,
        "harmonic_dim": harmonic_dim,
        "modulation_amplitude": modulation_amplitude,
        "cutoff": cutoff,
        "filter_width": filter_width,
        "n_harmonics": len(harmonic_orders),
    }
    out.add_proc_attrs("reconstruct_harmonics", proc_parameters)

    return out
