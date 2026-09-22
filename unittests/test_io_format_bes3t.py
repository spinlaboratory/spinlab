import os
import unittest

import spinlab as sl


class bes3t_format_tester(unittest.TestCase):
    def setUp(self):
        self.test_data_hyscore = os.path.join(".", "data", "bes3t", "HYSCORE.DSC")
        self.test_data_deer = os.path.join(".", "data", "bes3t", "DEER.DSC")
        self.test_data_ese = os.path.join(".", "data", "bes3t", "2D_ESE.DTA")
        self.test_data_1d = os.path.join(".", "data", "bes3t", "1D_CW.DTA")
        self.test_data_2d = os.path.join(".", "data", "bes3t", "2D_CW.YGF")
        self.test_data_cw_time_sweep = os.path.join(
            ".", "data", "bes3t", "CW_time_sweep.DSC"
        )

    def test_import_bes3t_hyscore(self):
        data = sl.io.formats.bes3t.import_bes3t(self.test_data_hyscore)
        self.assertEqual(data.dims, ["t2", "t1"])
        self.assertEqual(data.values.shape, (175, 175))
        self.assertEqual(max(data.coords["t2"]), 3520.0)
        self.assertEqual(max(data.coords["t1"]), 3520.0)

    def test_import_bes3t_deer(self):
        data = sl.io.formats.bes3t.import_bes3t(self.test_data_deer)
        self.assertEqual(data.dims, ["t2"])
        self.assertEqual(data.values.shape, (504,))
        self.assertEqual(data.attrs["frequency"], 33.85)

    def test_import_bes3t_ese(self):
        data = sl.io.formats.bes3t.import_bes3t(self.test_data_ese)
        self.assertEqual(data.dims, ["t2", "t1"])
        self.assertEqual(data.values.shape, (512, 50))
        self.assertEqual(data.attrs["frequency"], 9.296)

    def test_import_bes3t_1d(self):
        data = sl.io.formats.bes3t.import_bes3t(self.test_data_1d)
        self.assertEqual(data.dims, ["B0"])
        self.assertEqual(data.values.shape, (2250,))
        self.assertEqual(data.attrs["frequency"], 9.804448)

    def test_import_bes3t_2d(self):
        data = sl.io.formats.bes3t.import_bes3t(self.test_data_2d)
        self.assertEqual(data.dims, ["B0", "t1"])
        self.assertEqual(data.values.shape, (1600, 100))
        self.assertEqual(data.attrs["frequency"], 9.627213)
        self.assertEqual(data.coords["t1"][0], 0.0)
        self.assertEqual(data.coords["t1"][-1], 2180.53)

    def test_import_bes3t_cw_time_sweep(self):
        data = sl.io.formats.bes3t.import_bes3t(self.test_data_cw_time_sweep)
        self.assertEqual(data.dims, ["t2", "t1"])
        self.assertEqual(data.values.shape, (1000, 10))
        self.assertEqual(data.attrs["frequency"], 9.834281)
        self.assertEqual(data.coords["t1"][0], 1499.95)
        self.assertEqual(data.coords["t1"][-1], 1500.0500000000002)


if __name__ == "__main__":
    unittest.main()
