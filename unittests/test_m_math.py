import unittest
import spinlab as sl
import numpy as np


# FIX -> Should only use Fit functions, not import or processing functions
class slMath_windowTester(unittest.TestCase):
    def setUp(self):
        self.dim = "x"
        self.x = np.r_[-1:1:100j]
        self.y = sl.lineshape.gaussian(self.x, 0, 0.1)
        self.p0 = (0, 1)
        self.data = sl.SpinData(self.y, [self.dim], [self.x])

    def test_001_windows(self):
        # exponential
        x = np.linspace(-1, 1, 50)
        z = sl.window.exponential(x, 1)
        self.assertTrue(np.isclose(z[0], 1))
        self.assertTrue(z[-1] < 1)

        # gaussian
        y = np.array([-1, 0, 1])
        z = sl.window.gaussian(y, 1)
        self.assertTrue(z[0] < 1)
        self.assertTrue(z[1] == 1)
        self.assertTrue(z[-1] < 1)
