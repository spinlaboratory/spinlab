import os
import unittest

import spinlab as sl


class cnsi_auxiliary_tester(unittest.TestCase):
    def test_get_powers_from_topspin_power_file(self):
        powers = sl.io.auxiliary.cnsi.get_powers(
            os.path.join(".", "data", "topspin"), "power", [1, 10]
        )

        self.assertEqual(len(powers), 2)
        self.assertAlmostEqual(powers[0], -5.231)
        self.assertAlmostEqual(powers[1], -15.689)

    def test_get_powers_rejects_unknown_power_file_name(self):
        with self.assertRaises(TypeError):
            sl.io.auxiliary.cnsi.get_powers(
                os.path.join(".", "data", "topspin"), "not_power", [1]
            )


if __name__ == "__main__":
    unittest.main()
