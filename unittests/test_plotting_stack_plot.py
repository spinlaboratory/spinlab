import unittest

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import spinlab as sl
from numpy.testing import assert_allclose, assert_array_equal


class sl_plotting_stack_plot_tester(unittest.TestCase):
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

    def test_stack_offsets_each_column(self):
        sl.stack(self.data, offset=10.0)

        lines = plt.gca().lines
        self.assertEqual(len(lines), self.scan.size)
        assert_array_equal(lines[0].get_xdata(), self.x)
        assert_allclose(lines[0].get_ydata(), self.data.values[:, 0])
        assert_allclose(lines[1].get_ydata(), self.data.values[:, 1] + 10.0)
        assert_allclose(lines[2].get_ydata(), self.data.values[:, 2] + 20.0)

    def test_waterfall_offsets_lines_and_adds_fills(self):
        sl.waterfall(self.data, dx=0.1, dy=2.0)

        ax = plt.gca()
        self.assertEqual(len(ax.lines), self.scan.size)
        self.assertEqual(len(ax.collections), self.scan.size)
        assert_allclose(ax.lines[1].get_xdata(), self.x + 0.1)
        assert_allclose(ax.lines[1].get_ydata(), self.data.values[:, 1] + 2.0)


if __name__ == "__main__":
    unittest.main()
