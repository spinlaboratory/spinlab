import unittest
from numpy.testing import assert_array_equal
import spinlab as sl
import numpy as np
import logging

# logging.basicConfig(filename='phase_debug.log', encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)


class slNMR_tester(unittest.TestCase):
    def setUp(self):
        pts = 1024
        omega = 50 * sl.pi
        tau = 0.1
        t2 = np.r_[0 : 1 : 1j * pts]
        y = np.exp(1j * t2 * omega) * np.exp(-1 * t2 / tau)
        self.data = sl.SpinData(y, ["t2"], [t2])
        self.data.spinlab_attrs["frequency"] = 400e6

    def test_basic_nmr_processing(self):
        data = sl.remove_background(self.data)

        data = sl.left_shift(data)

        data = sl.apodize(data, lw=1)

        data = sl.fourier_transform(data)

        data = sl.autophase(data)

    def test_calc_enhancement(self):
        pass


class slNMR_tester_sim(unittest.TestCase):
    def setUp(self):
        p1 = np.array([0, 0, 0, 1, 2, 3, 4, 3, 2, 1, 0, 0, 0])
        p2 = np.array([0, 1, 2, 3, 4, 3, 2, 1, 0, 0, 0, 0, 0])
        p3 = np.array([0, 0, 0, 0, 0, 1, 2, 3, 4, 3, 2, 1, 0])
        self.data = sl.SpinData(
            np.array([p1, p2, p3]).T,
            ["x", "t2"],
            [np.arange(0, len(p1)), np.arange(0, 3)],
        )

    def test_align(self):
        self.aligned_data = sl.ndalign(self.data, dim="x")
        assert_array_equal(
            self.aligned_data.values,
            np.array(
                [
                    [0, 0, 0, 1, 2, 3, 4, 3, 2, 1, 0, 0, 0],
                    [0, 0, 0, 1, 2, 3, 4, 3, 2, 1, 0, 0, 0],
                    [0, 0, 0, 1, 2, 3, 4, 3, 2, 1, 0, 0, 0],
                ]
            ).T,
        )
