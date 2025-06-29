import unittest
import os
import spinlab as sl
from numpy.testing import assert_array_equal
import numpy as np

import logging
import sys
import pathlib
import warnings

logger = logging.getLogger(__name__)


class slTools_tester(unittest.TestCase):
    def setUp(self):
        x = np.r_[0:10]
        y = x**2.0
        self.data = sl.SpinData(y, ["t2"], [x])
        self.testdata = os.path.join(".", "data", "csv")
        p = pathlib.Path(self.testdata)
        self.data = sl.io.load_csv.load_csv(
            p.joinpath("csv_example.csv"),
            skiprows=1,
            maxrows=1000,
            tcol=0,
            real=1,
            imag=3,
            convert_time=lambda x: float(x.replace(",", ".")) / 1e6,
        )
        self.data.attrs["nmr_frequency"] = 14.86e6

        self.rnd_data = self.data.copy()

    def test_999_quicktests(self):
        # create_complex
        data_r = np.ones(100)
        data_c = np.ones(100) * 2
        #
        x = np.r_[0:100]
        y = np.array([x**2.0, x**3.0]).T

        # leads to warning
        rnd_data = sl.SpinData(y, ["t2", "bla"], [x,x])

        sl.processing.create_complex(rnd_data, data_r, data_c)

        # needs integrals:
        x = np.r_[0:100]
        y = np.array([x**2.0, x**3.0]).T
        data = sl.SpinData(y, ["t2", "Power"], [x, np.array([0, 1])])

        ft_data = sl.fourier_transform(data)
        integrals = sl.integrate(ft_data)
        sl.processing.calculate_enhancement(integrals)

        # makes data not consistent!
        # smooth
        sl.processing.smooth(data, window_length=3, polyorder=2)

        # left_shift
        sl.processing.left_shift(self.data, shift_points=5)

        # normalize
        sl.processing.normalize(self.data, dim="t2")

        # reference
        sl.processing.reference(self.data, dim="t2")

        # pseudo_modulation
        sl.processing.pseudo_modulation(self.data, 0.1, dim="t2")

    def test_000_functionality_signal_to_noise(self):
        """
        check only whether the function raises no error with SpinData input, not whether rsults are useful
        alot of simple tests lumped together

        Missing: check whether signal and noise are scalar values

        note that these tests are not really unittests but more integration tests
        """
        f = sl.processing.signal_to_noise

        self.assertRaises(ValueError, f, self.data, (300, 400), (500, 600))

        data = sl.fourier_transform(self.data)

        try:
            snr = f(data, (300, 400), (500, 600))
        except ValueError as e:
            self.fail("signal_to_noise reported ValueError {0}".format(e))
        self.assertTrue(not np.isnan(snr._values))

        snr = f(
            data,
            (300, 400),
            (500, 600),
        )
        # sldata object as output
        self.assertTrue(type(snr), type(self.data))

    def test_001_using_different_dimensions(self):
        f = sl.processing.signal_to_noise
        data = sl.fourier_transform(self.data)

        # some input checks, just to check that no errors are thrown:
        snr = f(data, [(300, 400)], [(500, 600)])
        snr = f(
            data, [(300, 400)], [(500, 600)], remove_background=(100, 200), deg=3
        )  # works with degree
        snr = f(
            data, [(300, 400)], [(500, 600)], remove_background=(100, 200)
        )  # works without degree
        snr = f(
            data, [(300, 400)], [(500, 600)], remove_background=[(100, 200)]
        )  # works with list as intended
        snr = f(
            data, [(-121.5, 104.1)], [(632.5, 1264.2)], remove_background=[(100, 200)]
        )
        snr = f(
            data,
            [(-121.5, 104.1)],
            [(632.5, 1264.2)],
            remove_background=[(-1300.1, -500.0)],
        )
        self.assertEqual(snr.shape, (1,))

        # with defaults
        snr = f(data, noise_region = [(0,1)])
        # with slices
        snr = f(data, slice(0, None), noise_region = [(0,1)], remove_background=[(100, 200)])

        # with more than one signal region:
        snr = f(data, [slice(0, None), (100, 300)], noise_region = [(0,1)])
        self.assertEqual(snr.shape[0], 2)

        self.assertEqual(snr.shape, (2,))

        # multiple noise regions
        snr2 = f(data, (0, 1000), noise_region = [(0,1)], remove_background=[(100, 200)])
        snr = f(
            data,
            slice(0, None),
            [slice(0, 100), slice(500, 600)],
            remove_background=[(100, 200)],
        )

    def test_002_SNR_on_higherDimensionalData(self):
        coords3 = [np.arange(0, 100), np.arange(0, 20), np.arange(0, 40)]
        data3 = np.random.random((100, 20, 40))
        SpinObj3 = sl.SpinData(data3, ["t2", "t3", "t4"], coords3)
        f = sl.processing.signal_to_noise

        # single snr region
        snr0 = f(SpinObj3, (10, 20), [(80, 90)], dim="t2")
        logger.info("snr0 (single regions) value shape is {0}".format(snr0.shape))
        self.assertEqual(len(snr0.shape), 3)
        self.assertEqual(snr0.shape, (1, 20, 40))

        snr = f(SpinObj3, [(10, 20), (30, 40), (50, 60)], [(80, 90)], dim="t2")
        self.assertEqual(snr.shape[0], 3)
        self.assertEqual(len(snr.shape), 3)
        self.assertEqual(snr.shape[1], 20)
        self.assertEqual(snr.shape[2], 40)

    def test_003_correct_snr_attribution(self):
        # create artificial testdata
        data = np.empty((100, 5, 8))
        for u in range(100):
            for k in range(5):
                for l in range(8):
                    # idea: [0,1,2,3,4] + [l*10+k+u*100 if x==50 else 0 for x in range(95)] along u
                    if u < 5:
                        data[u, k, l] = u
                    elif u == 50:
                        data[u, k, l] = l * 10 + k + u * 100
                    else:
                        data[u, k, l] = 0
        dims = ["f2", "a1", "a2"]
        coords = [np.arange(100), np.arange(5), np.arange(8)]
        SpinObj = sl.SpinData(data, dims, coords)

        snr = sl.processing.signal_to_noise(SpinObj, (45, 55), (0, 5), dim="f2")

        noise = np.std(np.arange(5))
        signal_10_2_5 = 5 * 10 + 2 + 100 * 10

        self.assertTrue(
            snr["signal_region", 0, "a1", 2, "a2", 5], signal_10_2_5 / noise
        )

    def test_004_abs_signal_test(self):
        pts = 100
        x = np.r_[0.0 : 99.0 : 1j * pts]
        y = sl.lineshape.gaussian(x, 50, 5, integral=1.0)

        y /= np.max(y)
        np.random.seed(100)
        y += np.random.randn(pts) * 0.1

        signal = np.max(y)
        noise = np.std(y[70:100])

        data = sl.SpinData(y, ["x"], [x])
        snr = sl.signal_to_noise(data, [(0, 100)], dim="x", noise_region=[(70, 100)])

        self.assertTrue(np.isclose(snr["signal_region", 0].values, signal / noise))
        # negative peak:
        data = -1 * data
        snr2 = sl.signal_to_noise(data, [(0, 100)], dim="x", noise_region=[(70, 100)])

        self.assertTrue(np.isclose(snr2["signal_region", 0].values, signal / noise))

    def test_005_complex_data_test(self):
        #
        # test on complex dataset
        #

        pts = 100
        x = np.r_[0.0 : 99.0 : 1j * pts]
        y = sl.lineshape.gaussian(x, 50, 5, integral=1.0)
        y = y.astype(complex) + 1j * np.random.randn(pts) * 0.1

        y /= np.max(y)
        np.random.seed(100)
        y += np.random.randn(pts) * 0.1

        # complex SNR
        signal = np.max(np.abs(y))
        noise = np.std(y[70:100])

        data = sl.SpinData(y, ["x"], [x])
        snr = sl.signal_to_noise(
            data, [(0, 100)], dim="x", noise_region=[(70, 100)], complex_noise=True
        )
        self.assertTrue(np.isclose(snr["signal_region", 0].values, signal / noise))

        # real SNR
        snr = sl.signal_to_noise(
            data, [(0, 100)], dim="x", noise_region=[(70, 100)], complex_noise=False
        )
        self.assertTrue(
            np.isclose(
                snr["signal_region", 0].values,
                np.real(np.max(np.abs(y))) / np.std(np.real(y[70:100])),
            )
        )

    def test_006_create_complex_tests(self):

        npDat = np.ones((100, 2, 25, 1, 10)) * 1.0123987
        npDat[:,1,...] = 0.51
        npCoords = [np.arange(k) + np.random.randint(10) for k in npDat.shape]
        npDims = ["1", "2", "3", "4", "5"]

        data=sl.SpinData(npDat,npDims,npCoords)

        complex_2 = sl.create_complex(data, "2")
        #this  operation will make data inconsistent and issue a warning, also complex_1 will be inconsistent, this is due to the old implementation of create_complex, therefore use catch_warnings context manager
        complex_1=None
        with warnings.catch_warnings() as w:
            warnings.simplefilter("ignore")
            complex_1 = sl.create_complex(data,data._values[:,0,...],data._values[:,1,...])


        self.assertEqual(complex_1.shape, complex_2.shape)
        self.assertEqual((100, 25, 1, 10), complex_2.shape)
        trueVal = np.all(
            np.isclose(complex_1._values - complex_2._values, 0, rtol=1e-04, atol=1e-07)
        )
        if not trueVal:
            print(max(abs(complex_1._values - complex_2._values)))
        self.assertTrue(trueVal)
        self.assertTrue(complex_2._self_consistent())
        trueVal = np.all(
            np.isclose(complex_2.coords[1] - npCoords[2], 0, rtol=1e-04, atol=1e-07)
        )
        if not trueVal:
            print(max(abs(complex_1._values - complex_2._values)))
        self.assertTrue(trueVal)

        npDat = np.ones((1, 1, 2, 100, 25, 1, 10, 1)) * 1.0123456789
        npDat[:,:,1,...] = 0.587
        npCoords = [np.arange(k) + np.random.randint(10) for k in npDat.shape]
        npDims = ["1", "2", "3", "4", "5", "6", "7", "8"]

        data = sl.SpinData(npDat, npDims, npCoords)

        complex_2 = sl.create_complex(data, "3")
        self.assertEqual((1, 1, 100, 25, 1, 10, 1), complex_2.shape)
        self.assertTrue(complex_2._self_consistent())

        # test with 5 dimensions in complex dimension
        npDat = np.ones((100, 5, 25, 1, 10)) * 1.0547891
        npDat[:,1,...] = 0.587
        npCoords = [np.arange(k) + np.random.randint(10) for k in npDat.shape]
        npDims = ["1", "2", "3", "4", "5"]

        data = sl.SpinData(npDat, npDims, npCoords)
        # warning
        self.assertWarns(UserWarning, sl.create_complex, data, "2")
        # warnings off from now
        warnings.filterwarnings("ignore")
        complex_3 = sl.create_complex(data, "2", real_index=1, imag_index=3)
        self.assertTrue(complex_3.shape == (100, 25, 1, 10))
        self.assertTrue(
            np.all(
                np.isclose(
                    np.real(complex_3._values),
                    np.real(data._values[:, 1, ...]),
                    rtol=1e-06,
                    atol=1e-07,
                )
            )
        )
        self.assertTrue(
            np.all(
                np.isclose(
                    np.imag(complex_3._values),
                    np.real(data._values[:, 3, ...]),
                    rtol=1e-06,
                    atol=1e-07,
                )
            )
        )

        complex_3 = sl.create_complex(data, "2")
        self.assertTrue(
            np.all(
                np.isclose(
                    np.real(complex_3._values),
                    np.real(data._values[:, 0, ...]),
                    rtol=1e-06,
                    atol=1e-07,
                )
            )
        )
        self.assertTrue(
            np.all(
                np.isclose(
                    np.imag(complex_3._values),
                    np.real(data._values[:, 1, ...]),
                    rtol=1e-06,
                    atol=1e-07,
                )
            )
        )
        

    def test_007_normalize_tests(self):

        # make testdata
        npDat = np.empty((500, 2, 3))  # 500->t2, 50 -> prm1, 3->prm2
        t2 = np.linspace(0, 100, 500)
        prm1AxisDat = np.atleast_2d(np.ones(npDat.shape[1]))
        tau = [100, 50, 25]
        for k in range(3):
            npDat[:, :, k] = (
                (k + 1)
                * np.atleast_2d(np.exp(-t2 / tau[k]) - np.random.random(len(t2))).T
                * prm1AxisDat
            )
            npDat[0, :, k] = k + 1

        data = sl.SpinData(
            npDat, ["t2", "prm1", "prm2"], [t2, np.arange(npDat.shape[1]), np.arange(3)]
        )
        data_1d = sl.SpinData(npDat[:, 0, 0], ["t2"], [t2])

        self.assertRaises(ValueError, sl.normalize, data, dim="f2")
        self.assertTrue(data["t2", (1, 80)].shape == (394, npDat.shape[1], 3))

        # no region &  no dim
        data_t = sl.normalize(data)
        data_t2 = sl.normalize(data_1d)
        self.assertTrue(
            np.all(
                np.isclose(data_t._values[0, :, 0], 0.333333, rtol=1e-04, atol=1e-07)
            )
        )
        self.assertTrue(
            np.all(
                np.isclose(data_t._values[0, :, 1], 0.666667, rtol=1e-04, atol=1e-07)
            )
        )
        self.assertTrue(
            np.all(np.isclose(data_t._values[0, :, 2], 1, rtol=1e-04, atol=1e-07))
        )

        self.assertTrue(np.all(np.isclose(data_t2._values[0], 1)))

        # no region & dim
        data_t = sl.normalize(data, dim="t2")
        data_t2 = sl.normalize(data_1d, dim="t2")
        self.assertTrue(
            np.all(np.isclose(data_t._values[0, :, :], 1, rtol=1e-04, atol=1e-07))
        )

        self.assertTrue(
            np.all(np.isclose(data_t2._values[0], 1, rtol=1e-04, atol=1e-07))
        )

        # with region & dim
        data._values[55, :, :] = np.max(data._values[55, :, :]) * 1.5
        data_t = sl.normalize(data, dim="t2", regions=(10, 50))
        maxvalues = np.max(data["t2", (10, 50)]._values, axis=0)
        refvalues = data["t2", 0]._values / maxvalues

        data_1d._values[55] = np.max(data_1d._values) * 1.5
        data_t2 = sl.normalize(data_1d, dim="t2", regions=(10, 50))
        maxvalues_1d = np.max(data_1d["t2", (10, 50)]._values, axis=0)
        refvalues_1d = data_1d["t2", 0]._values / maxvalues_1d

        trueVal = np.all(
            np.isclose(
                np.max(data_t["t2", (10, 50)]._values, axis=0),
                1,
                rtol=1e-03,
                atol=1e-03,
            )
        )
        if not trueVal:
            print(
                np.max(data_t["t2", (10, 50)]._values, axis=0),
                refvalues_1d,
                np.argmax(data_1d.values),
            )
        self.assertTrue(trueVal)
        self.assertTrue(
            np.all(np.isclose(data_t["t2", 0], refvalues, rtol=1e-04, atol=1e-07))
        )

        self.assertTrue(
            np.all(
                np.isclose(
                    np.max(data_t2["t2", (10, 50)]._values, axis=0),
                    1,
                    rtol=1e-04,
                    atol=1e-07,
                )
            )
        )
        self.assertTrue(
            np.all(np.isclose(data_t2["t2", 0], refvalues_1d, rtol=1e-04, atol=1e-07))
        )

        # with region and no dim
        data_t = sl.normalize(data, regions=(10, 50))
        data_t2 = sl.normalize(data_1d, regions=(10, 50))

        maxvalues = np.max(data["t2", (10, 50)]._values)
        refvalues = data["t2", 0]._values / maxvalues

        maxvalues_1d = np.max(data_1d["t2", (10, 50)]._values)
        refvalues_1d = data_1d["t2", 0]._values / maxvalues_1d

        self.assertTrue(
            np.all(
                np.isclose(
                    np.max(data_t["t2", (10, 50)]._values), 1, rtol=1e-04, atol=1e-07
                )
            )
        )
        self.assertTrue(np.all(np.isclose(data_t["t2", 0], refvalues)))

        self.assertTrue(
            np.all(
                np.isclose(
                    np.max(data_t2["t2", (10, 50)]._values), 1, rtol=1e-04, atol=1e-07
                )
            )
        )
        self.assertTrue(
            np.all(np.isclose(data_t2["t2", 0], refvalues_1d, rtol=1e-04, atol=1e-07))
        )
