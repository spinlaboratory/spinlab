import os
import unittest

import spinlab as sl


class specman_format_tester(unittest.TestCase):
    def setUp(self):
        self.test_data_2d = os.path.join(".", "data", "specman", "test_specman2D.exp")
        self.test_data_4d = os.path.join(".", "data", "specman", "test_specman4D.d01")
        self.test_data_field_monitor = os.path.join(
            ".", "data", "specman", "test_specman_field_monitor.exp"
        )

    def test_import_specman_2d(self):
        data = sl.io.formats.specman.import_specman(
            self.test_data_2d,
            autodetect_dims=False,
            autodetect_coords=False,
            make_complex=False,
        )
        self.assertEqual(data.dims, ["x0", "x1", "x2"])
        self.assertEqual(data.values.shape, (4500, 252, 2))

    def test_import_specman_4d(self):
        data = sl.io.formats.specman.import_specman(
            self.test_data_4d,
            autodetect_dims=False,
            autodetect_coords=False,
            make_complex=False,
        )
        self.assertEqual(data.dims, ["x0", "x1", "x2", "x3", "x4"])
        self.assertEqual(data.values.shape, (1500, 40, 5, 3, 2))

    def test_import_specman_2d_with_autodetect(self):
        data = sl.io.formats.specman.import_specman(
            self.test_data_2d,
            autodetect_dims=True,
            autodetect_coords=True,
            make_complex=False,
        )
        self.assertEqual(data.dims, ["t2", "t", "x"])
        self.assertEqual(data.values.shape, (4500, 252, 2))

    def test_import_specman_4d_with_autodetect(self):
        data = sl.io.formats.specman.import_specman(
            self.test_data_4d,
            autodetect_dims=True,
            autodetect_coords=True,
            make_complex=False,
        )
        self.assertEqual(data.dims, ["t2", "Fr_pump", "offset1", "tsquare", "x"])
        self.assertEqual(data.values.shape, (1500, 40, 5, 3, 2))

    def test_import_specman_field_monitor(self):
        data = sl.io.formats.specman.import_specman(
            self.test_data_field_monitor,
            autodetect_dims=True,
            autodetect_coords=True,
            make_complex=False,
        )
        self.assertEqual(data.dims, ["tau", "Field", "x"])
        self.assertEqual(data.values.shape, (101, 101, 2))
        self.assertEqual(data.coords["tau"][0], 3.0000000000000004e-07)


if __name__ == "__main__":
    unittest.main()
