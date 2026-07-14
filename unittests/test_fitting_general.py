import unittest
import warnings

import numpy as np
import spinlab as sl
from numpy.testing import assert_allclose, assert_array_equal

from spinlab.fitting.general import fit


def line(x, m, b):
    return m * x + b


def amplitude_line(x, amplitude):
    return amplitude * x


class slFit_tester(unittest.TestCase):
    def setUp(self):
        self.x = np.linspace(-1.0, 1.0, 21)
        self.y = line(self.x, 2.0, -0.5)
        self.data = sl.SpinData(self.y, ["x"], [self.x])

    def test_fit_1d_data(self):
        out = fit(line, self.data, dim="x", p0=(1, 0))

        assert_allclose(out["fit"].values, self.y)
        assert_array_equal(out["fit"].coords["x"], self.x)
        self.assertEqual(out["fit"].dims, ["x"])
        self.assertEqual(out["popt"].dims, ["popt"])
        assert_allclose(out["popt"].values, np.array([2.0, -0.5]))
        self.assertEqual(out["err"].shape, (2,))
        self.assertEqual(out["pcov"].dims, ["popt", "popt_cov"])
        self.assertEqual(out["pcov"].shape, (2, 2))
        self.assertEqual(out["fit"].proc_attrs[-1][0], "fit")
        self.assertEqual(out["fit"].proc_attrs[-1][1]["dim"], "x")

    def test_fit_defaults_to_first_dim(self):
        out = fit(line, self.data, p0=(1, 0))

        assert_allclose(out["fit"].values, self.y)
        assert_allclose(out["popt"].values, np.array([2.0, -0.5]))

    def test_fit_2d_data_along_first_dim(self):
        scan = np.arange(3)
        slopes = np.array([1.0, 2.0, 3.0])
        offsets = np.array([0.0, -1.0, 2.0])
        values = slopes.reshape(1, -1) * self.x.reshape(-1, 1) + offsets.reshape(1, -1)
        data = sl.SpinData(values, ["x", "scan"], [self.x, scan])

        out = fit(line, data, dim="x", p0=(1, 0))

        self.assertEqual(out["fit"].dims, ["x", "scan"])
        assert_allclose(out["fit"].values, values)
        self.assertEqual(out["popt"].dims, ["popt", "scan"])
        assert_allclose(out["popt"].values[0], slopes)
        assert_allclose(out["popt"].values[1], offsets)

    def test_fit_2d_data_along_second_dim(self):
        delay = np.arange(3)
        slopes = np.array([1.0, 2.0, 3.0, 4.0])
        offsets = np.array([0.0, -1.0, 2.0, 0.5])
        values = slopes.reshape(-1, 1) * delay.reshape(1, -1) + offsets.reshape(-1, 1)
        data = sl.SpinData(values, ["scan", "delay"], [np.arange(4), delay])

        out = fit(line, data, dim="delay", p0=(1, 0))

        self.assertEqual(out["fit"].dims, ["scan", "delay"])
        assert_allclose(out["fit"].values, values)
        self.assertEqual(out["popt"].dims, ["popt", "scan"])
        assert_allclose(out["popt"].values[0], slopes)
        assert_allclose(out["popt"].values[1], offsets)
        self.assertEqual(out["pcov"].dims, ["popt", "popt_cov", "scan"])
        self.assertEqual(out["pcov"].shape, (2, 2, 4))

    def test_fit_points_resamples_fit_curve_and_preserves_direction(self):
        out = fit(line, self.data, dim="x", p0=(1, 0), fit_points=11)

        expected_x = np.linspace(self.x[0], self.x[-1], 11)
        assert_allclose(out["fit"].coords["x"], expected_x)
        assert_allclose(out["fit"].values, line(expected_x, 2.0, -0.5))

    def test_fit_points_preserves_decreasing_coord_direction(self):
        x = self.x[::-1]
        y = line(x, 2.0, -0.5)
        data = sl.SpinData(y, ["x"], [x])

        out = fit(line, data, dim="x", p0=(1, 0), fit_points=11)

        assert_allclose(out["fit"].coords["x"], np.linspace(x[0], x[-1], 11))
        assert_allclose(out["fit"].values, line(out["fit"].coords["x"], 2.0, -0.5))

    def test_fit_accepts_scalar_p0_for_single_parameter_function(self):
        data = sl.SpinData(3.0 * self.x, ["x"], [self.x])

        out = fit(amplitude_line, data, dim="x", p0=1)

        self.assertEqual(out["popt"].shape, (1,))
        assert_allclose(out["popt"].values, np.array([3.0]))

    def test_fit_uses_1d_sigma(self):
        sigma = np.linspace(1.0, 2.0, self.x.size)

        out = fit(line, self.data, dim="x", p0=(1, 0), sigma=sigma, absolute_sigma=True)

        assert_allclose(out["popt"].values, np.array([2.0, -0.5]))

    def test_fit_uses_nd_sigma_per_unfolded_spectrum(self):
        scan = np.arange(2)
        slopes = np.array([1.0, 2.0])
        offsets = np.array([0.0, -1.0])
        values = slopes.reshape(1, -1) * self.x.reshape(-1, 1) + offsets.reshape(1, -1)
        sigma = np.tile(np.linspace(1.0, 2.0, self.x.size).reshape(-1, 1), (1, 2))
        data = sl.SpinData(values, ["x", "scan"], [self.x, scan])

        out = fit(line, data, dim="x", p0=(1, 0), sigma=sigma, absolute_sigma=True)

        assert_allclose(out["popt"].values[0], slopes)
        assert_allclose(out["popt"].values[1], offsets)

    def test_fit_invalid_inputs_raise_value_error(self):
        with self.assertRaises(ValueError):
            fit(line, self.data, dim="missing", p0=(1, 0))
        with self.assertRaises(ValueError):
            fit(line, self.data, dim="x", p0=None)
        with self.assertRaises(ValueError):
            fit(line, self.data, dim="x", p0=[[1, 0]])
        with self.assertRaises(ValueError):
            fit(line, self.data, dim="x", p0=(1, 0), fit_points=0)
        with self.assertRaises(ValueError):
            fit(line, self.data, dim="x", p0=(1, 0), fit_points="bad")
        with self.assertRaises(ValueError):
            fit(line, self.data, dim="x", p0=(1, 0), fit_points=True)
        with self.assertRaises(ValueError):
            fit(line, self.data, dim="x", p0=(1, 0), sigma=np.ones(3))
        with self.assertRaises(ValueError):
            fit(line, self.data, dim="x", p0=(1, 0), sigma=np.ones((2, 2)))

    def test_fit_rejects_complex_data(self):
        data = sl.SpinData(self.y.astype(complex), ["x"], [self.x])

        with self.assertRaises(ValueError):
            fit(line, data, dim="x", p0=(1, 0))

    def test_fit_validates_coordinate(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            bad_data = sl.SpinData(self.y, ["x"], [self.x[:-1]])
        with self.assertRaises(ValueError):
            fit(line, bad_data, dim="x", p0=(1, 0))

    def test_fit_does_not_mutate_input(self):
        original_values = self.data.values.copy()
        original_coord = self.data.coords["x"].copy()
        original_dims = self.data.dims.copy()

        fit(line, self.data, dim="x", p0=(1, 0), fit_points=11)

        assert_array_equal(self.data.values, original_values)
        assert_array_equal(self.data.coords["x"], original_coord)
        self.assertEqual(self.data.dims, original_dims)


if __name__ == "__main__":
    unittest.main()
