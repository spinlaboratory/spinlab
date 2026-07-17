import json
import os
import tempfile
import unittest

import numpy as np
from numpy.testing import assert_allclose

from spinlab.io.ciqtek import import_ciqtek


class CiqtekImport1DFieldSweep(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(".", "data", "ciqtek", "CWEPR-Field Sweep test.epr")
        self.data = import_ciqtek(self.path)

    def test_returns_spindata(self):
        import spinlab

        self.assertIsInstance(self.data, spinlab.SpinData)

    def test_dims(self):
        self.assertEqual(self.data.dims, ["B0"])

    def test_shape(self):
        self.assertEqual(self.data.values.shape, (1000,))

    def test_values_complex(self):
        self.assertTrue(np.iscomplexobj(self.data.values))

    def test_b0_axis_in_mT(self):
        # Raw field axis is in Gauss; import divides by 10 to get mT
        b0 = self.data.coords["B0"]
        assert_allclose(b0[0], 346.1401, rtol=1e-5)
        assert_allclose(b0[-1], 351.1401, rtol=1e-5)

    def test_b0_axis_length(self):
        self.assertEqual(len(self.data.coords["B0"]), 1000)

    def test_attr_x_points(self):
        self.assertEqual(self.data.attrs["x_points"], 1000)

    def test_attr_nscans(self):
        self.assertEqual(self.data.attrs["nscans"], 1)

    def test_attr_center_field(self):
        assert_allclose(self.data.attrs["center_field"], 3486.401, rtol=1e-6)

    def test_attr_modulation_amplitude(self):
        assert_allclose(self.data.attrs["modulation_amplitude"], 6.0, rtol=1e-6)

    def test_attr_frequency(self):
        assert_allclose(self.data.attrs["frequency"], 9.7768742742848, rtol=1e-6)

    def test_attr_experiment_type(self):
        self.assertEqual(self.data.attrs["experiment_type"], "epr_spectrum")

    def test_attr_experiment(self):
        self.assertEqual(self.data.attrs["experiment"], "CW EPR/1D Field Sweep")

    def test_attr_device(self):
        self.assertEqual(self.data.attrs["device"], "EPR200_2.0")

    def test_attr_create_time(self):
        self.assertEqual(self.data.attrs["create_time"], "2026-06-22 17:21:43.227")


class CiqtekImport1DFieldSweep500pt(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(
            ".", "data", "ciqtek", "CWEPR-1DFieldSweep_1_20260622154924.epr"
        )
        self.data = import_ciqtek(self.path)

    def test_dims(self):
        self.assertEqual(self.data.dims, ["B0"])

    def test_shape(self):
        self.assertEqual(self.data.values.shape, (500,))

    def test_b0_axis_length(self):
        self.assertEqual(len(self.data.coords["B0"]), 500)

    def test_attr_x_points(self):
        self.assertEqual(self.data.attrs["x_points"], 500)


class CiqtekImport2DTimeFieldSweep(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(
            ".",
            "data",
            "ciqtek",
            "CWEPR-2DTime-FieldSweep_Noise_Varied_Fields.epr",
        )
        self.data = import_ciqtek(self.path)

    def test_dims(self):
        self.assertEqual(self.data.dims, ["t2", "B0"])

    def test_shape(self):
        self.assertEqual(self.data.values.shape, (1000, 5))

    def test_values_complex(self):
        self.assertTrue(np.iscomplexobj(self.data.values))

    def test_t2_axis_first_point(self):
        assert_allclose(self.data.coords["t2"][0], 0.0, atol=1e-6)

    def test_t2_axis_last_point(self):
        assert_allclose(self.data.coords["t2"][-1], 180000.0, rtol=1e-5)

    def test_t2_axis_length(self):
        self.assertEqual(len(self.data.coords["t2"]), 1000)

    def test_b0_axis_values_in_mT(self):
        # Trace names: TimeField_2975 ... TimeField_3025 (Gauss) -> /10 = mT
        expected_mT = np.array([297.5, 298.75, 300.0, 301.25, 302.5])
        assert_allclose(self.data.coords["B0"], expected_mT, rtol=1e-5)

    def test_b0_axis_length(self):
        self.assertEqual(len(self.data.coords["B0"]), 5)

    def test_attr_x_points(self):
        self.assertEqual(self.data.attrs["x_points"], 1000)

    def test_attr_y_points(self):
        self.assertEqual(self.data.attrs["y_points"], 5)

    def test_attr_experiment_type(self):
        self.assertEqual(self.data.attrs["experiment_type"], "epr_spectrum")


class CiqtekImport2DTimeFieldSweep3000G(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(
            ".", "data", "ciqtek", "CWEPR-2DTime-FieldSweep_3000_G.epr"
        )
        self.data = import_ciqtek(self.path)

    def test_dims(self):
        self.assertEqual(self.data.dims, ["t2", "B0"])

    def test_shape(self):
        self.assertEqual(self.data.values.shape, (1000, 5))

    def test_b0_axis_in_mT(self):
        # Trace names: TimeField_3000, TimeField_3012.5, ... -> mT
        b0 = self.data.coords["B0"]
        self.assertEqual(len(b0), 5)
        # All field values should be near 300 mT (3000 G / 10)
        self.assertTrue(np.all(b0 > 295.0))
        self.assertTrue(np.all(b0 < 310.0))


class CiqtekImportErrors(unittest.TestCase):
    def test_wrong_extension_raises_type_error(self):
        with self.assertRaises(TypeError):
            import_ciqtek("data.txt")

    def test_no_extension_raises_type_error(self):
        with self.assertRaises(TypeError):
            import_ciqtek("datafile")

    def test_missing_data_raises_value_error(self):
        # Write a minimal valid .epr with empty lineDataList
        minimal = {
            "devicename": "test",
            "type": "test",
            "createTime": "",
            "filename": "",
            "setting": {},
            "dataStore": {"lineDataList": [], "xAxisName": "Field[G]"},
        }
        with tempfile.NamedTemporaryFile(
            suffix=".epr", mode="w", delete=False, encoding="utf-8"
        ) as f:
            json.dump(minimal, f)
            tmp_path = f.name
        try:
            with self.assertRaises(ValueError):
                import_ciqtek(tmp_path)
        finally:
            os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()
