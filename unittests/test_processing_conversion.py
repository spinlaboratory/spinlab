import io
import logging
import unittest
from contextlib import redirect_stdout

import numpy as np
import spinlab as sl
from numpy.testing import assert_allclose, assert_array_equal

from spinlab.processing.conversion import (
    calc_conversion_factor,
    calc_tp90,
    convert_power,
    dBm2w,
    decay2Ce,
    tp90_B1,
    w2dBm,
)


# logging.basicConfig(filename='conversion_debug.log', encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)


class sl_conversion_tester(unittest.TestCase):
    def setUp(self):
        self.power_dbm = np.array([0, 10, 20])
        self.power_w = np.array([0.001, 0.01, 0.1])
        self.values = np.array([1.0, 2.0, 3.0])
        self.data_dbm = sl.SpinData(
            self.values,
            dims=["Power"],
            coords=[self.power_dbm],
            spinlab_attrs={"power_unit": "dBm"},
        )
        self.data_w = sl.SpinData(
            self.values,
            dims=["Power"],
            coords=[self.power_w],
            spinlab_attrs={"power_unit": "W"},
        )

    def test_dBm2w_scalar(self):
        self.assertEqual(dBm2w(0), 0.001)
        self.assertEqual(dBm2w(10), 0.01)
        self.assertEqual(dBm2w(-300), 0)

    def test_dBm2w_list(self):
        out = dBm2w([0, 10, 20])

        self.assertIsInstance(out, list)
        assert_allclose(out, self.power_w)

    def test_dBm2w_integer_array_returns_float_array(self):
        out = dBm2w(self.power_dbm)

        self.assertTrue(np.issubdtype(out.dtype, np.floating))
        assert_allclose(out, self.power_w)

    def test_w2dBm_scalar(self):
        self.assertEqual(w2dBm(0.001), 0)
        self.assertEqual(w2dBm(0.01), 10)

    def test_w2dBm_list(self):
        out = w2dBm([0.001, 0.01, 0.1])

        self.assertIsInstance(out, list)
        assert_allclose(out, self.power_dbm)

    def test_w2dBm_integer_array_returns_float_array(self):
        out = w2dBm(np.array([1, 10, 100]))

        self.assertTrue(np.issubdtype(out.dtype, np.floating))
        assert_allclose(out, np.array([30.0, 40.0, 50.0]))

    def test_convert_power_numeric_uses_mode(self):
        assert_allclose(convert_power(self.power_dbm, mode="dBm2W"), self.power_w)
        assert_allclose(convert_power(self.power_w, mode="W2dBm"), self.power_dbm)

    def test_convert_power_spindata_dbm_to_w_uses_power_unit(self):
        out = convert_power(self.data_dbm)

        self.assertEqual(out.dims, ["Power"])
        self.assertEqual(out.shape, self.data_dbm.shape)
        self.assertEqual(out.spinlab_attrs["power_unit"], "W")
        self.assertEqual(out.proc_attrs[-1][0], "convert_power")
        self.assertEqual(out.proc_attrs[-1][1]["mode"], "dBm2W")
        assert_array_equal(out.values, self.values)
        assert_allclose(out.coords["Power"], self.power_w)

    def test_convert_power_spindata_w_to_dbm_uses_power_unit(self):
        out = convert_power(self.data_w, mode="dBm2W")

        self.assertEqual(out.spinlab_attrs["power_unit"], "dBm")
        self.assertEqual(out.proc_attrs[-1][1]["mode"], "W2dBm")
        assert_array_equal(out.values, self.values)
        assert_allclose(out.coords["Power"], self.power_dbm)

    def test_convert_power_spindata_without_power_unit_uses_mode(self):
        data = sl.SpinData(self.values, dims=["Power"], coords=[self.power_dbm])

        out = convert_power(data, mode="dBm2W")

        self.assertEqual(out.spinlab_attrs["power_unit"], "W")
        assert_allclose(out.coords["Power"], self.power_w)

    def test_convert_power_accepts_powers_dim_name(self):
        data = sl.SpinData(
            self.values,
            dims=["powers"],
            coords=[self.power_dbm],
            spinlab_attrs={"power_unit": "dBm"},
        )

        out = convert_power(data)

        self.assertEqual(out.dims, ["powers"])
        assert_allclose(out.coords["powers"], self.power_w)

    def test_convert_power_invalid_inputs_raise_value_error(self):
        data_no_power = sl.SpinData(self.values, dims=["x"], coords=[self.power_dbm])
        data_bad_unit = sl.SpinData(
            self.values,
            dims=["Power"],
            coords=[self.power_dbm],
            spinlab_attrs={"power_unit": "invalid"},
        )

        with self.assertRaises(ValueError):
            convert_power(self.power_dbm, mode="bad")
        with self.assertRaises(ValueError):
            convert_power(data_no_power)
        with self.assertRaises(ValueError):
            convert_power(data_bad_unit)

    def test_convert_power_does_not_mutate_input(self):
        original_values = self.data_dbm.values.copy()
        original_coord = self.data_dbm.coords["Power"].copy()
        original_attrs = self.data_dbm.spinlab_attrs.copy()

        convert_power(self.data_dbm)

        assert_array_equal(self.data_dbm.values, original_values)
        assert_array_equal(self.data_dbm.coords["Power"], original_coord)
        self.assertEqual(self.data_dbm.spinlab_attrs, original_attrs)

    def test_decay2Ce(self):
        decay_time = 1.5e-6
        gA = 2.0
        gB = 2.1
        FB = 0.3
        k = 2 * np.pi * sl.mu_0 * sl.mub**2 * gA * gB / (
            9 * np.sqrt(3) * sl.hbar
        )
        expected = 1 / (decay_time * k * 1000 * sl.N_A * FB)

        assert_allclose(decay2Ce(decay_time, gA, gB, FB), expected)

    def test_tp90_B1(self):
        self.assertEqual(tp90_B1(10e-9), 25e6)

    def test_calc_tp90_and_conversion_factor_are_inverse(self):
        c = 120.0
        P = 0.5
        Q = 2.0
        alpha = 3.0

        tp90 = calc_tp90(c, P, Q=Q, alpha=alpha)
        c_out = calc_conversion_factor(tp90, P, Q=Q, alpha=alpha)

        assert_allclose(c_out, c)

    def test_calc_helpers_verbose_print_only_when_requested(self):
        silent = io.StringIO()
        with redirect_stdout(silent):
            calc_conversion_factor(10e-9, 1.0)
        self.assertEqual(silent.getvalue(), "")

        verbose = io.StringIO()
        with redirect_stdout(verbose):
            calc_tp90(120.0, 0.5, verbose=True)
        self.assertIn("Input Parameters", verbose.getvalue())


if __name__ == "__main__":
    unittest.main()
