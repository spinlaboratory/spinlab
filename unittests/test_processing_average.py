import unittest

import numpy as np
import spinlab as sl
from numpy.testing import assert_allclose, assert_array_equal

from spinlab.processing.average import average


class sl_average_tester(unittest.TestCase):
    def setUp(self):
        self.avg_dim = "Average"
        self.avg_coord = np.arange(4)
        self.x = np.arange(10)
        self.values = np.array([self.x**2 * (i + 1) for i in self.avg_coord])
        self.data = sl.SpinData(
            self.values.copy(), [self.avg_dim, "x"], [self.avg_coord, self.x]
        )

    def test_average_defaults_to_first_dim(self):
        out = average(self.data)

        assert_array_equal(out.coords["x"], self.x)
        assert_allclose(out.values, np.mean(self.values, axis=0))
        self.assertEqual(out.dims, ["x"])
        self.assertEqual(out.proc_attrs[-1][0], "average")
        self.assertEqual(out.proc_attrs[-1][1]["dim"], "Average")

    def test_average_explicit_dim(self):
        out = average(self.data, dim="Average")

        assert_array_equal(out.coords["x"], self.x)
        assert_allclose(out.values, np.mean(self.values, axis=0))

    def test_average_old_axis_argument_is_supported(self):
        out = average(self.data, axis="Average")

        assert_allclose(out.values, np.mean(self.values, axis=0))
        self.assertEqual(out.proc_attrs[-1][1]["dim"], "Average")

    def test_average_axis_and_dim_together_raise_value_error(self):
        with self.assertRaises(ValueError):
            average(self.data, dim="Average", axis="x")

    def test_average_along_second_dim(self):
        out = average(self.data, dim="x")

        assert_array_equal(out.coords["Average"], self.avg_coord)
        assert_allclose(out.values, np.mean(self.values, axis=1))
        self.assertEqual(out.dims, ["Average"])

    def test_average_complex_data(self):
        data = sl.SpinData(
            self.values.astype(complex) * (1 + 1j),
            [self.avg_dim, "x"],
            [self.avg_coord, self.x],
        )

        out = average(data, dim="Average")

        assert_allclose(out.values, np.mean(data.values, axis=0))
        self.assertTrue(np.iscomplexobj(out.values))

    def test_average_invalid_dim_raises_value_error(self):
        with self.assertRaises(ValueError):
            average(self.data, dim="missing")

    def test_average_preserves_existing_proc_attrs(self):
        self.data.add_proc_attrs("previous", {"value": 1})

        out = average(self.data, dim="Average")

        self.assertEqual(out.proc_attrs[0], ("previous", {"value": 1}))
        self.assertEqual(out.proc_attrs[-1][0], "average")

    def test_average_does_not_mutate_input(self):
        original_values = self.data.values.copy()
        original_coords = self.data.coords["Average"].copy()
        original_dims = self.data.dims.copy()

        average(self.data, dim="Average")

        assert_array_equal(self.data.values, original_values)
        assert_array_equal(self.data.coords["Average"], original_coords)
        self.assertEqual(self.data.dims, original_dims)


if __name__ == "__main__":
    unittest.main()
