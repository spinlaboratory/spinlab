import unittest
import numpy as np
from numpy.testing import assert_allclose

from spinlab.theory.general import (
    distance_to_dipolar_coupling,
    sphere_orientations,
    sphere_quadrature,
    pake_pattern,
)
from spinlab.theory.helpers import Jp, Jm, Jx, Jy, Jz


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
            self.freq, self.theta, self.phi, self.coupling, self.lw, self.weights
        )
        self.assertEqual(len(spectrum), len(self.freq))

    def test_output_real(self):
        spectrum = pake_pattern(
            self.freq, self.theta, self.phi, self.coupling, self.lw, self.weights
        )
        self.assertTrue(np.isrealobj(spectrum))

    def test_symmetric(self):
        spectrum = pake_pattern(
            self.freq, self.theta, self.phi, self.coupling, self.lw, self.weights
        )
        # Odd-length FFT gives an exactly symmetric frequency axis
        assert_allclose(spectrum, spectrum[::-1], atol=1e-6)

    def test_horn_positions(self):
        spectrum = pake_pattern(
            self.freq, self.theta, self.phi, self.coupling, self.lw, self.weights
        )
        spectrum = spectrum - spectrum.min()
        # Horns should be near +/- coupling (6.51 MHz)
        # Find the two largest peaks
        pos_half = spectrum[len(self.freq) // 2 :]
        pos_freq = self.freq[len(self.freq) // 2 :]
        peak_idx = np.argmax(pos_half)
        assert_allclose(pos_freq[peak_idx] / self.coupling, 1.0, atol=0.15)

    def test_uniform_weights(self):
        spectrum_weighted = pake_pattern(
            self.freq, self.theta, self.phi, self.coupling, self.lw, self.weights
        )
        spectrum_uniform = pake_pattern(
            self.freq, self.theta, self.phi, self.coupling, self.lw
        )
        # Both should be real, same length, and reasonably similar in shape
        self.assertEqual(len(spectrum_weighted), len(spectrum_uniform))


class TestSpinOperatorsHalfSpin(unittest.TestCase):
    """Tests for j=1/2 spin operators against known Pauli matrices."""

    def setUp(self):
        self.j = 0.5

    def test_Jp_half(self):
        expected = np.array([[0, 1], [0, 0]], dtype=complex)
        assert_allclose(Jp(self.j), expected, atol=1e-10)

    def test_Jm_half(self):
        expected = np.array([[0, 0], [1, 0]], dtype=complex)
        assert_allclose(Jm(self.j), expected, atol=1e-10)

    def test_Jx_half(self):
        expected = 0.5 * np.array([[0, 1], [1, 0]], dtype=complex)
        assert_allclose(Jx(self.j), expected, atol=1e-10)

    def test_Jy_half(self):
        expected = 0.5 * np.array([[0, -1j], [1j, 0]], dtype=complex)
        assert_allclose(Jy(self.j), expected, atol=1e-10)

    def test_Jz_half(self):
        # Convention: index 0 corresponds to m = +j (descending m ordering)
        expected = np.array([[0.5, 0], [0, -0.5]], dtype=complex)
        assert_allclose(Jz(self.j), expected, atol=1e-10)

    def test_Jm_is_Jp_conjugate_transpose(self):
        assert_allclose(Jm(self.j), Jp(self.j).conj().T, atol=1e-10)


class TestSpinOperatorsCommutation(unittest.TestCase):
    """Commutation relations [Ji, Jj] = i*eps_ijk*Jk for several j values."""

    def _commutator(self, A, B):
        return A @ B - B @ A

    def _check_commutation(self, j):
        jx, jy, jz = Jx(j), Jy(j), Jz(j)
        assert_allclose(self._commutator(jx, jy), 1j * jz, atol=1e-10)
        assert_allclose(self._commutator(jy, jz), 1j * jx, atol=1e-10)
        assert_allclose(self._commutator(jz, jx), 1j * jy, atol=1e-10)

    def test_commutation_half(self):
        self._check_commutation(0.5)

    def test_commutation_one(self):
        self._check_commutation(1)

    def test_commutation_three_halves(self):
        self._check_commutation(1.5)

    def test_commutation_two(self):
        self._check_commutation(2)


class TestSpinOperatorsJ2(unittest.TestCase):
    """J^2 = j(j+1)*I for several j values."""

    def _check_j_squared(self, j):
        jx, jy, jz = Jx(j), Jy(j), Jz(j)
        j2 = jx @ jx + jy @ jy + jz @ jz
        expected = j * (j + 1) * np.eye(round(2 * j + 1))
        assert_allclose(j2.real, expected, atol=1e-10)
        assert_allclose(j2.imag, np.zeros_like(expected), atol=1e-10)

    def test_j2_half(self):
        self._check_j_squared(0.5)

    def test_j2_one(self):
        self._check_j_squared(1)

    def test_j2_three_halves(self):
        self._check_j_squared(1.5)

    def test_j2_two(self):
        self._check_j_squared(2)


class TestSpinOperatorsShape(unittest.TestCase):
    def test_matrix_size(self):
        for j in [0.5, 1, 1.5, 2, 2.5]:
            size = round(2 * j + 1)
            for op in [Jp, Jm, Jx, Jy, Jz]:
                self.assertEqual(op(j).shape, (size, size))

    def test_jx_jy_hermitian(self):
        for j in [0.5, 1, 1.5]:
            for op in [Jx, Jy, Jz]:
                m = op(j)
                assert_allclose(m, m.conj().T, atol=1e-10)


if __name__ == "__main__":
    unittest.main()
