import logging
import unittest

import numpy as np
import spinlab as sl
from numpy.testing import assert_allclose, assert_array_equal

from spinlab.processing.offset import background, remove_background


# logging.basicConfig(filename='offset_debug.log', encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)


def linear(x, m, b):
    return m * x + b


class sl_offset_tester(unittest.TestCase):
    def setUp(self):
        self.x = np.linspace(-1.0, 1.0, 501)
        self.baseline = 2.0 * self.x + 3.0
        self.signal = np.zeros_like(self.x)
        self.signal[(self.x >= -0.2) & (self.x <= 0.2)] = 5.0
        self.data_1d = sl.SpinData(
            self.baseline + self.signal, dims=["x"], coords=[self.x]
        )
        self.baseline_data = sl.SpinData(self.baseline, dims=["x"], coords=[self.x])

        self.scan = np.r_[0:4]
        self.baseline_2d = np.array(
            [(i + 1) * self.baseline for i in self.scan]
        ).T
        self.data_2d = sl.SpinData(
            self.baseline_2d, dims=["x", "scan"], coords=[self.x, self.scan]
        )

        self.complex_baseline = self.baseline + 1j * (-1.0 * self.x + 1.0)
        self.complex_data = sl.SpinData(
            self.complex_baseline, dims=["x"], coords=[self.x]
        )

    def test_background_constant_fit(self):
        values = np.ones_like(self.x) * 4.0
        data = sl.SpinData(values, dims=["x"], coords=[self.x])

        out = background(data, dim="x", deg=0)

        self.assertEqual(out.dims, ["x"])
        self.assertEqual(out.shape, data.shape)
        assert_array_equal(out.coords["x"], self.x)
        self.assertEqual(out.proc_attrs[-1][0], "background")
        self.assertEqual(
            out.proc_attrs[-1][1],
            {"dim": "x", "deg": 0, "regions": None, "func": None},
        )
        assert_allclose(out.values, values)

    def test_background_linear_fit(self):
        out = background(self.baseline_data, dim="x", deg=1)

        self.assertEqual(out.dims, ["x"])
        self.assertEqual(out.shape, self.baseline_data.shape)
        assert_allclose(out.values, self.baseline)

    def test_background_defaults_to_first_dim(self):
        out = background(self.data_2d, deg=1)

        self.assertEqual(out.dims, ["x", "scan"])
        self.assertEqual(out.shape, self.data_2d.shape)
        self.assertEqual(out.proc_attrs[-1][1]["dim"], "x")
        assert_allclose(out.values, self.baseline_2d)

    def test_background_uses_selected_regions(self):
        regions = [(-1.0, -0.5), (0.5, 1.0)]

        out = background(self.data_1d, dim="x", deg=1, regions=regions)

        self.assertEqual(out.proc_attrs[-1][1]["regions"], regions)
        assert_allclose(out.values, self.baseline, atol=1e-12)

    def test_background_2d_along_first_dim(self):
        out = background(self.data_2d, dim="x", deg=1)

        self.assertEqual(out.dims, ["x", "scan"])
        self.assertEqual(out.shape, self.data_2d.shape)
        assert_array_equal(out.coords["scan"], self.scan)
        assert_allclose(out.values, self.baseline_2d)

    def test_background_complex_data(self):
        out = background(self.complex_data, dim="x", deg=1)

        self.assertEqual(out.dims, ["x"])
        self.assertEqual(out.shape, self.complex_data.shape)
        assert_allclose(out.values, self.complex_baseline)

    def test_background_with_custom_fit_function(self):
        out = background(self.baseline_data, dim="x", func=linear, p0=(1.0, 1.0))

        self.assertEqual(out.dims, ["x"])
        self.assertEqual(out.proc_attrs[-1][0], "background")
        self.assertEqual(out.proc_attrs[-1][1]["func"], "linear")
        self.assertEqual(out.proc_attrs[-1][1]["p0"], (1.0, 1.0))
        assert_allclose(out.values, self.baseline, atol=1e-12)

    def test_remove_background_constant_fit(self):
        values = np.ones_like(self.x) * 4.0
        data = sl.SpinData(values, dims=["x"], coords=[self.x])

        out = remove_background(data, dim="x", deg=0)

        self.assertEqual(out.dims, ["x"])
        self.assertEqual(out.shape, data.shape)
        self.assertEqual(out.proc_attrs[-1][0], "remove_background")
        self.assertEqual(
            out.proc_attrs[-1][1],
            {"dim": "x", "deg": 0, "regions": None, "func": None},
        )
        assert_allclose(out.values, np.zeros_like(values), atol=1e-12)

    def test_remove_background_defaults_to_first_dim(self):
        out = remove_background(self.data_2d, deg=1)

        self.assertEqual(out.dims, ["x", "scan"])
        self.assertEqual(out.shape, self.data_2d.shape)
        self.assertEqual(out.proc_attrs[-1][1]["dim"], "x")
        assert_allclose(out.values, np.zeros_like(self.baseline_2d), atol=1e-12)

    def test_remove_background_linear_regions_preserves_signal(self):
        regions = [(-1.0, -0.5), (0.5, 1.0)]

        out = remove_background(self.data_1d, dim="x", deg=1, regions=regions)

        self.assertEqual(out.dims, ["x"])
        self.assertEqual(out.shape, self.data_1d.shape)
        assert_array_equal(out.coords["x"], self.x)
        self.assertEqual(out.proc_attrs[-1][0], "remove_background")
        self.assertEqual(out.proc_attrs[-1][1]["regions"], regions)
        assert_allclose(out.values, self.signal, atol=1e-12)

    def test_remove_background_2d_along_first_dim(self):
        out = remove_background(self.data_2d, dim="x", deg=1)

        self.assertEqual(out.dims, ["x", "scan"])
        self.assertEqual(out.shape, self.data_2d.shape)
        assert_array_equal(out.coords["scan"], self.scan)
        assert_allclose(out.values, np.zeros_like(self.baseline_2d), atol=1e-12)

    def test_remove_background_complex_data(self):
        out = remove_background(self.complex_data, dim="x", deg=1)

        self.assertEqual(out.dims, ["x"])
        assert_allclose(out.values, np.zeros_like(self.complex_baseline), atol=1e-12)

    def test_background_invalid_dim_raises_value_error(self):
        with self.assertRaises(ValueError):
            background(self.data_1d, dim="not_a_dim", deg=1)

    def test_remove_background_invalid_dim_raises_value_error(self):
        with self.assertRaises(ValueError):
            remove_background(self.data_1d, dim="not_a_dim", deg=1)

    def test_background_does_not_mutate_input(self):
        original_values = self.data_1d.values.copy()
        original_coords = self.data_1d.coords["x"].copy()
        original_dims = self.data_1d.dims.copy()

        background(self.data_1d, dim="x", deg=1)

        self.assertEqual(self.data_1d.dims, original_dims)
        assert_array_equal(self.data_1d.coords["x"], original_coords)
        assert_allclose(self.data_1d.values, original_values)

    def test_remove_background_does_not_mutate_input(self):
        original_values = self.data_1d.values.copy()
        original_coords = self.data_1d.coords["x"].copy()
        original_dims = self.data_1d.dims.copy()

        remove_background(self.data_1d, dim="x", deg=1)

        self.assertEqual(self.data_1d.dims, original_dims)
        assert_array_equal(self.data_1d.coords["x"], original_coords)
        assert_allclose(self.data_1d.values, original_values)


if __name__ == "__main__":
    unittest.main()
