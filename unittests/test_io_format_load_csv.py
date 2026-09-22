import pathlib
import unittest

import spinlab as sl


class load_csv_format_tester(unittest.TestCase):
    def setUp(self):
        self.testdata = pathlib.Path(".", "data", "csv")

    def test_import_csv_arr_lna_fid(self):
        data = sl.io.formats.load_csv.load_csv(
            self.testdata.joinpath("csv_example.csv"),
            skiprows=1,
            maxrows=115,
            tcol=0,
            real=1,
            imag=3,
        )
        self.assertEqual(data.dims[0], "t2")
        self.assertEqual(data.values[1], 5e3 + 1j * 25000)
        self.assertEqual(data.coords[0][1], 20)
        self.assertEqual(data.values.size, 115)

    def test_none_time_column_uses_index_coord(self):
        data = sl.io.formats.load_csv.load_csv(
            self.testdata.joinpath("csv_example.csv"),
            skiprows=1,
            maxrows=115,
            tcol=None,
            real=1,
            imag=3,
        )
        self.assertEqual(data.dims[0], "t2")
        self.assertEqual(data.values[1], 5e3 + 1j * 25000)
        self.assertEqual(data.coords[0][100], 100)
        self.assertEqual(data.values.size, 115)

    def test_none_imag_column_sets_imag_to_zero(self):
        data = sl.io.formats.load_csv.load_csv(
            self.testdata.joinpath("csv_example.csv"),
            skiprows=1,
            maxrows=115,
            tcol=None,
            real=1,
            imag=None,
        )
        self.assertEqual(data.dims[0], "t2")
        self.assertEqual(data.values[1], 5e3)
        self.assertEqual(data.coords[0][100], 100)
        self.assertEqual(data.values.size, 115)


if __name__ == "__main__":
    unittest.main()
