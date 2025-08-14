# %%
"""
=================================
Load EPR spectrum (Bruker format)
=================================

In this example we will create a simple processing script to demonstrate how to load an EPR spectrum and perform some very basic data processing.

"""
# %%
# Load EPR Data
# -------------
# To get started we first have to initialize the Python environment by importing the SpinLab package and the PyPlot module of Matplotlib.

import spinlab as sl
import matplotlib.pyplot as plt

# %%
# Next, we will import an EPR spectrum. SpinLab can handle a variety of data formats, such as the Bruker ElexSys, Bruker EMX, SpecMan4EPR, etc. If a data format is not available, the experimental data can still be imported as a text file. To request adding a new data format please head over to the GitHub Issues pages and open an issue.
# For this example we will load a spectrum recorded on a Bruker EMX spectrometer, saved in the bes3t format.

data = sl.load("../data/bes3t/1D_CW.DTA")

# %%
# Note, that now import format is given. SpinLab will automatically detect the data format and will apply the appropriate import routine. Once the data is loaded, SpinLab will create a spinlab data object and will store the object in the variable ``data``.

# %%
# To get a first glimps of the data  you can use the SpinLab function ``fancy_plot`` to plot the data. The function ``fancy_plot`` automatically recognizes the type of the spectrum (EPR, NMR, ...) and creates appropriate axis labels without any further input required. If the data format is not recognized, SpinLab will revert to a simple plot of the data.

plt.figure()
sl.fancy_plot(data)
plt.show()

# %%
# Process EPR Data
# ----------------
# In the next section, we will demonstrate some basic EPR data processing.

# %%
# First, let's perform a baseline correction using the ``remove_backgraound`` function. This will fit a 0th order polynomial to the data along the dimension B0 and will subtract this offset from the data.

data_proc = sl.remove_background(data, dim="B0")

# %%
# Notice how the spindata object ``data`` is the input for the processing function and how the result of the operation is stored in a new spindata object called ``data_proc``. Alternatively, you can also overwrite the existing spindata object. Note, when experimental data is imported into SpinLab and stored as a data object, SpinLab will also import all attributes (meta data) of the spectrum. These are stored in the sub-class ``attrs``. An audit trail of all sub-sequent processing steps is stored in the sub-class ``proc_attrs``. These steps can be displayed using the Python print command:

print(data_proc.proc_attrs)

# %%
# To plot the corrected spectrum simply use:

sl.fancy_plot(data_proc, xlim=[344, 354], title="My EPR Spectrum")
plt.show()

# %%
# To display a figure showing the data before and after process simply add another line to plot the other data set:

sl.fancy_plot(data, xlim=[344, 354])
sl.fancy_plot(data_proc, xlim=[344, 354])
plt.show()

# %%
# The function ''fancy_plot'' is helpful to create simple plots. It automatically recognizes the data type and will create a plot using an appropriate font size and will add commonly used axis labels to the plot. For more complicated figures the matplotlib functions can be used. All plotting functions of the matplotlib pyplot package are already loaded into the SpinLab environment. Below is an example showing how to use matpolotlib commands to create a figure:

sl.plt.figure()
sl.plt.plot(data.coords["B0"], data.values.real, label="No Background Correction")
sl.plt.plot(data_proc.coords["B0"], data_proc.values.real, label="Background Correction")
sl.plt.xlabel("Magnetic Field (mT)")
sl.plt.ylabel("EPR Signal Intensity (a.u.)")
sl.plt.grid(True)
sl.plt.tight_layout()
sl.plt.legend(loc = "lower left")
sl.plt.show()

# %%
# Note that a DC offset of about -0.5 was removed by the ``remove_background`` function.

# %%
# Show EPR Attributes
# -------------------
# To show a list of spectra attributes with the EPR spectrum that were imported from the data set use the flag ``showPar`` and set it to ``True``.

sl.fancy_plot(data_proc, xlim=[344, 354], title="EPR Spectrum", showPar=True)
sl.plt.show()
