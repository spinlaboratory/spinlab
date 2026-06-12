import spinlab as _sl
import numpy as _np
from ..core.data import SpinData


def decay2Ce(decay_time, gA, gB, FB):
    """Convert decay time to effective concentration

    Convert the decay rate (mono exponential decay, or stretched exponential)
    into an effective concentration. See Jeschke/Schweiger "Principles of
    pulse electron paramagnetic resonance", p. 415, eq. 13.3.4

    Args:
        decay_time (float):     Decay time from mono exponential fit (s)
        gA, gB:                 (isotropic) g-values of spin A and B
        FB:                     Fraction of B spins excited by pump pulse
                                (DEER modulation depth)

    Returns:
        float: Effective concentration.

    Examples:

        >>> Ce = sl.decay2Ce(decay_time=1.5e-6, gA=2.0, gB=2.1, FB=0.3)
    """

    # Eq. 13.3.5 (p. 415)
    k = 2 * _np.pi * _sl.mu_0 * _sl.mub**2 * gA * gB / (9 * _np.sqrt(3) * _sl.hbar)

    c_effective = 1 / (decay_time * k * 1000 * _sl.N_A * FB)

    return c_effective


def convert_power(data, mode="dBm2W"):
    """Convert power between dBm and W.

    For SpinData input, the coordinate whose dimension is named "Power" or
    "powers" is converted. If ``spinlab_attrs["power_unit"]`` is present, it
    determines the conversion direction regardless of ``mode``. Otherwise,
    ``mode`` determines the conversion direction.

    Non-SpinData input is converted directly according to ``mode``.

    Args:
        data (SpinData, array, list, float or int): Power values or SpinData
            with a power coordinate.
        mode (str): "dBm2W" or "W2dBm". Defaults to "dBm2W".

    Returns:
        out (SpinData, array, list, float or int)

    Raises:
        ValueError: If no power dimension is found, power_unit is invalid, or
            mode is invalid.

    Examples:

        >>> data = sl.load("path/to/data")
        >>> data = sl.convert_power(data)
        >>> powers_w = sl.convert_power([0, 10, 20], mode="dBm2W")
        >>> powers_dbm = sl.convert_power([0.001, 0.01, 0.1], mode="W2dBm")

    """
    if isinstance(data, SpinData):
        out = data.copy()
        dims = out.dims
        for dim in dims:
            if dim.lower() == "power" or dim.lower() == "powers":
                break
            elif dim == dims[-1]:
                raise ValueError("Power is not in dim")
            else:
                continue

        if "power_unit" in out.spinlab_attrs.keys():
            if out.spinlab_attrs["power_unit"] == "dBm":
                mode = "dBm2W"
            elif out.spinlab_attrs["power_unit"] == "W":
                mode = "W2dBm"
            else:
                raise ValueError("Power unit in spinlab_attrs is invalid")

        if mode.lower() == "dbm2w":
            power_unit = "W"
            f = dBm2w
        elif mode.lower() == "w2dbm":
            power_unit = "dBm"
            f = w2dBm
        else:
            raise ValueError("Mode is not acceptable")

        out.coords[dim] = f(out.coords[dim])
        proc_parameters = {
            "mode": mode,
        }
        out.spinlab_attrs["power_unit"] = power_unit
        proc_attr_name = "convert_power"
        out.add_proc_attrs(proc_attr_name, proc_parameters)

        return out

    else:
        if mode.lower() == "dbm2w":
            f = dBm2w
        elif mode.lower() == "w2dbm":
            f = w2dBm
        else:
            raise ValueError("Mode is not acceptable")
        return f(data)


def dBm2w(power_in_dBm):
    """Convert power in dBm to power in W

    Convert a microwave power given in dBm to W. Note that for values <= -190 dBm the output power in W is set to 0.

    Args:
        power_in_dBm (array, list, float or int): Power in (dBm)

    Returns:
        float (array, list, float or int): Power in (W). Numpy array outputs are
            floating-point arrays.

    Examples:

        >>> sl.dBm2w(0)
        0.001
        >>> sl.dBm2w([0, 10, 20])
        [0.001, 0.01, 0.1]
        >>> sl.dBm2w(np.array([0, 10, 20]))
        array([0.001, 0.01 , 0.1  ])

    """

    if isinstance(power_in_dBm, _np.ndarray):
        power_in_W = power_in_dBm.astype(float, copy=True)
        for index in range(len(power_in_dBm)):
            power_in_W[index] = dBm2w(power_in_dBm[index])
        return power_in_W

    elif isinstance(power_in_dBm, list):
        power_in_W = power_in_dBm.copy()
        for index in range(len(power_in_dBm)):
            power_in_W[index] = dBm2w(power_in_dBm[index])
        return power_in_W

    else:
        power_in_W = 10.0 ** (power_in_dBm / 10.0) / 1000.0
        # Set values below 1 pW to 0 W
        power_in_W = 0 if power_in_W <= 1e-22 else power_in_W

    return power_in_W


def w2dBm(power_in_W):
    """Convert power in W to power in dBm

    Convert a microwave power given in W to dBm

    Args:
        power_in_W (array, list, float or int):   Power in (W)

    Returns:
        float (array, list, float or int): Power in (dBm). Numpy array outputs
            are floating-point arrays.

    Examples:

        >>> sl.w2dBm(0.001)
        0.0
        >>> sl.w2dBm([0.001, 0.01, 0.1])
        [0.0, 10.0, 20.0]
        >>> sl.w2dBm(np.array([0.001, 0.01, 0.1]))
        array([ 0., 10., 20.])

    """
    if isinstance(power_in_W, _np.ndarray):
        power_in_dBm = power_in_W.astype(float, copy=True)
        for index in range(len(power_in_W)):
            power_in_dBm[index] = w2dBm(power_in_W[index])
        return power_in_dBm

    elif isinstance(power_in_W, list):
        power_in_dBm = power_in_W.copy()
        for index in range(len(power_in_W)):
            power_in_dBm[index] = w2dBm(power_in_W[index])
        return power_in_dBm

    else:
        power_in_dBm = 10.0 * _np.log10(1000 * power_in_W)

    return power_in_dBm


def tp90_B1(tp90):
    """Calculate B1 field strength from 90 degree pulse length.

    Args:
        tp90 (float):       Pulse length of the 90 degree pulse (s)

    Returns:
        B1 (float):         B1 field strength (Hz)

    Examples:

        >>> sl.tp90_B1(10e-9)
        25000000.0
    """

    B1_Hz = 1 / tp90 / 4

    return B1_Hz


def calc_tp90(c, P, Q=1, alpha=0, verbose=False):
    r"""Calculate 90 degree pulse length

    Calculate 90 degree pulse length (tp90) from probe conversion factor and
    applied RF power. Optionally, the quality factor and attenuation can be
    given as input arguments. A formatted output can be generated when setting
    the verbose flag to True.

    Args:
        c (float):          Probe conversion factor (G/sqrt(W))
        P (float):          Input RF power
        Q (float):          Optionally, probe quality factor. Default value is 1
        alpha (float):      Optionally, attenuation (dB)
        verbose (boolean):  Optionally, return results in formatted output

    Returns:
        tp90 (float):       90 degree pulse length (ns)

    .. math::

    """

    power_at_probe = P / (10 ** (alpha / 10))
    b1_g = c * _np.sqrt(power_at_probe * Q)
    b1_mhz = b1_g * 2.804 * 1e-6

    tp90 = 1 / b1_mhz / 4 * 1e-12

    if verbose == True:
        print(" ")
        print("*** Input Parameters ***")
        print("Conversion Factor c (G/sqrt(W)): ", c)
        print("Input RF Power P (W):            ", P)
        print("Quality Factor Q:                ", Q)
        print("Attenuation alpha (dB):          ", alpha)
        print(" ")
        print("*** Results ***")
        print("RF power at probe (W):           ", power_at_probe)
        print("B1 Field Strength (G):           ", b1_g)
        print("B1 Field Strength (MHz):         ", b1_mhz * 1e6)
        print("tp90 (ns):                       ", tp90 * 1e9)

    return tp90


def calc_conversion_factor(tp90, P, Q=1, alpha=0, verbose=False):
    """Calculate probe conversion factor

    Calculate the probe microwave conversion factor from the 90 degree pulse length (tp90), and applied RF power. Optionally, the quality factor and attenuation can be given as input arguments. The function returns the conversion factor in (G/sqrt(W)). A formatted output can be generated when setting the verbose flag to True.

    Args:
        tp90 (float):       90 degree pulse length (ns)
        P (float):          Input RF power
        Q (float):          Optionally, probe quality factor. Default value is 1
        alpha (float):      Optionally, attenuation (dB)
        verbose (boolean):  Optionally, return results in formatted output

    Returns:
        c (float):          Probe conversion factor (G/sqrt(W))

    .. math::

    """

    power_at_probe = P / (10 ** (alpha / 10))

    b1_mhz = 1 / tp90 / 4 * 1e-12

    b1_Hz = 1 / tp90 / 4
    print(b1_Hz * 1e-6)

    b1_g = b1_mhz / 2.804e-6

    c = b1_g / _np.sqrt(power_at_probe * Q)

    if verbose == True:
        print(" ")
        print("*** Input Parameters ***")
        print("tp90 (ns):                       ", tp90 * 1e9)
        print("Input Power P (W):               ", P)
        print("Quality Factor Q:                ", Q)
        print("Attenuation alpha (dB):          ", alpha)
        print(" ")
        print("*** Results ***")
        print("Power at probe (W):              ", power_at_probe)
        print("B1 Field Strength (G):           ", b1_g)
        print("B1 Field Strength (MHz):         ", b1_mhz * 1e6)
        print("Conversion Factor c (G/sqrt(W)): ", c)
