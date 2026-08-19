import os
import unittest

import spinlab as sl
from numpy.testing import assert_array_equal


class topspin_format_tester(unittest.TestCase):
    def setUp(self):
        self.testdata = os.path.join(".", "data", "topspin")

    def test_import_topspin_exp1_is_fid(self):
        data = sl.io.formats.topspin.import_topspin(os.path.join(self.testdata, "1"))
        self.assertEqual(data.dims[0], "t2")
        self.assertEqual(data.values.size, 8192)
        self.assertAlmostEqual(data.attrs["nmr_frequency"], 14831413.270000001)

    def test_import_topspin_exp5_is_2d_phcyc(self):
        data = sl.io.formats.topspin.import_topspin(os.path.join(self.testdata, "5"))
        self.assertEqual(data.values.shape[0], 11973)
        self.assertEqual(data.dims, ["t2", "t1"])
        self.assertAlmostEqual(data.attrs["nmr_frequency"], 14831413.270000001)

    def test_import_topspin_exp28_is_2d(self):
        data = sl.io.formats.topspin.import_topspin(os.path.join(self.testdata, "28"))
        self.assertEqual(data.values.shape, (7983, 8))
        self.assertEqual(data.dims, ["t2", "t1"])
        self.assertAlmostEqual(data.attrs["nmr_frequency"], 14831413.270000001)

    def test_load_topspin_jcamp_dx(self):
        attrs = sl.io.formats.topspin.load_topspin_jcamp_dx(
            os.path.join(self.testdata, "1", "acqus")
        )
        self.assertEqual(attrs["DIGTYP"], 9)
        self.assertAlmostEqual(attrs["O1"], 1413.27)
        assert_array_equal(attrs["XGAIN"], [0, 0, 0, 0])
        assert_array_equal(attrs["TPOAL"], [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])


if __name__ == "__main__":
    unittest.main()
