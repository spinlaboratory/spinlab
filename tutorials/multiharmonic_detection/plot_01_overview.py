"""
.. _MHD_Overview:

Multi-Harmonic Detection: Overview (#1)
========================================
"""

# %%
# In conventional CW EPR spectroscopy the magnetic field is modulated and the
# signal is phase-sensitively detected at the modulation frequency (`lock-in
# detection <https://en.wikipedia.org/wiki/Lock-in_amplifier>`_), giving the
# familiar 1st-derivative spectrum. Increasing the modulation amplitude
# improves the signal-to-noise ratio (S/N), but broadens the line once the
# modulation amplitude becomes comparable to the linewidth (overmodulation) -- a direct
# trade-off between sensitivity and resolution. If only the 1st harmonic is detected, the native line shape of the signal can not be recovered.
#
# Multi-harmonic detection (MHD) can be used to restore the native line shape. Instead of detecting
# only at the modulation frequency (the 1st harmonic), also the higher harmonics (2nd, 3rd, ....) can be detected. For this, the lock-in detector has to be able to demodulate the signal also at these higher harmonics. Combining
# several harmonics allows the *undistorted* 1st-derivative line to be
# reconstructed even when the modulation amplitude is several times the
# linewidth, recovering the S/N benefit of over-modulation without distorting the native line shape.
#
# This tutorial series follows the following literature references:
#
# * Tseitlin, Eaton, Eaton, *J. Magn. Reson.* 209 (2011) 277-281
# * Yu, Tseytlin, Eaton, Eaton, *J. Magn. Reson.* 254 (2015) 86-92
# * Tseitlin, Iyudin, Tseitlin, *Appl. Magn. Reson.* 35 (2009) 569-580
#
# and uses SpinLab's :func:`~spinlab.processing.harmonics.combine_harmonics`
# and :func:`~spinlab.processing.harmonics.reconstruct_harmonics` functions.

# %%
# The reconstruction filter
# --------------------------
# Each harmonic spectrum :math:`s_n(B)` is related to the Fourier transform
# :math:`F(u)` of the true 1st-derivative line :math:`f(B)` through a Bessel-function-based filter :math:`D_n(u)` that depends only on
# the modulation amplitude :math:`h_m` and the harmonic order :math:`n`:
#
# .. math::
#
#     S_n(u) = D_n(u)\, F(u)
#
#
#     D_n(u) = \frac{h_m}{4n}\, j^{-(n-1)}
#              \left[ J_{n-1}\!\left(\frac{h_m u}{2}\right)
#                   + J_{n+1}\!\left(\frac{h_m u}{2}\right) \right]
#
# :math:`D_n(u)` behaves like a filter with an oscillatory envelope: it has
# zeros where information about :math:`F(u)` is lost for that harmonic alone.
# Crucially, different harmonics have zeros at different positions in
# :math:`u`, so combining several harmonics fills in what any single harmonic
# is missing. The plot below shows this directly.

import numpy as np
import spinlab as sl
from scipy.special import jv

modulation_amplitude = 2.5  # arbitrary field units


def Dn(u, n, hm):
    z = hm * u / 2.0
    return (hm / (4.0 * n)) * ((-1j) ** (n - 1)) * (jv(n - 1, z) + jv(n + 1, z))


u = np.linspace(0, 6, 600)

sl.plt.figure()
for n in range(1, 6):
    sl.plt.plot(u, np.abs(Dn(u, n, modulation_amplitude)), label=f"$|D_{n}(u)|$")
sl.plt.xlabel("u")
sl.plt.ylabel("|D$_n$(u)|")
sl.plt.title(f"Reconstruction filters, h$_m$ = {modulation_amplitude}")
sl.plt.legend()
sl.plt.tight_layout()
sl.plt.show()

# %%
# :math:`D_1(u)` (blue) is largest near :math:`u = 0` but has zeros further
# out; :math:`D_2(u)` through :math:`D_5(u)` have their own maxima roughly
# where :math:`D_1(u)` is weak or zero. The Fourier transform :math:`F(u)` of
# the true line can be recovered at essentially every :math:`u` by combining
# all the harmonics, weighted toward whichever harmonic carries the most
# information at that :math:`u`:
#
# .. math::
#
#     F(u) = \frac{\sum_n D_n^*(u)\, S_n(u)}{\sum_n |D_n(u)|^2}\, \mathrm{LPF}(u)
#
# Inverse Fourier transformation gives back the reconstructed 1st-derivative
# spectrum :math:`f(B)`. In SpinLab this is what
# :func:`~spinlab.processing.harmonics.reconstruct_harmonics` computes.

# %%
# How much S/N can be gained?
# ---------------------------
# The obvious question, does this actually work/help, and does it matter whether
# the optional low-pass filter (``LPF(u)`` above, controlled by the
# ``cutoff``/``filter_width`` arguments) is used is a legitimate quuestion, and the following example does illustrate the case. Here,
# a single Gaussian-derivative line at a modulation ratio
# (:math:`h_m / \Delta B_{pp} \approx 1.25`) with the corresponding first five harmonics is simulated, prior to adding some noise. For this study, we will compare the following scenarios:
#
# 1. the overmodulated 1st harmonic alone (acquisition without MHD),
# 2. the MHD reconstruction with no low-pass filtering,
# 3. the MHD reconstruction with a properly tuned low-pass filter.

from spinlab.math.lineshape import gaussian

rng = np.random.default_rng(0)

B = np.linspace(-20, 20, 1024)
sigma = 1.0  # Gaussian linewidth; DHpp = 2*sigma = 2.0
modulation_amplitude = 2.5  # modulation ratio hm/DHpp = 1.25
n_harmonics = 5
noise_std = 0.007

absorption_data = sl.SpinData(gaussian(B, x0=0, sigma=sigma, integral=1.0), ["B0"], [B])

harmonics = np.zeros((len(B), n_harmonics), dtype=complex)
for n in range(1, n_harmonics + 1):
    harmonic_n = sl.pseudo_modulation(
        absorption_data, modulation_amplitude=modulation_amplitude, order=n
    ).values
    harmonics[:, n - 1] = harmonic_n + rng.normal(0, noise_std, len(B))

data = sl.SpinData(harmonics, ["B0", "harmonic"], [B, np.arange(1, n_harmonics + 1)])


def snr(y, signal_range=(-4, 4), noise_range=(10, 20)):
    signal_mask = (B >= signal_range[0]) & (B <= signal_range[1])
    noise_mask = (np.abs(B) >= noise_range[0]) & (np.abs(B) <= noise_range[1])
    peak_to_peak = y[signal_mask].max() - y[signal_mask].min()
    noise = y[noise_mask].std()
    return peak_to_peak / noise


s1 = data.values[:, 0].real
f_unfiltered = sl.reconstruct_harmonics(data, modulation_amplitude).values.real
f_filtered = sl.reconstruct_harmonics(
    data, modulation_amplitude, cutoff=2.0, filter_width=0.25
).values.real

snr_s1 = snr(s1)
snr_unfiltered = snr(f_unfiltered)
snr_filtered = snr(f_filtered)

print(f"S/N, raw 1st harmonic:            {snr_s1:.1f}")
print(f"S/N, MHD reconstruction, no LPF:   {snr_unfiltered:.1f}")
print(f"S/N, MHD reconstruction, with LPF: {snr_filtered:.1f}")

# %%
# In this example, the 1st harmonic (no MHD) alone gives a S/N ~20. Reconstructing
# from all 5 harmonics *without* a low-pass filter is actually **worse**
# (S/N ~5) -- combining harmonics also combines their noise, and at high
# :math:`u` every :math:`D_n(u)` is small, so noise gets amplified on
# division. Only once a low-pass filter suppresses that poorly-conditioned
# high-:math:`u` region does the reconstruction pay off, reaching S/N ~69 here
# -- roughly a **3.5x improvement** over conventional single-harmonic detection,
# with a linewidth close to that of the raw 1st harmonic itself. Pushing
# ``cutoff`` higher narrows the reconstructed line further, toward the true
# (unbroadened) linewidth, but at a steep cost in S/N -- see
# :ref:`MHD_ParameterOptimization` for that tradeoff quantified directly.
#
# The takeaway: the S/N gain from MHD is not automatic. It comes from
# *properly filtered* reconstruction; an unfiltered reconstruction can be
# worse than just using the 1st harmonic. Choosing ``cutoff``/``filter_width``
# well matters as much as acquiring the extra harmonics in the first place --
# see the :ref:`MHD_ParameterOptimization` tutorial for how to tune these parameters
# systematically.

sl.plt.figure(figsize=(7, 8))
sl.plt.subplot(3, 1, 1)
sl.plt.plot(B, s1)
sl.plt.title(f"1st harmonic (S/N = {snr_s1:.1f})")
sl.plt.subplot(3, 1, 2)
sl.plt.plot(B, s1, color=sl.colors.secondary2, label="s$_1$(B), raw 1st harmonic")
sl.plt.plot(B, f_unfiltered, label="MHD reconstruction, no filter")
sl.plt.legend()
sl.plt.title(f"MHD reconstruction, no filter (S/N = {snr_unfiltered:.1f})")
sl.plt.subplot(3, 1, 3)
sl.plt.plot(
    B, s1 / np.max(np.abs(s1)), color=sl.colors.secondary2, label="s$_1$(B), raw 1st harmonic"
)
sl.plt.plot(B, f_filtered / np.max(np.abs(f_filtered)), label="MHD reconstruction, filtered")
sl.plt.legend()
sl.plt.title(f"MHD reconstruction, filtered (normalized) (S/N = {snr_filtered:.1f})")
sl.plt.xlabel("B0")
sl.plt.tight_layout()
sl.plt.show()

# %%
# Continue to :ref:`MHD_Simulation` for a full worked example on a simulated
# two-line spectrum.
