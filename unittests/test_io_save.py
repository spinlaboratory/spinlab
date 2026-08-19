import unittest
import spinlab as sl
import os
from numpy.testing import assert_array_equal
import numpy as np


class io_save_tester(unittest.TestCase):
    def setUp(self):
        self.x = np.r_[0:10]
        self.y = self.x**2
        self.data = sl.SpinData(self.y, ["x"], [self.x])

        self.ws = {"data": self.data}

    def test_h5_save(self):
        sl.save(
            self.data,
            os.path.join(".", "unittests", "test_save_SpinData.h5"),
            overwrite=True,
        )

        os.remove(os.path.join(".", "unittests", "test_save_SpinData.h5"))

    def test_h5_save_ws(self):
        sl.save(
            self.ws,
            os.path.join(".", "unittests", "test_save_SpinData_dict.h5"),
            overwrite=True,
        )

        os.remove(os.path.join(".", "unittests", "test_save_SpinData_dict.h5"))

    def test_mat_save_and_load_roundtrip(self):
        self.data.attrs["label"] = "quadratic"
        self.data.spinlab_attrs["data_type"] = "test"
        filename = os.path.join(".", "unittests", "test_save_SpinData.mat")

        sl.save(self.data, filename)
        loaded = sl.load(filename)

        assert_array_equal(loaded.values, self.data.values)
        self.assertEqual(loaded.dims, self.data.dims)
        assert_array_equal(loaded.coords["x"], self.data.coords["x"])
        self.assertEqual(loaded.attrs["label"], "quadratic")
        self.assertEqual(loaded.spinlab_attrs["data_type"], "test")

        os.remove(filename)

    def test_detect_save_format_is_case_insensitive_for_extensions(self):
        self.assertEqual(sl.io.save._detect_save_format("example.H5"), "h5")
        self.assertEqual(sl.io.save._detect_save_format("example.h5"), "h5")
        self.assertEqual(sl.io.save._detect_save_format("example.MAT"), "mat")
        self.assertEqual(sl.io.save._detect_save_format("example.mat"), "mat")


if __name__ == "__main__":
    pass
