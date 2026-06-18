import numpy as _np
from scipy.optimize import curve_fit
from ..core.data import SpinData


def _get_fit_dim(data, dim):
    if dim is None:
        if len(data.dims) == 0:
            raise ValueError("Cannot fit data without dimensions.")
        return data.dims[0]
    if dim not in data.dims:
        raise ValueError("dim {0} not in data.dims ({1})".format(dim, data.dims))
    return dim


def _as_parameter_array(p0):
    if p0 is None:
        raise ValueError("p0 must be provided")
    p0 = _np.asarray(p0, dtype=float)
    if p0.ndim == 0:
        p0 = p0.reshape(1)
    if p0.ndim != 1:
        raise ValueError("p0 must be a scalar or 1D array-like")
    return p0


def _validate_fit_coord(data, dim):
    coord = _np.asarray(data.coords[dim])
    if coord.ndim != 1:
        raise ValueError("coord for dim {0} must be one-dimensional".format(dim))
    if coord.size == 0:
        raise ValueError("coord for dim {0} must contain at least one value".format(dim))
    if coord.size != data.shape[data.index(dim)]:
        raise ValueError("coord for dim {0} must match data length".format(dim))
    return coord


def _validate_fit_points(fit_points):
    if fit_points is None:
        return None
    if isinstance(fit_points, bool):
        raise ValueError("fit_points must be a positive integer")
    try:
        fit_points_int = int(fit_points)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("fit_points must be a positive integer")
    if fit_points_int != fit_points or fit_points_int < 1:
        raise ValueError("fit_points must be a positive integer")
    return fit_points_int


def _prepare_sigma(sigma, data, dim):
    if sigma is None:
        return None

    sigma = _np.asarray(sigma)
    if sigma.ndim == 0:
        return sigma.item()

    if sigma.ndim == 1:
        if sigma.size != data.shape[data.index(dim)]:
            raise ValueError("1D sigma must match the fit dimension length")
        return sigma

    if sigma.shape != data.shape:
        raise ValueError("ND sigma must match data shape")

    sigma_data = SpinData(sigma, data.dims.copy(), list(data.coords.copy()))
    sigma_data.unfold(dim)
    return sigma_data


def _sigma_for_spectrum(prepared_sigma, ix):
    if isinstance(prepared_sigma, SpinData):
        return prepared_sigma.values[:, ix]
    return prepared_sigma


def fit(
    f,
    data,
    dim=None,
    p0=None,
    fit_points=None,
    sigma=None,
    absolute_sigma=False,
    check_finite=True,
    bounds=(-1 * _np.inf, _np.inf),
    method=None,
    jac=None,
    **kwargs,
):
    """Fitting function for SpinData

    Args:
        f (func): Function used in scipy.curve_fit
        data (SpinData): Data for fit
        dim (str or None): Dimension to perform fit along. If None, the first dimension is used.
        p0 (tuple): Initial guess for fit
        fit_points (int): Number of points to use in the fit. If None (default), the number of points is the same as the data.
        kwargs: Additional parameters for scipy.curve_fit

    Returns:
        out (dict): Dictionary of fit, fitting parameters, and error

    Examples:
        >>> data = sl.load("path/to/data")
        >>> out = sl.fit(sl.lineshape.gaussian, data, dim="f2", p0=(0, 1))
        >>> fit = out["fit"]
        >>> popt = out["popt"]
    """

    dim = _get_fit_dim(data, dim)
    p0 = _as_parameter_array(p0)
    fit_points = _validate_fit_points(fit_points)
    coord = _validate_fit_coord(data, dim)
    if _np.iscomplexobj(data.values):
        raise ValueError("fit currently supports real-valued SpinData only")
    prepared_sigma = _prepare_sigma(sigma, data, dim)
    fit = data.copy()

    index = fit.index(dim)
    dims = fit.dims.copy()
    coords = list(fit.coords.copy())
    shape = list(fit.shape)

    if fit_points is not None:
        new_coord = _np.linspace(coord[0], coord[-1], fit_points)
    else:
        new_coord = coord

    shape[index] = len(new_coord)
    coords[index] = new_coord
    fit_out = SpinData(_np.zeros(shape), dims, coords)

    fit_out.unfold(dim)
    fit.unfold(dim)

    xdata = fit.coords[dim]

    popt_list = []
    perr_list = []
    pcov_list = []
    for ix in range(fit.shape[1]):
        ydata = fit.values[:, ix]
        out = curve_fit(
            f,
            xdata,
            ydata,
            p0=p0,
            sigma=_sigma_for_spectrum(prepared_sigma, ix),
            absolute_sigma=absolute_sigma,
            check_finite=check_finite,
            bounds=bounds,
            method=method,
            jac=jac,
            **kwargs,
        )
        fit_values = f(new_coord, *out[0])
        fit_out.values[:, ix] = fit_values
        popt = out[0]
        pcov = out[1]
        perr = _np.sqrt(_np.diag(pcov))
        popt_list.append(popt)
        perr_list.append(perr)
        pcov_list.append(pcov)

    folded_order = list(fit.attrs["folded_order"])
    remaining_dims = [d for d in folded_order if d != dim]
    remaining_coords = [data.coords[d] for d in remaining_dims]
    remaining_shape = [len(c) for c in remaining_coords]
    p_shape = [len(p0)] + remaining_shape
    popt_array = _np.array(popt_list).T.reshape(p_shape)
    perr_array = _np.array(perr_list).T.reshape(p_shape)
    pcov_shape = [len(p0), len(p0)] + remaining_shape
    pcov_array = _np.moveaxis(_np.array(pcov_list), 0, -1).reshape(pcov_shape)

    fit.fold()
    fit_out.fold()

    pdims = ["popt"] + remaining_dims
    pcoords = [_np.array(range(0, len(p0)))] + remaining_coords
    pcov_dims = ["popt", "popt_cov"] + remaining_dims
    pcov_coords = [
        _np.array(range(0, len(p0))),
        _np.array(range(0, len(p0))),
    ] + remaining_coords

    popt_data = SpinData(popt_array, pdims, pcoords)
    perr_data = SpinData(perr_array, pdims, pcoords)
    pcov_data = SpinData(pcov_array, pcov_dims, pcov_coords)

    proc_parameters = {
        "function": getattr(f, "__name__", repr(f)),
        "dim": dim,
        "p0": p0,
        "fit_points": fit_points,
        "absolute_sigma": absolute_sigma,
        "check_finite": check_finite,
        "bounds": bounds,
        "method": method,
        "jac": None if jac is None else getattr(jac, "__name__", repr(jac)),
    }
    fit_out.add_proc_attrs("fit", proc_parameters)
    popt_data.add_proc_attrs("fit", proc_parameters)
    perr_data.add_proc_attrs("fit", proc_parameters)
    pcov_data.add_proc_attrs("fit", proc_parameters)

    out = {
        "fit": fit_out,
        "popt": popt_data,
        "err": perr_data,
        "pcov": pcov_data,
    }

    return out
