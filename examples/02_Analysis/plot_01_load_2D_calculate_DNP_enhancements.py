# %%
"""
.. _plot_01_load_2D_calculate_Spin_enhancements:

===================================================
Load a 2D sldata object and calculate enhancements
===================================================

This example demonstrates how to import Spin-NMR data in form of a 2D sldata object from an hdf5 file, calculate the Spin enhancement factors and plot the enhancement vs. the applied microwave power. This example uses the 2D data object that was created in a previous tutorial (:ref:`plot_04_create_sldata_object_from_individual_files`). The sample is 10 mM TEMPO in Toluene measured at 14.5MHz (X-Band ODNP spectroscopy).

"""
# %%
# Load NMR Spectra
# ----------------
# In this example, we will calculate the Spin enhancement factor for each individual Spin spectrum and create a figure showing the Spin enhancement versus the applied microwave power. For this, we will import the 2D sldata object created in the previous sample. If you are not yet familiar with how to concatenate individual spectra into the 2D sldata object, check out this tutorial: :ref:`plot_04_create_sldata_object_from_individual_files`.
#
# First, load the 2D spinlab data object:

import spinlab as sl
from spinlab.processing.integration import integrate

sampleTag = "10 mM TEMPO in Toluene"
file_name_path = "../../data/h5/PowerBuildUp.h5"
data = sl.load(file_name_path)

# %%
# Calculate Spin Enhancement Factors
# ---------------------------------
# SpinLab provides a convenient way to calculate the Spin enhancement factors by using the ``calculate_enhancement`` function. Enhancement factors are calculated using integrals. Integrals can be calculated over the entire spectrum, multiple regions, or can be just a single point. However, without calculating integrals first, the ``calculate_enhancement`` function will return an error.

integrals = sl.integrate(data)
enhancements = sl.calculate_enhancement(integrals)

# %%
# In this case, the integral is calculated over the entire spectrum followed by calculating the enhancement factors.

# %%
# .. note::
#     The default behavior of the ``calculate_enhancement`` function is to use the first spectrum as the Off signal. If this is the case, the argument ``off_spectrum`` is not necessary. If you want to specify a particular spectrum that contains the off signal, use the ``off_spectrum`` argument.

# #     The ``calculate_enhancement``` function can also calculate the enhancement for specific regions of the spectrum. THis behavior will be discussed in the next example (:ref:`07_align_nmr_spectra`).


# %%
# Plot Enhancement Data
# ---------------------
# Finally, we can plot the enhancement data versus the microwave power.

sl.fancy_plot(enhancements, title=sampleTag + ", ODNP Enhancements")
sl.plt.show()
