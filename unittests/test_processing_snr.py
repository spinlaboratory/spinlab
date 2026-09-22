import logging
import os
import pathlib
import unittest
import warnings

import numpy as np
import spinlab as sl

from spinlab.processing.snr import signal_to_noise


logger = logging.getLogger(__name__)


class sl_snr_tester(unittest.TestCase):
    def setUp(self):
        testdata = os.path.join(".", "data", "csv")
        p = pathlib.Path(testdata)
        self.data = sl.io.formats.load_csv.load_csv(
            p.joinpath("csv_example.csv"),
            skiprows=1,
            maxrows=1000,
            tcol=0,
            real=1,
            imag=3,
            convert_time=lambda x: float(x.replace(",", ".")) / 1e6,
        )
        self.data.attrs["nmr_frequency"] = 14.86e6

    def test_functionality_signal_to_noise(self):
        self.assertRaises(ValueError, signal_to_noise, self.data, (300, 400), (500, 600))

        data = sl.fourier_transform(self.data)

        try:
            snr = signal_to_noise(data, (300, 400), (500, 600))
        except ValueError as e:
            self.fail("signal_to_noise reported ValueError {0}".format(e))
        self.assertTrue(not np.isnan(snr._values))

        snr = signal_to_noise(data, (300, 400), (500, 600))
        self.assertTrue(type(snr), type(self.data))

    def test_using_different_dimensions(self):
        data = sl.fourier_transform(self.data)

        signal_to_noise(data, [(300, 400)], [(500, 600)])
        signal_to_noise(data, [(300, 400)], [(500, 600)], remove_background=(100, 400), deg=3)
        signal_to_noise(data, [(300, 400)], [(500, 600)], remove_background=(100, 200))
        signal_to_noise(data, [(300, 400)], [(500, 600)], remove_background=[(100, 200)])
        signal_to_noise(data, [(-121.5, 104.1)], [(632.5, 1264.2)], remove_background=[(100, 200)])
        snr = signal_to_noise(
            data,
            [(-121.5, 104.1)],
            [(632.5, 1264.2)],
            remove_background=[(-1300.1, -500.0)],
        )
        self.assertEqual(snr.shape, (1,))

        signal_to_noise(data, noise_region=[(0, 1)])
        signal_to_noise(data, slice(0, None), noise_region=[(0, 1)], remove_background=[(100, 400)])

        snr = signal_to_noise(data, [slice(0, None), (100, 300)], noise_region=[(0, 1)])
        self.assertEqual(snr.shape, (2,))

        signal_to_noise(data, (0, 1000), noise_region=[(0, 1)], remove_background=[(100, 400)])
        signal_to_noise(
            data,
            slice(0, None),
            [slice(0, 100), slice(500, 600)],
            remove_background=[(100, 200)],
        )

    def test_snr_on_higher_dimensional_data(self):
        coords3 = [np.arange(0, 100), np.arange(0, 20), np.arange(0, 40)]
        data3 = np.random.random((100, 20, 40))
        SpinObj3 = sl.SpinData(data3, ["t2", "t3", "t4"], coords3)

        snr0 = signal_to_noise(SpinObj3, (10, 20), [(80, 90)], dim="t2")
        logger.info("snr0 (single regions) value shape is {0}".format(snr0.shape))
        self.assertEqual(snr0.shape, (1, 20, 40))

        snr = signal_to_noise(SpinObj3, [(10, 20), (30, 40), (50, 60)], [(80, 90)], dim="t2")
        self.assertEqual(snr.shape, (3, 20, 40))

    def test_correct_snr_attribution(self):
        data = np.empty((100, 5, 8))
        for u in range(100):
            for k in range(5):
                for l in range(8):
                    if u < 5:
                        data[u, k, l] = u
                    elif u == 50:
                        data[u, k, l] = l * 10 + k + u * 100
                    else:
                        data[u, k, l] = 0
        SpinObj = sl.SpinData(data, ["f2", "a1", "a2"], [np.arange(100), np.arange(5), np.arange(8)])

        snr = signal_to_noise(SpinObj, (45, 55), (0, 5), dim="f2")

        noise = np.std(np.arange(5))
        signal_10_2_5 = 5 * 10 + 2 + 100 * 10

        self.assertTrue(
            snr["signal_region", 0, "a1", 2, "a2", 5], signal_10_2_5 / noise
        )

    def test_zero_noise_returns_inf_without_runtime_warning(self):
        x = np.arange(10)
        y = np.zeros(10)
        y[5] = 1
        data = sl.SpinData(y, ["x"], [x])

        with warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            snr = signal_to_noise(
                data, signal_region=(4, 6), noise_region=(0, 3), dim="x"
            )

        self.assertTrue(np.isinf(snr["signal_region", 0].values))

    def test_abs_signal_test(self):
        pts = 100
        x = np.r_[0.0 : 99.0 : 1j * pts]
        y = sl.lineshape.gaussian(x, 50, 5, integral=1.0)

        y /= np.max(y)
        np.random.seed(100)
        y += np.random.randn(pts) * 0.1

        signal = np.max(y)
        noise = np.std(y[70:100])

        data = sl.SpinData(y, ["x"], [x])
        snr = signal_to_noise(data, [(0, 100)], dim="x", noise_region=[(70, 100)])

        self.assertTrue(np.isclose(snr["signal_region", 0].values, signal / noise))

        data = -1 * data
        snr2 = signal_to_noise(data, [(0, 100)], dim="x", noise_region=[(70, 100)])

        self.assertTrue(np.isclose(snr2["signal_region", 0].values, signal / noise))

    def test_complex_data_test(self):
        pts = 100
        x = np.r_[0.0 : 99.0 : 1j * pts]
        y = sl.lineshape.gaussian(x, 50, 5, integral=1.0)
        y = y.astype(complex) + 1j * np.random.randn(pts) * 0.1

        y /= np.max(y)
        np.random.seed(100)
        y += np.random.randn(pts) * 0.1

        signal = np.max(np.abs(y))
        noise = np.std(y[70:100])

        data = sl.SpinData(y, ["x"], [x])
        snr = signal_to_noise(
            data, [(0, 100)], dim="x", noise_region=[(70, 100)], complex_noise=True
        )
        self.assertTrue(np.isclose(snr["signal_region", 0].values, signal / noise))

        snr = signal_to_noise(
            data, [(0, 100)], dim="x", noise_region=[(70, 100)], complex_noise=False
        )
        self.assertTrue(
            np.isclose(
                snr["signal_region", 0].values,
                np.real(np.max(np.abs(y))) / np.std(np.real(y[70:100])),
            )
        )


if __name__ == "__main__":
    unittest.main()
