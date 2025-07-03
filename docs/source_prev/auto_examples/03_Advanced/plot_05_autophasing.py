# %%
"""
.. _plot_05_autophasing:

===================================
Using the SpinLab autophase function
===================================

This example demonstrates how to use the SpinLab autophase function on a sldata object.

"""
# %%
# The following example shows how the autophase function can be conveniently used.
# To get started, first, setup the python environment:

import spinlab as sl

# %%
# Let's load some example data
# the data consists of 4 fid that are phase cycled (0-90-180-270)

data = sl.load("../../data/prospa/water_phase_cycled/data.2d")

# %%
# we are interested in the spectra
# and only the arbitrary part from -900 to -100 ppm

data = sl.fourier_transform(data)["f2", (-900.0, -100.0)]

# %%
# we look at the real part of the spectra

data_real = data.real

# %%
# lets plot the spectrum for all 4 cycles

sl.fancy_plot(data_real)

# %%
# clearly the spectra are phase cycled, but we'd like to have them phased all the same
# we can use sl.autophase for that:

data_phased = sl.autophase(data)
sl.fancy_plot(data_phased)
