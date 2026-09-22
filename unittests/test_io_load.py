import contextlib
import inspect
import io
import os
import pathlib
import unittest

import spinlab as sl
from numpy.testing import assert_array_equal


class io_load_tester(unittest.TestCase):
    def test_detect_load_format_is_case_insensitive_for_extensions(self):
        self.assertEqual(sl.io.load._detect_load_format("example.DSC"), "xepr")
        self.assertEqual(sl.io.load._detect_load_format("example.dsc"), "xepr")
        self.assertEqual(sl.io.load._detect_load_format("example.H5"), "h5")
        self.assertEqual(sl.io.load._detect_load_format("example.MAT"), "mat")

    def test_registered_loaders_accept_verbose(self):
        for data_format, loader in sl.io.load._LOADERS.items():
            with self.subTest(data_format=data_format):
                self.assertIn("verbose", inspect.signature(loader).parameters)

    def test_load_list_without_coord_uses_index_coord(self):
        test_data = os.path.join(".", "data", "prospa", "toluene_10mM_Tempone")
        paths = [
            os.path.join(test_data, "%i" % expNum, "data.csv") for expNum in [1, 21]
        ]

        data = sl.load(paths, data_format="prospa", dim="scan")

        self.assertEqual(data.dims, ["t2", "scan"])
        self.assertEqual(data.values.shape, (16384, 2))
        assert_array_equal(data.coords["scan"], [0, 1])

    def test_load_dispatches_to_requested_format(self):
        data = sl.load(
            os.path.join(".", "data", "prospa", "toluene_10mM_Tempone", "1", "data.csv"),
            data_format="prospa",
        )

        self.assertEqual(data.dims, ["t2"])
        self.assertEqual(data.values.shape, (16384,))

    def test_csv_verbose_reports_loaded_data(self):
        p = pathlib.Path(".", "data", "csv", "csv_example.csv")
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            sl.io.formats.load_csv.load_csv(
                p,
                skiprows=1,
                maxrows=5,
                tcol=0,
                real=1,
                imag=3,
                convert_time=lambda x: float(x.replace(",", ".")) / 1e6,
                verbose=True,
            )

        output = buffer.getvalue()
        self.assertIn("CSV file:", output)
        self.assertIn("loaded SpinData", output)


if __name__ == "__main__":
    unittest.main()
