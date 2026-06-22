import numpy as _np

from ..constants import constants as _const


_UNIT_CONVERSIONS = {
    "rad/s": 1.0,
    "Hz": 1.0 / (2 * _const.pi),
    "MHz": 1.0 / (2 * _const.pi * 1e6),
    "GHz": 1.0 / (2 * _const.pi * 1e9),
}


def distance_to_dipolar_coupling(r, g1=_const.ge, g2=_const.ge, unit="Hz"):
    r"""Convert electron-electron distance to dipolar coupling frequency.

    Args:
        r (float or array_like): Inter-spin distance in meters.
        g1 (float): g-value of electron 1 (default: free electron).
        g2 (float): g-value of electron 2 (default: free electron).
        unit (str): Output unit: "Hz", "MHz", "GHz", or "rad/s" (default: "Hz").

    Returns:
        ndarray: Dipolar coupling in the requested unit.

    .. math::

        \omega_{dd} = \frac{\mu_0}{4\pi} \frac{g_1 g_2 \mu_B^2}{\hbar r^3}

    """
    r_m = _np.asarray(r, dtype=float)

    omega_dd = (_const.mu_0 / (4 * _const.pi)) * (g1 * g2 * _const.mub**2) / (_const.hbar * r_m**3)

    if unit not in _UNIT_CONVERSIONS:
        raise ValueError(
            f"Unknown unit '{unit}'. Choose from {list(_UNIT_CONVERSIONS.keys())}."
        )

    return omega_dd * _UNIT_CONVERSIONS[unit]


def sphere_orientations(n):
    r"""Generate equally spaced orientations on a unit sphere.

    Args:
        n (int): Number of polar bands. The total number of orientations
            depends on the partitioning and will generally be larger than n.

    Returns:
        tuple: (theta, phi) arrays of polar and azimuthal angles in radians.
            Theta ranges over [0, pi], phi over [0, 2*pi].

    """
    n = int(n)
    half_indices = _np.arange(0.5, n, 1.0)
    np_j = _np.ceil(n * _np.sin(half_indices * _const.pi / n)).astype(int)
    n_total = np_j.sum()

    theta = _np.empty(n_total)
    phi = _np.empty(n_total)

    theta_j = 0.0
    idx = 0
    for j in range(n):
        cos_arg = _np.clip(_np.cos(theta_j) - 2 * np_j[j] / n_total, -1.0, 1.0)
        dtheta = _np.arccos(cos_arg) - theta_j
        count = np_j[j]

        theta[idx : idx + count] = theta_j + dtheta / 2
        dphi = 2 * _const.pi / count
        phi[idx : idx + count] = _np.arange(0.5, count, 1.0) * dphi

        idx += count
        theta_j += dtheta

    return theta, phi
