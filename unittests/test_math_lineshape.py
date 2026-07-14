import unittest

import numpy as np
import spinlab as sl
from numpy.testing import assert_allclose
from scipy.special import wofz

from spinlab.math import lineshape


class sl_lineshape_tester(unittest.TestCase):
    def setUp(self):
        self.x = np.linspace(-5.0, 5.0, 1001)

    def test_gaussian_formula(self):
        x0 = 0.5
        sigma = 0.8
        integral = 2.0
        expected = (
            integral
            / (sigma * np.sqrt(2.0 * sl.pi))
            * np.exp(-((self.x - x0) ** 2) / (2.0 * sigma**2))
        )

        assert_allclose(
            lineshape.gaussian(self.x, x0=x0, sigma=sigma, integral=integral),
            expected,
        )

    def test_gaussian_accepts_list_and_scales_integral(self):
        x = [-1.0, 0.0, 1.0]

        out = lineshape.gaussian(x, x0=0.0, sigma=1.0, integral=2.0)
        reference = lineshape.gaussian(np.array(x), x0=0.0, sigma=1.0, integral=1.0)

        self.assertEqual(out.shape, (3,))
        assert_allclose(out, 2.0 * reference)

    def test_lorentzian_formula(self):
        x0 = -0.3
        gamma = 0.7
        integral = 1.5
        expected = (
            integral
            * (1.0 / (sl.pi * gamma))
            * gamma**2
            / ((self.x - x0) ** 2 + gamma**2)
        )

        assert_allclose(
            lineshape.lorentzian(self.x, x0=x0, gamma=gamma, integral=integral),
            expected,
        )

    def test_lorentzian_derivative_formula_and_numeric_flag(self):
        x0 = 0.2
        gamma = 0.5
        integral = 1.25
        expected = (
            integral
            * (-1.0 / (sl.pi * gamma))
            * gamma**2
            / ((self.x - x0) ** 2 + gamma**2) ** 2
            * 2.0
            * (self.x - x0)
        )

        assert_allclose(
            lineshape.lorentzian(
                self.x, x0=x0, gamma=gamma, integral=integral, deriv=True
            ),
            expected,
        )
        assert_allclose(
            lineshape.lorentzian(
                self.x, x0=x0, gamma=gamma, integral=integral, deriv=1
            ),
            expected,
        )

    def test_lorentzian_accepts_list(self):
        out = lineshape.lorentzian([-1.0, 0.0, 1.0], x0=0.0, gamma=1.0)

        self.assertEqual(out.shape, (3,))
        self.assertGreater(out[1], out[0])

    def test_voigtian_formula(self):
        x0 = 0.4
        sigma = 0.8
        gamma = 0.3
        integral = 1.7
        z = ((x0 - self.x) + 1j * gamma) / (sigma * np.sqrt(2.0))
        expected = integral * np.real(wofz(z)) / (sigma * np.sqrt(2.0 * sl.pi))

        assert_allclose(
            lineshape.voigtian(
                self.x, x0=x0, sigma=sigma, gamma=gamma, integral=integral
            ),
            expected,
        )

    def test_voigtian_derivative_formula_and_numeric_flag(self):
        x0 = -0.25
        sigma = 0.9
        gamma = 0.2
        integral = 0.75
        z = ((self.x - x0) + 1j * gamma) / (sigma * np.sqrt(2.0))
        xc = self.x - x0
        expected = (
            integral
            / sigma**3
            / np.sqrt(2.0 * sl.pi)
            * (gamma * np.imag(wofz(z)) - xc * np.real(wofz(z)))
        )

        assert_allclose(
            lineshape.voigtian(
                self.x,
                x0=x0,
                sigma=sigma,
                gamma=gamma,
                integral=integral,
                deriv=True,
            ),
            expected,
        )
        assert_allclose(
            lineshape.voigtian(
                self.x,
                x0=x0,
                sigma=sigma,
                gamma=gamma,
                integral=integral,
                deriv=1,
            ),
            expected,
        )

    def test_voigtian_accepts_list(self):
        out = lineshape.voigtian([-1.0, 0.0, 1.0], x0=0.0, sigma=1.0, gamma=0.5)

        self.assertEqual(out.shape, (3,))
        self.assertGreater(out[1], out[0])

    def test_invalid_derivative_flag_raises_value_error(self):
        with self.assertRaises(ValueError):
            lineshape.lorentzian(self.x, x0=0.0, gamma=1.0, deriv="bad")

        with self.assertRaises(ValueError):
            lineshape.voigtian(self.x, x0=0.0, sigma=1.0, gamma=1.0, deriv="bad")

    def test_top_level_lineshape_exports(self):
        self.assertIs(sl.lineshape.gaussian, lineshape.gaussian)
        self.assertIs(sl.lineshape.lorentzian, lineshape.lorentzian)
        self.assertIs(sl.lineshape.voigtian, lineshape.voigtian)


if __name__ == "__main__":
    unittest.main()
