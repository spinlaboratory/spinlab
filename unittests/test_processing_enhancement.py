import unittest

import numpy as np
import spinlab as sl

from spinlab.processing.enhancement import calculate_enhancement


class sl_enhancement_tester(unittest.TestCase):
    def test_calculate_enhancement_for_power_integrals(self):
        values = np.array([2 + 2j, 4 + 4j, 1 + 1j])
        data = sl.SpinData(values, ["Power"], [np.array([0, 1, 2])])
        data.attrs["experiment_type"] = "integrals"

        out = calculate_enhancement(data, off_spectrum_index=0, return_complex_values=True)

        np.testing.assert_allclose(out.values, np.array([1 + 0j, 2 + 0j, 0.5 + 0j]))
        self.assertEqual(out.attrs["experiment_type"], "enhancements_P")
        self.assertEqual(out.proc_attrs[-1][0], "calculate_enhancement")

    def test_calculate_enhancement_returns_real_by_default(self):
        values = np.array([2 + 2j, 4 + 4j])
        data = sl.SpinData(values, ["Power"], [np.array([0, 1])])
        data.attrs["experiment_type"] = "integrals"

        out = calculate_enhancement(data, off_spectrum_index=0)

        np.testing.assert_allclose(out.values, np.array([1, 2]))

    def test_calculate_enhancement_rejects_non_integrals(self):
        data = sl.SpinData(np.ones(2), ["Power"], [np.array([0, 1])])
        data.attrs["experiment_type"] = "spectrum"

        with self.assertRaises(ValueError):
            calculate_enhancement(data)

    def test_calculate_enhancement_requires_experiment_type(self):
        data = sl.SpinData(np.ones(2), ["Power"], [np.array([0, 1])], attrs={})

        with self.assertRaises(KeyError):
            calculate_enhancement(data)


if __name__ == "__main__":
    unittest.main()
