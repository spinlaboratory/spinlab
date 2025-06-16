import numpy as _np
from ..core.data import SpinData
import scipy.constants as _const


def fid(points=1024, snr=100.0):
    """Generate an FID dataset for testing

    Args:
        points (int): Number of points in FID
        snr (float): Signal to noise ratio of FID

    Returns:
        SpinData: FID in SpinData object
    """

    t2 = _np.r_[0 : 1 : 1j * points]

    values = (
        _np.exp(1j * 2 * _const.pi * 100.0 * t2) * _np.exp(-1 * t2 / 0.10)
        + _np.random.randn(points) / snr
    )

    attrs = {"nmr_frequency": 300e6}

    return SpinData(values, ["t2"], [t2])


def ir(points=(1024,), snr=10):
    """Generate an IR dataset for testing"""
    return NotImplemented


def nd(*args):
    """Generate n-dimensional dataset for testing"""
    return NotImplemented
