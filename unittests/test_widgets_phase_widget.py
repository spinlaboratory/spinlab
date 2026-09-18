import unittest
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import spinlab as sl
from numpy.testing import assert_allclose


class sl_widgets_phase_widget_tester(unittest.TestCase):
    def setUp(self):
        plt.close("all")
        self.f2 = np.array([-1.0, 0.0, 1.0])
        self.values = np.array([1.0 + 1.0j, 2.0 + 0.5j, 3.0 - 1.0j])
        self.data = sl.SpinData(self.values.copy(), ["f2"], [self.f2])

    def tearDown(self):
        plt.close("all")

    def test_phase_widget_applies_zero_and_first_order_phase(self):
        def set_manual_phase():
            widgets = plt.gcf()._widgets
            widgets["phase"].set_val(90)
            widgets["phase1"].set_val(10)

        with patch("spinlab.widgets.phase_widget.plt.show", side_effect=set_manual_phase):
            out = sl.phase_widget(self.data, dim="f2")

        expected = self.values * np.exp(-1j * np.pi * 90 / 180.0)
        expected *= np.exp(-1j * np.pi * 10 * self.f2 / 180.0)

        assert_allclose(out.values, expected)
        assert_allclose(self.data.values, self.values)
        self.assertEqual(out.attrs["phase0"], 90)
        self.assertEqual(out.attrs["phase1"], 10)
        self.assertEqual(out.proc_attrs[-1][0], "manualphase")
        self.assertEqual(out.proc_attrs[-1][1], {"phase": 90, "phase1": 10})

    def test_phase_widget_broadcasts_first_order_phase_on_selected_dim(self):
        scan = np.array([0, 1])
        values = np.column_stack([self.values, 2.0 * self.values])
        data = sl.SpinData(values.copy(), ["f2", "scan"], [self.f2, scan])

        def set_manual_phase():
            widgets = plt.gcf()._widgets
            widgets["phase"].set_val(0)
            widgets["phase1"].set_val(20)

        with patch("spinlab.widgets.phase_widget.plt.show", side_effect=set_manual_phase):
            out = sl.phase_widget(data, dim="f2")

        expected = values * np.exp(
            -1j * np.pi * 20 * self.f2.reshape(-1, 1) / 180.0
        )
        assert_allclose(out.values, expected)

    def test_phase_widget_exposes_sliders_and_buttons_on_figure(self):
        captured = {}

        def capture_widgets():
            captured.update(plt.gcf()._widgets)

        with patch("spinlab.widgets.phase_widget.plt.show", side_effect=capture_widgets):
            sl.phase_widget(self.data.copy(), dim="f2")

        for name in ["phase", "phase1", "reset", "plus_90", "minus_90", "rescale"]:
            with self.subTest(name=name):
                self.assertIn(name, captured)

    def test_phase_widget_invalid_dim_raises_value_error(self):
        with self.assertRaises(ValueError):
            sl.phase_widget(self.data, dim="missing")

    def test_phase_widget_is_exported_at_top_level(self):
        from spinlab.widgets.phase_widget import phase_widget

        self.assertIs(sl.phase_widget, phase_widget)


if __name__ == "__main__":
    unittest.main()
