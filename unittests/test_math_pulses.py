import tempfile
import unittest
from pathlib import Path

import numpy as np
import spinlab as sl
from numpy.testing import assert_allclose, assert_array_equal

from spinlab.math import pulses


class sl_pulses_tester(unittest.TestCase):
    def setUp(self):
        self.tp = 1.0
        self.resolution = 0.25
        self.t = np.r_[0.0 : self.tp : self.resolution]

    def test_adiabatic_formula(self):
        BW = 2.0
        beta = 3.0
        beta_scaled = beta / self.tp
        mu = np.pi * BW / beta_scaled
        expected = (1.0 / np.cosh(beta_scaled * (self.t - 0.5 * self.tp))) ** (
            1.0 + 1.0j * mu
        )

        t, pulse = pulses.adiabatic(
            self.tp, BW=BW, beta=beta, resolution=self.resolution
        )

        assert_array_equal(t, self.t)
        assert_allclose(pulse, expected)
        self.assertTrue(np.iscomplexobj(pulse))

    def test_chirp_formula(self):
        BW = 4.0
        k = BW / self.tp
        expected = np.exp(
            1.0j * 2.0 * np.pi * ((k / 2.0) * ((self.t - self.tp / 2.0) ** 2.0))
        )

        t, pulse = pulses.chirp(self.tp, BW=BW, resolution=self.resolution)

        assert_array_equal(t, self.t)
        assert_allclose(pulse, expected)
        self.assertTrue(np.iscomplexobj(pulse))

    def test_wurst_formula(self):
        N = 4
        expected = (
            1.0
            - np.abs(
                np.cos(np.pi * (self.t - self.tp / 2.0) / self.tp + np.pi / 2.0)
            )
            ** N
        ) + 0j

        t, pulse = pulses.wurst(self.tp, N=N, resolution=self.resolution)

        assert_array_equal(t, self.t)
        assert_allclose(pulse, expected)
        self.assertTrue(np.iscomplexobj(pulse))

    def test_gaussian_formula(self):
        sigmas = 2.0
        sigma = 0.5 * self.tp / sigmas
        expected = np.exp(
            -1.0 * (self.t - self.tp / 2.0) ** 2.0 / (2.0 * sigma**2.0)
        ) + 0j

        t, pulse = pulses.gaussian(self.tp, sigmas=sigmas, resolution=self.resolution)

        assert_array_equal(t, self.t)
        assert_allclose(pulse, expected)
        self.assertTrue(np.iscomplexobj(pulse))

    def test_square_without_padding(self):
        t, pulse = pulses.square(self.tp, resolution=self.resolution)

        assert_array_equal(t, self.t)
        assert_allclose(pulse, np.ones_like(self.t, dtype=complex))
        self.assertTrue(np.iscomplexobj(pulse))

    def test_square_with_padding_centers_pulse(self):
        t_length = 2.0
        expected_t = np.r_[0.0 : t_length : self.resolution]
        expected_pulse = np.zeros_like(expected_t, dtype=complex)
        expected_pulse[(expected_t >= 0.5) & (expected_t < 1.5)] = 1.0

        t, pulse = pulses.square(
            self.tp, t_length=t_length, resolution=self.resolution
        )

        assert_array_equal(t, expected_t)
        assert_allclose(pulse, expected_pulse)
        self.assertTrue(np.iscomplexobj(pulse))
        self.assertEqual(np.count_nonzero(pulse), int(self.tp / self.resolution))

    def test_plane_wave_formula(self):
        f = 2.0
        expected = np.exp(1.0j * 2.0 * np.pi * f * (self.t - self.tp / 2.0))

        t, pulse = pulses.plane_wave(self.tp, f=f, resolution=self.resolution)

        assert_array_equal(t, self.t)
        assert_allclose(pulse, expected)
        self.assertTrue(np.iscomplexobj(pulse))

    def test_sinc_formula_and_center_limit(self):
        n = 3
        x = (self.t - self.tp / 2.0) / (0.5 * self.tp)
        scale = ((n + 1.0) / 2.0) * np.pi
        expected = np.empty_like(x)
        center = np.isclose(x, 0.0)
        expected[center] = scale
        expected[~center] = np.sin(scale * x[~center]) / x[~center]

        t, pulse = pulses.sinc(self.tp, n=n, resolution=self.resolution)

        assert_array_equal(t, self.t)
        assert_allclose(pulse, expected)
        self.assertTrue(np.all(np.isfinite(pulse)))
        self.assertEqual(pulse[center][0], scale)

    def test_save_and_load_real_shape(self):
        pulse = np.array([0.0, 0.5, 1.0])

        with tempfile.TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / "real_shape.txt"
            pulses.save_shape(pulse, filename, num=7)
            out = pulses.load_shape(filename)

        assert_allclose(out, pulse.astype(complex), atol=5e-5)

    def test_save_and_load_complex_shape(self):
        pulse = np.array([0.0 + 0.0j, 0.5 + 0.25j, 1.0 - 0.5j], dtype=np.complex64)

        with tempfile.TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / "complex_shape.txt"
            pulses.save_shape(pulse, filename, num=8)
            out = pulses.load_shape(filename)

        assert_allclose(out, pulse, atol=5e-5)

    def test_save_shape_requires_1d_array(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / "bad_shape.txt"
            with self.assertRaises(ValueError):
                pulses.save_shape(np.ones((2, 2)), filename)

    def test_pulse_generators_validate_positive_inputs(self):
        invalid_cases = [
            (pulses.adiabatic, (0.0, 1.0, 1.0), {}),
            (pulses.adiabatic, (1.0, 1.0, 0.0), {}),
            (pulses.adiabatic, (1.0, 1.0, 1.0), {"resolution": 0.0}),
            (pulses.chirp, (0.0, 1.0), {}),
            (pulses.chirp, (1.0, 1.0), {"resolution": -0.1}),
            (pulses.wurst, (1.0, 0.0), {}),
            (pulses.gaussian, (1.0, 0.0), {}),
            (pulses.square, (0.0,), {}),
            (pulses.square, (1.0,), {"t_length": -1.0}),
            (pulses.plane_wave, (0.0, 1.0), {}),
            (pulses.sinc, (1.0, 0.0), {}),
        ]

        for func, args, kwargs in invalid_cases:
            with self.subTest(func=func.__name__, args=args, kwargs=kwargs):
                with self.assertRaises(ValueError):
                    func(*args, **kwargs)

    def test_top_level_pulses_exports(self):
        self.assertIs(sl.pulses.adiabatic, pulses.adiabatic)
        self.assertIs(sl.pulses.chirp, pulses.chirp)
        self.assertIs(sl.pulses.wurst, pulses.wurst)
        self.assertIs(sl.pulses.gaussian, pulses.gaussian)
        self.assertIs(sl.pulses.square, pulses.square)
        self.assertIs(sl.pulses.plane_wave, pulses.plane_wave)
        self.assertIs(sl.pulses.sinc, pulses.sinc)
        self.assertIs(sl.pulses.save_shape, pulses.save_shape)
        self.assertIs(sl.pulses.load_shape, pulses.load_shape)


if __name__ == "__main__":
    unittest.main()
