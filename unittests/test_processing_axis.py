import unittest

import numpy as np
import spinlab as sl
from numpy.testing import assert_allclose, assert_array_equal

from spinlab.processing.axis import left_shift, reference


class sl_axis_tester(unittest.TestCase):
    def setUp(self):
        self.x = np.arange(10)
        self.data = sl.SpinData(self.x.astype(float), ["t2"], [self.x.copy()])

    def test_left_shift_removes_points_from_left(self):
        out = left_shift(self.data, dim="t2", shift_points=3)

        assert_array_equal(out.values, self.data.values[3:])
        assert_array_equal(out.coords["t2"], self.x[3:])
        self.assertEqual(out.proc_attrs[-1][0], "left_shift")
        self.assertEqual(out.proc_attrs[-1][1]["points"], 3)

    def test_reference_shifts_coordinate_and_records_proc_attrs(self):
        out = reference(self.data, dim="t2", old_ref=2, new_ref=5)

        assert_allclose(out.coords["t2"], self.x + 3)
        assert_array_equal(out.values, self.data.values)
        self.assertEqual(out.proc_attrs[-1][0], "reference")
        self.assertEqual(out.proc_attrs[-1][1]["old_ref"], 2)
        self.assertEqual(out.proc_attrs[-1][1]["new_ref"], 5)

    def test_reference_does_not_mutate_input(self):
        original_coord = self.data.coords["t2"].copy()

        reference(self.data, dim="t2", old_ref=2, new_ref=5)

        assert_array_equal(self.data.coords["t2"], original_coord)


if __name__ == "__main__":
    unittest.main()
