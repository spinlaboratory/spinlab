import logging
import unittest

import numpy as np
import spinlab as sl
from numpy.testing import assert_allclose, assert_array_equal

from spinlab.math import window
from spinlab.processing.apodization import apodize


# logging.basicConfig(filename='apodization_debug.log', encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)


class sl_apodization_tester(unittest.TestCase):
    def setUp(self):
        self.t = np.linspace(0.0, 1.0, 8)
        self.values_1d = np.ones_like(self.t)
        self.data_1d = sl.SpinData(self.values_1d, dims=["t2"], coords=[self.t])

        self.scan = np.r_[0:3]
        self.values_2d = np.ones((self.t.size, self.scan.size))
        self.data_2d = sl.SpinData(
            self.values_2d, dims=["t2", "scan"], coords=[self.t, self.scan]
        )
        self.complex_values_1d = (1.0 + 2.0j) * np.ones_like(self.t)
        self.complex_data_1d = sl.SpinData(
            self.complex_values_1d, dims=["t2"], coords=[self.t]
        )
        self.complex_values_2d = (1.0 + 2.0j) * np.ones(
            (self.t.size, self.scan.size)
        )
        self.complex_data_2d = sl.SpinData(
            self.complex_values_2d, dims=["t2", "scan"], coords=[self.t, self.scan]
        )

    def test_apodize_defaults_to_first_dim(self):
        out = apodize(self.data_2d, lw=1.0)
        expected_window = window.exponential(self.t, lw=1.0).reshape(-1, 1)

        self.assertEqual(out.dims, ["t2", "scan"])
        self.assertEqual(out.shape, self.data_2d.shape)
        self.assertEqual(out.proc_attrs[-1][0], "window")
        self.assertEqual(out.proc_attrs[-1][1], {"dim": "t2", "kind": "exponential", "lw": 1.0})
        assert_array_equal(out.coords["t2"], self.t)
        assert_array_equal(out.coords["scan"], self.scan)
        assert_allclose(out.values, self.values_2d * expected_window)

    def test_apodize_1d_exponential(self):
        out = apodize(self.data_1d, dim="t2", kind="exponential", lw=1.0)

        assert_allclose(out.values, window.exponential(self.t, lw=1.0))
        self.assertEqual(out.proc_attrs[-1][1]["dim"], "t2")
        self.assertEqual(out.proc_attrs[-1][1]["kind"], "exponential")

    def test_apodize_2d_along_second_dim(self):
        out = apodize(self.data_2d, dim="scan", kind="hann")
        expected_window = window.hann(self.scan).reshape(1, -1)

        self.assertEqual(out.dims, ["t2", "scan"])
        self.assertEqual(out.shape, self.data_2d.shape)
        assert_allclose(out.values, self.values_2d * expected_window)

    def test_apodize_complex_1d_data(self):
        out = apodize(self.complex_data_1d, dim="t2", kind="exponential", lw=1.0)
        expected_window = window.exponential(self.t, lw=1.0)

        self.assertTrue(np.iscomplexobj(out.values))
        assert_allclose(out.values, self.complex_values_1d * expected_window)

    def test_apodize_complex_2d_data(self):
        out = apodize(self.complex_data_2d, dim="t2", kind="exponential", lw=1.0)
        expected_window = window.exponential(self.t, lw=1.0).reshape(-1, 1)

        self.assertTrue(np.iscomplexobj(out.values))
        self.assertEqual(out.dims, ["t2", "scan"])
        assert_allclose(out.values, self.complex_values_2d * expected_window)

    def test_apodize_kind_is_case_insensitive(self):
        out = apodize(self.data_1d, dim="t2", kind="HaMmInG")

        self.assertEqual(out.proc_attrs[-1][1]["kind"], "hamming")
        assert_allclose(out.values, window.hamming(self.t))

    def test_apodize_supported_windows(self):
        cases = [
            ("exponential", {"lw": 1.0}, window.exponential(self.t, lw=1.0)),
            ("gaussian", {"lw": 1.0}, window.gaussian(self.t, lw=1.0)),
            ("hann", {}, window.hann(self.t)),
            ("hamming", {}, window.hamming(self.t)),
            (
                "lorentz_gauss",
                {"lw": 0.1, "gauss_lw": 0.1},
                window.lorentz_gauss(self.t, lw=0.1, gauss_lw=0.1),
            ),
            ("traf", {"lw": 1.0}, window.traf(self.t, lw=1.0)),
            ("sin2", {}, window.sin2(self.t)),
        ]

        for kind, kwargs, expected_window in cases:
            with self.subTest(kind=kind):
                out = apodize(self.data_1d, dim="t2", kind=kind, **kwargs)

                self.assertEqual(out.proc_attrs[-1][1]["kind"], kind)
                assert_allclose(out.values, expected_window)

    def test_apodize_invalid_kind_raises_value_error(self):
        with self.assertRaises(ValueError):
            apodize(self.data_1d, dim="t2", kind="not_a_window")

    def test_apodize_invalid_dim_raises_value_error(self):
        with self.assertRaises(ValueError):
            apodize(self.data_1d, dim="not_a_dim", lw=1.0)

    def test_apodize_missing_required_window_argument_raises_type_error(self):
        with self.assertRaises(TypeError):
            apodize(self.data_1d, dim="t2", kind="exponential")

    def test_apodize_does_not_mutate_input(self):
        original_values = self.data_2d.values.copy()
        original_t = self.data_2d.coords["t2"].copy()
        original_scan = self.data_2d.coords["scan"].copy()
        original_dims = self.data_2d.dims.copy()

        apodize(self.data_2d, dim="t2", lw=1.0)

        self.assertEqual(self.data_2d.dims, original_dims)
        assert_array_equal(self.data_2d.coords["t2"], original_t)
        assert_array_equal(self.data_2d.coords["scan"], original_scan)
        assert_allclose(self.data_2d.values, original_values)


if __name__ == "__main__":
    unittest.main()
