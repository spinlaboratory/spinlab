import os
import unittest

import numpy as np
import spinlab as sl


class power_auxiliary_tester(unittest.TestCase):
    def test_import_power_mat_file(self):
        t, p = sl.io.auxiliary.power.import_power(
            os.path.join(".", "data", "topspin", "power.mat")
        )

        self.assertEqual(t.shape, p.shape)
        self.assertGreater(t.size, 0)
        self.assertTrue(np.isfinite(t).all())
        self.assertTrue(np.isfinite(p).all())
        self.assertAlmostEqual(t[0], 0.28200006)
        self.assertAlmostEqual(p[0], -23.388)

    def test_import_power_rejects_unknown_extension(self):
        result = sl.io.auxiliary.power.import_power("unknown.txt")

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
