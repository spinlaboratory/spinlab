import unittest
from numpy.testing import assert_allclose, assert_array_equal
import spinlab as sl
import numpy as np


# FIX -> Should only use Fit functions, not import or processing functions
class slFit_tester(unittest.TestCase):
    def setUp(self):
        self.dim = "x"
        self.x = np.r_[-1:1:100j]
        self.y = sl.lineshape.gaussian(self.x, 0, 0.1)
        self.p0 = (0, 1)
        self.data = sl.SpinData(self.y, [self.dim], [self.x])

    def test_fit_function(self):
        out = sl.fit(sl.lineshape.gaussian, self.data, dim=self.dim, p0=self.p0)
        fit = out["fit"]
        print(fit)
        print(fit.coords["x"])

        assert_allclose(self.data.values, fit.values)
        assert_array_equal(self.data.coords["x"], fit.coords["x"])
