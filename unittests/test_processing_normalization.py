import unittest

import numpy as np
import spinlab as sl
from numpy.testing import assert_allclose

from spinlab.processing.normalization import normalize


class sl_normalization_tester(unittest.TestCase):
    def setUp(self):
        self.t2 = np.arange(5)
        self.scan = np.arange(2)
        self.values = np.array(
            [
                [1.0, 2.0],
                [2.0, 4.0],
                [4.0, 8.0],
                [8.0, 16.0],
                [16.0, 32.0],
            ]
        )
        self.data = sl.SpinData(self.values.copy(), ["t2", "scan"], [self.t2, self.scan])
        self.data_1d = sl.SpinData(self.values[:, 0].copy(), ["t2"], [self.t2])

    def test_normalize_rejects_missing_dim(self):
        with self.assertRaises(ValueError):
            normalize(self.data, dim="f2")

    def test_normalize_global_amplitude(self):
        out = normalize(self.data)

        assert_allclose(out.values, self.values / 32.0)
        self.assertEqual(out.proc_attrs[-1][0], "normalized")

    def test_normalize_1d_global_amplitude(self):
        out = normalize(self.data_1d)

        assert_allclose(out.values, self.values[:, 0] / 16.0)

    def test_normalize_along_dim(self):
        out = normalize(self.data, dim="t2")

        expected = self.values / np.array([16.0, 32.0]).reshape(1, -1)
        assert_allclose(out.values, expected)
        assert_allclose(out.values[-1], np.ones(2))

    def test_normalize_1d_along_dim(self):
        out = normalize(self.data_1d, dim="t2")

        assert_allclose(out.values, self.values[:, 0] / 16.0)

    def test_normalize_along_dim_with_region(self):
        out = normalize(self.data, dim="t2", regions=(1, 3))

        expected = self.values / np.array([4.0, 8.0]).reshape(1, -1)
        assert_allclose(out.values, expected)
        assert_allclose(np.max(out["t2", (1, 3)].values, axis=0), np.ones(2))

    def test_normalize_global_with_region(self):
        out = normalize(self.data, regions=(1, 3))

        assert_allclose(out.values, self.values / 8.0)
        assert_allclose(np.max(out["t2", (1, 3)].values), 1.0)


if __name__ == "__main__":
    unittest.main()
