import numpy as _np


def buildup_function(p, E_max, p_half):
    r"""Calculate an enhancement buildup curve with a baseline of 1.

    Args:
        p (array_like): Microwave power values.
        E_max (float): Saturating enhancement relative to the baseline.
        p_half (float): Power where the enhancement term reaches half of
            ``E_max``.

    Returns:
        ndarray: Buildup curve evaluated at ``p``.

    .. math::

        f(p) = 1 + E_\mathrm{max} \frac{p}{p_{1/2} + p}

    Examples:
        >>> import numpy as np
        >>> import spinlab as sl
        >>> power = np.array([0.0, 1.0, 2.0])
        >>> y = sl.relaxation.buildup_function(power, E_max=-10.0, p_half=1.0)
    """

    p = _np.asarray(p)
    return 1 + E_max * p / (p_half + p)


def general_biexp(t, C1, C2, tau1, C3, tau2):
    r"""Calculate a bi-exponential curve.

    Args:
        t (array_like): Time values.
        C1 (float): Constant offset.
        C2 (float): Amplitude of the first exponential component.
        tau1 (float): Time constant of the first exponential component.
        C3 (float): Amplitude of the second exponential component.
        tau2 (float): Time constant of the second exponential component.

    Returns:
        ndarray: Bi-exponential curve evaluated at ``t``.

    .. math::

        f(t) = C_1 + C_2 e^{-t/\tau_1} + C_3 e^{-t/\tau_2}

    Examples:
        >>> import numpy as np
        >>> import spinlab as sl
        >>> t = np.linspace(0.0, 5.0, 51)
        >>> y = sl.relaxation.general_biexp(t, C1=0.0, C2=1.0, tau1=0.5, C3=0.2, tau2=3.0)
    """

    t = _np.asarray(t)
    return C1 + C2 * _np.exp(-1.0 * t / tau1) + C3 * _np.exp(-1.0 * t / tau2)


def general_exp(t, C1, C2, tau):
    r"""Calculate a mono-exponential curve.

    Args:
        t (array_like): Time values.
        C1 (float): Constant offset.
        C2 (float): Exponential amplitude.
        tau (float): Exponential time constant.

    Returns:
        ndarray: Mono-exponential curve evaluated at ``t``.

    .. math::

        f(t) = C_1 + C_2 e^{-t/\tau}

    Examples:
        >>> import numpy as np
        >>> import spinlab as sl
        >>> t = np.linspace(0.0, 5.0, 51)
        >>> y = sl.relaxation.general_exp(t, C1=0.0, C2=1.0, tau=2.0)
    """

    t = _np.asarray(t)
    return C1 + C2 * _np.exp(-1.0 * t / tau)


def ksigma_smax(p, E_max, p_half):
    r"""Calculate an asymptotic saturation curve without a baseline offset.

    Args:
        p (array_like): Microwave power values.
        E_max (float): Saturating value of the curve.
        p_half (float): Power where the curve reaches half of ``E_max``.

    Returns:
        ndarray: Saturation curve evaluated at ``p``.

    .. math::

        f(p) = E_\mathrm{max} \frac{p}{p_{1/2} + p}

    Examples:
        >>> import numpy as np
        >>> import spinlab as sl
        >>> power = np.array([0.0, 1.0, 2.0])
        >>> y = sl.relaxation.ksigma_smax(power, E_max=5.0, p_half=1.0)
    """

    p = _np.asarray(p)
    return E_max * p / (p_half + p)


def logistic(x, c, x0, L, k):
    r"""Calculate a logistic growth curve.

    Args:
        x (array_like): Input values.
        c (float): Baseline offset.
        x0 (float): Midpoint of the sigmoid.
        L (float): Sigmoid amplitude.
        k (float): Growth steepness.

    Returns:
        ndarray: Logistic curve evaluated at ``x``.

    .. math::

        f(x) = c + \frac{L}{1 + e^{-k(x-x_0)}}

    Examples:
        >>> import numpy as np
        >>> import spinlab as sl
        >>> x = np.linspace(0.0, 1.0, 5)
        >>> y = sl.relaxation.logistic(x, c=0.0, x0=0.5, L=1.0, k=2.0)
    """

    x = _np.asarray(x)
    return c + L / (1.0 + _np.exp(-1.0 * k * (x - x0)))


def t1(t, T1, M_0, M_inf):
    r"""Calculate a T1 exponential recovery curve.

    This form can describe inversion-recovery or saturation-recovery data
    depending on the chosen initial magnetization ``M_0``.

    Args:
        t (array_like): Time values.
        T1 (float): Longitudinal relaxation time constant.
        M_0 (float): Initial magnetization at ``t = 0``.
        M_inf (float): Equilibrium magnetization as ``t`` approaches infinity.

    Returns:
        ndarray: T1 recovery curve evaluated at ``t``.

    .. math::

        f(t) = M_{\infty} - (M_{\infty} - M_0)e^{-t/T_1}

    Examples:
        >>> import numpy as np
        >>> import spinlab as sl
        >>> t = np.linspace(0.0, 10.0, 101)
        >>> y = sl.relaxation.t1(t, T1=2.0, M_0=-1.0, M_inf=1.0)
    """

    t = _np.asarray(t)
    return M_inf - (M_inf - M_0) * _np.exp(-1.0 * t / T1)


def t2(t, M_0, T2, p=1.0):
    r"""Calculate a stretched or mono-exponential T2 decay curve.

    Args:
        t (array_like): Time values.
        M_0 (float): Initial signal amplitude.
        T2 (float): Transverse relaxation time constant.
        p (float): Stretching exponent. The default ``p=1`` gives a standard
            mono-exponential decay.

    Returns:
        ndarray: T2 decay curve evaluated at ``t``.

    .. math::

        f(t) = M_0 e^{-(t/T_2)^p}

    Examples:
        >>> import numpy as np
        >>> import spinlab as sl
        >>> t = np.linspace(0.0, 5.0, 51)
        >>> y = sl.relaxation.t2(t, M_0=1.0, T2=1.5)
    """

    t = _np.asarray(t)
    return M_0 * _np.exp(-1.0 * (t / T2) ** p)
