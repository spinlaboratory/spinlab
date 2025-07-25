# %%
"""
.. _plot_04_reference_spectra:

==================
Reference  Spectra
==================

This example demonstrates how to reference spectra using Toluene as an example.
"""
# %%
# Load Toluene Spectra
# -------------------------------
# Start with importing data and creating the SpinLab workspace.
# The data has been processed and saved in .h5 file.

import numpy as np
import spinlab as sl

sampleTag = "10 mM TEMPO in Toluene"
file_name_path = "../../data/prospa/toluene_10mM_Tempone/42"
data = sl.load(file_name_path)

data.attrs["experiment_type"] = "nmr_spectrum"
data = sl.apodize(data, lw=10)
data = sl.fourier_transform(data)

# %%
# Plot Toluene Spectra
# --------------------
# Once the data are imported and processed, it is time to plot the 1D spectra.

sl.fancy_plot(data, xlim=[-20, 20], title=sampleTag)
sl.plt.show()


# %%
# Find Toluene Peaks
# ------------------
# In the previous example, we have demonstrated how to find peaks. Now, we apply the SpinLab function *find_peaks* to get a SpinData object of all peaks. 


peaks = sl.find_peaks(data)
sl.peak_info(peaks)

# %%
# Reference Proton Peak
# ---------------------
# We can see that chemical shift for proton peak is roughly at 2.79 ppm. 
# Let's reference this peak to 7.70 ppm applying the SpinLab function *reference*.

data = sl.reference(data, old_ref = 2.79, new_ref = 7.70)

# We can plot the spectra after reference.
sl.fancy_plot(data, xlim=[-10, 30], title=sampleTag)
sl.plt.show()

# %%
# Check the Proton Peak
# ---------------------
# After we referenced the peaks, we can apply *find_peaks* functions again to get a SpinData object of all peaks. 

peaks = sl.find_peaks(data)
sl.peak_info(peaks)
