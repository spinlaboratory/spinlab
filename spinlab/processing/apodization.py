import numpy as _np

from ..math import window

_windows = {
    "exponential": window.exponential,
    "gaussian": window.gaussian,
    "hann": window.hann,
    "hamming": window.hamming,
    "lorentz_gauss": window.lorentz_gauss,
    "traf": window.traf,
    "sin2": window.sin2,
}


def apodize(data, dim="t2", kind="exponential", **kwargs):
    r"""Apply Apodization to data along a given dimension. Currently the following window functions are implemented: exponential, gaussian, hanning, hamming, and sin-squared. In addition the following window transformation functions are implemented: traf, and lorentz_gauss

    Args:
        data (SpinData): Data object
        dim (str): Dimension to apply apodization along, "t2" by default
        kind (str): Type of apodization, "exponential" by default
        kwargs: Arguments to be passed to apodization function, e.g. line width parameter

    Returns:
        SpinData: Data object with window function applied, including attr "window"

    Examples:
        Examples of using apodize

        Exponential line broadening using a line width of 2 Hz along the f2 dimension

        >>> data = sl.apodize(data, lw = 2)

        Lorentz-Gauss transformation:

        >>> data = sl.apodize(data, dim = 't2', kind = 'lorentz_gauss', lw = 4, gauss_lw = 8)

    Functions:

    .. math::

        \mathrm{exponential}    &=  \exp(-2t * \mathrm{linewidth}) &

        \mathrm{gaussian}       &=  \exp((\mathrm{linewidth[0]} * t) - (\mathrm{linewidth[1]} * t^{2})) &

        \mathrm{hamming}        &=  0.53836 + 0.46164\cos(\pi * n/(N-1)) &

        \mathrm{han}            &=  0.5 + 0.5\cos(\pi * n/(N-1)) &

        \mathrm{sin2}           &=  \cos((-0.5\pi * n/(N - 1)) + \pi)^{2} &

        \mathrm{lorentz\_gauss} &=  \exp(L -  G^{2}) &

               L(t)    &=  \pi * \mathrm{linewidth[0]} * t &

               G(t)    &=  0.6\pi * \mathrm{linewidth[1]} * (\mathrm{gaussian\_max} * (N - 1) - t) &

        \mathrm{traf}           &=  (f1 * (f1 + f2)) / (f1^{2} + f2^{2}) &

               f1(t)   &=  \exp(-t * \pi * \mathrm{linewidth[0]}) &

               f2(t)   &=  \exp((t - T) * \pi * \mathrm{linewidth[1]}) &
    """

    out = data.copy()

    index = out.index(dim)
    coord = out.coords[dim]

    kind = str(kind).lower()  # kind of apodization is a lower case string

    if kind not in _windows:
        raise ValueError(
            'Window function "%s" not valid. Available window functions are: %s.  See documentation for more details.'
            % (kind, list(_windows.keys()))
        )
    window = _windows[kind]
    apwin = window(coord, **kwargs)

    out_shape = out.shape

    new_shape = [1 if ix != index else out_shape[index] for ix in range(out.ndim)]
    apwin = _np.reshape(apwin, new_shape)

    out *= apwin

    proc_parameters = {
        "kind": kind,
    }
    for key in kwargs:
        proc_parameters[key] = kwargs[key]
    proc_attr_name = "window"
    out.add_proc_attrs(proc_attr_name, proc_parameters)

    return out
