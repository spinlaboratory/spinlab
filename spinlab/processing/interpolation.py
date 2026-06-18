"""
SpinLab uses numpy.interp function to interpolate SpinData object

Author: Yen-Chun Huang
"""

import numpy as _np
from ._utils import get_default_dim


def _interp_with_extrapolation(new_coord, coord, values, left, right, extrapolate):
    new_values = _np.interp(new_coord, coord, values, left=left, right=right)

    if not extrapolate:
        return new_values

    left_mask = new_coord < coord[0]
    right_mask = new_coord > coord[-1]

    if _np.any(left_mask) and left is None:
        slope = (values[1] - values[0]) / (coord[1] - coord[0])
        new_values[left_mask] = values[0] + slope * (new_coord[left_mask] - coord[0])

    if _np.any(right_mask) and right is None:
        slope = (values[-1] - values[-2]) / (coord[-1] - coord[-2])
        new_values[right_mask] = values[-1] + slope * (
            new_coord[right_mask] - coord[-1]
        )

    return new_values


def interp(data, dim=None, new_coord=None, left=None, right=None, extrapolate=False):
    """
    Interpolate SpinData object

    Args:
        data (SpinData): Data object
        dim (str or None): Dimension to interpolate. If None, the first
            dimension is used.
        new_coord (list or numpy.arrays): New one-dimensional coordinate array
            for the interpolated axis.
        left (optional: float or complex): Corresponding to data value, see numpy.interp for more details
        right (optional: float or complex): Corresponding to data value, see numpy.interp for more details
        extrapolate (bool): If True, linearly extrapolate outside the source
            coordinate range. Explicit left or right values override
            extrapolation on that side.

    Returns:
        data (SpinData): interpolated data object

    Examples:
        >>> data = sl.load("path/to/data")
        >>> data = sl.interp(data, new_coord=np.r_[-10:10:1000j])
        >>> data = sl.interp(data, dim='f2', new_coord=np.r_[-10:10:1000j])

    .. Note::

        The source coordinate along ``dim`` must be monotonic increasing or
        monotonic decreasing. ``new_coord`` must be monotonic in the same
        direction as the source coordinate. Decreasing source coordinates are
        handled by reversing the source coordinate and values before
        interpolation.

    """

    out = data.copy()
    dim = get_default_dim(out, dim, "interpolate")

    proc_parameters = {
        "dim": dim,
        "new_coord": new_coord,
        "left": left,
        "right": right,
        "extrapolate": extrapolate,
    }

    if new_coord is None:
        raise ValueError("new_coord must be provided")

    if len(_np.shape(new_coord)) != 1:
        raise ValueError("The input coord can only be one dimension")

    if isinstance(new_coord, list):
        new_coord = _np.array(new_coord)

    if len(new_coord) == 0:
        raise ValueError("new_coord must contain at least one point")

    coord = _np.asarray(out.coords[dim])
    if len(coord) < 2:
        raise ValueError(
            "Cannot interpolate dim %s. Coordinate must contain at least two points."
            % dim
        )

    coord_diff = _np.diff(coord)
    if _np.all(coord_diff > 0):
        if len(new_coord) > 1 and not _np.all(_np.diff(new_coord) > 0):
            raise ValueError("new_coord must be increasing for dim %s." % dim)
        interp_coord = coord
        interp_values = out.values
    elif _np.all(coord_diff < 0):
        if len(new_coord) > 1 and not _np.all(_np.diff(new_coord) < 0):
            raise ValueError("new_coord must be decreasing for dim %s." % dim)
        interp_coord = coord[::-1]
        interp_values = _np.flip(out.values, axis=out.index(dim))
    else:
        raise ValueError("Coordinate for dim %s must be monotonic." % dim)

    index = out.index(dim)
    values = _np.moveaxis(interp_values, index, 0)
    original_shape = values.shape
    flat_values = values.reshape(original_shape[0], -1)

    new_values = _np.array(
        [
            _interp_with_extrapolation(
                new_coord,
                interp_coord,
                flat_values[:, ix],
                left,
                right,
                extrapolate,
            )
            for ix in range(flat_values.shape[1])
        ]
    ).T
    new_values = new_values.reshape((len(new_coord),) + original_shape[1:])
    out.values = _np.moveaxis(new_values, 0, index)
    out.coords[dim] = new_coord

    proc_attr_name = "interp"
    out.add_proc_attrs(proc_attr_name, proc_parameters)

    return out
