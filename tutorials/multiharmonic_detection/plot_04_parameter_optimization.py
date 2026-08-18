"""
.. _MHD_ParameterOptimization:

Multi-Harmonic Detection: Parameter Optimization (#4)
========================================================
"""

# %%
# :func:`~spinlab.processing.harmonics.reconstruct_harmonics` takes two
# optional parameters, ``cutoff`` and ``filter_width``, that control a
# low-pass filter applied in the Fourier-conjugate domain before the inverse
# transform. Earlier tutorials in this series showed that these are not
# optional extras: an unfiltered reconstruction can be *worse* than simply
# using the 1st harmonic, because combining harmonics also combines their
# noise, and noise dominates at high :math:`u` where every :math:`D_n(u)` is
# small.
#
# This tutorial shows how to choose ``cutoff``/``filter_width`` systematically,
# and -- just as importantly -- when no choice of filter can help, because the
# number of available harmonics is fundamentally too small for the
# over-modulation ratio being used.

import numpy as np
import spinlab as sl
from spinlab.math.lineshape import gaussian

# %%
# A hard case: high modulation ratio, few harmonics
# ----------------------------------------------------
# Bruker's Signal Processing Unit (SPU), used to acquire the real data in the
# previous tutorial, provides at most 5 simultaneous harmonics. To see the
# limits of that constraint, this example over-modulates a single Gaussian
# line far more aggressively than the previous tutorials: a modulation ratio
# :math:`h_m / \Delta B_{pp} \approx 10`.

rng = np.random.default_rng(1)

B = np.linspace(-20, 20, 1024)
sigma = 1.0  # DHpp = 2*sigma = 2.0
modulation_amplitude = 20.0  # modulation ratio ~ 10
n_harmonics = 5
noise_std = 0.002

absorption_data = sl.SpinData(gaussian(B, x0=0, sigma=sigma, integral=1.0), ["B0"], [B])

harmonics = np.zeros((len(B), n_harmonics), dtype=complex)
for n in range(1, n_harmonics + 1):
    harmonic_n = sl.pseudo_modulation(
        absorption_data, modulation_amplitude=modulation_amplitude, order=n
    ).values
    harmonics[:, n - 1] = harmonic_n + rng.normal(0, noise_std, len(B))

data = sl.SpinData(harmonics, ["B0", "harmonic"], [B, np.arange(1, n_harmonics + 1)])

# %%
# Grid-scanning cutoff and filter_width
# ----------------------------------------
# Rather than guess, scan a grid of ``cutoff``/``filter_width`` combinations
# and measure both the reconstructed peak-to-peak linewidth and the S/N for
# each.


def measure(y, signal_range=(-6, 6), noise_range=(10, 20)):
    signal_mask = (B >= signal_range[0]) & (B <= signal_range[1])
    noise_mask = (np.abs(B) >= noise_range[0]) & (np.abs(B) <= noise_range[1])
    Bi, yi = B[signal_mask], y[signal_mask]
    dhpp = abs(Bi[np.argmin(yi)] - Bi[np.argmax(yi)])
    peak_to_peak = yi.max() - yi.min()
    noise = y[noise_mask].std()
    return dhpp, peak_to_peak / noise


cutoffs = np.arange(0.1, 3.05, 0.1)
widths = np.arange(0.02, 1.0, 0.02)

snr_grid = np.zeros((len(cutoffs), len(widths)))
for i, cutoff in enumerate(cutoffs):
    for j, width in enumerate(widths):
        f = sl.reconstruct_harmonics(data, modulation_amplitude, cutoff=cutoff, filter_width=width)
        _, snr_grid[i, j] = measure(f.values.real)

best_i, best_j = np.unravel_index(np.argmax(snr_grid), snr_grid.shape)
best_cutoff, best_width = cutoffs[best_i], widths[best_j]
print(f"best S/N = {snr_grid[best_i, best_j]:.2f} at cutoff={best_cutoff:.2f}, filter_width={best_width:.2f}")

sl.plt.figure()
sl.plt.pcolormesh(widths, cutoffs, snr_grid, shading="auto")
sl.plt.colorbar(label="S/N")
sl.plt.plot(best_width, best_cutoff, "r*", markersize=15)
sl.plt.xlabel("filter_width")
sl.plt.ylabel("cutoff")
sl.plt.title("S/N vs. filter parameters")
sl.plt.tight_layout()
sl.plt.show()

# %%
# There is a well-defined optimum, not a flat or noisy landscape -- a good
# sign that the reconstruction responds predictably to the filter, rather
# than the "best" point being a numerical fluke.

# %%
# The resolution floor
# ------------------------
# Does the *best* S/N also give back the true, narrow linewidth? Sweep
# ``cutoff`` (at a fixed, proportional ``filter_width``) and track both the
# reconstructed linewidth and the S/N.

sweep_cutoffs = np.arange(0.1, 3.01, 0.05)
dhpps, snrs = [], []
for cutoff in sweep_cutoffs:
    f = sl.reconstruct_harmonics(
        data, modulation_amplitude, cutoff=cutoff, filter_width=max(0.3 * cutoff, 0.02)
    )
    dhpp, snr = measure(f.values.real)
    dhpps.append(dhpp)
    snrs.append(snr)

true_dhpp = 2 * sigma

fig, ax1 = sl.plt.subplots()
ax1.plot(sweep_cutoffs, dhpps, "C0-", label="reconstructed DHpp")
ax1.axhline(true_dhpp, color="C0", linestyle="--", alpha=0.6, label="true DHpp")
ax1.set_xlabel("cutoff")
ax1.set_ylabel("peak-to-peak linewidth", color="C0")
ax1.tick_params(axis="y", labelcolor="C0")
ax2 = ax1.twinx()
ax2.plot(sweep_cutoffs, snrs, "C3-", label="S/N")
ax2.set_ylabel("S/N", color="C3")
ax2.tick_params(axis="y", labelcolor="C3")
ax1.legend(loc="upper right")
sl.plt.title("Resolution vs. S/N tradeoff")
sl.plt.tight_layout()
sl.plt.show()

# %%
# As ``cutoff`` increases, the reconstructed linewidth shrinks toward the
# true value, but S/N eventually collapses from noise amplification -- and
# even at the largest cutoffs tried here, the linewidth never quite reaches
# the true value. This is not a failure of filter tuning: it is a hard limit
# set by how many harmonics were used.
#
# Each harmonic's filter :math:`D_n(u)` only carries real information about
# the spectrum out to about :math:`u \sim 2n/h_m` (see the filter plot in
# :ref:`MHD_Overview`). With :math:`N_H` harmonics available, the total
# reconstructable bandwidth is capped at
#
# .. math::
#
#     u_{max} \sim \frac{2 N_H}{h_m}
#
# which sets a floor on the narrowest linewidth that can be recovered,
# roughly :math:`\Delta B_{min} \sim 1/u_{max} = h_m / (2 N_H)`. No amount of
# filter tuning can beat this -- beyond :math:`u_{max}` there simply is no
# information left, only noise.

u_max = 2 * n_harmonics / modulation_amplitude
predicted_floor = 1 / u_max
print(f"predicted resolution floor: {predicted_floor:.2f} (true DHpp = {true_dhpp:.2f})")

# %%
# Here the predicted floor is comparable to the true linewidth itself --
# this modulation ratio asks 5 harmonics to resolve a line sitting right at
# the edge of what they can represent. Yu et al. (2015, Table 2) found that a
# modulation ratio of 10 needed roughly **45** harmonics for reliable
# reconstruction of a similarly narrow line; 5 is not enough.
#
# Practical guidance
# ----------------------
# * If you need the true, narrow lineshape recovered with good S/N, use a
#   *lower* modulation ratio (:math:`h_m/\Delta B_{pp} \lesssim 1\text{-}2`)
#   -- see :ref:`MHD_Simulation` for an example where 5 harmonics is plenty.
# * If you must keep a large modulation amplitude (e.g. for a broad
#   co-existing line), accept a broadened but higher-S/N reconstruction, and
#   pick ``cutoff``/``filter_width`` from a grid scan like the one above.
# * If you need both a large modulation amplitude *and* full resolution, you
#   need more harmonics than a 5-channel hardware detector provides -- e.g.
#   by digitizing the raw transient signal and demodulating many harmonics in
#   software, as in Yu et al. (2015).
