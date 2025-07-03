# %%
"""
.. _plot_03_load_EPR_Spectrum_Bruker:

======================================
Load EPR spectrum in Bruker EMX format
======================================

In this example we demonstrate how to load and EPR spectrum and process the data.

"""
# %%
# Load EPR Data
# -------------
# First, add SpinLab to the Python environment,

import spinlab as sl

# %%
# and then import an EPR spectrum. SpinLab can handle spectra recorded on different spectrometers such as the Bruker ElexSys, the Bruker EMX system, or home-built spectrometers running on Boris Epel's software SpecMan4EPR. In this example we will load a spectrum from a Bruker EMX system.

data = sl.load("../../data/bes3t/1D_CW.DTA")

# %%
# Process EPR Data
# ----------------
# In this section, we will demonstrate some basic EPR processing.

# %%
# First, let's perform a baseline correction using a zeroth order polynomial to remove a DC offset:
data_proc = sl.remove_background(data, dim="B0")

# %%
# Here a new slData object is created containing the corrected data. This is helpful, if the processing for different data sets need to be compared. The remove_background function will calculate a zero order polynomial background and will subtract this value from the data. To plot the corrected spectrum simply use:

sl.fancy_plot(data_proc, xlim=[344, 354], title="EPR Spectrum")

# %%
# The ''fancy_plot'' function is very helpful to create simple plots. For more complicated figures the matplotlib functions can be used. Note, that the plotting functions of the matplotlib package are already loaded into the SpinLab environment.

sl.plt.figure()
sl.plt.plot(data.coords["B0"], data.values.real, label="No Background Correction")
sl.plt.plot(
    data_proc.coords["B0"], data_proc.values.real, label="Background Correction"
)
sl.plt.xlabel("Magnetic Field (mT)")
sl.plt.ylabel("EPR Signal Intensity (a.u.)")
sl.plt.grid(True)
sl.plt.tight_layout()
sl.plt.legend()
sl.plt.show()

# %%
# Note the DC offset of about -0.5.

# %%
# Show EPR Attributes
# -------------------
# To show a list of attributes with the EPR spectrum

sl.fancy_plot(data_proc, xlim=[344, 354], title="EPR Spectrum", showPar=True)
sl.plt.show()
