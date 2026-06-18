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


def require_min_coord_size(coord, dim, min_size, operation_name="process"):
    """Return ``coord`` as a 1D array and require at least ``min_size`` points."""
    coord = ensure_1d_coord(coord, dim)
    if coord.size < min_size:
        raise ValueError(
            f"Cannot {operation_name} dim {dim}. Coordinate must contain at least {min_size} points."
        )
    return coord


def monotonic_direction(coord, dim):
    """Return ``1`` for increasing coordinates and ``-1`` for decreasing."""
    coord = require_min_coord_size(coord, dim, 2, "check coordinate direction for")
    coord_diff = _np.diff(coord)
    if _np.all(coord_diff > 0):
        return 1
    if _np.all(coord_diff < 0):
        return -1
    raise ValueError(f"Coordinate for dim {dim} must be monotonic.")


def validate_matching_coord_direction(coord, new_coord, dim, new_name="new_coord"):
    """Require ``new_coord`` to be monotonic in the same direction as ``coord``."""
    direction = monotonic_direction(coord, dim)
    new_coord = ensure_1d_coord(new_coord, new_name)
    if new_coord.size > 1:
        new_diff = _np.diff(new_coord)
        if direction > 0 and not _np.all(new_diff > 0):
            raise ValueError(f"{new_name} must be increasing for dim {dim}.")
        if direction < 0 and not _np.all(new_diff < 0):
            raise ValueError(f"{new_name} must be decreasing for dim {dim}.")
    return direction


def evenly_spaced_coord_spacing(coord, dim, operation_name="process"):
    """Return coordinate spacing after validating 1D, length, and even spacing."""
    coord = require_min_coord_size(coord, dim, 2, operation_name)
    coord_diff = _np.diff(coord)
    if _np.any(coord_diff == 0):
        raise ValueError(f"Coordinate for dim {dim} must be strictly monotonic.")
    if not _np.allclose(coord_diff, coord_diff[0]):
        raise ValueError(f"Coordinate for dim {dim} must be evenly spaced.")
    return coord_diff[0]


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
