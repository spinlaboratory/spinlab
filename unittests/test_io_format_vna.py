import unittest

import numpy as np
import spinlab as sl
from numpy.testing import assert_array_equal


class vna_format_tester(unittest.TestCase):
    def test_get_sldata_from_1d_trace(self):
        coords = np.array([1.0, 2.0, 3.0])
        values = np.array([1 + 1j, 2 + 2j, 3 + 3j])
        attrs = {"data_format": "VNA", "data_order": ["s11"]}

        data = sl.io.formats.vna.get_sldata(values, coords, attrs)

        self.assertEqual(data.dims, ["f"])
        assert_array_equal(data.values, values)
        assert_array_equal(data.coords["f"], coords)
        self.assertEqual(data.spinlab_attrs["data_format"], "VNA")

    def test_get_sldata_from_2d_trace_concatenates_s_parameter_dim(self):
        coords = np.array([1.0, 2.0, 3.0])
        values = np.array(
            [
                [1 + 1j, 2 + 2j, 3 + 3j],
                [4 + 4j, 5 + 5j, 6 + 6j],
            ]
        )
        attrs = {"data_format": "VNA", "data_order": ["s11", "s21"]}

        data = sl.io.formats.vna.get_sldata(values, coords, attrs, concat_dim="s")

        self.assertEqual(data.dims, ["f", "s"])
        self.assertEqual(data.shape, (3, 2))
        assert_array_equal(data.coords["f"], coords)
        assert_array_equal(data.coords["s"], [0, 1])


if __name__ == "__main__":
    unittest.main()
