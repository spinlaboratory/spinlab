import unittest
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import spinlab as sl
from numpy.testing import assert_array_equal


class sl_widgets_align_widget_tester(unittest.TestCase):
    def setUp(self):
        plt.close("all")
        self.x = np.arange(5)
        self.scan = np.arange(3)
        self.values = np.vstack(
            [
                np.arange(5),
                np.arange(10, 15),
                np.arange(20, 25),
            ]
        ).T
        self.data = sl.SpinData(self.values, ["x", "scan"], [self.x, self.scan])

    def tearDown(self):
        plt.close("all")

    def test_align_widget_uses_slider_value_to_roll_each_trace(self):
        original_values = self.data.values.copy()

        def set_manual_index():
            plt.gcf()._widgets["index"].set_val(1)

        with patch("spinlab.widgets.align_widget._plt.show", side_effect=set_manual_index):
            out = sl.align_widget(self.data, dim="scan")

        expected = original_values.copy()
        for ix in range(self.scan.size):
            expected[:, ix] = np.roll(original_values[:, ix], ix)

        self.assertIs(out, self.data)
        assert_array_equal(out.values, expected)
        self.assertEqual(out.proc_attrs[-1][0], "manualalign")
        self.assertEqual(out.proc_attrs[-1][1], {"dim": "scan"})

    def test_align_widget_exposes_slider_and_buttons_on_figure(self):
        captured = {}

        def capture_widgets():
            captured.update(plt.gcf()._widgets)

        with patch("spinlab.widgets.align_widget._plt.show", side_effect=capture_widgets):
            sl.align_widget(self.data.copy(), dim="scan")

        self.assertIn("index", captured)
        self.assertIn("reset", captured)
        self.assertIn("increment", captured)
        self.assertIn("decrement", captured)

    def test_align_widget_invalid_inputs_raise_value_error(self):
        data_1d = sl.SpinData(self.x, ["x"], [self.x])

        with self.assertRaises(ValueError):
            sl.align_widget(data_1d, dim="x")
        with self.assertRaises(ValueError):
            sl.align_widget(self.data, dim="missing")

    def test_align_widget_is_exported_at_top_level(self):
        from spinlab.widgets.align_widget import align_widget

        self.assertIs(sl.align_widget, align_widget)


if __name__ == "__main__":
    unittest.main()
