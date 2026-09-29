import unittest

import numpy as np
import spinlab as sl
from numpy.testing import assert_allclose

from spinlab.math import relaxation


class sl_relaxation_tester(unittest.TestCase):
    def setUp(self):
        self.t = np.linspace(0.0, 5.0, 11)
        self.p = np.linspace(0.0, 10.0, 11)

    def test_buildup_function_formula(self):
        E_max = -12.0
        p_half = 2.5
        expected = 1.0 + E_max * self.p / (p_half + self.p)

        assert_allclose(
            relaxation.buildup_function(self.p, E_max=E_max, p_half=p_half),
            expected,
        )

    def test_buildup_function_accepts_list(self):
        out = relaxation.buildup_function([0.0, 1.0, 2.0], E_max=4.0, p_half=1.0)

        self.assertEqual(out.shape, (3,))
        assert_allclose(out, np.array([1.0, 3.0, 11.0 / 3.0]))

    def test_ksigma_smax_formula(self):
        E_max = 8.0
        p_half = 3.0
        expected = E_max * self.p / (p_half + self.p)

        assert_allclose(
            relaxation.ksigma_smax(self.p, E_max=E_max, p_half=p_half),
            expected,
        )

    def test_ksigma_smax_accepts_list(self):
        out = relaxation.ksigma_smax([0.0, 1.0, 2.0], E_max=4.0, p_half=1.0)

        self.assertEqual(out.shape, (3,))
        assert_allclose(out, np.array([0.0, 2.0, 8.0 / 3.0]))

    def test_general_exp_formula(self):
        C1 = 0.5
        C2 = 2.0
        tau = 1.25
        expected = C1 + C2 * np.exp(-1.0 * self.t / tau)

        assert_allclose(relaxation.general_exp(self.t, C1=C1, C2=C2, tau=tau), expected)

    def test_general_exp_accepts_list(self):
        out = relaxation.general_exp([0.0, 1.0], C1=1.0, C2=2.0, tau=2.0)

        self.assertEqual(out.shape, (2,))
        assert_allclose(out, np.array([3.0, 1.0 + 2.0 * np.exp(-0.5)]))

    def test_general_biexp_formula(self):
        C1 = 0.2
        C2 = 1.5
        tau1 = 0.8
        C3 = -0.4
        tau2 = 3.0
        expected = C1 + C2 * np.exp(-1.0 * self.t / tau1)
        expected += C3 * np.exp(-1.0 * self.t / tau2)

        assert_allclose(
            relaxation.general_biexp(
                self.t, C1=C1, C2=C2, tau1=tau1, C3=C3, tau2=tau2
            ),
            expected,
        )

    def test_general_biexp_accepts_list(self):
        out = relaxation.general_biexp(
            [0.0, 1.0], C1=0.0, C2=1.0, tau1=1.0, C3=2.0, tau2=2.0
        )

        self.assertEqual(out.shape, (2,))
        assert_allclose(out[0], 3.0)

    def test_t1_formula(self):
        T1 = 1.7
        M_0 = -1.0
        M_inf = 2.0
        expected = M_inf - (M_inf - M_0) * np.exp(-1.0 * self.t / T1)

        assert_allclose(relaxation.t1(self.t, T1=T1, M_0=M_0, M_inf=M_inf), expected)

    def test_t1_accepts_list(self):
        out = relaxation.t1([0.0, 1.0], T1=2.0, M_0=-1.0, M_inf=1.0)

        self.assertEqual(out.shape, (2,))
        assert_allclose(out[0], -1.0)

    def test_t2_formula(self):
        M_0 = 2.5
        T2 = 1.2
        p = 1.4
        expected = M_0 * np.exp(-1.0 * (self.t / T2) ** p)

        assert_allclose(relaxation.t2(self.t, M_0=M_0, T2=T2, p=p), expected)

    def test_t2_accepts_list(self):
        out = relaxation.t2([0.0, 1.0], M_0=2.0, T2=2.0)

        self.assertEqual(out.shape, (2,))
        assert_allclose(out, np.array([2.0, 2.0 * np.exp(-0.5)]))

    def test_logistic_formula(self):
        c = 0.5
        x0 = 2.0
        L = 3.0
        k = 1.25
        expected = c + L / (1.0 + np.exp(-1.0 * k * (self.t - x0)))

        assert_allclose(relaxation.logistic(self.t, c=c, x0=x0, L=L, k=k), expected)

    def test_logistic_accepts_list(self):
        out = relaxation.logistic([0.0, 1.0], c=0.0, x0=0.0, L=2.0, k=1.0)

        self.assertEqual(out.shape, (2,))
        assert_allclose(out, 2.0 / (1.0 + np.exp(-1.0 * np.array([0.0, 1.0]))))

    def test_top_level_relaxation_exports(self):
        self.assertIs(sl.relaxation.buildup_function, relaxation.buildup_function)
        self.assertIs(sl.relaxation.general_exp, relaxation.general_exp)
        self.assertIs(sl.relaxation.general_biexp, relaxation.general_biexp)
        self.assertIs(sl.relaxation.ksigma_smax, relaxation.ksigma_smax)
        self.assertIs(sl.relaxation.logistic, relaxation.logistic)
        self.assertIs(sl.relaxation.t1, relaxation.t1)
        self.assertIs(sl.relaxation.t2, relaxation.t2)


if __name__ == "__main__":
    unittest.main()
