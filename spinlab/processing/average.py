import numpy as _np


def _get_average_dim(data, dim):
    if dim is None:
        if len(data.dims) == 0:
            raise ValueError("Cannot average data without dimensions.")
        return data.dims[0]
    if dim not in data.dims:
        raise ValueError("dim {0} not in data.dims ({1})".format(dim, data.dims))
    return dim


def average(data, dim=None, axis=None):
    """Average a dimension using numpy.mean

    Args:
        data (object) : SpinData object
        dim (str or None): Dimension to average. If None, the first dimension is used.
        axis (str or None): Deprecated alias for ``dim``.

    Returns:
        SpinData: Averaged data

    Examples:

        >>> data = sl.load("path/to/data")
        >>> data_averaged = sl.average(data)
        >>> data_averaged = sl.average(data, dim="Average")
    """
    if axis is not None:
        if dim is not None:
            raise ValueError("Use either dim or axis, not both.")
        dim = axis
    dim = _get_average_dim(data, dim)

    out = data.copy()
    proc_attr_name = "average"
    proc_parameters = {"dim": dim}
    proc_attrs_list = out.proc_attrs.copy()

    out = _np.mean(out, axis=dim)  # it will automatically assign proc_attrs
    out.proc_attrs = proc_attrs_list
    out.add_proc_attrs(proc_attr_name, proc_parameters)

    return out
