import unittest

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import spinlab as sl
from matplotlib.image import AxesImage
from numpy.testing import assert_allclose


class sl_plotting_image_tester(unittest.TestCase):
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

    def test_imshow_returns_image_and_sets_default_extent(self):
        image = sl.imshow(self.data)

        self.assertIsInstance(image, AxesImage)
        self.assertEqual(plt.gca().get_xlabel(), "scan")
        self.assertEqual(plt.gca().get_ylabel(), "x")
        assert_allclose(image.get_extent(), [0, 2, 0.0, 1.0])
        self.assertEqual(image.origin, "lower")

    def test_imshow_accepts_extent_origin_and_aspect(self):
        extent = [10.0, 20.0, 30.0, 40.0]

        image = sl.imshow(self.data, extent=extent, origin="upper", aspect="equal")

        assert_allclose(image.get_extent(), extent)
        self.assertEqual(image.origin, "upper")
        self.assertEqual(plt.gca().get_aspect(), 1.0)


if __name__ == "__main__":
    unittest.main()
