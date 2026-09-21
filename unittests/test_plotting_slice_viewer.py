import unittest
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import spinlab as sl
from numpy.testing import assert_allclose


class sl_plotting_slice_viewer_tester(unittest.TestCase):
    def setUp(self):
        plt.close("all")
        self.x = np.linspace(0.0, 1.0, 5)
        self.scan = np.array([0, 1, 2])
        self.data = sl.SpinData(
            self.x.reshape(-1, 1) + self.scan.reshape(1, -1),
            ["x", "scan"],
            [self.x, self.scan],
        )

    def tearDown(self):
        plt.close("all")

    def test_slice_viewer_real_data_returns_figure_and_updates_slider(self):
        with patch("spinlab.plotting.slice_viewer._plt.show"):
            fig = sl.slice_viewer(self.data, scroll_dim="scan")

        self.assertEqual(len(fig.axes[0].lines), 1)
        self.assertEqual(fig.axes[0].get_xlabel(), "x")
        self.assertEqual(fig.axes[0].get_ylabel(), "Intensity")
        slider = fig._widgets[0]
        slider.set_val(2)
        assert_allclose(fig.axes[0].lines[0].get_ydata(), self.data.values[:, 2])
        self.assertIn("scan = 2", fig.axes[0].get_title())

    def test_slice_viewer_complex_data_plots_real_and_imag(self):
        values = self.data.values + 1j * (2.0 * self.data.values)
        data = sl.SpinData(values, ["x", "scan"], [self.x, self.scan])

        with patch("spinlab.plotting.slice_viewer._plt.show"):
            fig = sl.slice_viewer(data, scroll_dim="scan")

        self.assertEqual(len(fig.axes[0].lines), 2)
        slider = fig._widgets[0]
        slider.set_val(1)
        assert_allclose(fig.axes[0].lines[0].get_ydata(), values[:, 1].real)
        assert_allclose(fig.axes[0].lines[1].get_ydata(), values[:, 1].imag)

    def test_slice_viewer_requires_2d_data(self):
        data_1d = sl.SpinData(self.x, ["x"], [self.x])

        with self.assertRaises(ValueError):
            sl.slice_viewer(data_1d)


if __name__ == "__main__":
    unittest.main()
