"""Module which provides functions to analyze relaxation measurements"""

import numpy as _np
from ..fitting import fit
from ..math import *


def inversion_recovery_fit(integrals):
    """Fit an inversion recovery experiment to extract the longitudinal relaxation time T1.

    Fits the real part of the integrated signal intensities to the inversion
    recovery function :func:`spinlab.math.relaxation.t1` using an automatically
    estimated initial guess.

    Args:
        integrals (SpinData): Integrated signal intensities as a function of
            the inversion recovery delay time. The data object must have a
            dimension labeled ``"t1"``.

    Returns:
        dict: Fit results dictionary containing the fitted curve, optimal
            parameters, and fit errors (see :func:`spinlab.fitting.fit`).

    .. note::
        This function is currently under development. Results are printed to
        the console but not yet returned in a structured format.
    """
    # Estimate an initial guess from experimental data

    initial_guess = (2.0, -4000, 4000)

    fit_results = fit(relaxation.t1, integrals.real, dim="t1", p0=initial_guess)

    # fit returns dictionary with results

    print(fit_results)

    # print(fit_results['fit'])

    # fit = out['fit']
    # popt = out['popt']
    # err = out['err']

    # T1 = popt['popt',0]
    # M_0 = popt['popt',1]
    # M_inf = popt['popt',2]

    # return out
