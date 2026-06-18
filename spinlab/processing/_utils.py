import numpy as _np


def get_default_dim(data, dim=None, operation_name="process"):
    """Return ``dim`` or the first dimension when ``dim`` is None.

    Examples:
        >>> data = sl.load("path/to/data")
        >>> dim = get_default_dim(data, None, "process")
    """
    if dim is None:
        if len(data.dims) == 0:
            raise ValueError(f"Cannot {operation_name} data without dimensions.")
        return data.dims[0]
    return validate_dim(data, dim)


def validate_dim(data, dim):
    """Raise ``ValueError`` if ``dim`` is not present in ``data``.

    Examples:
        >>> data = sl.load("path/to/data")
        >>> dim = validate_dim(data, "f2")
    """
    if dim not in data.dims:
        raise ValueError(f"dim {dim} not in data.dims ({data.dims})")
    return dim


def normalize_region_input(region):
    """Normalize a single region into a list of regions.

    ``None`` is returned unchanged. Two-value tuples/lists are wrapped in a
    list; longer iterables are assumed to already be a region list.

    Examples:
        >>> normalize_region_input((0, 10))
        [(0, 10)]
    """
    if region is None:
        return None
    try:
        length = len(region)
    except TypeError:
        return [region]
    if length == 2:
        first = region[0]
        if isinstance(first, (tuple, list, slice)):
            return region
        return [tuple(region)]
    return region


def ensure_1d_coord(coord, dim):
    """Return ``coord`` as a 1D NumPy array.

    Examples:
        >>> data = sl.load("path/to/data")
        >>> coord = ensure_1d_coord(data.coords["f2"], "f2")
    """
    coord = _np.asarray(coord)
    if coord.ndim != 1:
        raise ValueError(f"coord for dim {dim} must be one-dimensional")
    if coord.size == 0:
        raise ValueError(f"coord for dim {dim} must contain at least one value")
    return coord


def reshape_along_dim(values, data, dim):
    """Reshape 1D ``values`` for broadcasting along ``dim`` of ``data``.

    Examples:
        >>> data = sl.load("path/to/data")
        >>> weights = reshape_along_dim(data.coords["f2"], data, "f2")
    """
    dim = validate_dim(data, dim)
    values = _np.asarray(values)
    shape = [1 for _ in data.dims]
    shape[data.dims.index(dim)] = values.size
    return values.reshape(shape)
