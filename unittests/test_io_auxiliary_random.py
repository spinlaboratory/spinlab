import unittest

import numpy as np
from numpy.testing import assert_array_equal

import spinlab as sl


class random_data_tester(unittest.TestCase):
    def test_ir_returns_2d_inversion_recovery_data(self):
        data = sl.io.auxiliary.random.ir(points=(128, 7), seed=1)

        self.assertEqual(data.dims, ["t2", "t1"])
        self.assertEqual(data.shape, (128, 7))
        self.assertEqual(data.coords["t2"].size, 128)
        self.assertEqual(data.coords["t1"].size, 7)
        self.assertTrue(np.iscomplexobj(data.values))
        self.assertEqual(data.attrs["experiment_type"], "inversion_recovery")
        self.assertEqual(data.spinlab_attrs["data_type"], "NMR")

    def test_ir_accepts_custom_t1_coord(self):
        t1 = np.array([0.0, 0.5, 1.0])

        data = sl.io.auxiliary.random.ir(points=(64, 3), t1=t1, seed=1)

        assert_array_equal(data.coords["t1"], t1)

    def test_ir_seed_is_reproducible(self):
        data_1 = sl.io.auxiliary.random.ir(points=(32, 4), seed=10)
        data_2 = sl.io.auxiliary.random.ir(points=(32, 4), seed=10)

        assert_array_equal(data_1.values, data_2.values)

    def test_nd_returns_requested_shape(self):
        data = sl.io.auxiliary.random.nd(4, 5, dims=["x", "scan"], seed=2)

        self.assertEqual(data.dims, ["x", "scan"])
        self.assertEqual(data.shape, (4, 5))
        assert_array_equal(data.coords["x"], np.arange(4))
        assert_array_equal(data.coords["scan"], np.arange(5))
        self.assertEqual(data.attrs["experiment_type"], "synthetic")

    def test_nd_accepts_shape_and_coords(self):
        coords = [np.linspace(0.0, 1.0, 3), np.array([10.0, 20.0])]

        data = sl.io.auxiliary.random.nd(
            shape=(3, 2),
            dims=["delay", "scan"],
            coords=coords,
            complex_data=True,
            snr=20.0,
            seed=3,
        )

        self.assertEqual(data.shape, (3, 2))
        self.assertTrue(np.iscomplexobj(data.values))
        assert_array_equal(data.coords["delay"], coords[0])
        assert_array_equal(data.coords["scan"], coords[1])

    def test_nd_seed_is_reproducible(self):
        data_1 = sl.io.auxiliary.random.nd((3, 2), seed=5)
        data_2 = sl.io.auxiliary.random.nd((3, 2), seed=5)

        assert_array_equal(data_1.values, data_2.values)

    def test_nd_validates_dims_and_coords(self):
        with self.assertRaises(ValueError):
            sl.io.auxiliary.random.nd(3, 2, dims=["x"])

        with self.assertRaises(ValueError):
            sl.io.auxiliary.random.nd(3, coords=[np.arange(2)])


if __name__ == "__main__":
    unittest.main()
