import logging
import unittest

import numpy as np
import spinlab as sl
from numpy.testing import assert_array_equal

from spinlab.processing.align import ndalign


# logging.basicConfig(filename='align_debug.log', encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)


class sl_align_tester(unittest.TestCase):
    def setUp(self):
        self.x = np.arange(13)
        self.scan = np.arange(3)
        self.reference_peak = np.array([0, 0, 0, 1, 2, 3, 4, 3, 2, 1, 0, 0, 0])
        self.left_shifted_peak = np.array([0, 1, 2, 3, 4, 3, 2, 1, 0, 0, 0, 0, 0])
        self.right_shifted_peak = np.array([0, 0, 0, 0, 0, 1, 2, 3, 4, 3, 2, 1, 0])
        self.values = np.array(
            [self.reference_peak, self.left_shifted_peak, self.right_shifted_peak]
        ).T
        self.data = sl.SpinData(
            self.values,
            dims=["x", "scan"],
            coords=[self.x, self.scan],
        )
        self.expected = np.array([self.reference_peak] * 3).T

    def test_ndalign_defaults_to_first_dim(self):
        out = ndalign(self.data)

        self.assertEqual(out.dims, ["x", "scan"])
        self.assertEqual(out.shape, self.data.shape)
        self.assertEqual(out.proc_attrs[-1][0], "ndalign")
        self.assertEqual(out.proc_attrs[-1][1]["dim"], "x")
        self.assertIsNone(out.proc_attrs[-1][1]["reference"])
        self.assertIsNone(out.proc_attrs[-1][1]["reference_shape"])
        assert_array_equal(out.coords["x"], self.x)
        assert_array_equal(out.coords["scan"], self.scan)
        assert_array_equal(out.values, self.expected)

    def test_ndalign_explicit_dim(self):
        out = ndalign(self.data, dim="x")

        assert_array_equal(out.values, self.expected)
        self.assertEqual(out.proc_attrs[-1][1]["dim"], "x")

    def test_ndalign_with_center_and_width(self):
        out = ndalign(self.data, dim="x", center=6, width=8)

        assert_array_equal(out.values, self.expected)
        self.assertEqual(out.proc_attrs[-1][1]["center"], 6)
        self.assertEqual(out.proc_attrs[-1][1]["width"], 8)

    def test_ndalign_with_array_reference(self):
        out = ndalign(self.data, dim="x", reference=self.reference_peak)

        assert_array_equal(out.values, self.expected)
        self.assertEqual(out.proc_attrs[-1][1]["reference"], "ndarray")
        self.assertEqual(out.proc_attrs[-1][1]["reference_shape"], self.reference_peak.shape)

    def test_ndalign_with_spindata_reference(self):
        reference = sl.SpinData(self.reference_peak, dims=["x"], coords=[self.x])

        out = ndalign(self.data, dim="x", reference=reference)

        assert_array_equal(out.values, self.expected)
        self.assertEqual(out.proc_attrs[-1][1]["reference"], "SpinData")
        self.assertEqual(out.proc_attrs[-1][1]["reference_shape"], reference.shape)

    def test_ndalign_with_selected_range_reference(self):
        selected_reference = self.reference_peak[:-1]

        out = ndalign(self.data, dim="x", reference=selected_reference)

        assert_array_equal(out.values, self.expected)

    def test_ndalign_with_decreasing_coord(self):
        data = sl.SpinData(
            self.values[::-1, :],
            dims=["x", "scan"],
            coords=[self.x[::-1], self.scan],
        )

        out = ndalign(data)

        self.assertEqual(out.dims, ["x", "scan"])
        assert_array_equal(out.coords["x"], self.x[::-1])
        assert_array_equal(out.values[::-1, :], self.expected)

    def test_ndalign_preserves_complex_dtype(self):
        data = sl.SpinData(
            self.values.astype(complex) * (1.0 + 1.0j),
            dims=["x", "scan"],
            coords=[self.x, self.scan],
        )

        out = ndalign(data, dim="x")

        self.assertTrue(np.iscomplexobj(out.values))
        assert_array_equal(out.values, self.expected * (1.0 + 1.0j))

    def test_ndalign_center_and_width_must_be_supplied_together(self):
        with self.assertRaises(ValueError):
            ndalign(self.data, dim="x", center=6)
        with self.assertRaises(ValueError):
            ndalign(self.data, dim="x", width=8)

    def test_ndalign_width_must_be_positive(self):
        with self.assertRaises(ValueError):
            ndalign(self.data, dim="x", center=6, width=0)

    def test_ndalign_empty_selected_range_raises_value_error(self):
        with self.assertRaises(ValueError):
            ndalign(self.data, dim="x", center=100, width=1)

    def test_ndalign_reference_length_must_match_range_or_full_dim(self):
        with self.assertRaises(ValueError):
            ndalign(self.data, dim="x", reference=np.array([1, 2, 3]))

    def test_ndalign_invalid_dim_raises_value_error(self):
        with self.assertRaises(ValueError):
            ndalign(self.data, dim="not_a_dim")

    def test_ndalign_does_not_mutate_input(self):
        original_values = self.data.values.copy()
        original_x = self.data.coords["x"].copy()
        original_scan = self.data.coords["scan"].copy()
        original_dims = self.data.dims.copy()

        ndalign(self.data, dim="x")

        self.assertEqual(self.data.dims, original_dims)
        assert_array_equal(self.data.coords["x"], original_x)
        assert_array_equal(self.data.coords["scan"], original_scan)
        assert_array_equal(self.data.values, original_values)


if __name__ == "__main__":
    unittest.main()
