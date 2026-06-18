import numpy as _np


def normalize(data, amplitude=True, dim=None, regions=None):
    """Normalize spectrum

    The function is used to normalize the amplitude (or area) of a spectrum to a value of 1. The sign of the original data will be conserved.

    Args:
        data (SpinData):         Data object
        amplitude (boolean):    True: normalize amplitude, false: normalize area. The default is True
        dim (str or None):      The dimension to normalize, if None the data is normalized to the maximum of the whole dataset. If regions are provided and dim is None, the first dimension is used for the region selection.
        regions (None, list):   Tuple to specify range of normalize reference e.g. (-99., 99.), if None the whole range is used for normalization

    Returns:
        data (SpinDdata):        Normalized data object

    Examples:
        >>> data = sl.load("path/to/data")
        >>> normalized = sl.normalize(data)
        >>> normalized = sl.normalize(data, dim="f2", regions=(-5, 5))
    """

    region_dim = data.dims[0] if (regions is not None and dim is None) else dim

    if (region_dim not in data.dims) and (region_dim is not None):
        raise ValueError(
            "Cannot normalize to dim {}, available dimensions are {}".format(
                region_dim, data.dims
            )
        )

    out = data.copy()

    if amplitude is True:
        if regions and (dim is not None):
            try:
                factor = _np.atleast_2d(
                    _np.max(_np.abs(out[dim, regions]), axis=dim)._values
                ).reshape(1, -1)
            except AttributeError:
                # now 1D
                factor = _np.max(_np.abs(out[dim, regions]), axis=dim)

            out.unfold(dim)
            out._values = out.values / factor
            out.fold()

        elif regions and (dim is None):
            factor = _np.max(_np.abs(out[region_dim, regions].values))
            out._values = out.values / factor

        elif (regions is None) and (dim is None):
            factor = _np.max(_np.abs(out.values))
            out._values = out.values / factor

        elif (regions is None) and (dim is not None):
            try:
                factor = _np.atleast_2d(
                    _np.max(_np.abs(out), axis=dim)._values
                ).reshape(1, -1)
            except AttributeError:
                factor = _np.max(_np.abs(out), axis=dim)

            out.unfold(dim)
            out._values = out.values / factor
            out.fold()

    elif amplitude is False:
        out.values = out.values  # Normalize to area = 1, not implemented yet

    proc_attr_name = "normalized"
    proc_parameters = {
        "amplitude": amplitude,
    }

    out.add_proc_attrs(proc_attr_name, proc_parameters)

    return out
