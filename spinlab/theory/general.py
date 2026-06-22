import numpy as _np

from spinlab.constants.constants import mu_0, pi, hbar, mub, ge


def distance_to_dipolar_coupling(r, g1=ge, g2=ge, unit="MHz"):
    r"""Convert electron-electron distance to dipolar coupling frequency.

    Args:
        r (float or array_like): Inter-spin distance in nanometers.
        g1 (float): g-value of electron 1 (default: free electron).
        g2 (float): g-value of electron 2 (default: free electron).
        unit (str): Output unit: "MHz", "GHz", "Hz", or "rad/s" (default: "MHz").

    Returns:
        ndarray: Dipolar coupling in the requested unit.

    .. math::

        \omega_{dd} = \frac{\mu_0}{4\pi} \frac{g_1 g_2 \mu_B^2}{\hbar r^3}

    """
    r_m = _np.asarray(r, dtype=float) * 1e-9

    omega_dd = (mu_0 / (4 * pi)) * (g1 * g2 * mub**2) / (hbar * r_m**3)

    conversions = {
        "rad/s": 1.0,
        "Hz": 1.0 / (2 * pi),
        "MHz": 1.0 / (2 * pi * 1e6),
        "GHz": 1.0 / (2 * pi * 1e9),
    }

    if unit not in conversions:
        raise ValueError(
            f"Unknown unit '{unit}'. Choose from {list(conversions.keys())}."
        )

    return omega_dd * conversions[unit]
