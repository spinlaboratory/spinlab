import unittest
import spinlab as sl
import os
import warnings
import numpy as _np
from numpy.testing import assert_array_equal
import logging

logger = logging.getLogger(__name__)


class import_topspin_tester(unittest.TestCase):
    def setUp(self):
        self.testdata = os.path.join(".", "data", "topspin")

    def test_import_topspin_exp1_is_fid(self):
        data = sl.load(os.path.join(self.testdata, str(1)), data_format="topspin")
        self.assertEqual(data.dims[0], "t2")
        self.assertEqual(data.values.size, 8192)
        self.assertAlmostEqual(data.attrs["nmr_frequency"], 14831413.270000001)

    def test_import_topspin_exp5_is_2d_phcyc(self):
        data = sl.load(os.path.join(self.testdata, str(5)), data_format="topspin")
        self.assertEqual(data.values.shape[0], 11973)
        self.assertEqual(data.dims, ["t2", "t1"])
        self.assertAlmostEqual(data.attrs["nmr_frequency"], 14831413.270000001)

    def test_import_topspin_exp28_is_2d(self):
        data = sl.load(os.path.join(self.testdata, str(28)), data_format="topspin")
        self.assertEqual(data.values.shape, (7983, 8))
        self.assertEqual(data.dims, ["t2", "t1"])
        self.assertAlmostEqual(data.attrs["nmr_frequency"], 14831413.270000001)

    def test_import_topspin_jcamp_dx(self):
        attrs = sl.io.topspin.load_topspin_jcamp_dx(
            os.path.join(self.testdata, "1", "acqus")
        )
        self.assertEqual(attrs["DIGTYP"], 9)
        self.assertAlmostEqual(attrs["O1"], 1413.27)
        assert_array_equal(attrs["XGAIN"], [0, 0, 0, 0])
        assert_array_equal(attrs["TPOAL"], [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])


class prospa_import_tester(unittest.TestCase):
    def setUp(self):
        self.test_data = os.path.join(".", "data", "prospa", "toluene_10mM_Tempone")

    def test_import_prospa_exp_is_1d(self):
        datas = [
            sl.load(
                os.path.join(self.test_data, "%i" % expNum, "data.csv"),
                data_format="prospa",
            )
            for expNum in [1, 21, 42]
        ]
        for i, data in enumerate(datas):
            self.assertEqual(data.values.shape, (16384,))
            self.assertEqual(data.dims, ["t2"])
            self.assertAlmostEqual(data.attrs["nmr_frequency"], 14244500.0)
        self.assertAlmostEqual(datas[0].values[365], -0.217937 + 0.24907j)
        self.assertAlmostEqual(datas[1].values[365], 0.0400292 - 0.0756107j)
        self.assertAlmostEqual(datas[2].values[365], 1.09858 - 2.57966j)


class vnmrj_import_tester(unittest.TestCase):
    def setUp(self):
        self.test_data2Ds = [
            os.path.join(".", "data", "vnmrj", s)
            for s in ["10mM_tempol_in_water_array.fid"]
        ]
        self.test_data1Ds = [
            os.path.join(".", "data", "vnmrj", s)
            for s in [
                "10mM_tempol_in_water_mw_40dBm.fid",
                "10mM_tempol_in_water_mw_off.fid",
            ]
        ]

    def test_import_vnmrj_1d(self):
        datas = [sl.load(path=path, data_format="vnmrj") for path in self.test_data1Ds]
        for i, data in enumerate(datas):
            self.assertEqual(data.values.shape, (131072,))
            self.assertEqual(
                data.dims,
                [
                    "t2",
                ],
            )
            self.assertAlmostEqual(data.attrs["nmr_frequency"], 14244283.4231)
        self.assertAlmostEqual(datas[0].values[365], (-20378767 + 2734659j))
        self.assertAlmostEqual(datas[1].values[365], (-950662 - 138458j))

    def test_import_vnmrj_2d(self):
        datas = [sl.load(path=path, data_format="vnmrj") for path in self.test_data2Ds]
        for i, data in enumerate(datas):
            self.assertEqual(data.values.shape, (131072, 5))
            self.assertEqual(data.dims, ["t2", "t1"])
            self.assertAlmostEqual(data.attrs["nmr_frequency"], 14244283.4231)
        self.assertAlmostEqual(datas[0].values[365, 3], (-1263136 - 1063328.5j))


class specman_import_tester(unittest.TestCase):
    def setUp(self):
        self.test_data_2D = os.path.join(".", "data", "specman", "test_specman2D.exp")
        self.test_data_4D = os.path.join(".", "data", "specman", "test_specman4D.d01")
        self.test_data_field_monitor = os.path.join(
            ".", "data", "specman", "test_specman_field_monitor.exp"
        )

    def test_import_specman_2D(self):
        data = sl.load(
            self.test_data_2D,
            data_format="specman",
            autodetect_dims=False,
            autodetect_coords=False,
            make_complex=False,
        )
        self.assertEqual(data.dims, ["x0", "x1", "x2"])
        self.assertEqual(data.values.shape, (4500, 252, 2))

    def test_import_specman_4D(self):
        data = sl.load(
            self.test_data_4D,
            data_format="specman",
            autodetect_dims=False,
            autodetect_coords=False,
            make_complex=False,
        )
        self.assertEqual(data.dims, ["x0", "x1", "x2", "x3", "x4"])
        self.assertEqual(data.values.shape, (1500, 40, 5, 3, 2))

    def test_import_specman_2D_with_autodetect(self):
        data = sl.load(
            self.test_data_2D,
            data_format="specman",
            autodetect_dims=True,
            autodetect_coords=True,
            make_complex=False,
        )
        self.assertEqual(data.dims, ["t2", "t", "x"])
        self.assertEqual(data.values.shape, (4500, 252, 2))

    def test_import_specman_4D_with_autodetect(self):
        data = sl.load(
            self.test_data_4D,
            data_format="specman",
            autodetect_dims=True,
            autodetect_coords=True,
            make_complex=False,
        )
        self.assertEqual(data.dims, ["t2", "Fr_pump", "offset1", "tsquare", "x"])
        self.assertEqual(data.values.shape, (1500, 40, 5, 3, 2))

    def test_import_specman_field_monitor(self):
        data = sl.load(
            self.test_data_field_monitor,
            data_format="specman",
            autodetect_dims=True,
            autodetect_coords=True,
            make_complex=False,
        )
        self.assertEqual(data.dims, ["tau", "Field", "x"])
        self.assertEqual(data.values.shape, (101, 101, 2))
        self.assertEqual(data.coords["tau"][0], 3.0000000000000004e-07)


class bes3t_import_tester(unittest.TestCase):
    def setUp(self):
        self.test_data_HYSCORE = os.path.join(".", "data", "bes3t", "HYSCORE.DSC")
        self.test_data_DEER = os.path.join(".", "data", "bes3t", "DEER.DSC")
        self.test_data_ESE = os.path.join(".", "data", "bes3t", "2D_ESE.DTA")
        self.test_data_1D = os.path.join(".", "data", "bes3t", "1D_CW.DTA")
        self.test_data_2D = os.path.join(".", "data", "bes3t", "2D_CW.YGF")
        self.test_data_CW_time_sweep = os.path.join(
            ".", "data", "bes3t", "CW_time_sweep.DSC"
        )

    def test_import_bes3t_HYSCORE(self):
        data = sl.load(self.test_data_HYSCORE, data_format="xepr")
        self.assertEqual(data.dims, ["t2", "t1"])
        self.assertEqual(data.values.shape, (175, 175))
        self.assertEqual(max(data.coords["t2"]), 3520.0)
        self.assertEqual(max(data.coords["t1"]), 3520.0)

    def test_import_bes3t_DEER(self):
        data = sl.load(self.test_data_DEER, data_format="xepr")
        self.assertEqual(data.dims, ["t2"])
        self.assertEqual(data.values.shape, (504,))
        self.assertEqual(data.attrs["frequency"], 33.85)

    def test_import_bes3t_ESE(self):
        data = sl.load(self.test_data_ESE, data_format="xepr")
        self.assertEqual(data.dims, ["t2", "t1"])
        self.assertEqual(data.values.shape, (512, 50))
        self.assertEqual(data.attrs["frequency"], 9.296)

    def test_import_bes3t_1D(self):
        data = sl.load(self.test_data_1D, data_format="xenon")
        self.assertEqual(data.dims, ["B0"])
        self.assertEqual(data.values.shape, (2250,))
        self.assertEqual(data.attrs["frequency"], 9.804448)

    def test_import_bes3t_2D(self):
        data = sl.load(self.test_data_2D, data_format="xenon")
        self.assertEqual(data.dims, ["B0", "t1"])
        self.assertEqual(data.values.shape, (1600, 100))
        self.assertEqual(data.attrs["frequency"], 9.627213)
        # t1 axis is nonlinear (YTYP IGD) and read from the .YGF file
        self.assertEqual(data.coords["t1"][0], 0.0)
        self.assertEqual(data.coords["t1"][-1], 2180.53)

    def test_import_bes3t_CW_time_sweep(self):
        # CW time-sweep: linear Time axis (t2), nonlinear per-scan Field
        # axis (t1) read from the .YGF file. XNAM=Time also exercises the
        # sweep_domain == "Time" branch of load_dsc, which previously
        # raised a KeyError when attenuation/pulse_attenuation were absent.
        data = sl.load(self.test_data_CW_time_sweep, data_format="xepr")
        self.assertEqual(data.dims, ["t2", "t1"])
        self.assertEqual(data.values.shape, (1000, 10))
        self.assertEqual(data.attrs["frequency"], 9.834281)
        self.assertEqual(data.coords["t1"][0], 1499.95)
        self.assertEqual(data.coords["t1"][-1], 1500.0500000000002)


class esr5000_import_tester(unittest.TestCase):
    def setUp(self):
        self.test_data_coffee = os.path.join(".", "data", "esr5000", "Coffee.xml")
        self.test_data_bitumen = os.path.join(".", "data", "esr5000", "Bitumen.xml")

    def test_import_esr5000_coffee(self):
        data = sl.load(self.test_data_coffee, data_format="esr5000")
        self.assertEqual(data.dims, ["B0"])
        self.assertEqual(data.values.shape, (3107,))
        self.assertEqual(data.attrs["frequency"], 9.45816496965447)
        self.assertEqual(data.attrs["q_value"], 2051.4248046875)
        self.assertEqual(data.attrs["nscans"], 1)
        self.assertAlmostEqual(data.coords["B0"][0], 331.53399658203125)
        self.assertAlmostEqual(data.coords["B0"][-1], 342.0386657714844)
        # default signal is "absorption" -- the real-valued channel
        # matching ESRStudio's own .DSC/.DTA exports
        self.assertTrue(_np.isrealobj(data.values))
        self.assertAlmostEqual(data.values[365], 3.7853982239281443)

    def test_import_esr5000_bitumen(self):
        data = sl.load(self.test_data_bitumen, data_format="esr5000")
        self.assertEqual(data.dims, ["B0"])
        self.assertEqual(data.values.shape, (5892,))
        self.assertEqual(data.attrs["frequency"], 9.47938556968456)
        self.assertEqual(data.attrs["q_value"], -1.0)
        self.assertEqual(data.attrs["nscans"], 10)
        self.assertAlmostEqual(data.coords["B0"][0], 86.6401850382487)
        self.assertAlmostEqual(data.coords["B0"][-1], 590.5849609375)
        self.assertTrue(_np.isrealobj(data.values))
        self.assertAlmostEqual(data.values[365], -6.636497485025046)

    def test_import_esr5000_complex(self):
        # real part is the sinus channel, imaginary part is the cosinus
        # channel -- see the "complex" note in import_esr5000's docstring
        for path, expected in [
            (self.test_data_coffee, -75.49862990973563 - 11.63869396713729j),
            (self.test_data_bitumen, -95.66189177853802 - 13.73977131689887j),
        ]:
            data = sl.load(path, data_format="esr5000", signal="complex")
            self.assertTrue(_np.iscomplexobj(data.values))
            self.assertAlmostEqual(data.values[365], expected)

    def test_import_esr5000_signal_flag(self):
        for path, idx, sinus, cosinus, absorption in [
            (
                self.test_data_coffee,
                365,
                -75.49862990973563,
                -11.63869396713729,
                3.7853982239281443,
            ),
            (
                self.test_data_bitumen,
                365,
                -95.66189177853802,
                -13.73977131689887,
                -6.636497485025046,
            ),
        ]:
            data_sinus = sl.load(path, data_format="esr5000", signal="sinus")
            data_cosinus = sl.load(path, data_format="esr5000", signal="cosinus")
            data_absorption = sl.load(path, data_format="esr5000", signal="absorption")
            self.assertTrue(_np.isrealobj(data_sinus.values))
            self.assertTrue(_np.isrealobj(data_cosinus.values))
            self.assertTrue(_np.isrealobj(data_absorption.values))
            self.assertAlmostEqual(data_sinus.values[idx], sinus)
            self.assertAlmostEqual(data_cosinus.values[idx], cosinus)
            self.assertAlmostEqual(data_absorption.values[idx], absorption)

        with self.assertRaises(ValueError):
            sl.load(self.test_data_coffee, data_format="esr5000", signal="bogus")

    def test_import_esr5000_raw(self):
        data = sl.load(self.test_data_coffee, data_format="esr5000", raw=True)
        self.assertEqual(data.dims, ["t2"])
        self.assertEqual(data.values.shape, (15529,))
        self.assertTrue(_np.isrealobj(data.values))
        self.assertAlmostEqual(data.coords["t2"][0], 0.045)
        self.assertAlmostEqual(data.coords["t2"][1], 0.047)
        self.assertAlmostEqual(data.values[0], 0.0)
        self.assertAlmostEqual(data.values[-1], -4.705190860668182)
        # BField, reconstructed onto the same native time axis, is not the
        # untouched raw signal -- it is provided separately in attrs.
        self.assertEqual(len(data.attrs["field_raw"]), 3107)
        self.assertAlmostEqual(data.attrs["field_raw"][0], 331.53399658203125)
        self.assertAlmostEqual(data.attrs["field_raw"][-1], 342.0386657714844)
        self.assertEqual(len(data.attrs["field_raw_time"]), 3107)

        data_complex = sl.load(
            self.test_data_coffee, data_format="esr5000", signal="complex", raw=True
        )
        self.assertEqual(data_complex.dims, ["t2"])
        self.assertEqual(data_complex.values.shape, (31148,))
        self.assertTrue(_np.iscomplexobj(data_complex.values))

        with self.assertRaises(ValueError):
            sl.load(
                self.test_data_coffee,
                data_format="esr5000",
                raw=True,
                resolution=100,
            )

    def test_import_esr5000_resolution(self):
        # downsampling below the native 31148-point sinus/cosinus curves
        # should not warn
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            data = sl.load(
                self.test_data_coffee, data_format="esr5000", resolution=1000
            )
            self.assertEqual(data.values.shape, (1000,))
            self.assertEqual(len(w), 0)

        # requesting more points than the native raw samples should warn
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            data = sl.load(
                self.test_data_coffee, data_format="esr5000", resolution=60000
            )
            self.assertEqual(data.values.shape, (60000,))
            self.assertEqual(len(w), 1)
            self.assertIn("exceeds", str(w[0].message))

    def test_import_esr5000_resolution_matches_nominal_sweep(self):
        # An explicit `resolution` spans the nominal sweep_start/sweep_stop
        # (Bfrom/Bto), not the literal BField curve endpoints (which
        # overshoot slightly) -- this is the field window vendor-exported
        # files at a given point count use, e.g. ESRStudio's own .DSC
        # export of the same measurement at 2000 points uses exactly
        # 331.7-341.7, not the XML's literal 331.534-342.039.
        data = sl.load(self.test_data_coffee, data_format="esr5000", resolution=2000)
        self.assertAlmostEqual(data.coords["B0"][0], data.attrs["sweep_start"])
        self.assertAlmostEqual(data.coords["B0"][-1], data.attrs["sweep_stop"])
        self.assertAlmostEqual(data.attrs["sweep_start"], 331.7)
        self.assertAlmostEqual(data.attrs["sweep_stop"], 341.7)

        # the default (no resolution given) output is unchanged: it keeps
        # the literal BField curve, overshoot and all
        default_data = sl.load(self.test_data_coffee, data_format="esr5000")
        self.assertAlmostEqual(default_data.coords["B0"][0], 331.53399658203125)
        self.assertAlmostEqual(default_data.coords["B0"][-1], 342.0386657714844)

    def test_import_esr5000_proc_attrs(self):
        for kwargs, expected in [
            (
                {},
                {
                    "signal": "absorption",
                    "raw": False,
                    "resolution": None,
                    "native_samples": 15529,
                    "output_samples": 3107,
                },
            ),
            (
                {"resolution": 2000},
                {
                    "signal": "absorption",
                    "raw": False,
                    "resolution": 2000,
                    "native_samples": 15529,
                    "output_samples": 2000,
                },
            ),
            (
                {"raw": True},
                {
                    "signal": "absorption",
                    "raw": True,
                    "resolution": None,
                    "native_samples": 15529,
                    "output_samples": 15529,
                },
            ),
        ]:
            data = sl.load(self.test_data_coffee, data_format="esr5000", **kwargs)
            self.assertEqual(len(data.proc_attrs), 1)
            name, proc_dict = data.proc_attrs[0]
            self.assertEqual(name, "esr5000_import")
            self.assertEqual(proc_dict, expected)


class esr5000_dipsweep_import_tester(unittest.TestCase):
    def setUp(self):
        self.test_data = os.path.join(".", "data", "esr5000", "DipSweep.xml")

    def test_import_esr5000_dipsweep(self):
        # A cavity tuning dip: XDatasource="Frequency", YDatasource=
        # "ADC_24bit". Both curves are already sample-aligned (no field
        # curve, no time-based registration needed), unlike field-sweep
        # spectra.
        data = sl.load(self.test_data, data_format="esr5000")
        self.assertEqual(data.dims, ["f"])
        self.assertEqual(data.values.shape, (1001,))
        self.assertTrue(_np.isrealobj(data.values))
        self.assertEqual(data.attrs["experiment_type"], "cavity_dip_sweep")
        self.assertAlmostEqual(data.coords["f"][0], 9.412607)
        self.assertAlmostEqual(data.coords["f"][-1], 9.432606999999999)
        self.assertAlmostEqual(data.values[0], 4242094.5)
        self.assertAlmostEqual(data.values[-1], 4135889.0)
        self.assertAlmostEqual(data.values.min(), 37383.9609375)

        self.assertEqual(len(data.proc_attrs), 1)
        name, proc_dict = data.proc_attrs[0]
        self.assertEqual(name, "esr5000_import")
        self.assertEqual(
            proc_dict,
            {
                "signal": None,
                "raw": False,
                "resolution": None,
                "native_samples": 1001,
                "output_samples": 1001,
            },
        )

    def test_import_esr5000_dipsweep_rejects_field_sweep_options(self):
        # signal/raw/resolution are field-sweep-only options and must be
        # rejected (not silently ignored) on a non-field-sweep file.
        for kwargs in [
            {"signal": "complex"},
            {"signal": "absorption"},
            {"raw": True},
            {"resolution": 500},
        ]:
            with self.assertRaises(ValueError):
                sl.load(self.test_data, data_format="esr5000", **kwargs)


class winepr_import_tester(unittest.TestCase):
    def setUp(self):
        self.test_data_ESP = os.path.join(".", "data", "parspc", "ExampleESP.par")
        self.test_data_1D = os.path.join(".", "data", "parspc", "Example1D.spc")
        self.test_data_2D = os.path.join(".", "data", "parspc", "Example2D.spc")

    def test_import_winepr_ESP(self):
        data = sl.load(self.test_data_ESP, data_format="esp")
        self.assertEqual(data.dims, ["t2"])
        self.assertEqual(data.values.shape, (1024,))
        self.assertEqual(data.attrs["conversion_time"], 81.92)

    def test_import_winepr_1D(self):
        data = sl.load(self.test_data_1D, data_format="winepr")
        self.assertEqual(data.dims, ["B0"])
        self.assertEqual(data.values.shape, (512,))
        self.assertEqual(data.attrs["temperature"], 294.2)

    def test_import_winepr_2D(self):
        data = sl.load(self.test_data_2D, data_format="winepr")
        self.assertEqual(data.dims, ["B0", "t1"])
        self.assertEqual(data.values.shape, (1024, 15))
        self.assertEqual(data.attrs["frequency"], 9.79)


class delta_import_tester(unittest.TestCase):
    def setUp(self):
        self.test_data_1D = os.path.join(".", "data", "delta", "50percCHCL3.jdf")
        self.test_data_2D = os.path.join(".", "data", "delta", "lineshape_drift.jdf")

    def test_import_delta_1D(self):
        data = sl.load(self.test_data_1D, data_format="delta")
        self.assertEqual(data.dims, ["t2"])
        self.assertEqual(data.values.shape, (16384,))
        self.assertEqual(max(data.coords["t2"]), 0.262128)

    def test_import_delta_2D(self):
        data = sl.load(self.test_data_2D, data_format="delta")
        self.assertEqual(data.dims, ["t2", "t1"])
        self.assertEqual(data.values.shape, (8192, 256))
        self.assertEqual(max(data.coords["t2"]), 0.5451929600000001)
        self.assertEqual(max(data.coords["t1"]), 11.953125)


class csv_import_tester(unittest.TestCase):
    def setUp(self):
        self.testdata = os.path.join(".", "data", "csv")

    def test_import_csv_arrLNA_fid(self):
        import pathlib

        p = pathlib.Path(self.testdata)
        data = sl.io.load_csv.load_csv(
            p.joinpath("csv_example.csv"),
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

    def test_remove_data_csv_arrLNA_fid(self):
        import pathlib

        p = pathlib.Path(self.testdata)
        data = sl.io.load_csv.load_csv(
            p.joinpath("csv_example.csv"),
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

    def test_set_imag_to_zero(self):
        import pathlib

        p = pathlib.Path(self.testdata)
        data = sl.io.load_csv.load_csv(
            p.joinpath("csv_example.csv"),
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


class spinlab_configparse_tester(unittest.TestCase):
    def test_000_escape_split(self):
        # config
        import sys
        import configparser
        from pathlib import Path

        p = Path(__file__).parent.joinpath("spinlab")
        sys.path.insert(0, p)
        p = str(p)
        from spinlab import config as slconfig

        cfg = configparser.ConfigParser(
            converters={
                "list": lambda x: list(x.strip("[").strip("]").split(",")),
                "args_kwargs": slconfig.config._kwarg_converter,
            }
        )

        string1 = "Contact Time t$_c$ [s]"
        string2 = r"abc=1,def\=2,ghi=3"

        cfg_file = str(Path(__file__).parent.joinpath("data_testconfig.cfg"))
        cfg.read(cfg_file)

        args2, kwargs2 = cfg.getargs_kwargs("UNITTEST_EXAMPLE", "test1")
        logger.info("{0}\n{1}".format(args2, kwargs2))
        self.assertEqual(len(args2), 1)
        self.assertEqual(len(kwargs2), 2)
        self.assertEqual(kwargs2["ghi"], "3")
        self.assertEqual(args2[0], "def=2")

        args1, kwargs1 = cfg.getargs_kwargs("UNITTEST_EXAMPLE", "test0")
        logger.info("{0}\n{1}".format(args1, kwargs1))
        self.assertEqual(len(args1), 1)
        self.assertEqual(len(kwargs1), 0)
        self.assertEqual(args1[0], string1)


if __name__ == "__main__":
    unittest.main()
    pass
