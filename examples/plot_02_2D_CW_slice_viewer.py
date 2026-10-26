"""
.. _slice_viewer_example:

Interactive 2D Data Viewer (#2)
================================
"""

# %%
# This example demonstrates how to use the interactive slice viewer to browse
# through a 2D EPR dataset. The dataset is a 2D CW EPR experiment with 100
# time slices recorded across a 1600-point field sweep.

import spinlab as sl

# %%
# Load the 2D CW EPR dataset. SpinLab automatically detects the BES3T format.

data = sl.load("../data/bes3t/2D_CW.DSC")

print("Dimensions:", data.dims)
print("Shape:     ", data.shape)

# %%
# The ``slice_viewer`` opens an interactive matplotlib figure with a slider
# that lets you step through each time slice along the ``t1`` dimension.
# The EPR spectrum along ``B0`` is displayed for the selected slice.
#
# .. note::
#    The figure below is a static preview. To use the interactive slider,
#    download and run the example script or Jupyter notebook linked at the
#    bottom of this page.

sl.slice_viewer(data, scroll_dim="t1")
