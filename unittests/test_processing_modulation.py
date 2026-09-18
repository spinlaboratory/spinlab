import unittest

import numpy as np
import spinlab as sl

from spinlab.processing.modulation import pseudo_modulation


class sl_modulation_tester(unittest.TestCase):
    def test_pseudo_modulation_preserves_axis_and_records_proc_attrs(self):
        x = np.linspace(-1, 1, 64)
        values = np.exp(-(x**2) / 0.1)
        data = sl.SpinData(values, ["B0"], [x])

        out = pseudo_modulation(data, modulation_amplitude=0.01, dim="B0")

        self.assertEqual(out.dims, ["B0"])
        self.assertEqual(out.shape, data.shape)
        self.assertTrue(np.isrealobj(out.values))
        self.assertEqual(out.proc_attrs[-1][0], "pseudo_modulation")
        self.assertEqual(out.proc_attrs[-1][1]["dim"], "B0")


if __name__ == "__main__":
    unittest.main()
