"""
.. _MHD_ExperimentalData:

Multi-Harmonic Detection: Experimental Data (#3)
====================================================
"""

# %%
# This tutorial applies the workflow from :ref:`MHD_Simulation` to a series of
# real BDPA measurements recorded on a Bruker E580 with a Signal Processing
# Unit (SPU) providing 5 simultaneous in-phase harmonics, at modulation
# amplitudes from 0.5 G (minimal over-modulation, used as the reference) up
# to about 20 G (strongly over-modulated).

import numpy as np
import spinlab as sl

# %%
# The reference spectrum
# --------------------------
# 0.5 G is well below the BDPA linewidth, so this 1st-harmonic-only
# measurement is an essentially undistorted reference for everything that
# follows.

reference = sl.load("../../data/EPR/Multi-Harmonic Detection/004_BDPA_0.5MA_1st.DTA")

sl.plt.figure()
sl.plot(reference)
sl.plt.title("Reference spectrum (h$_m$ = 0.5 G, 1st harmonic only)")
sl.plt.tight_layout()
sl.plt.show()

# %%
# Loading the over-modulated harmonics
# ------------------------------------------
# These files record only in-phase (0 deg) harmonics -- 5 real traces, no
# 90 deg channel. :func:`~spinlab.processing.harmonics.label_harmonics`
# relabels the trace dimension as harmonic order (there is nothing to pair
# into complex values here, unlike the dual-phase data used in earlier
# tutorials).

files = {
    5.0: "007_BDPA_5MA_5harm.DTA",
    10.0: "008_BDPA_10MA_5harm.DTA",
    15.0: "009_BDPA_15MA_5harm.DTA",
    19.79: "010_BDPA_20MA_5harm.DTA",
}

harmonics = {}
for modulation_amplitude_G, filename in files.items():
    data = sl.load(f"../../data/EPR/Multi-Harmonic Detection/{filename}")
    harmonics[modulation_amplitude_G] = sl.label_harmonics(data)

print(harmonics[5.0])

# %%
# Raw harmonics, no reconstruction
# --------------------------------------
# Before doing any MHD processing, a 2x2 grid of the raw harmonic data
# (field vs. harmonic order) for all four modulation amplitudes shows how
# over-modulation both broadens and shifts intensity across harmonics as
# h$_m$ increases.

sl.plt.figure(figsize=(9, 7))
for i, modulation_amplitude_G in enumerate(files, start=1):
    sl.plt.subplot(2, 2, i)
    sl.imshow(harmonics[modulation_amplitude_G])
    sl.plt.title(f"h$_m$ = {modulation_amplitude_G} G")
    sl.plt.colorbar()
sl.plt.tight_layout()
sl.plt.show()

# %%
# Finding optimum reconstruction parameters
# -----------------------------------------------
# For each modulation amplitude, ``cutoff``/``filter_width`` are grid-scanned
# to maximize S/N, following the same approach as
# :ref:`MHD_ParameterOptimization`.

B = reference.coords["B0"]


def snr(values, signal_range=(349.0, 353.0), noise_range_low=348.0, noise_range_high=354.0):
    signal_mask = (B >= signal_range[0]) & (B <= signal_range[1])
    noise_mask = (B < noise_range_low) | (B > noise_range_high)
    peak_to_peak = values[signal_mask].max() - values[signal_mask].min()
    noise = values[noise_mask].std()
    return peak_to_peak / noise


def optimize_filter(data, modulation_amplitude, cutoffs, widths):
    best_snr, best_cutoff, best_width = 0, None, None
    for cutoff in cutoffs:
        for width in widths:
            f = sl.reconstruct_harmonics(data, modulation_amplitude, cutoff=cutoff, filter_width=width)
            s = snr(f.values.real)
            if s > best_snr:
                best_snr, best_cutoff, best_width = s, cutoff, width
    return best_cutoff, best_width, best_snr


cutoffs = np.arange(0.5, 20.01, 0.5)
widths = np.arange(0.25, 4.01, 0.25)

reconstructed = {}
best_params = {}
for modulation_amplitude_G in files:
    modulation_amplitude_mT = modulation_amplitude_G / 10  # G -> mT, matches B0 axis
    cutoff, width, _ = optimize_filter(
        harmonics[modulation_amplitude_G], modulation_amplitude_mT, cutoffs, widths
    )
    best_params[modulation_amplitude_G] = (cutoff, width)
    reconstructed[modulation_amplitude_G] = sl.reconstruct_harmonics(
        harmonics[modulation_amplitude_G], modulation_amplitude_mT, cutoff=cutoff, filter_width=width
    )
    print(f"h_m = {modulation_amplitude_G:5.2f} G: best cutoff={cutoff}, filter_width={width}")

# %%
# Reconstructed spectra vs. the reference
# -----------------------------------------------

sl.plt.figure(figsize=(9, 7))
for i, modulation_amplitude_G in enumerate(files, start=1):
    sl.plt.subplot(2, 2, i)
    sl.plt.plot(B, reference.values, color=sl.colors.secondary2, label="reference (0.5 G)")
    sl.plot(reconstructed[modulation_amplitude_G], label="reconstructed")
    sl.plt.legend()
    sl.plt.title(f"h$_m$ = {modulation_amplitude_G} G")
sl.plt.tight_layout()
sl.plt.show()

# %%
# Signal-to-noise gain
# ------------------------
# Comparing each reconstruction's S/N against both the reference spectrum
# and the raw (unreconstructed) 1st harmonic at the same modulation
# amplitude.

snr_reference = snr(reference.values)
print(f"S/N, reference (h_m = 0.5 G):  {snr_reference:.0f}")
print()

for modulation_amplitude_G in files:
    snr_raw = snr(harmonics[modulation_amplitude_G].values[:, 0])
    snr_recon = snr(reconstructed[modulation_amplitude_G].values.real)
    print(
        f"h_m = {modulation_amplitude_G:5.2f} G:  "
        f"raw s1 S/N = {snr_raw:6.0f}  |  "
        f"reconstructed S/N = {snr_recon:6.0f}  |  "
        f"gain vs. reference = {snr_recon / snr_reference:.2f}x  |  "
        f"gain vs. raw s1 = {snr_recon / snr_raw:.2f}x"
    )

# %%
# Reconstruction improves S/N by roughly 4-10x over the reference spectrum,
# and 3-5x over simply using the raw over-modulated 1st harmonic, across the
# entire range of modulation amplitudes tested. The gain is largest at the
# lower end (5-10 G) and decreases at 15-20 G, consistent with
# :ref:`MHD_ParameterOptimization`: as the modulation ratio grows, 5
# harmonics increasingly cannot fully resolve the line, so more of the
# reconstruction's improvement goes toward the resolution floor rather than
# S/N. Even so, at every modulation amplitude tested here, multi-harmonic
# reconstruction is a clear improvement over both the reference measurement
# and the raw over-modulated 1st harmonic.
