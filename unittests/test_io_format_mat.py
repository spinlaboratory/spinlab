import os
import unittest

import numpy as np
import spinlab as sl
from numpy.testing import assert_array_equal


class mat_format_tester(unittest.TestCase):
    def setUp(self):
        self.filename = os.path.join(".", "unittests", "test_io_format_mat.mat")
        self.data = sl.SpinData(
            np.arange(6).reshape(3, 2),
            ["x", "scan"],
            [np.arange(3), np.array([10, 20])],
            attrs={"label": "matrix"},
            spinlab_attrs={"data_type": "test"},
        )

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_save_and_import_mat_roundtrip(self):
        sl.io.formats.mat.save_mat(self.data, self.filename)

        loaded = sl.io.formats.mat.import_mat(self.filename)

        assert_array_equal(loaded.values, self.data.values)
        self.assertEqual(loaded.dims, self.data.dims)
        assert_array_equal(loaded.coords["x"], self.data.coords["x"])
        assert_array_equal(loaded.coords["scan"], self.data.coords["scan"])
        self.assertEqual(loaded.attrs["label"], "matrix")
        self.assertEqual(loaded.spinlab_attrs["data_type"], "test")


if __name__ == "__main__":
    unittest.main()
