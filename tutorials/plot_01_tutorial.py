
"""
Tutorial Spectrum
=================

This example demonstrates how to load and plot an Echo-Detected Field-Sweep (EDFS) spectrum.

"""
# %%
# First the Python environment needs to be prepared by importing the SpinLab Python package.

import spinlab as sl
import numpy as np

# %%
# Next load the spectrum and plot it

data = sl.load("../data/EPR/Echo-Detected Field-Sweep/17478-EDFS.exp")

sl.plt.figure()
sl.fancy_plot(data)
sl.plt.show()


