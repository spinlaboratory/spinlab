import unittest
import warnings

import numpy as np
import spinlab as sl

from spinlab.processing.complex_data import create_complex


class sl_complex_data_tester(unittest.TestCase):
    def test_create_complex_from_external_real_and_imag_arrays(self):
        template = sl.SpinData(
            np.ones((3, 2)), ["x", "complex"], [np.arange(3), np.arange(2)]
        )
        real = np.array([1, 2, 3])
        imag = np.array([4, 5, 6])

        out = create_complex(template, real, imag)

        self.assertEqual(out.dims, ["x"])
        np.testing.assert_allclose(out.values, real + 1j * imag)
        self.assertEqual(template.dims, ["x", "complex"])

    def test_create_complex_tests(self):
        npDat = np.ones((100, 2, 25, 1, 10)) * 1.0123987
        npDat[:, 1, ...] = 0.51
        npCoords = [np.arange(k) + np.random.randint(10) for k in npDat.shape]
        npDims = ["1", "2", "3", "4", "5"]

        data = sl.SpinData(npDat, npDims, npCoords)

        complex_2 = create_complex(data, "2")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            complex_1 = create_complex(data, data._values[:, 0, ...], data._values[:, 1, ...])

        self.assertEqual(complex_1.shape, complex_2.shape)
        self.assertEqual((100, 25, 1, 10), complex_2.shape)
        self.assertTrue(np.all(np.isclose(complex_1._values - complex_2._values, 0, rtol=1e-04, atol=1e-07)))
        self.assertTrue(complex_2._self_consistent())
        self.assertTrue(np.all(np.isclose(complex_2.coords[1] - npCoords[2], 0, rtol=1e-04, atol=1e-07)))

        npDat = np.ones((1, 1, 2, 100, 25, 1, 10, 1)) * 1.0123456789
        npDat[:, :, 1, ...] = 0.587
        npCoords = [np.arange(k) + np.random.randint(10) for k in npDat.shape]
        npDims = ["1", "2", "3", "4", "5", "6", "7", "8"]

        data = sl.SpinData(npDat, npDims, npCoords)

        complex_2 = create_complex(data, "3")
        self.assertEqual((1, 1, 100, 25, 1, 10, 1), complex_2.shape)
        self.assertTrue(complex_2._self_consistent())

        npDat = np.ones((100, 5, 25, 1, 10)) * 1.0547891
        npDat[:, 1, ...] = 0.587
        npCoords = [np.arange(k) + np.random.randint(10) for k in npDat.shape]
        npDims = ["1", "2", "3", "4", "5"]

        data = sl.SpinData(npDat, npDims, npCoords)
        self.assertWarns(UserWarning, create_complex, data, "2")

        warnings.filterwarnings("ignore")
        complex_3 = create_complex(data, "2", real_index=1, imag_index=3)
        self.assertTrue(complex_3.shape == (100, 25, 1, 10))
        self.assertTrue(np.all(np.isclose(np.real(complex_3._values), np.real(data._values[:, 1, ...]), rtol=1e-06, atol=1e-07)))
        self.assertTrue(np.all(np.isclose(np.imag(complex_3._values), np.real(data._values[:, 3, ...]), rtol=1e-06, atol=1e-07)))

        complex_3 = create_complex(data, "2")
        self.assertTrue(np.all(np.isclose(np.real(complex_3._values), np.real(data._values[:, 0, ...]), rtol=1e-06, atol=1e-07)))
        self.assertTrue(np.all(np.isclose(np.imag(complex_3._values), np.real(data._values[:, 1, ...]), rtol=1e-06, atol=1e-07)))


if __name__ == "__main__":
    unittest.main()
