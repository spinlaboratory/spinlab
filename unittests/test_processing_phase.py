import logging
import unittest
from unittest.mock import patch

import numpy as np
import spinlab as sl
from numpy.testing import assert_allclose, assert_array_equal

from spinlab.processing.phase import (
    _autophase,
    _deriveF,
    _optimfun,
    autophase,
    autophase_dep,
    phase,
    phase_cycle,
)


# logging.basicConfig(filename='phase_debug.log', encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)


class sl_phase_tester(unittest.TestCase):
    def setUp(self):
        self.x = np.linspace(-1.0, 1.0, 101)
        self.ones_1d = sl.SpinData(
            np.ones(self.x.size, dtype=complex), dims=["f2"], coords=[self.x]
        )
        self.scan = np.r_[0:3]
        self.ones_2d = sl.SpinData(
            np.ones((self.x.size, self.scan.size), dtype=complex),
            dims=["f2", "scan"],
            coords=[self.x, self.scan],
        )

    def test_deriveF_first_derivative(self):
        f = self.x**2
        dx = self.x[1] - self.x[0]

        out = _deriveF(f, dx, deriv=1)

        assert_allclose(out, 2 * self.x, atol=1e-10)

    def test_deriveF_second_derivative(self):
        f = self.x**2
        dx = self.x[1] - self.x[0]

        out = _deriveF(f, dx, deriv=2)

        assert_allclose(out, np.ones_like(self.x) * 2, atol=1e-10)

    def test_deriveF_invalid_derivative_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            _deriveF(self.x, self.x[1] - self.x[0], deriv=5)

    def test_deriveF_third_derivative(self):
        f = self.x**3
        dx = self.x[1] - self.x[0]

        out = _deriveF(f, dx, deriv=3)

        assert_allclose(out, np.ones_like(self.x) * 6, atol=1e-9)

    def test_deriveF_fourth_derivative(self):
        f = self.x**4
        dx = self.x[1] - self.x[0]

        out = _deriveF(f, dx, deriv=4)

        assert_allclose(out, np.ones_like(self.x) * 24, atol=1e-8)

    def test_deriveF_short_input_raises_value_error(self):
        with self.assertRaises(ValueError):
            _deriveF(np.r_[0.0, 1.0], dx=1.0, deriv=1)

    def test_phase_defaults_to_first_dim(self):
        out = phase(self.ones_2d, p0=90)

        self.assertEqual(out.dims, ["f2", "scan"])
        self.assertEqual(out.proc_attrs[-1][0], "phase_correction")
        assert_allclose(out.values, 1j * np.ones_like(self.ones_2d.values))

    def test_phase_zero_order_1d(self):
        out = phase(self.ones_1d, dim="f2", p0=90)

        self.assertEqual(out.dims, ["f2"])
        assert_array_equal(out.coords["f2"], self.x)
        assert_allclose(out.values, 1j * np.ones_like(self.ones_1d.values))
        assert_allclose(out.proc_attrs[-1][1]["p0"], np.array([np.pi / 2]))
        assert_allclose(out.proc_attrs[-1][1]["p1"], np.array([0.0]))

    def test_phase_negative_zero_order(self):
        out = phase(self.ones_1d, dim="f2", p0=-90)

        assert_allclose(out.values, -1j * np.ones_like(self.ones_1d.values))

    def test_phase_negative_first_order(self):
        out = phase(self.ones_1d, dim="f2", p1=-180)
        expected = np.exp(
            1j * (-np.pi * np.linspace(0.0, 1.0, self.x.size).reshape(-1))
        )

        assert_allclose(out.values, expected)

    def test_phase_first_order(self):
        out = phase(self.ones_1d, dim="f2", p1=180)
        expected = np.exp(1j * (np.pi * np.linspace(0.0, 1.0, self.x.size)))

        assert_allclose(out.values, expected)
        assert_allclose(out.values[-1], -1.0 + 0.0j, atol=1e-15)

    def test_phase_modulo_behavior(self):
        out_positive = phase(self.ones_1d, dim="f2", p0=450, p1=540)
        out_expected_positive = phase(self.ones_1d, dim="f2", p0=90, p1=180)
        out_negative = phase(self.ones_1d, dim="f2", p0=-450, p1=-540)
        out_expected_negative = phase(self.ones_1d, dim="f2", p0=-90, p1=-180)

        assert_allclose(out_positive.values, out_expected_positive.values)
        assert_allclose(out_negative.values, out_expected_negative.values)

    def test_phase_along_non_first_dim(self):
        data = sl.SpinData(
            np.ones((3, 4), dtype=complex),
            dims=["scan", "phase"],
            coords=[np.arange(3), np.arange(4)],
        )

        out = phase(data, dim="phase", p1=180)

        expected_phase = np.exp(1j * np.pi * np.linspace(0.0, 1.0, 4)).reshape(1, -1)
        assert_allclose(out.values, np.ones((3, 4)) * expected_phase)
        self.assertEqual(out.dims, ["scan", "phase"])

    def test_phase_array_zero_order_for_2d_data(self):
        p0 = np.array([0, 90, 180])

        out = phase(self.ones_2d, dim="f2", p0=p0)

        expected = np.ones_like(self.ones_2d.values)
        expected[:, 0] *= 1
        expected[:, 1] *= 1j
        expected[:, 2] *= -1
        assert_allclose(out.values, expected, atol=1e-15)

    def test_phase_array_first_order_for_2d_data(self):
        p1 = np.array([0, 90, 180])

        out = phase(self.ones_2d, dim="f2", p1=p1)

        expected = np.exp(
            1j * np.linspace(0.0, 1.0, self.x.size).reshape(-1, 1) * np.deg2rad(p1)
        )
        assert_allclose(out.values, expected)

    def test_phase_list_zero_order_for_2d_data(self):
        out = phase(self.ones_2d, dim="f2", p0=[0, 90, 180])

        expected = np.ones_like(self.ones_2d.values)
        expected[:, 0] *= 1
        expected[:, 1] *= 1j
        expected[:, 2] *= -1
        assert_allclose(out.values, expected, atol=1e-15)

    def test_phase_array_zero_and_first_order_for_2d_data(self):
        p0 = np.array([0, 90, 180])
        p1 = np.array([0, 90, 180])

        out = phase(self.ones_2d, dim="f2", p0=p0, p1=p1)

        expected = np.exp(
            1j
            * (
                np.deg2rad(p0).reshape(1, -1)
                + np.linspace(0.0, 1.0, self.x.size).reshape(-1, 1)
                * np.deg2rad(p1).reshape(1, -1)
            )
        )
        assert_allclose(out.values, expected)

    def test_phase_mismatched_phase_array_length_raises_value_error(self):
        with self.assertRaises(ValueError):
            phase(self.ones_2d, dim="f2", p0=[0, 90])
        with self.assertRaises(ValueError):
            phase(self.ones_2d, dim="f2", p1=[0, 90])

    def test_phase_stores_pivot_in_processing_attrs(self):
        out = phase(self.ones_1d, dim="f2", p1=180, pivot=0.2)

        self.assertEqual(out.proc_attrs[-1][1]["pivot"], 0.2)

    def test_phase_pivot_shifts_first_order_phase_ramp(self):
        out = phase(self.ones_1d, dim="f2", p1=180, pivot=0.0)
        phase_axis = (self.x - 0.0) / (self.x[-1] - self.x[0])
        expected = np.exp(1j * np.pi * phase_axis)

        assert_allclose(out.values, expected)
        assert_allclose(out.values[self.x.size // 2], 1.0 + 0.0j, atol=1e-15)

    def test_phase_invalid_dim_raises_value_error(self):
        with self.assertRaises(ValueError):
            phase(self.ones_1d, dim="not_a_dim", p0=90)

    def test_phase_does_not_mutate_input(self):
        original_values = self.ones_2d.values.copy()
        original_coords = self.ones_2d.coords["f2"].copy()
        original_dims = self.ones_2d.dims.copy()

        phase(self.ones_2d, dim="f2", p0=90)

        self.assertEqual(self.ones_2d.dims, original_dims)
        assert_array_equal(self.ones_2d.coords["f2"], original_coords)
        assert_array_equal(self.ones_2d.values, original_values)

    def test_phase_cycle_defaults_to_first_dim(self):
        data = sl.SpinData(
            np.ones(4, dtype=complex), dims=["phase"], coords=[np.arange(4)]
        )

        out = phase_cycle(data, receiver_phase=[0, 1, 2, 3])

        expected = np.array([1, -1j, -1, 1j], dtype=complex)
        self.assertEqual(out.dims, ["phase"])
        self.assertEqual(out.proc_attrs[-1][0], "phasecycle")
        self.assertEqual(out.proc_attrs[-1][1]["dim"], "phase")
        assert_array_equal(out.proc_attrs[-1][1]["receiver_phase"], np.array([0, 1, 2, 3]))
        assert_allclose(out.values, expected)

    def test_phase_cycle_repeats_receiver_phase(self):
        data = sl.SpinData(
            np.ones(8, dtype=complex), dims=["phase"], coords=[np.arange(8)]
        )

        out = phase_cycle(data, dim="phase", receiver_phase=[0, 1, 2, 3])

        expected = np.array([1, -1j, -1, 1j, 1, -1j, -1, 1j], dtype=complex)
        assert_allclose(out.values, expected)

    def test_phase_cycle_2d_along_second_dim(self):
        data = sl.SpinData(
            np.ones((3, 4), dtype=complex),
            dims=["x", "phase"],
            coords=[np.arange(3), np.arange(4)],
        )

        out = phase_cycle(data, dim="phase", receiver_phase=[0, 1, 2, 3])

        expected = np.array([1, -1j, -1, 1j], dtype=complex).reshape(1, -1)
        assert_allclose(out.values, np.ones((3, 4)) * expected)

    def test_phase_cycle_invalid_inputs_raise_value_error(self):
        data = sl.SpinData(
            np.ones(5, dtype=complex), dims=["phase"], coords=[np.arange(5)]
        )

        with self.assertRaises(ValueError):
            phase_cycle(data, dim="not_a_dim", receiver_phase=[0])
        with self.assertRaises(ValueError):
            phase_cycle(data, dim="phase")
        with self.assertRaises(ValueError):
            phase_cycle(data, dim="phase", receiver_phase=[])
        with self.assertRaises(ValueError):
            phase_cycle(data, dim="phase", receiver_phase=[0, 1])

    def test_phase_cycle_does_not_mutate_input(self):
        data = sl.SpinData(
            np.ones(4, dtype=complex), dims=["phase"], coords=[np.arange(4)]
        )
        original_values = data.values.copy()
        original_coords = data.coords["phase"].copy()

        phase_cycle(data, dim="phase", receiver_phase=[0, 1, 2, 3])

        assert_array_equal(data.values, original_values)
        assert_array_equal(data.coords["phase"], original_coords)

    def test_autophase_defaults_to_first_dim_and_applies_optimizer_result(self):
        data = sl.SpinData(
            np.ones((4, 2), dtype=complex),
            dims=["f2", "scan"],
            coords=[np.arange(4), np.arange(2)],
        )

        with patch("spinlab.processing.phase._autophase", return_value=(np.pi / 2, 0)):
            out = autophase(data)

        assert_allclose(out.values, 1j * np.ones_like(data.values))
        self.assertEqual(out.dims, ["f2", "scan"])
        self.assertEqual(out.proc_attrs[0][0], "autophase")
        self.assertEqual(out.proc_attrs[0][1]["dim"], "f2")
        self.assertEqual(len(out.proc_attrs[0][1]["phasetuples"]), 2)

    def test_autophase_full_proc_attr_false_does_not_store_phase_tuples(self):
        with patch("spinlab.processing.phase._autophase", return_value=(np.pi / 2, 0)):
            out = autophase(self.ones_2d, dim="f2", full_proc_attr=False)

        assert_allclose(out.values, 1j * np.ones_like(self.ones_2d.values))
        self.assertEqual(out.proc_attrs[0][0], "autophase")
        self.assertNotIn("phasetuples", out.proc_attrs[0][1])

    def test_autophase_reference_slice_applies_reference_phase(self):
        data = sl.SpinData(
            np.ones((4, 2), dtype=complex),
            dims=["f2", "scan"],
            coords=[np.arange(4), np.arange(2)],
        )

        with patch("spinlab.processing.phase._autophase", return_value=(np.pi / 2, 0)):
            out = autophase(data, dim="f2", reference_slice=("scan", 1))

        assert_allclose(out.values, 1j * np.ones_like(data.values))
        self.assertEqual(out.dims, ["f2", "scan"])
        assert_array_equal(out.coords["f2"], data.coords["f2"])
        assert_array_equal(out.coords["scan"], data.coords["scan"])

    def test_optimfun_returns_finite_value(self):
        data = np.exp(-(self.x**2)) * np.exp(-1j * np.pi / 3)

        out = _optimfun([np.pi / 3, 0], data, deriv=1, gamma=5e-3, dx=self.x[1] - self.x[0])

        self.assertTrue(np.isfinite(out))

    def test_optimfun_flat_data_returns_finite_value(self):
        data = np.ones(self.x.size, dtype=complex)

        out = _optimfun([0.0, 0.0], data, deriv=1, gamma=5e-3, dx=self.x[1] - self.x[0])

        self.assertTrue(np.isfinite(out))

    def test_autophase_rejects_nonuniform_coordinates(self):
        coords = self.x.copy()
        coords[10] += 0.001

        with self.assertRaises(ValueError):
            _autophase(np.ones_like(coords, dtype=complex), coords, "f2", deriv=1, gamma=5e-3)

    def test_deprecated_autophase_dep_search_runs(self):
        data = sl.SpinData(
            np.ones(16, dtype=complex), dims=["f2"], coords=[np.arange(16)]
        )

        out = autophase_dep(data, dim="f2", method="search")

        self.assertEqual(out.proc_attrs[-1][0], "autophase")
        self.assertIn("phase0", out.attrs)

    def test_deprecated_autophase_dep_manual_first_order_applies_phase(self):
        data = sl.SpinData(
            np.ones((4, 2), dtype=complex),
            dims=["f2", "scan"],
            coords=[np.arange(4), np.arange(2)],
        )
        phase_values = np.array([0, np.pi / 2, np.pi, 3 * np.pi / 2])

        out = autophase_dep(
            data, dim="f2", order="first", phase=phase_values, method="manual"
        )

        expected = np.exp(-1j * phase_values).reshape(-1, 1) * np.ones((4, 2))
        assert_allclose(out.values, expected, atol=1e-15)


if __name__ == "__main__":
    unittest.main()
