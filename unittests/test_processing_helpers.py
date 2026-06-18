import unittest

import numpy as np
import spinlab as sl
from numpy.testing import assert_array_equal

from spinlab.processing import helpers
from spinlab.processing.axis import left_shift, reference
from spinlab.processing.complex_data import create_complex
from spinlab.processing.enhancement import calculate_enhancement
from spinlab.processing.modulation import pseudo_modulation
from spinlab.processing.normalization import normalize
from spinlab.processing.smoothing import smooth
from spinlab.processing.snr import signal_to_noise


class sl_processing_helpers_tester(unittest.TestCase):
    def setUp(self):
        self.data = sl.SpinData(np.arange(6).reshape(3, 2), ["x", "scan"], [np.arange(3), np.arange(2)])

    def test_compatibility_exports_point_to_canonical_functions(self):
        self.assertIs(helpers.left_shift, left_shift)
        self.assertIs(helpers.reference, reference)
        self.assertIs(helpers.create_complex, create_complex)
        self.assertIs(helpers.calculate_enhancement, calculate_enhancement)
        self.assertIs(helpers.pseudo_modulation, pseudo_modulation)
        self.assertIs(helpers.normalize, normalize)
        self.assertIs(helpers.smooth, smooth)
        self.assertIs(helpers.signal_to_noise, signal_to_noise)
        self.assertIs(sl.processing.helpers.normalize, normalize)
        self.assertIs(sl.processing.normalize, normalize)
        self.assertIs(sl.normalize, normalize)

    def test_get_default_dim(self):
        self.assertEqual(helpers.get_default_dim(self.data, None, "test"), "x")
        self.assertEqual(helpers.get_default_dim(self.data, "scan", "test"), "scan")

        empty = sl.SpinData(np.array([]), [], [])
        with self.assertRaises(ValueError):
            helpers.get_default_dim(empty, None, "test")

    def test_validate_dim(self):
        self.assertEqual(helpers.validate_dim(self.data, "x"), "x")
        with self.assertRaises(ValueError):
            helpers.validate_dim(self.data, "missing")

    def test_normalize_region_input(self):
        self.assertIsNone(helpers.normalize_region_input(None))
        self.assertEqual(helpers.normalize_region_input((1, 2)), [(1, 2)])
        self.assertEqual(helpers.normalize_region_input([1, 2]), [(1, 2)])
        self.assertEqual(helpers.normalize_region_input([(1, 2), (3, 4)]), [(1, 2), (3, 4)])
        self.assertEqual(helpers.normalize_region_input(slice(0, 2)), [slice(0, 2)])

    def test_ensure_1d_coord(self):
        coord = helpers.ensure_1d_coord([0, 1, 2], "x")
        assert_array_equal(coord, np.array([0, 1, 2]))

        with self.assertRaises(ValueError):
            helpers.ensure_1d_coord(np.ones((2, 2)), "x")
        with self.assertRaises(ValueError):
            helpers.ensure_1d_coord([], "x")

    def test_require_min_coord_size(self):
        coord = helpers.require_min_coord_size([0, 1], "x", 2, "test")
        assert_array_equal(coord, np.array([0, 1]))

        with self.assertRaises(ValueError):
            helpers.require_min_coord_size([0], "x", 2, "test")

    def test_monotonic_direction(self):
        self.assertEqual(helpers.monotonic_direction([0, 1, 2], "x"), 1)
        self.assertEqual(helpers.monotonic_direction([2, 1, 0], "x"), -1)

        with self.assertRaises(ValueError):
            helpers.monotonic_direction([0, 2, 1], "x")

    def test_validate_matching_coord_direction(self):
        self.assertEqual(
            helpers.validate_matching_coord_direction([0, 1, 2], [0, 0.5, 1], "x"),
            1,
        )
        self.assertEqual(
            helpers.validate_matching_coord_direction([2, 1, 0], [2, 1.5, 1], "x"),
            -1,
        )

        with self.assertRaises(ValueError):
            helpers.validate_matching_coord_direction([0, 1, 2], [1, 0], "x")

    def test_evenly_spaced_coord_spacing(self):
        self.assertEqual(helpers.evenly_spaced_coord_spacing([0, 2, 4], "x"), 2)

        with self.assertRaises(ValueError):
            helpers.evenly_spaced_coord_spacing([0, 1, 3], "x")

    def test_reshape_along_dim(self):
        out = helpers.reshape_along_dim(np.array([1, 2, 3]), self.data, "x")
        self.assertEqual(out.shape, (3, 1))
        assert_array_equal(out[:, 0], np.array([1, 2, 3]))


if __name__ == "__main__":
    unittest.main()
