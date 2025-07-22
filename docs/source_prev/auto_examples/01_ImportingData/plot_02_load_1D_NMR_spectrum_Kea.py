# %%
"""
.. _plot_02_load_1D_NMR_spectrum_Kea:

=====================================
Load two 1D NMR spectra in Kea format
=====================================

In this example we demonstrate how to import two ODNP-enhanced NMR spectra, one recorded with a microwave power of 0 W (off-signal) and one with a microwave power of 2 W (on-signal). The spectra are recorded using a Magritek Kea system.

The example script has three different sections:

#. Load and Process Off-Signal
#. Load and Process On-Signal
#. Create a Figure and Plot On/Off Spectra

"""
# %%
# Make sure to start with importing SpinLab
import spinlab as sl

# %%
# Load and Process Off-Signal
# -----------------------------
# The next section demonstrates how the FID is imported into SpinLab and processed. Processing involves removing any DC offset, followed by a 15 Hz linewidth apodization, prior to performing the Fourier transformation.

########## OFF Signal (P = 0 W) ##########
data_off = sl.load("../../data/prospa/10mM_TEMPO_Water/1Pulse_20200929/35/data.1d")

data_off = sl.remove_background(data_off)
data_off = sl.apodize(data_off, lw=15)
data_off = sl.fourier_transform(data_off)

# %%
# Load and Process ON-Signal
# ----------------------------
# Importing the on-signal involves the same steps as importing the off-signal. Once processed the data is copied to the results buffer 'onSignal'.

########## ON Signal (P = 2 W) ##########
data_on = sl.load("../../data/prospa/10mM_TEMPO_Water/1Pulse_20200929/51/data.1d")

data_on = sl.remove_background(data_on)
data_on = sl.apodize(data_on, lw=15)
data_on = sl.fourier_transform(data_on)

# %%
# Plot Microwave On/Off Spin Spectra
# ---------------------------------
# First plot spectra individually

sampleTag = "10 mM TEMPO in Water"

sl.plt.figure()
sl.fancy_plot(data_on, title=sampleTag + ", MW On Spectrum")

sl.plt.figure()
sl.fancy_plot(data_off, title=sampleTag + ", MW Off Spectrum")
sl.plt.show()

# %%
# Next plot both spectra in the same figure

sl.plt.figure()
sl.fancy_plot(data_on, xlim=[-20, 20])
sl.fancy_plot(data_off * 50, xlim=[-20, 20])
sl.plt.title(sampleTag + ", MW ON/OFF(*50)")
sl.plt.tight_layout()
sl.plt.show()
