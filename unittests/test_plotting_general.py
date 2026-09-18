import unittest
import warnings

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import spinlab as sl
from numpy.testing import assert_array_equal


class sl_plotting_general_tester(unittest.TestCase):
    def setUp(self):
        plt.close("all")
        self.x = np.linspace(0.0, 1.0, 5)
        self.scan = np.array([0, 1, 2])
        self.data_1d = sl.SpinData(self.x**2, ["x"], [self.x])
        self.data_2d = sl.SpinData(
            self.x.reshape(-1, 1) + self.scan.reshape(1, -1),
            ["x", "scan"],
            [self.x, self.scan],
        )

    def tearDown(self):
        plt.close("all")

    def test_plot_1d_sets_xlabel_and_returns_lines(self):
        lines = sl.plot(self.data_1d)

        self.assertEqual(len(lines), 1)
        assert_array_equal(lines[0].get_xdata(), self.x)
        assert_array_equal(lines[0].get_ydata(), self.data_1d.values)
        self.assertEqual(plt.gca().get_xlabel(), "x")

    def test_plot_2d_unfolds_selected_dim_and_restores_input(self):
        original_dims = self.data_2d.dims.copy()
        original_values = self.data_2d.values.copy()

        lines = sl.plot(self.data_2d, dim="x")

        self.assertEqual(len(lines), self.scan.size)
        assert_array_equal(lines[0].get_xdata(), self.x)
        assert_array_equal(lines[1].get_ydata(), self.data_2d.values[:, 1])
        self.assertEqual(self.data_2d.dims, original_dims)
        assert_array_equal(self.data_2d.values, original_values)

    def test_plot_forwards_semilogy_keyword(self):
        data = sl.SpinData(np.exp(self.x), ["x"], [self.x])

        out = sl.plot(data, semilogy=True)

        self.assertEqual(len(out), 1)
        self.assertEqual(plt.gca().get_yscale(), "log")

    def test_fancy_plot_missing_experiment_type_falls_back_to_plot(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            out = sl.fancy_plot(self.data_1d)

        self.assertIsNone(out)
        self.assertEqual(len(plt.gca().lines), 1)
        self.assertTrue(
            any("experiment_type not defined" in str(w.message) for w in caught)
        )

    def test_fancy_plot_nmr_spectrum_sets_labels_and_reverses_xaxis(self):
        data = sl.SpinData(
            self.x,
            ["ppm"],
            [self.x],
            attrs={"experiment_type": "nmr_spectrum", "nmr_frequency": 400e6},
        )

        lines = sl.fancy_plot(data)

        self.assertEqual(len(lines), 1)
        self.assertEqual(plt.gca().get_xlabel(), "Chemical Shift $\\delta$ (ppm)")
        self.assertEqual(plt.gca().get_ylabel(), "NMR Signal Intensity (a.u.)")
        xlim = plt.gca().get_xlim()
        self.assertGreater(xlim[0], xlim[1])


if __name__ == "__main__":
    unittest.main()
