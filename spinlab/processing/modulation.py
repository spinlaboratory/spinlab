import numpy as _np
from scipy.fft import fft as _fft
from scipy.fft import ifft as _ifft
from scipy.special import jv as _jv

from ..constants import constants as _const


def pseudo_modulation(data, modulation_amplitude, dim="B0", order=1, zero_padding=2):
    """Calculate the first derivative of an EPR spectrum due to field modulation

    Calculation is based on Hyde et al., "Pseudo Field Modulation in EPR
    Spectroscopy", Applied Magnetic Resonance 1 (1990): 483-496.

    Args:
        data (SpinData): SpinData object (typically an absorption line EPR spectrum)
        modulation_amplitude: Peak to peak modulation amplitude. The unit is equal to the unit of the axis. E.g. if the spectrum axis is given in (T), the unit of the modulation amplitude is in (T) as well.
        dim: Dimension to pseudo modulate (default is B0)
        order: Harmonic of field modulation (default is 1, 1st derivative)
        zero_padding: Number of points for zero-padding (multiples of spectrum vector length). Default is 2. Increase this number for short signal vectors.

    Returns:
        data (SpinData): Pseudo modulated spectrum


    Examples:
        .. code-block:: python

            spec = sl.load("path/to/data")

            # Calculate pseudo_modulated spectrum (1st derivative). Field axis given in (T)
            spec_mod = sl.pseudo_modulation(spec, modulation_amplitude=0.001)

            # Calculate pseudo_modulated spectrum (2nd derivative). Field axis given in (T)
            spec_mod = sl.pseudo_modulation(spec, modulation_amplitude=0.001, order=2)

    """

    out = data.copy()
    out.unfold(dim)

    proc_parameters = {
        "dim": dim,
        "modulation_amplitude": modulation_amplitude,
        "order": order,
        "zero_padding": zero_padding,
    }

    n = len(out.coords[dim])
    delta_B = out.coords[dim][2] - out.coords[dim][1]
    Zmin = 0
    Zmax = _const.pi * modulation_amplitude / delta_B
    Z = _np.linspace(Zmin, Zmax, zero_padding * n)

    spec = out.values
    spec = _np.squeeze(spec)

    fft_spec = _fft(spec, zero_padding * n)  # Zero pad data
    fft_spec[int(n) + 1 : zero_padding * n] = 0

    fft_spec_mod = fft_spec * _jv(order, Z)
    # Convolute fft spectrum with bessel function

    spec_mod = _ifft(fft_spec_mod)
    spec_mod = 1j**order * spec_mod[0:n]  # Pick the right dimension for higher orders
    spec_mod = _np.real(spec_mod)  # Only return real part

    out.values = spec_mod

    out.fold()

    proc_attr_name = "pseudo_modulation"
    out.add_proc_attrs(proc_attr_name, proc_parameters)

    return out
