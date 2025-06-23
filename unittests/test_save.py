import unittest
import spinlab as sl
import os
from numpy.testing import assert_array_equal
import numpy as np


class save_h5_tester(unittest.TestCase):
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


if __name__ == "__main__":
    pass
