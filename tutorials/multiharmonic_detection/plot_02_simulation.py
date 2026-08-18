"""
.. _MHD_Simulation:

Multi-Harmonic Detection: Simulated Spectrum (#2)
===================================================
"""

# %%
# In this tutorial two different spectra are first simulated:
#
# 1. The first harmonic of a two-line spectrum, recorded with a modulation amplitude well below the linewidth. This simulates the case when no MHD is used for dectedion.
# 2. The same two-line spectrum recoreded with a larger modulation amplitude to gain S/N, and to show how :func:`~spinlab.processing.harmonics.reconstruct_harmonics` recovers the undistorted lineshape from the resulting harmonics.
#
# This allows us to check the methodology directly against the regular (no overmodulated spectrum).

# Let's start with importing the required Python modules:

import numpy as np
import spinlab as sl
from spinlab.math.lineshape import gaussian

# %%
# The "conventional" CW EPR spectrum
# ----------------------------------
# Here we simulated two Gaussian lines with different linewidths, close enough to slightly
# overlap. Using a modulation amplitude well below the
# narrowest linewidth (1 G) gives an essentially undistorted 1st-derivative
# spectrum. We will use this spectrum as the reference spectrum.

B_start, B_end, B_npts = 3450, 3550, 1024
B = np.linspace(B_start, B_end, B_npts)

line_B0 = [3496, 3504]
line_lw = [1, 3]
line_amplitude = [1, 5]

sig_clean = np.zeros(B_npts)
for B0_i, lw_i, amplitude_i in zip(line_B0, line_lw, line_amplitude):
    sig_clean += gaussian(B, x0=B0_i, sigma=lw_i, integral=amplitude_i)
sig_clean = sig_clean / np.max(sig_clean)

absorption_data = sl.SpinData(sig_clean, ["B0"], [B])

# %%
# First the absorption spectrum is calculated and noise is added to the higher harmonics.

rng = np.random.default_rng(0)
noise_std = 0.0003

modulation_amplitude_conventional = 0.2  # << 1 G, the narrowest linewidth

conventional = sl.pseudo_modulation(
    absorption_data, modulation_amplitude=modulation_amplitude_conventional, order=1
)
conventional.values = conventional.values + rng.normal(0, noise_std, B_npts)

sl.plt.figure()
sl.plot(conventional)
sl.plt.title("Simulated CW EPR spectrum (not over-modulation)")
sl.plt.tight_layout()
sl.plt.show()

# %%
# Over-modulating for S/N, and calculating the harmonics
# -----------------------------------------------------------
# Suppose the same sample is now measured at a much larger modulation
# amplitude to improve S/N. A conventional, 1st-harmonic-only measurement at
# this amplitude would be badly broadened. Multi-harmonic detection instead
# records several harmonics and reconstructs the undistorted line
# afterward. Harmonics 1 through 5 are calculated here with
# :func:`~spinlab.processing.pseudo_modulation`, one call per harmonic order,
# and stacked along a "harmonic" dimension -- the same layout that
# :func:`~spinlab.processing.harmonics.combine_harmonics` produces when
# importing real multi-harmonic instrument data.

modulation_amplitude = 2  # modulation ratio ~1 relative to the narrow (1 G) line
n_harmonics = 5

harmonics = np.zeros((B_npts, n_harmonics), dtype=complex)
for n in range(1, n_harmonics + 1):
    harmonic_n = sl.pseudo_modulation(
        absorption_data, modulation_amplitude=modulation_amplitude, order=n
    ).values
    harmonics[:, n - 1] = harmonic_n + rng.normal(0, noise_std, B_npts)

data = sl.SpinData(harmonics, ["B0", "harmonic"], [B, np.arange(1, n_harmonics + 1)])

sl.plt.figure()
sl.imshow(np.real(data))
sl.plt.colorbar(label="Intensity")
sl.plt.title("Simulated harmonics")
sl.plt.tight_layout()
sl.plt.show()

# %%
# Most of the intensity is concentrated in the 1st and 2nd harmonics, with
# little left by the 4th or 5th -- a sign that the modulation amplitude here
# is only modestly over-modulating these lines. Broader lines generally
# retain intensity out to higher harmonic order than narrow ones at a given
# modulation amplitude, since the same :math:`h_m` represents a smaller
# over-modulation ratio relative to a larger linewidth.

# %%
# Reconstruct and compare to the conventional spectrum
# -----------------------------------------------------------
# Reconstructing without a low-pass filter first, to see the raw result.

conventional_norm = conventional.values.real / np.max(np.abs(conventional.values.real))

f_unfiltered = sl.reconstruct_harmonics(data, modulation_amplitude)
f_unfiltered_norm = f_unfiltered.values.real / np.max(np.abs(f_unfiltered.values.real))

sl.plt.figure()
sl.plt.plot(B, conventional_norm, label="conventional 1st harmonic (reference)")
sl.plt.plot(B, f_unfiltered_norm, label="reconstructed, no filter")
sl.plt.legend()
sl.plt.title("Reconstruction without a low-pass filter (normalized)")
sl.plt.tight_layout()
sl.plt.show()

# %%
# As in the overview tutorial, the unfiltered reconstruction is dominated by
# amplified noise. Applying a low-pass filter in the Fourier-conjugate domain
# recovers a clean, minimally-broadened lineshape that closely tracks the
# conventional spectrum -- a distortion-free result that a conventional,
# single-harmonic over-modulated measurement could not have produced.

f_filtered = sl.reconstruct_harmonics(data, modulation_amplitude, cutoff=4.0, filter_width=0.1)
f_filtered_norm = f_filtered.values.real / np.max(np.abs(f_filtered.values.real))

sl.plt.figure()
sl.plt.plot(B, conventional_norm, label="conventional 1st harmonic (reference)")
sl.plt.plot(B, f_filtered_norm, label="reconstructed, filtered")
sl.plt.legend()
sl.plt.title("Filtered reconstruction vs. conventional spectrum (normalized)")
sl.plt.tight_layout()
sl.plt.show()

# %%
# Continue to :ref:`MHD_ExperimentalData` to apply the same workflow to real
# instrument data.
