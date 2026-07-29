import unittest
import numpy as np
from numpy.testing import assert_allclose

from spinlab.theory.helpers import Jp, Jm, Jx, Jy, Jz


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
