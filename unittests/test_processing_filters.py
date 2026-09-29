import unittest

import numpy as np
import spinlab as sl

from spinlab.processing.filters import low_pass, smooth


class sl_smoothing_tester(unittest.TestCase):
    def test_smooth_preserves_shape_dims_and_records_proc_attrs(self):
        x = np.arange(11)
        values = x.astype(float) ** 2
        data = sl.SpinData(values, ["t2"], [x])

        out = smooth(data, dim="t2", window_length=5, polyorder=2)

        self.assertEqual(out.shape, data.shape)
        self.assertEqual(out.dims, data.dims)
        np.testing.assert_allclose(out.values, values, atol=1e-12)
        self.assertEqual(out.proc_attrs[-1][0], "smooth")
        self.assertEqual(out.proc_attrs[-1][1]["window_length"], 5)

    def test_low_pass_returns_filtered_copy(self):
        axis = np.arange(400) / 1000.0
        low_frequency = np.sin(2 * np.pi * 10 * axis)
        high_frequency = 0.5 * np.sin(2 * np.pi * 200 * axis)
        data = sl.SpinData(low_frequency + high_frequency, ["t2"], [axis])

        out = low_pass(data, cutoff_hz=50, num_taps=31)

        self.assertIsNot(out, data)
        np.testing.assert_allclose(out.values[50:-50], low_frequency[50:-50], atol=0.08)
        np.testing.assert_allclose(data.values, low_frequency + high_frequency)

    def test_low_pass_rejects_invalid_cutoff(self):
        axis = np.arange(400) / 1000.0
        data = sl.SpinData(np.ones(400), ["t2"], [axis])

        with self.assertRaisesRegex(ValueError, "Nyquist"):
            low_pass(data, cutoff_hz=500)

    def test_smooth_works_on_2d_data_along_selected_dim(self):
        x = np.arange(11)
        scan = np.arange(2)
        values = np.vstack([x.astype(float) ** 2, x.astype(float) ** 2 + 1]).T
        data = sl.SpinData(values, ["t2", "scan"], [x, scan])

        out = smooth(data, dim="t2", window_length=5, polyorder=2)

        self.assertEqual(out.shape, data.shape)
        np.testing.assert_allclose(out.values, values, atol=1e-12)


if __name__ == "__main__":
    unittest.main()
