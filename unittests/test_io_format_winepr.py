import os
import unittest

import spinlab as sl


class winepr_format_tester(unittest.TestCase):
    def setUp(self):
        self.test_data_esp = os.path.join(".", "data", "parspc", "ExampleESP.par")
        self.test_data_1d = os.path.join(".", "data", "parspc", "Example1D.spc")
        self.test_data_2d = os.path.join(".", "data", "parspc", "Example2D.spc")

    def test_import_winepr_esp(self):
        data = sl.io.formats.winepr.import_winepr(self.test_data_esp)
        self.assertEqual(data.dims, ["t2"])
        self.assertEqual(data.values.shape, (1024,))
        self.assertEqual(data.attrs["conversion_time"], 81.92)

    def test_import_winepr_1d(self):
        data = sl.io.formats.winepr.import_winepr(self.test_data_1d)
        self.assertEqual(data.dims, ["B0"])
        self.assertEqual(data.values.shape, (512,))
        self.assertEqual(data.attrs["temperature"], 294.2)

    def test_import_winepr_2d(self):
        data = sl.io.formats.winepr.import_winepr(self.test_data_2d)
        self.assertEqual(data.dims, ["B0", "t1"])
        self.assertEqual(data.values.shape, (1024, 15))
        self.assertEqual(data.attrs["frequency"], 9.79)


if __name__ == "__main__":
    unittest.main()
