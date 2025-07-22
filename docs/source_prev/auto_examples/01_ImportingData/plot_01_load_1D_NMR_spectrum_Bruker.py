# %%
"""
.. _plot_01_load_1D_NMR_spectrum_Bruker:

======================================
Load 1D NMR spectrum in TopSpin format
======================================

This example demonstrates how to load and process a single 1D NMR spectrum recorded on a Bruker spectrometer acquired using TopSpin. This examples also demonstrates how to access the various components of the data object and generally how to interact with the functions.

"""
# %%
# First you need to prepare the Python environment by importing SpinLab.

import spinlab as sl
import matplotlib.pylab as plt

# %%
# Load and Process the NMR Spectrum
# ---------------------------------
# In this example we use a 1D NMR spectrum acquired using TopSpin. Example data is located in the data folder. All data enters into the same object structure so this example applies to any NMR format. SpinLab will try to identify the format of the NMR spectrum (e.g. TopSpin, VnmrJ, Kea, etc.). This will work in most cases. If the autodetect fails, the format can be explicitly given using the data_type attribute of the load function (e.g. data_type = "topspin").
# Remove digital filter is a boolean. If true, it will remove group delay in the topspin data.

data = sl.load("../../data/topspin/1", remove_digital_filter=True)
data.attrs["experiment_type"] = "nmr_spectrum"

# %%
# The spectral data is now stored in the data object. SpinLab uses object oriented programming, therefore, data is not just a variable. It is a slData object. Next, we will perform some basic data processing, methods that are pretty standard in NMR spectroscopy. For this just pass the slData object from one function to the next.

data = sl.apodize(data, lw=100)
data = sl.fourier_transform(data)

# %%
# This procedure removes the DC offset, performs an apodization with a window function (100 Hz linewidth), followed by a Fourier transforms. By default a zero filling of factor two is performed prior to Fourier transforming the spectrum.
#
# NMR spectra are typically phase sensitive (complex data) and the final processing step is to phase the spectrum. In SpinLab you can either manually phase correct the spectrum using the 'phase' function and by giving a phase explicitly:

data = sl.phase(data, p0=145, p1=0)
# %%
# Or by using the autophase function to automatically search for and apply the best phase angle (for reference only)

# data = sl.autophase(data, force_positive=True)

# %%
# Plot Processed Data
# -------------------

# %%
# SpinLab automatically takes care of the name of the coordinates. For NMR spectra, the dimensions are named "t2" and "t1" for the direct and indirect dimension of a FID, respectively. After the Fourier Transformation these dimensions will be renamed to "f2" and "f1", respectively. Dimensions can be renamed by the user. However, several features in SpinLab take advantage of the dimension name and processing or plotting functions will change their behavior according to the type of the spectrum.

# %%
# To plot the NMR spectrum simply use the following command. By default, only the real part of the NMR spectrum is shown.

sl.fancy_plot(data)
sl.plt.show()

# %%
# Note, that the SpinLab plotting function will automatically reverse the direction of the x axis, as it is custom for NRM spectra and axis labels are automatically generated

# %%
# The integrated plotting function allows for additional input arguments. For example to only show a portion of the spectrum use the xlim argument. A title can be passed to the function using the title argument. This can also be a variable. For example:

sampleTag = "ODNP Experiment of 10 mM TEMPO in Water"

sl.fancy_plot(data, xlim=[-100, 100], title=sampleTag, showPar=True)
sl.plt.show()

# %%
# Advanced Usage
# --------------
# The slData objects stores many more attributes for the data set, which are loaded automatically when loading the experimental data. For example, the NMR frequency can be easily accessed as follows:

nmr_frequency = data.attrs["nmr_frequency"]
print(nmr_frequency)

# %%
# All variables in SpinLab are stored in SI units. Therefore, the NMR frequency is given in (Hz).
# If needed, access your processed spectrum as follows:

x_axis = data.coords["f2"]  # ppm axis
spectrum = data.values  # spectrum
