import unittest
from numpy.testing import assert_allclose, assert_array_equal
import spinlab as sl
import numpy as np
import logging
from spinlab.processing.integration import cumulative_integrate, integrate


# logging.basicConfig(filename='phase_debug.log', encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)


class sl_integration_tester(unittest.TestCase):
    def setUp(self):
        self.x = np.linspace(0, 2, 501)
        self.y = 2 * self.x + 1
        self.data_1d = sl.SpinData(self.y, dims=["x0"], coords=[self.x])

        self.scan = np.r_[0:4]
        self.values_2d = np.array([(i + 1) * self.y for i in self.scan]).T
        self.data_2d = sl.SpinData(
            self.values_2d, dims=["x0", "scan"], coords=[self.x, self.scan]
        )

        self.complex_values = self.y + 1j * (self.x**2)
        self.data_complex = sl.SpinData(
            self.complex_values, dims=["x0"], coords=[self.x]
        )

    def test_integrate_1d_full_region(self):
        out = integrate(self.data_1d, dim="x0")

        self.assertEqual(out.dims, [])
        self.assertEqual(out.shape, ())
        self.assertEqual(out.attrs["experiment_type"], "integrals")
        self.assertEqual(out.proc_attrs[-1][0], "integrate")
        self.assertEqual(out.proc_attrs[-1][1], {"dim": "x0", "regions": None})
        assert_allclose(out.values, np.trapezoid(self.y, self.x))

    def test_integrate_defaults_to_first_dim(self):
        out = integrate(self.data_2d)

        self.assertEqual(out.dims, ["scan"])
        self.assertEqual(out.shape, (4,))
        assert_array_equal(out.coords["scan"], self.scan)
        self.assertEqual(out.proc_attrs[-1][1], {"dim": "x0", "regions": None})
        assert_allclose(out.values, np.trapezoid(self.values_2d, self.x, axis=0))

    def test_integrate_single_tuple_region(self):
        out = integrate(self.data_1d, dim="x0", regions=(0.0, 1.0))
        sliced = self.data_1d["x0", (0.0, 1.0)]

        self.assertEqual(out.dims, ["integrals"])
        self.assertEqual(out.shape, (1,))
        assert_array_equal(out.coords["integrals"], np.array([0]))
        self.assertEqual(out.proc_attrs[-1][1]["regions"], ((0.0, 1.0),))
        assert_allclose(out.values[0], np.trapezoid(sliced.values, sliced.coords["x0"]))

    def test_integrate_multiple_regions(self):
        regions = [(0.0, 0.5), (1.0, 2.0)]
        out = integrate(self.data_1d, dim="x0", regions=regions)
        expected = [
            np.trapezoid(
                self.data_1d["x0", region].values,
                self.data_1d["x0", region].coords["x0"],
            )
            for region in regions
        ]

        self.assertEqual(out.dims, ["integrals"])
        self.assertEqual(out.shape, (2,))
        assert_array_equal(out.coords["integrals"], np.array([0, 1]))
        self.assertEqual(out.attrs["experiment_type"], "integrals")
        self.assertEqual(out.proc_attrs[-1][0], "integrate")
        self.assertEqual(out.proc_attrs[-1][1]["regions"], regions)
        assert_allclose(out.values, expected)

    def test_integrate_2d_along_first_dim(self):
        out = integrate(self.data_2d, dim="x0")

        self.assertEqual(out.dims, ["scan"])
        self.assertEqual(out.shape, (4,))
        assert_array_equal(out.coords["scan"], self.scan)
        self.assertEqual(out.attrs["experiment_type"], "integrals")
        self.assertEqual(out.proc_attrs[-1][0], "integrate")
        assert_allclose(out.values, np.trapezoid(self.values_2d, self.x, axis=0))

    def test_integrate_2d_along_second_dim(self):
        out = integrate(self.data_2d, dim="scan")

        self.assertEqual(out.dims, ["x0"])
        self.assertEqual(out.shape, self.x.shape)
        assert_array_equal(out.coords["x0"], self.x)
        self.assertEqual(out.attrs["experiment_type"], "integrals")
        assert_allclose(out.values, np.trapezoid(self.values_2d, self.scan, axis=1))

    def test_integrate_complex_data(self):
        out = integrate(self.data_complex, dim="x0")

        expected = np.trapezoid(self.complex_values, self.x)
        self.assertEqual(out.dims, [])
        assert_allclose(out.values, expected)

    def test_integrate_invalid_dim_raises_value_error(self):
        with self.assertRaises(ValueError):
            integrate(self.data_1d, dim="not_a_dim")

    def test_integrate_does_not_mutate_input(self):
        original_values = self.data_2d.values.copy()
        original_x = self.data_2d.coords["x0"].copy()
        original_scan = self.data_2d.coords["scan"].copy()
        original_dims = self.data_2d.dims.copy()
        original_attrs = self.data_2d.attrs.copy()

        integrate(self.data_2d, dim="x0")

        self.assertEqual(self.data_2d.dims, original_dims)
        self.assertEqual(self.data_2d.attrs, original_attrs)
        assert_array_equal(self.data_2d.coords["x0"], original_x)
        assert_array_equal(self.data_2d.coords["scan"], original_scan)
        assert_allclose(self.data_2d.values, original_values)

    def test_cumulative_integrate_1d(self):
        out = cumulative_integrate(self.data_1d, dim="x0")

        self.assertEqual(out.dims, ["x0"])
        self.assertEqual(out.shape, self.data_1d.shape)
        assert_array_equal(out.coords["x0"], self.x)
        self.assertEqual(out.proc_attrs[-1][0], "cumulative_integrate")
        self.assertEqual(out.proc_attrs[-1][1], {"dim": "x0", "regions": None})
        assert_allclose(out.values, self.x**2 + self.x)

    def test_cumulative_integrate_defaults_to_first_dim(self):
        out = cumulative_integrate(self.data_2d)
        expected = np.array([(i + 1) * (self.x**2 + self.x) for i in self.scan]).T

        self.assertEqual(out.dims, ["x0", "scan"])
        self.assertEqual(out.shape, self.data_2d.shape)
        self.assertEqual(out.proc_attrs[-1][1], {"dim": "x0", "regions": None})
        assert_allclose(out.values, expected)

    def test_cumulative_integrate_2d_along_first_dim(self):
        out = cumulative_integrate(self.data_2d, dim="x0")
        expected = np.array([(i + 1) * (self.x**2 + self.x) for i in self.scan]).T

        self.assertEqual(out.dims, ["x0", "scan"])
        self.assertEqual(out.shape, self.data_2d.shape)
        assert_array_equal(out.coords["x0"], self.x)
        assert_array_equal(out.coords["scan"], self.scan)
        self.assertEqual(out.proc_attrs[-1][0], "cumulative_integrate")
        assert_allclose(out.values, expected)

    def test_cumulative_integrate_regions_returns_region_list(self):
        regions = [(0.0, 0.5), (1.0, 2.0)]
        out = cumulative_integrate(self.data_1d, dim="x0", regions=regions)

        self.assertEqual(len(out), 2)
        for region, region_out in zip(regions, out):
            sliced = self.data_1d["x0", region]
            self.assertEqual(region_out.dims, ["x0"])
            assert_array_equal(region_out.coords["x0"], sliced.coords["x0"])
            self.assertEqual(region_out.proc_attrs[-1][0], "cumulative_integrate")
            assert_allclose(
                region_out.values,
                sliced.coords["x0"] ** 2
                + sliced.coords["x0"]
                - (sliced.coords["x0"][0] ** 2 + sliced.coords["x0"][0]),
                atol=1e-12,
            )

    def test_cumulative_integrate_invalid_dim_raises_value_error(self):
        with self.assertRaises(ValueError):
            cumulative_integrate(self.data_1d, dim="not_a_dim")

    def test_cumulative_integrate_does_not_mutate_input(self):
        original_values = self.data_1d.values.copy()
        original_coords = self.data_1d.coords["x0"].copy()
        original_dims = self.data_1d.dims.copy()

        cumulative_integrate(self.data_1d, dim="x0")

        self.assertEqual(self.data_1d.dims, original_dims)
        assert_array_equal(self.data_1d.coords["x0"], original_coords)
        assert_allclose(self.data_1d.values, original_values)


if __name__ == "__main__":
    unittest.main()
