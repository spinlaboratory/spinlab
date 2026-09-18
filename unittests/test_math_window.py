import logging
import unittest

import numpy as np
import spinlab as sl
from numpy.testing import assert_allclose

from spinlab.math import window


# logging.basicConfig(filename='window_debug.log', encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)


class sl_window_tester(unittest.TestCase):
    def setUp(self):
        self.x = np.linspace(0.0, 1.0, 8)

    def test_exponential_formula(self):
        lw = 2.0
        expected = np.exp(-sl.pi * (self.x - self.x[0]) * lw)

        assert_allclose(window.exponential(self.x, lw=lw), expected)

    def test_exponential_accepts_list(self):
        out = window.exponential([0.0, 0.5, 1.0], lw=1.0)
        expected = np.exp(-sl.pi * np.array([0.0, 0.5, 1.0]))

        assert_allclose(out, expected)

    def test_gaussian_formula(self):
        x = np.array([-1.0, 0.0, 1.0])
        lw = 1.0
        sigma = lw / (2.0 * np.sqrt(2.0 * np.log(2.0)))
        expected = np.exp(-1 * 2.0 * sl.pi**2.0 * (x**2.0) * (sigma**2.0))

        assert_allclose(window.gaussian(x, lw=lw), expected)

    def test_gaussian_accepts_list(self):
        out = window.gaussian([-1.0, 0.0, 1.0], lw=1.0)

        self.assertEqual(out.shape, (3,))
        self.assertEqual(out[1], 1.0)

    def test_hann_formula_and_int_input(self):
        N = 8
        expected = 0.5 + 0.5 * np.cos(sl.pi * np.arange(N) / (N - 1))

        assert_allclose(window.hann(N), expected)
        assert_allclose(window.hann(self.x), expected)

    def test_hamming_formula_and_int_input(self):
        N = 8
        expected = 0.53836 + 0.46164 * np.cos(sl.pi * np.arange(N) / (N - 1))

        assert_allclose(window.hamming(N), expected)
        assert_allclose(window.hamming(self.x), expected)

    def test_sin2_formula_and_int_input(self):
        N = 8
        expected = np.cos((-0.5 * sl.pi * np.arange(N) / (N - 1)) + sl.pi) ** 2

        assert_allclose(window.sin2(N), expected)
        assert_allclose(window.sin2(self.x), expected)

    def test_traf_formula(self):
        lw = 1.0
        T2 = 1.0 / (sl.pi * lw)
        T = np.max(self.x)
        E = np.exp(-1 * self.x / T2)
        e = np.exp(-1 * (T - self.x) / T2)
        expected = E * (E + e) / (E**2 + e**2)

        assert_allclose(window.traf(self.x, lw=lw), expected)

    def test_traf_accepts_list(self):
        out = window.traf([0.0, 0.5, 1.0], lw=1.0)

        self.assertEqual(out.shape, (3,))

    def test_lorentz_gauss_formula(self):
        lw = 0.1
        gauss_lw = 0.2
        gaussian_max = 0.5
        N = len(self.x)
        expo = sl.pi * self.x * lw
        gaus = 0.6 * sl.pi * gauss_lw * (gaussian_max * (N - 1) - self.x)
        expected = np.exp(expo - gaus**2).reshape(N)

        assert_allclose(
            window.lorentz_gauss(
                self.x, lw=lw, gauss_lw=gauss_lw, gaussian_max=gaussian_max
            ),
            expected,
        )

    def test_lorentz_gauss_accepts_list(self):
        out = window.lorentz_gauss([0.0, 0.5, 1.0], lw=0.1, gauss_lw=0.2)

        self.assertEqual(out.shape, (3,))

    def test_empty_coordinate_raises_value_error(self):
        for func, kwargs in [
            (window.exponential, {"lw": 1.0}),
            (window.gaussian, {"lw": 1.0}),
            (window.traf, {"lw": 1.0}),
            (window.lorentz_gauss, {"lw": 0.1, "gauss_lw": 0.2}),
        ]:
            with self.subTest(func=func.__name__):
                with self.assertRaises(ValueError):
                    func([], **kwargs)

    def test_taper_window_length_must_be_at_least_two(self):
        for func in [window.hann, window.hamming, window.sin2]:
            with self.subTest(func=func.__name__):
                with self.assertRaises(ValueError):
                    func(1)
                with self.assertRaises(ValueError):
                    func([0.0])


if __name__ == "__main__":
    unittest.main()
