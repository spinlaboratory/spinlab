"""
Echo Transient with Phase Cycle(#6)
===================================
"""

# %%
# This example demonstrates how to load and plot an echo transient (time trace) of a stimulated echo using a 64-step phase cycle to remove all unwanted echoes.

import spinlab as sl
import numpy as np

# %%
# Once the Python environment is properly set up the data files can be loaded.

data_E580 = sl.load("../data/EPR/Echo-Transient-Phase-Cycling/33726-ETPC.DTA")
data_E580.attrs["experiment_type"] = "epr_transient_E580"

# %%
# E580: BDPA/PS
# -------------

sl.plt.figure()
sl.fancy_plot(data_E580)
sl.plt.title("Two-Pulse ESEEM, BDPA/PS, E580, X-Band")
sl.plt.show()

# %%
# The data set can be downloaded from the  :ref:`SampleData` page.
