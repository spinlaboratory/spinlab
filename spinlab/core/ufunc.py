from .data import SpinData
import numpy as _np

__all__ = ["generate_data"]


def generate_data(shape):
    """Generate a SpinData object filled with random normal values.

    Args:
        shape (tuple): Shape of the output array. Each element defines the
            length of one dimension. Dimensions are labeled ``x0``, ``x1``, etc.

    Returns:
        SpinData: Data object with random values and integer coordinates.
    """
    size = 1
    dims = []
    coords = []
    for ix, length in enumerate(shape):
        dims.append("x" + str(ix))
        coords.append(_np.array(range(length)))
        size *= length

    values = _np.random.randn(size)

    return SpinData(values, dims, coords)


def ones(shape, dtype=None):
    """Return a SpinData object filled with ones.

    Args:
        shape (tuple): Shape of the output array.
        dtype (data-type, optional): Desired data type of the array. Defaults to float64.

    Returns:
        SpinData: Data object of given shape filled with ones and integer coordinates.
    """
    values = _np.ones(shape, dtype=dtype)
    coords = []
    dims = []
    for ix in range(len(shape)):
        dims.append(str(ix))
        coords.append(_np.arange(shape[ix]))

    return SpinData(values, dims, coords)


def ones_like(a):
    """Return a SpinData object of ones with the same shape and dtype as a given object.

    Args:
        a (SpinData): Reference object. Shape and dtype are taken from this object.

    Returns:
        SpinData: Data object filled with ones matching the shape and dtype of ``a``.
    """
    return ones(a.shape, a.dtype)


def zeros(shape, dtype=None):
    """Return a SpinData object filled with zeros.

    Args:
        shape (tuple): Shape of the output array.
        dtype (data-type, optional): Desired data type of the array. Defaults to float64.

    Returns:
        SpinData: Data object of given shape filled with zeros and integer coordinates.
    """
    values = _np.zeros(shape, dtype=dtype)
    coords = []
    dims = []
    for ix in range(len(shape)):
        dims.append(str(ix))
        coords.append(_np.arange(shape[ix]))

    return SpinData(values, dims, coords)


def zeros_like(a):
    """Return a SpinData object of zeros with the same shape and dtype as a given object.

    Args:
        a (SpinData): Reference object. Shape, dtype, dims, coords, and attrs are
            taken from this object.

    Returns:
        SpinData: Data object filled with zeros matching the shape and dtype of ``a``.
    """
    zeros_ = zeros(a.shape, a.dtype)
    zeros_.dims = a.dims
    zeros_.coords = a.coords
    zeros_.attrs = a.attrs
    return zeros(a.shape, a.dtype)


def randn(shape):
    """Return a SpinData object filled with random samples from a standard normal distribution.

    Args:
        shape (tuple): Shape of the output array.

    Returns:
        SpinData: Data object with random normal values and integer coordinates.
    """
    values = _np.random.randn(*shape)
    coords = []
    dims = []
    for ix in range(len(shape)):
        dims.append(str(ix))
        coords.append(_np.arange(shape[ix]))

    return SpinData(values, dims, coords)


def randn_like(a):
    """Return a SpinData object of random normal values with the same shape as a given object.

    Args:
        a (SpinData): Reference object. Shape is taken from this object.

    Returns:
        SpinData: Data object filled with random normal values matching the shape of ``a``.
    """
    return randn(a.shape)
