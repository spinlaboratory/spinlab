import os
import unittest

import numpy as np
import spinlab as sl
from numpy.testing import assert_array_equal


class h5_format_tester(unittest.TestCase):
    def setUp(self):
        self.filename = os.path.join(".", "unittests", "test_io_format_h5.h5")
        self.data = sl.SpinData(np.arange(5), ["x"], [np.arange(5)])

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_save_and_load_single_spindata(self):
        sl.io.formats.h5.save_h5({"__SpinDATA__": self.data}, self.filename, overwrite=True)

        loaded = sl.io.formats.h5.load_h5(self.filename)

        assert_array_equal(loaded.values, self.data.values)
        self.assertEqual(loaded.dims, self.data.dims)
        assert_array_equal(loaded.coords["x"], self.data.coords["x"])

    def test_save_and_load_workspace_dict(self):
        sl.io.formats.h5.save_h5({"data": self.data}, self.filename, overwrite=True)

        loaded = sl.io.formats.h5.load_h5(self.filename)

        self.assertIn("data", loaded)
        assert_array_equal(loaded["data"].values, self.data.values)


if __name__ == "__main__":
    unittest.main()
