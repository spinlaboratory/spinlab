import unittest
from numpy.testing import assert_allclose, assert_array_equal
import spinlab as sl
import numpy as np
import logging
from spinlab.processing.fft import _convert_to_ppm, _rename_ft_dim, zero_fill

# logging.basicConfig(filename='phase_debug.log', encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)


class sl_fft_tester(unittest.TestCase):
    def setUp(self):
        pts = 1024
        omega = 50 * sl.pi
        tau = 0.1
        t2 = np.r_[0 : 1 : 1j * pts]
        y = np.exp(1j * t2 * omega) * np.exp(-1 * t2 / tau)
        self.data_1d = sl.SpinData(y, ["t2"], [t2])
        self.data_1d.spinlab_attrs["frequency"] = 400e6

        t1 = np.r_[0:8]
        y_2d = np.array([y * (i + 1) for i in t1]).T
        self.data_2d = sl.SpinData(y_2d, ["t2", "t1"], [t2, t1])
        self.data_2d.spinlab_attrs["frequency"] = 400e6

    def test_fourier_transform_1d(self):
        ft_data = sl.fourier_transform(
            self.data_1d, zero_fill_factor=4, convert_to_ppm=False
        )

        self.assertEqual(ft_data.dims, ["f2"])
        self.assertEqual(ft_data.shape, (4096,))
        self.assertEqual(ft_data.coords["f2"].size, 4096)
        self.assertEqual(ft_data.proc_attrs[-1][0], "fourier_transform")
        assert_allclose(
            ft_data.values,
            np.fft.fftshift(np.fft.fft(self.data_1d.values, n=4096)),
        )

    def test_fourier_transform_1d_shifted_coordinate(self):
        ft_data = sl.fourier_transform(self.data_1d, convert_to_ppm=False)

        dt = self.data_1d.coords["t2"][1] - self.data_1d.coords["t2"][0]
        expected_coord = (1.0 / (self.data_1d.shape[0] * dt)) * np.r_[
            0 : self.data_1d.shape[0]
        ]
        expected_coord -= 1.0 / (2 * dt)

        assert_allclose(ft_data.coords["f2"], expected_coord)

    def test_inverse_fourier_transform_1d_roundtrip(self):
        ft_data = sl.fourier_transform(self.data_1d, convert_to_ppm=False)
        out = sl.inverse_fourier_transform(ft_data, convert_from_ppm=False)

        self.assertEqual(out.dims, ["t2"])
        self.assertEqual(out.shape, self.data_1d.shape)
        self.assertEqual(out.proc_attrs[-1][0], "inverse_fourier_transform")
        assert_allclose(out.values, self.data_1d.values)

    def test_inverse_fourier_transform_shift_false_roundtrip(self):
        ft_data = sl.fourier_transform(
            self.data_1d, shift=False, convert_to_ppm=False
        )
        out = sl.inverse_fourier_transform(
            ft_data, shift=False, convert_from_ppm=False
        )

        self.assertEqual(out.dims, ["t2"])
        self.assertEqual(out.shape, self.data_1d.shape)
        assert_allclose(out.values, self.data_1d.values)

    def test_fourier_transform_2d_along_t2(self):
        ft_data = sl.fourier_transform(
            self.data_2d, dim="t2", zero_fill_factor=4, convert_to_ppm=False
        )

        self.assertEqual(ft_data.dims, ["f2", "t1"])
        self.assertEqual(ft_data.shape, (4096, 8))
        assert_array_equal(ft_data.coords["t1"], self.data_2d.coords["t1"])
        self.assertEqual(ft_data.proc_attrs[-1][0], "fourier_transform")
        assert_allclose(
            ft_data.values,
            np.fft.fftshift(np.fft.fft(self.data_2d.values, n=4096, axis=0), axes=0),
        )

    def test_inverse_fourier_transform_2d_roundtrip(self):
        ft_data = sl.fourier_transform(
            self.data_2d, dim="t2", convert_to_ppm=False
        )
        out = sl.inverse_fourier_transform(
            ft_data, dim="f2", convert_from_ppm=False
        )

        self.assertEqual(out.dims, ["t2", "t1"])
        self.assertEqual(out.shape, self.data_2d.shape)
        assert_array_equal(out.coords["t1"], self.data_2d.coords["t1"])
        self.assertEqual(out.proc_attrs[-1][0], "inverse_fourier_transform")
        assert_allclose(out.values, self.data_2d.values)

    def test_fourier_transform_2d_along_t1(self):
        ft_data = sl.fourier_transform(
            self.data_2d, dim="t1", zero_fill_factor=2, convert_to_ppm=False
        )

        self.assertEqual(ft_data.dims, ["t2", "f1"])
        self.assertEqual(ft_data.shape, (1024, 16))
        assert_array_equal(ft_data.coords["t2"], self.data_2d.coords["t2"])
        self.assertEqual(ft_data.coords["f1"].size, 16)
        assert_allclose(
            ft_data.values,
            np.fft.fftshift(np.fft.fft(self.data_2d.values, n=16, axis=1), axes=1),
        )

    def test_fourier_transform_without_frequency_does_not_convert_to_ppm(self):
        data = self.data_1d.copy()
        data.spinlab_attrs["data_type"] = "NMR"
        data.spinlab_attrs.pop("frequency", None)
        data.attrs.pop("frequency", None)

        with self.assertWarns(UserWarning) as warning:
            ft_data = sl.fourier_transform(data, convert_to_ppm=True)

        self.assertIn("Frequency not found", str(warning.warning))
        self.assertEqual(ft_data.dims, ["f2"])
        dt = data.coords["t2"][1] - data.coords["t2"][0]
        expected_coord = (1.0 / (data.shape[0] * dt)) * np.r_[0 : data.shape[0]]
        expected_coord -= 1.0 / (2 * dt)
        assert_allclose(ft_data.coords["f2"], expected_coord)
        assert_allclose(
            ft_data.values,
            np.fft.fftshift(np.fft.fft(data.values)),
        )

    def test_fourier_transform_convert_to_ppm_with_frequency(self):
        ft_data = sl.fourier_transform(self.data_1d, convert_to_ppm=True)

        dt = self.data_1d.coords["t2"][1] - self.data_1d.coords["t2"][0]
        expected_coord = (1.0 / (self.data_1d.shape[0] * dt)) * np.r_[
            0 : self.data_1d.shape[0]
        ]
        expected_coord -= 1.0 / (2 * dt)
        expected_coord /= self.data_1d.spinlab_attrs["frequency"] / 1.0e6

        assert_allclose(ft_data.coords["f2"], expected_coord)
        self.assertTrue(ft_data.proc_attrs[-1][1]["convert_to_ppm"])

    def test_fourier_transform_convert_to_ppm_default_uses_nmr_data_type(self):
        data = self.data_1d.copy()
        data.spinlab_attrs["data_type"] = "NMR"

        ft_data = sl.fourier_transform(data)

        dt = data.coords["t2"][1] - data.coords["t2"][0]
        expected_coord = (1.0 / (data.shape[0] * dt)) * np.r_[0 : data.shape[0]]
        expected_coord -= 1.0 / (2 * dt)
        expected_coord /= data.spinlab_attrs["frequency"] / 1.0e6

        assert_allclose(ft_data.coords["f2"], expected_coord)
        self.assertTrue(ft_data.proc_attrs[-1][1]["convert_to_ppm"])

    def test_fourier_transform_nmr_data_type_forces_convert_to_ppm(self):
        data = self.data_1d.copy()
        data.spinlab_attrs["data_type"] = "NMR"

        ft_data = sl.fourier_transform(data, convert_to_ppm=False)

        dt = data.coords["t2"][1] - data.coords["t2"][0]
        expected_coord = (1.0 / (data.shape[0] * dt)) * np.r_[0 : data.shape[0]]
        expected_coord -= 1.0 / (2 * dt)
        expected_coord /= data.spinlab_attrs["frequency"] / 1.0e6

        assert_allclose(ft_data.coords["f2"], expected_coord)
        self.assertTrue(ft_data.proc_attrs[-1][1]["convert_to_ppm"])

    def test_fourier_transform_convert_to_ppm_default_false_for_non_nmr(self):
        data = self.data_1d.copy()
        del data.spinlab_attrs["frequency"]

        ft_data = sl.fourier_transform(data)

        dt = data.coords["t2"][1] - data.coords["t2"][0]
        expected_coord = (1.0 / (data.shape[0] * dt)) * np.r_[0 : data.shape[0]]
        expected_coord -= 1.0 / (2 * dt)

        assert_allclose(ft_data.coords["f2"], expected_coord)
        self.assertFalse(ft_data.proc_attrs[-1][1]["convert_to_ppm"])

    def test_fourier_transform_forced_ppm_ignores_frequency_outside_spinlab_attrs(self):
        data = self.data_1d.copy()
        data.spinlab_attrs.pop("frequency", None)
        data.spinlab_attrs["nmr_frequency"] = 400e6
        data.attrs["frequency"] = 400e6
        data.attrs["nmr_frequency"] = 400e6

        with self.assertWarns(UserWarning) as warning:
            ft_data = sl.fourier_transform(data, convert_to_ppm=True)

        dt = data.coords["t2"][1] - data.coords["t2"][0]
        expected_coord = (1.0 / (data.shape[0] * dt)) * np.r_[0 : data.shape[0]]
        expected_coord -= 1.0 / (2 * dt)

        self.assertIn("Frequency not found", str(warning.warning))
        assert_allclose(ft_data.coords["f2"], expected_coord)
        self.assertTrue(ft_data.proc_attrs[-1][1]["convert_to_ppm"])

    def test_fourier_transform_shift_false(self):
        ft_data = sl.fourier_transform(
            self.data_1d, shift=False, convert_to_ppm=False
        )

        dt = self.data_1d.coords["t2"][1] - self.data_1d.coords["t2"][0]
        expected_coord = (1.0 / (self.data_1d.shape[0] * dt)) * np.r_[
            0 : self.data_1d.shape[0]
        ]

        self.assertEqual(ft_data.dims, ["f2"])
        assert_allclose(ft_data.coords["f2"], expected_coord)
        assert_allclose(ft_data.values, np.fft.fft(self.data_1d.values))

    def test_fourier_transform_non_time_dim_keeps_dim_name(self):
        x = np.r_[0:16]
        values = np.sin(2 * np.pi * x / x.size)
        data = sl.SpinData(values, ["x"], [x])

        ft_data = sl.fourier_transform(data, dim="x", convert_to_ppm=False)

        self.assertEqual(ft_data.dims, ["x"])
        self.assertEqual(ft_data.shape, data.shape)
        assert_allclose(
            ft_data.values,
            np.fft.fftshift(np.fft.fft(data.values)),
        )

    def test_fourier_transform_invalid_dim_raises_value_error(self):
        with self.assertRaises(ValueError):
            sl.fourier_transform(self.data_1d, dim="not_a_dim")

    def test_fourier_transform_does_not_mutate_input(self):
        original_values = self.data_1d.values.copy()
        original_coords = self.data_1d.coords["t2"].copy()
        original_dims = self.data_1d.dims.copy()

        sl.fourier_transform(self.data_1d, zero_fill_factor=4, convert_to_ppm=False)

        self.assertEqual(self.data_1d.dims, original_dims)
        assert_array_equal(self.data_1d.coords["t2"], original_coords)
        assert_allclose(self.data_1d.values, original_values)

    def test_fourier_transform_zero_fill_factor_less_than_one_defaults_to_one(self):
        for zero_fill_factor in [0, -2]:
            ft_data = sl.fourier_transform(
                self.data_1d,
                zero_fill_factor=zero_fill_factor,
                convert_to_ppm=False,
            )

            self.assertEqual(ft_data.shape, self.data_1d.shape)
            assert_allclose(
                ft_data.values,
                np.fft.fftshift(np.fft.fft(self.data_1d.values)),
            )

    def test_rename_ft_dim(self):
        self.assertEqual(_rename_ft_dim("t2", "t", "f"), "f2")
        self.assertEqual(_rename_ft_dim("t", "t", "f"), "f")
        self.assertEqual(_rename_ft_dim("time", "t", "f"), "time")
        self.assertEqual(_rename_ft_dim("x", "t", "f"), "x")
        self.assertEqual(_rename_ft_dim("f2", "f", "t"), "t2")

    def test_fourier_transform_short_coord_raises_value_error(self):
        data = sl.SpinData(np.array([1.0]), ["t2"], [np.array([0.0])])

        with self.assertRaises(ValueError):
            sl.fourier_transform(data, convert_to_ppm=False)

    def test_zero_fill_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            zero_fill()

    def test_convert_to_ppm_does_not_mutate_input(self):
        freq_coord = np.array([-2000.0, 0.0, 2000.0])
        original_coord = freq_coord.copy()

        out = _convert_to_ppm(freq_coord, 400e6)

        expected = np.array([-5.0, 0.0, 5.0])
        assert_allclose(out, expected)
        assert_allclose(freq_coord, original_coord)


if __name__ == "__main__":
    unittest.main()
    pass
