import unittest

import numpy as np
import spinlab as sl
from numpy.testing import assert_allclose, assert_array_equal


def gaussian(x, center, width=0.02, amplitude=1.0):
    return amplitude * np.exp(-((x - center) ** 2) / width)


class slAnalysisPeaksTester(unittest.TestCase):
    def setUp(self):
        self.x = np.linspace(-2.0, 2.0, 101)
        self.frequency = 400e6
        self.values = gaussian(self.x, 0.48)
        self.data = sl.SpinData(
            self.values,
            ["x"],
            [self.x],
            spinlab_attrs={"frequency": self.frequency},
        )

    def test_find_peaks_defaults_to_first_dim(self):
        out = sl.find_peaks(self.data, normalize=False, height=0.5)

        self.assertEqual(out.dims, ["peak_info", "index"])
        assert_array_equal(out.coords["index"], np.array([0]))
        self.assertEqual(out.attrs["experiment_type"], "peak_list")
        self.assertEqual(out.attrs["data_type"], "peak_list")
        self.assertEqual(out.proc_attrs[-1][0], "peak_list")
        self.assertEqual(out.proc_attrs[-1][1]["dims"], "x")
        assert_allclose(out.values[0], np.array([62]))
        assert_allclose(out.values[1], np.array([0.48]))
        assert_allclose(out.values[2], np.array([self.values[62]]))
        self.assertGreater(out.values[3, 0], 0)

    def test_find_peaks_accepts_dim_alias(self):
        out = sl.find_peaks(self.data, dim="x", normalize=False, height=0.5)

        assert_allclose(out.values[0], np.array([62]))

    def test_find_peaks_uses_legacy_nmr_frequency_fallback(self):
        data = sl.SpinData(
            self.values,
            ["x"],
            [self.x],
            attrs={"nmr_frequency": self.frequency},
        )

        out = sl.find_peaks(data, normalize=False, height=0.5)

        assert_allclose(out.values[0], np.array([62]))
        self.assertGreater(out.values[3, 0], 0)

    def test_find_peaks_multiple_regions_keep_original_indices(self):
        values = gaussian(self.x, -0.6) + gaussian(self.x, 0.6)
        data = sl.SpinData(
            values,
            ["x"],
            [self.x],
            spinlab_attrs={"frequency": self.frequency},
        )

        out = sl.find_peaks(
            data,
            normalize=False,
            regions=[(-0.8, -0.4), (0.4, 0.8)],
            height=0.5,
        )

        assert_array_equal(out.values[0].astype(int), np.array([35, 65]))
        assert_allclose(out.values[1], np.array([-0.6, 0.6]))

    def test_find_peaks_normalizes_negative_peak_for_detection(self):
        values = -gaussian(self.x, 0.48)
        data = sl.SpinData(
            values,
            ["x"],
            [self.x],
            spinlab_attrs={"frequency": self.frequency},
        )

        out = sl.find_peaks(data, normalize=True, height=0.5)

        assert_array_equal(out.values[0].astype(int), np.array([62]))
        assert_allclose(out.values[2], np.array([values[62]]))
        self.assertLess(out.values[2, 0], 0)

    def test_find_peaks_uses_real_part_of_complex_data(self):
        values = self.values + 1j * np.linspace(0.0, 1.0, self.x.size)
        data = sl.SpinData(
            values,
            ["x"],
            [self.x],
            spinlab_attrs={"frequency": self.frequency},
        )

        out = sl.find_peaks(data, normalize=False, height=0.5)

        assert_array_equal(out.values[0].astype(int), np.array([62]))
        assert_allclose(out.values[2], np.array([self.values[62]]))

    def test_find_peaks_2d_data_can_use_non_last_peak_dim(self):
        scan = np.array([0, 1])
        values = np.stack(
            [gaussian(self.x, 0.48), gaussian(self.x, -0.48)],
            axis=0,
        )
        data = sl.SpinData(
            values,
            ["scan", "x"],
            [scan, self.x],
            spinlab_attrs={"frequency": self.frequency},
        )

        out = sl.find_peaks(data, dims="x", normalize=False, height=0.5)

        self.assertEqual(out.dims, ["peak_info", "index", "scan"])
        assert_array_equal(out.coords["scan"], scan)
        assert_array_equal(out.values[0, 0, :].astype(int), np.array([62, 38]))
        assert_allclose(out.values[1, 0, :], np.array([0.48, -0.48]))

    def test_find_peaks_invalid_inputs_raise_value_error(self):
        with self.assertRaises(ValueError):
            sl.find_peaks(self.data, dims="missing")

        with self.assertRaises(ValueError):
            sl.find_peaks(self.data, dims="x", dim="x")

        data_without_frequency = sl.SpinData(self.values, ["x"], [self.x])
        with self.assertRaises(ValueError):
            sl.find_peaks(data_without_frequency, normalize=False, height=0.5)


if __name__ == "__main__":
    unittest.main()
