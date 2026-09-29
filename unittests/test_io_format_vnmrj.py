import os
import unittest

import spinlab as sl


class vnmrj_format_tester(unittest.TestCase):
    def setUp(self):
        self.test_data_2d = [
            os.path.join(".", "data", "vnmrj", "10mM_tempol_in_water_array.fid")
        ]
        self.test_data_1d = [
            os.path.join(".", "data", "vnmrj", name)
            for name in [
                "10mM_tempol_in_water_mw_40dBm.fid",
                "10mM_tempol_in_water_mw_off.fid",
            ]
        ]

    def test_import_vnmrj_1d(self):
        datas = [sl.io.formats.vnmrj.import_vnmrj(path) for path in self.test_data_1d]
        for data in datas:
            self.assertEqual(data.values.shape, (131072,))
            self.assertEqual(data.dims, ["t2"])
            self.assertAlmostEqual(data.attrs["nmr_frequency"], 14244283.4231)
        self.assertAlmostEqual(datas[0].values[365], (-20378767 + 2734659j))
        self.assertAlmostEqual(datas[1].values[365], (-950662 - 138458j))

    def test_import_vnmrj_2d(self):
        datas = [sl.io.formats.vnmrj.import_vnmrj(path) for path in self.test_data_2d]
        for data in datas:
            self.assertEqual(data.values.shape, (131072, 5))
            self.assertEqual(data.dims, ["t2", "t1"])
            self.assertAlmostEqual(data.attrs["nmr_frequency"], 14244283.4231)
        self.assertAlmostEqual(datas[0].values[365, 3], (-1263136 - 1063328.5j))


if __name__ == "__main__":
    unittest.main()
