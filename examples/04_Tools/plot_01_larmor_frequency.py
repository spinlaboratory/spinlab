# %%
"""
.. _plot_01_larmor_frequency:

=======================================
Calculate/Plot Nuclear Larmor Frequency
=======================================

This example demonstrates how to use the tool to calculate the nuclear Larmor frequency.

"""
# %%
# Get Magnetic Resonance Properties
# =================================
# SpinLab stores a dictionary called ``gmrProperties`` with magnetic resonance properties of all nuclei of the periodic table. The dictionary is modeled after the Matlab function *gmr* written, and implemented by |GMRFunctionMatlab|. For more details see the detailed documentation of the dictionary. The dictionary stores the following parameters:
#
# * Spin Quantum Number
# * Gyromagnetic Ratio (Hz/T)
# * Nuclear Quadrupole Moment (fm^2, 100 barns)
# * Isotope Natural Abundance (%)
# * Relative Sensitivity with Respect to 1H at same B_{0}
#
# (for nuclei with I > 1/2), and some more parameters. This dictionary can be used to provide nuclear properties in any calculation, it is also used by the SpinLab function ``mr_properties``.
#
# To get started, first, setup the python environment:

import spinlab as sl
import matplotlib.pyplot as plt

# %%
# Let's query some of the parameters:

# %%
# **Proton Gyromagnetic Ratio**

print("v_L(1H) = ", sl.mr_properties("1H"), "(Hz/T)")

# %%
# **Nirogen 14N nuclear spin quantum number**

print("I = ", sl.mr_properties("14N", "spin"))

# %%
# **Carbon 13 (13C) natural abundance**

print(sl.mr_properties("13C", "natAbundance"), " %")

# %%
# **Plot Gyromagnetic Ratios for Elements in the Periodic Table**

gmr = [value[1] for value in sl.gmrProperties.values()]

plt.figure()
plt.plot(gmr[1:-1])
plt.xlabel("Index")
plt.ylabel("Gyromagnetic Ratio (10^7r/Ts)")
plt.grid(True)
plt.show()
