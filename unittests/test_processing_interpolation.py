import logging
import unittest

import numpy as np
import spinlab as sl
from numpy.testing import assert_allclose, assert_array_equal

from spinlab.processing.interpolation import interp


# logging.basicConfig(filename='interp_debug.log', encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)


class sl_interpolation_tester(unittest.TestCase):
    def setUp(self):
        self.x = np.linspace(0.0, 4.0, 5)
        self.values_1d = 2.0 * self.x + 1.0
        self.data_1d = sl.SpinData(self.values_1d, dims=["x"], coords=[self.x])

        self.scan = np.r_[0:3]
        self.values_2d = np.array([(i + 1) * self.values_1d for i in self.scan]).T
        self.data_2d = sl.SpinData(
            self.values_2d, dims=["x", "scan"], coords=[self.x, self.scan]
        )
        self.delay = np.array([0.0, 1.0])
        self.values_3d = np.stack(
            [self.values_2d, self.values_2d + 10.0], axis=2
        )
        self.data_3d = sl.SpinData(
            self.values_3d,
            dims=["x", "scan", "delay"],
            coords=[self.x, self.scan, self.delay],
        )

    def test_interp_1d(self):
        new_coord = np.array([0.5, 1.5, 2.5, 3.5])

        out = interp(self.data_1d, dim="x", new_coord=new_coord)

        self.assertEqual(out.dims, ["x"])
        self.assertEqual(out.shape, new_coord.shape)
        assert_array_equal(out.coords["x"], new_coord)
        self.assertEqual(out.proc_attrs[-1][0], "interp")
        self.assertEqual(out.proc_attrs[-1][1]["dim"], "x")
        assert_array_equal(out.proc_attrs[-1][1]["new_coord"], new_coord)
        assert_allclose(out.values, np.interp(new_coord, self.x, self.values_1d))

    def test_interp_defaults_to_first_dim(self):
        new_coord = np.array([0.5, 1.5, 2.5, 3.5])

        out = interp(self.data_2d, new_coord=new_coord)

        self.assertEqual(out.dims, ["x", "scan"])
        self.assertEqual(out.shape, (4, 3))
        self.assertEqual(out.proc_attrs[-1][1]["dim"], "x")
        assert_array_equal(out.coords["x"], new_coord)
        assert_array_equal(out.coords["scan"], self.scan)
        expected = np.array(
            [
                np.interp(new_coord, self.x, self.values_2d[:, ix])
                for ix in range(self.values_2d.shape[1])
            ]
        ).T
        assert_allclose(out.values, expected)

    def test_interp_2d_along_second_dim(self):
        new_coord = np.array([0.5, 1.5])

        out = interp(self.data_2d, dim="scan", new_coord=new_coord)

        self.assertEqual(out.dims, ["x", "scan"])
        self.assertEqual(out.shape, (5, 2))
        assert_array_equal(out.coords["x"], self.x)
        assert_array_equal(out.coords["scan"], new_coord)
        expected = np.array(
            [
                np.interp(new_coord, self.scan, self.values_2d[ix, :])
                for ix in range(self.values_2d.shape[0])
            ]
        )
        assert_allclose(out.values, expected)

    def test_interp_3d_along_middle_dim(self):
        new_coord = np.array([0.5, 1.5])

        out = interp(self.data_3d, dim="scan", new_coord=new_coord)

        self.assertEqual(out.dims, ["x", "scan", "delay"])
        self.assertEqual(out.shape, (5, 2, 2))
        assert_array_equal(out.coords["x"], self.x)
        assert_array_equal(out.coords["scan"], new_coord)
        assert_array_equal(out.coords["delay"], self.delay)
        expected = np.empty((5, 2, 2))
        for ix in range(self.values_3d.shape[0]):
            for iz in range(self.values_3d.shape[2]):
                expected[ix, :, iz] = np.interp(
                    new_coord, self.scan, self.values_3d[ix, :, iz]
                )
        assert_allclose(out.values, expected)

    def test_interp_complex_data(self):
        values = self.values_1d + 1j * (self.x**2)
        data = sl.SpinData(values, dims=["x"], coords=[self.x])
        new_coord = np.array([0.5, 1.5, 2.5])

        out = interp(data, dim="x", new_coord=new_coord)

        assert_array_equal(out.coords["x"], new_coord)
        assert_allclose(out.values, np.interp(new_coord, self.x, values))

    def test_interp_decreasing_source_coord_with_decreasing_new_coord(self):
        x = self.x[::-1]
        values = self.values_1d[::-1]
        data = sl.SpinData(values, dims=["x"], coords=[x])
        new_coord = np.array([2.5, 1.5, 0.5])

        out = interp(data, dim="x", new_coord=new_coord)

        assert_array_equal(out.coords["x"], new_coord)
        assert_allclose(out.values, np.interp(new_coord, self.x, self.values_1d))

    def test_interp_accepts_list_new_coord(self):
        new_coord = [0.5, 1.5, 2.5]

        out = interp(self.data_1d, dim="x", new_coord=new_coord)

        assert_array_equal(out.coords["x"], np.array(new_coord))
        assert_allclose(out.values, np.interp(new_coord, self.x, self.values_1d))

    def test_interp_new_coord_must_match_source_direction(self):
        new_coord = np.array([2.5, 0.5, 1.5])

        with self.assertRaises(ValueError):
            interp(self.data_1d, dim="x", new_coord=new_coord)

    def test_interp_decreasing_source_rejects_increasing_new_coord(self):
        x = self.x[::-1]
        values = self.values_1d[::-1]
        data = sl.SpinData(values, dims=["x"], coords=[x])

        with self.assertRaises(ValueError):
            interp(data, dim="x", new_coord=np.array([0.5, 1.5, 2.5]))

    def test_interp_uses_left_and_right_values(self):
        new_coord = np.array([-1.0, 0.5, 5.0])

        out = interp(self.data_1d, dim="x", new_coord=new_coord, left=-10, right=20)

        assert_array_equal(out.coords["x"], new_coord)
        assert_allclose(
            out.values,
            np.interp(new_coord, self.x, self.values_1d, left=-10, right=20),
        )
        self.assertEqual(out.proc_attrs[-1][1]["left"], -10)
        self.assertEqual(out.proc_attrs[-1][1]["right"], 20)
        self.assertFalse(out.proc_attrs[-1][1]["extrapolate"])

    def test_interp_default_out_of_bounds_uses_edge_values(self):
        new_coord = np.array([-1.0, 0.5, 5.0])

        out = interp(self.data_1d, dim="x", new_coord=new_coord)

        assert_allclose(out.values, np.interp(new_coord, self.x, self.values_1d))

    def test_interp_linear_extrapolation(self):
        new_coord = np.array([-1.0, 0.5, 5.0])

        out = interp(self.data_1d, dim="x", new_coord=new_coord, extrapolate=True)

        expected = 2.0 * new_coord + 1.0
        assert_allclose(out.values, expected)
        self.assertTrue(out.proc_attrs[-1][1]["extrapolate"])

    def test_interp_left_right_override_extrapolation(self):
        new_coord = np.array([-1.0, 0.5, 5.0])

        out = interp(
            self.data_1d,
            dim="x",
            new_coord=new_coord,
            left=-10,
            right=20,
            extrapolate=True,
        )

        expected = np.array([-10.0, 2.0, 20.0])
        assert_allclose(out.values, expected)
        self.assertTrue(out.proc_attrs[-1][1]["extrapolate"])

    def test_interp_complex_linear_extrapolation(self):
        values = (2.0 * self.x + 1.0) + 1j * (-self.x + 3.0)
        data = sl.SpinData(values, dims=["x"], coords=[self.x])
        new_coord = np.array([-1.0, 0.5, 5.0])

        out = interp(data, dim="x", new_coord=new_coord, extrapolate=True)

        expected = (2.0 * new_coord + 1.0) + 1j * (-new_coord + 3.0)
        assert_allclose(out.values, expected)

    def test_interp_2d_linear_extrapolation(self):
        new_coord = np.array([-1.0, 0.5, 5.0])

        out = interp(self.data_2d, dim="x", new_coord=new_coord, extrapolate=True)

        expected = np.array(
            [(i + 1) * (2.0 * new_coord + 1.0) for i in self.scan]
        ).T
        self.assertEqual(out.shape, (3, 3))
        assert_allclose(out.values, expected)

    def test_interp_new_coord_must_be_provided(self):
        with self.assertRaises(ValueError):
            interp(self.data_1d, dim="x")

    def test_interp_new_coord_must_not_be_empty(self):
        with self.assertRaises(ValueError):
            interp(self.data_1d, dim="x", new_coord=np.array([]))

    def test_interp_new_coord_must_be_1d(self):
        with self.assertRaises(ValueError):
            interp(self.data_1d, dim="x", new_coord=np.array([[0.0, 1.0]]))

    def test_interp_source_coord_must_have_at_least_two_points(self):
        data = sl.SpinData(np.array([1.0]), dims=["x"], coords=[np.array([0.0])])

        with self.assertRaises(ValueError):
            interp(data, dim="x", new_coord=np.array([0.0]))

    def test_interp_source_coord_must_be_monotonic(self):
        data = sl.SpinData(
            np.array([0.0, 1.0, 2.0]), dims=["x"], coords=[np.array([0.0, 2.0, 1.0])]
        )

        with self.assertRaises(ValueError):
            interp(data, dim="x", new_coord=np.array([0.5]))

    def test_interp_invalid_dim_raises_value_error(self):
        with self.assertRaises(ValueError):
            interp(self.data_1d, dim="not_a_dim", new_coord=np.array([0.5]))

    def test_interp_does_not_mutate_input(self):
        original_values = self.data_2d.values.copy()
        original_x = self.data_2d.coords["x"].copy()
        original_scan = self.data_2d.coords["scan"].copy()
        original_dims = self.data_2d.dims.copy()

        interp(self.data_2d, dim="x", new_coord=np.array([0.5, 1.5]))

        self.assertEqual(self.data_2d.dims, original_dims)
        assert_array_equal(self.data_2d.coords["x"], original_x)
        assert_array_equal(self.data_2d.coords["scan"], original_scan)
        assert_allclose(self.data_2d.values, original_values)


if __name__ == "__main__":
    unittest.main()
