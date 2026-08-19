import os
import unittest

import spinlab as sl


class delta_format_tester(unittest.TestCase):
    def setUp(self):
        self.test_data_1d = os.path.join(".", "data", "delta", "50percCHCL3.jdf")
        self.test_data_2d = os.path.join(".", "data", "delta", "lineshape_drift.jdf")

    def test_import_delta_1d(self):
        data = sl.io.formats.delta.import_delta(self.test_data_1d)
        self.assertEqual(data.dims, ["t2"])
        self.assertEqual(data.values.shape, (16384,))
        self.assertEqual(max(data.coords["t2"]), 0.262128)

    def test_import_delta_2d(self):
        data = sl.io.formats.delta.import_delta(self.test_data_2d)
        self.assertEqual(data.dims, ["t2", "t1"])
        self.assertEqual(data.values.shape, (8192, 256))
        self.assertEqual(max(data.coords["t2"]), 0.5451929600000001)
        self.assertEqual(max(data.coords["t1"]), 11.953125)


if __name__ == "__main__":
    unittest.main()
