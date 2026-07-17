import numpy as _np

from ..constants import constants as _const

_UNIT_CONVERSIONS = {
    "Hz": 1.0,
    "MHz": 1.0e-6,
    "GHz": 1.0e-9,
    "rad/s": 2 * _const.pi,
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

        \nu_{dd} = \frac{\mu_0}{4\pi} \frac{g_1 g_2 \mu_B^2}{h r^3}

    """
    r_m = _np.asarray(r, dtype=float)

    nu_dd = (
        (_const.mu_0 / (4 * _const.pi))
        * (g1 * g2 * _const.mub**2)
        / (_const.h * r_m**3)
    )

    if unit not in _UNIT_CONVERSIONS:
        raise ValueError(
            f"Unknown unit '{unit}'. Choose from {list(_UNIT_CONVERSIONS.keys())}."
        )

    return nu_dd * _UNIT_CONVERSIONS[unit]


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


def sphere_quadrature(n_theta, n_phi):
    r"""Generate orientations and weights using Gauss-Legendre quadrature.

    Args:
        n_theta (int): Number of polar angle nodes.
        n_phi (int): Number of azimuthal angle nodes (uniformly spaced).

    Returns:
        tuple: (theta, phi, weights) arrays. Theta and phi are in radians,
            weights incorporate the solid angle element and are normalized
            to sum to one.

    """
    cos_theta, w_theta = _np.polynomial.legendre.leggauss(n_theta)
    theta_nodes = _np.arccos(cos_theta)
    phi_nodes = _np.linspace(0, 2 * _const.pi, n_phi, endpoint=False)
    w_phi = 2 * _const.pi / n_phi

    theta = _np.repeat(theta_nodes, n_phi)
    phi = _np.tile(phi_nodes, n_theta)
    weights = _np.repeat(w_theta * w_phi, n_phi)
    weights /= weights.sum()

    return theta, phi, weights


def pake_pattern(freq, theta, phi, coupling, linewidth, weights=None):
    r"""Calculate the Pake pattern for a dipolar-coupled spin pair.

    Args:
        freq (array_like): Frequency axis in Hz.
        theta (array_like): Polar angles in radians from
            :func:`sphere_quadrature` or :func:`sphere_orientations`.
        phi (array_like): Azimuthal angles in radians.
        coupling (float): Dipolar coupling constant in Hz from
            :func:`distance_to_dipolar_coupling`.
        linewidth (float): Lorentzian line broadening in Hz.
        weights (array_like, optional): Quadrature weights for each
            orientation from :func:`sphere_quadrature`. If None, all
            orientations are weighted equally.

    Returns:
        ndarray: Pake pattern intensity evaluated at the given frequencies.

    The dipolar frequency for each orientation is:

    .. math::

        \nu(\theta) = \nu_{dd} (3 \cos^2\theta - 1)

    Broadening is applied as a convolution via multiplication with an
    exponential decay in the time domain.

    """
    freq = _np.asarray(freq, dtype=float)
    theta = _np.asarray(theta)
    n_points = len(freq)

    if weights is None:
        weights = _np.ones(len(theta)) / len(theta)
    else:
        weights = _np.asarray(weights, dtype=float)

    df = freq[1] - freq[0]
    dt = 1.0 / (n_points * df)
    t = _np.arange(n_points) * dt

    cos2 = _np.cos(theta) ** 2
    freqs_pos = coupling * (3 * cos2 - 1)
    freqs_neg = -freqs_pos

    fid = _np.sum(
        weights[:, None]
        * (
            _np.exp(2j * _const.pi * freqs_pos[:, None] * t[None, :])
            + _np.exp(2j * _const.pi * freqs_neg[:, None] * t[None, :])
        ),
        axis=0,
    )
    fid *= _np.exp(-_const.pi * linewidth * t)

    spectrum = _np.real(_np.fft.fftshift(_np.fft.fft(fid)))

    return spectrum
