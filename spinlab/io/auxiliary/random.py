"""Synthetic SpinData generators for examples and tests."""

import numpy as _np
import scipy.constants as _const

from ...core.data import SpinData


def _get_rng(seed=None):
    if seed is None:
        return _np.random
    return _np.random.default_rng(seed)


def _normal(rng, shape):
    if hasattr(rng, "normal"):
        return rng.normal(size=shape)
    return rng.randn(*shape)


def _normalize_shape(args, shape=None):
    if shape is not None and args:
        raise TypeError("Provide either positional shape values or shape=, not both")
    if shape is None:
        shape = args if args else (1024,)
    if len(shape) == 1 and isinstance(shape[0], (tuple, list)):
        shape = tuple(shape[0])
    shape = tuple(int(point) for point in shape)
    if any(point <= 0 for point in shape):
        raise ValueError("All dimensions must contain at least one point")
    return shape


def _default_dims(ndim):
    if ndim == 1:
        return ["x"]
    return ["x%i" % index for index in range(ndim)]


def _default_coords(shape):
    return [_np.arange(point) for point in shape]


def fid(points=1024, snr=100.0, seed=None):
    """Generate an FID dataset for testing.

    Args:
        points (int): Number of points in the FID.
        snr (float): Signal-to-noise ratio.
        seed (int): Random seed for reproducible noise.

    Returns:
        SpinData: Complex FID with dimension ``"t2"``.
    """
    rng = _get_rng(seed)
    t2 = _np.r_[0 : 1 : 1j * int(points)]

    values = (
        _np.exp(1j * 2 * _const.pi * 100.0 * t2) * _np.exp(-1 * t2 / 0.10)
        + _normal(rng, int(points)) / snr
    )

    attrs = {"nmr_frequency": 300e6, "experiment_type": "nmr_spectrum"}
    spinlab_attrs = {"data_type": "NMR", "frequency": 300e6}

    return SpinData(values, ["t2"], [t2], attrs=attrs, spinlab_attrs=spinlab_attrs)


def ir(
    points=(1024, 16),
    snr=10.0,
    T1=1.0,
    T2=0.10,
    frequency=100.0,
    t1=None,
    seed=None,
):
    """Generate a synthetic inversion-recovery FID series.

    Args:
        points (tuple): Number of points along ``("t2", "t1")``. If a single
            integer is given, it is interpreted as the number of ``t1`` delays
            and the direct dimension uses 1024 points.
        snr (float): Signal-to-noise ratio of the FID series.
        T1 (float): Longitudinal recovery time constant.
        T2 (float): Transverse FID decay time constant.
        frequency (float): Oscillation frequency in Hz along ``t2``.
        t1 (array_like): Optional inversion recovery delays.
        seed (int): Random seed for reproducible noise.

    Returns:
        SpinData: Complex 2D data with dimensions ``["t2", "t1"]``.

    Examples:
        >>> data = sl.io.auxiliary.random.ir(points=(256, 8), seed=1)
    """
    if isinstance(points, int):
        points = (1024, points)
    points = tuple(int(point) for point in points)
    if len(points) == 1:
        points = (1024, points[0])
    if len(points) != 2:
        raise ValueError("points must be an int or a tuple of (t2_points, t1_points)")
    if any(point <= 0 for point in points):
        raise ValueError("All dimensions must contain at least one point")

    t2_points, t1_points = points
    t2 = _np.r_[0 : 1 : 1j * t2_points]
    if t1 is None:
        t1 = _np.linspace(0.0, 5.0 * T1, t1_points)
    else:
        t1 = _np.asarray(t1, dtype=float)
        if t1.size != t1_points:
            raise ValueError("t1 must have the same length as the t1 dimension")

    rng = _get_rng(seed)
    recovery = 1.0 - 2.0 * _np.exp(-t1 / T1)
    fid_shape = (t2_points, 1)
    recovery_shape = (1, t1_points)
    fid_values = _np.exp(1j * 2 * _const.pi * frequency * t2).reshape(fid_shape)
    fid_values *= _np.exp(-t2 / T2).reshape(fid_shape)
    values = fid_values * recovery.reshape(recovery_shape)
    values = values + _normal(rng, points) / snr

    attrs = {
        "experiment_type": "inversion_recovery",
        "nmr_frequency": 300e6,
        "T1": T1,
        "T2": T2,
    }
    spinlab_attrs = {"data_type": "NMR", "frequency": 300e6}

    return SpinData(
        values, ["t2", "t1"], [t2, t1], attrs=attrs, spinlab_attrs=spinlab_attrs
    )


def nd(
    *args, shape=None, dims=None, coords=None, complex_data=False, snr=None, seed=None
):
    """Generate an n-dimensional synthetic SpinData object.

    Args:
        *args: Shape values, e.g. ``nd(8, 4)``. A single tuple is also accepted.
        shape (tuple): Alternative way to provide the shape.
        dims (list): Optional dimension names.
        coords (list): Optional coordinate arrays.
        complex_data (bool): If True, generate complex random values.
        snr (float): If provided, add random noise scaled by ``1 / snr`` to a
            smooth deterministic signal.
        seed (int): Random seed for reproducible output.

    Returns:
        SpinData: Synthetic n-dimensional data.

    Examples:
        >>> data = sl.io.auxiliary.random.nd(8, 4, dims=["x", "scan"], seed=1)
    """
    shape = _normalize_shape(args, shape=shape)
    if dims is None:
        dims = _default_dims(len(shape))
    if coords is None:
        coords = _default_coords(shape)
    if len(dims) != len(shape):
        raise ValueError("dims length must match the number of dimensions")
    if len(coords) != len(shape):
        raise ValueError("coords length must match the number of dimensions")

    coords = [_np.asarray(coord) for coord in coords]
    for axis, (coord, size) in enumerate(zip(coords, shape)):
        if coord.size != size:
            raise ValueError(
                "coords[{0}] length must match shape[{0}] ({1})".format(axis, size)
            )

    rng = _get_rng(seed)
    grid = _np.meshgrid(*coords, indexing="ij")
    values = _np.zeros(shape, dtype=float)
    for axis_grid in grid:
        scale = _np.ptp(axis_grid)
        if scale == 0:
            scale = 1.0
        values += _np.cos(2.0 * _const.pi * (axis_grid - axis_grid.min()) / scale)
    values /= len(shape)

    if snr is None:
        values = _normal(rng, shape)
    else:
        values = values + _normal(rng, shape) / snr

    if complex_data:
        values = values + 1j * _normal(rng, shape) / (snr if snr else 1.0)

    attrs = {"experiment_type": "synthetic"}
    return SpinData(values, list(dims), coords, attrs=attrs)
