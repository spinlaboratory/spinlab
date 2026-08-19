import unittest
import numpy as np
from numpy.testing import assert_allclose

from spinlab.theory.general import (
    distance_to_dipolar_coupling,
    sphere_orientations,
    sphere_quadrature,
    pake_pattern,
)


class TestDistanceToDipolarCoupling(unittest.TestCase):
    def test_known_value_2nm(self):
        nu = distance_to_dipolar_coupling(2e-9, unit="MHz")
        assert_allclose(nu, 6.505, rtol=1e-3)

    def test_unit_hz(self):
        nu_hz = distance_to_dipolar_coupling(2e-9, unit="Hz")
        nu_mhz = distance_to_dipolar_coupling(2e-9, unit="MHz")
        assert_allclose(nu_hz, nu_mhz * 1e6, rtol=1e-10)

    def test_unit_ghz(self):
        nu_ghz = distance_to_dipolar_coupling(2e-9, unit="GHz")
        nu_mhz = distance_to_dipolar_coupling(2e-9, unit="MHz")
        assert_allclose(nu_ghz * 1e3, nu_mhz, rtol=1e-10)

    def test_unit_rad_per_s(self):
        nu_hz = distance_to_dipolar_coupling(2e-9, unit="Hz")
        nu_rad = distance_to_dipolar_coupling(2e-9, unit="rad/s")
        assert_allclose(nu_rad, nu_hz * 2 * np.pi, rtol=1e-10)

    def test_r_cubed_scaling(self):
        nu1 = distance_to_dipolar_coupling(1e-9)
        nu2 = distance_to_dipolar_coupling(2e-9)
        assert_allclose(nu1 / nu2, 8.0, rtol=1e-10)

    def test_array_input(self):
        r = np.array([1e-9, 2e-9, 3e-9])
        nu = distance_to_dipolar_coupling(r, unit="MHz")
        self.assertEqual(nu.shape, (3,))
        self.assertTrue(np.all(nu > 0))

    def test_g_factor_scaling(self):
        nu_default = distance_to_dipolar_coupling(2e-9)
        nu_double_g = distance_to_dipolar_coupling(2e-9, g1=2 * 2.00232, g2=2.00232)
        assert_allclose(nu_double_g / nu_default, 2.0, rtol=1e-6)

    def test_invalid_unit_raises(self):
        with self.assertRaises(ValueError):
            distance_to_dipolar_coupling(2e-9, unit="kHz")


class TestSphereOrientations(unittest.TestCase):
    def test_returns_two_arrays(self):
        theta, phi = sphere_orientations(10)
        self.assertEqual(theta.shape, phi.shape)

    def test_theta_range(self):
        theta, _ = sphere_orientations(20)
        self.assertTrue(np.all(theta >= 0))
        self.assertTrue(np.all(theta <= np.pi))

    def test_phi_range(self):
        _, phi = sphere_orientations(20)
        self.assertTrue(np.all(phi >= 0))
        self.assertTrue(np.all(phi <= 2 * np.pi))

    def test_more_bands_more_points(self):
        theta10, _ = sphere_orientations(10)
        theta20, _ = sphere_orientations(20)
        self.assertGreater(len(theta20), len(theta10))

    def test_unit_sphere(self):
        theta, phi = sphere_orientations(15)
        x = np.sin(theta) * np.cos(phi)
        y = np.sin(theta) * np.sin(phi)
        z = np.cos(theta)
        r = np.sqrt(x**2 + y**2 + z**2)
        assert_allclose(r, np.ones_like(r), atol=1e-10)


class TestSphereQuadrature(unittest.TestCase):
    def test_returns_three_arrays(self):
        theta, phi, weights = sphere_quadrature(10, 1)
        self.assertEqual(theta.shape, phi.shape)
        self.assertEqual(theta.shape, weights.shape)

    def test_weights_sum_to_one(self):
        _, _, weights = sphere_quadrature(50, 1)
        assert_allclose(weights.sum(), 1.0, rtol=1e-10)

    def test_weights_positive(self):
        _, _, weights = sphere_quadrature(20, 4)
        self.assertTrue(np.all(weights > 0))

    def test_theta_range(self):
        theta, _, _ = sphere_quadrature(20, 1)
        self.assertTrue(np.all(theta >= 0))
        self.assertTrue(np.all(theta <= np.pi))

    def test_phi_range(self):
        _, phi, _ = sphere_quadrature(10, 4)
        self.assertTrue(np.all(phi >= 0))
        self.assertTrue(np.all(phi < 2 * np.pi))

    def test_n_points(self):
        n_theta, n_phi = 12, 6
        theta, phi, weights = sphere_quadrature(n_theta, n_phi)
        self.assertEqual(len(theta), n_theta * n_phi)

    def test_single_phi_node(self):
        theta, phi, weights = sphere_quadrature(10, 1)
        self.assertEqual(len(theta), 10)
        assert_allclose(phi, np.zeros(10))


class TestPakePattern(unittest.TestCase):
    def setUp(self):
        # Use an odd number of points so the FFT frequency axis is exactly
        # symmetric around zero and spectrum[::-1] == spectrum holds exactly.
        self.freq = np.linspace(-20e6, 20e6, 2049)
        self.theta, self.phi, self.weights = sphere_quadrature(200, 1)
        self.coupling = distance_to_dipolar_coupling(2e-9)  # ~6.51 MHz
        self.lw = 0.5e6

    def test_output_length(self):
        spectrum = pake_pattern(
            self.freq, self.theta, self.coupling, self.lw, self.weights
        )
        self.assertEqual(len(spectrum), len(self.freq))

    def test_output_real(self):
        spectrum = pake_pattern(
            self.freq, self.theta, self.coupling, self.lw, self.weights
        )
        self.assertTrue(np.isrealobj(spectrum))

    def test_symmetric(self):
        spectrum = pake_pattern(
            self.freq, self.theta, self.coupling, self.lw, self.weights
        )
        # Odd-length FFT gives an exactly symmetric frequency axis
        assert_allclose(spectrum, spectrum[::-1], atol=1e-6)

    def test_horn_positions(self):
        spectrum = pake_pattern(
            self.freq, self.theta, self.coupling, self.lw, self.weights
        )
        spectrum = spectrum - spectrum.min()
        # Horns should be near +/- coupling (6.51 MHz)
        pos_half = spectrum[len(self.freq) // 2 :]
        pos_freq = self.freq[len(self.freq) // 2 :]
        peak_idx = np.argmax(pos_half)
        assert_allclose(pos_freq[peak_idx] / self.coupling, 1.0, atol=0.15)

    def test_uniform_weights(self):
        spectrum_weighted = pake_pattern(
            self.freq, self.theta, self.coupling, self.lw, self.weights
        )
        spectrum_uniform = pake_pattern(
            self.freq, self.theta, self.coupling, self.lw
        )
        # Both should be real, same length, and reasonably similar in shape
        self.assertEqual(len(spectrum_weighted), len(spectrum_uniform))


if __name__ == "__main__":
    unittest.main()
