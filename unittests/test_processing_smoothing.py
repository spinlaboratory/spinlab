import unittest

import numpy as np
import spinlab as sl

from spinlab.processing.smoothing import smooth


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
