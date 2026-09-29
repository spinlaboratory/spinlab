import os
import unittest

import spinlab as sl


class prospa_format_tester(unittest.TestCase):
    def setUp(self):
        self.test_data = os.path.join(".", "data", "prospa", "toluene_10mM_Tempone")

    def test_import_prospa_exp_is_1d(self):
        datas = [
            sl.io.formats.prospa.import_prospa(
                os.path.join(self.test_data, "%i" % exp_num, "data.csv")
            )
            for exp_num in [1, 21, 42]
        ]
        for data in datas:
            self.assertEqual(data.values.shape, (16384,))
            self.assertEqual(data.dims, ["t2"])
            self.assertAlmostEqual(data.attrs["nmr_frequency"], 14244500.0)
        self.assertAlmostEqual(datas[0].values[365], -0.217937 + 0.24907j)
        self.assertAlmostEqual(datas[1].values[365], 0.0400292 - 0.0756107j)
        self.assertAlmostEqual(datas[2].values[365], 1.09858 - 2.57966j)


if __name__ == "__main__":
    unittest.main()
