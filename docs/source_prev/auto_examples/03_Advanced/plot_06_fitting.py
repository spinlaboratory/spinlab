# %%
"""
.. _plot_06_fitting:

=============================
Using the SpinLab Fit function
=============================

This example demonstrates how to use the SpinLab fit function on a sldata object.

"""
# %%
# The following example shows how the autophase function can be conveniently used.
# To get started, first, setup the python environment:

import spinlab as sl
import numpy as np

# %%
# Let's generate a test data set with some noise
# the test data is a lorentzian distribution with some noise added

pts = 1024
x = np.r_[-50:50:1j*pts]

np.random.seed(101)

values = sl.math.lineshape.lorentzian(x, 0, 0.5, 1.5)
values += np.random.randn(pts)*0.05

data = sl.SpinData(values, ['f2'], [x])


# %%
# Now we guess the initial parameters of the fit
# we create a spectrum with the initial guess to compare to our test data

init_guess = [0, 0.5, 1.0]

guess_values = sl.math.lineshape.lorentzian(x, *init_guess)

guess = sl.SpinData(guess_values, ['f2'], [x])

# %%
# now we perform the fit
# the output is a dictionary of SpinData objects containting the "fit" and optimal parameters "popt"

out = sl.fit(sl.math.lineshape.lorentzian, data, 'f2', init_guess)
fit = out['fit']
popt = out['popt']

print('Optimal Fit Values')
print(popt.values) # print optimal fitting values


# %%
# Now we plot the data, initial guess and fit

sl.plt.figure('data')
sl.plot(data, label = 'data')
sl.plot(guess, label = 'guess')
sl.plot(fit, label = 'fit')
sl.plt.legend()
sl.plt.show()
