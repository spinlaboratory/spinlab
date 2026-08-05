import os
import tempfile
import unittest

import numpy as np
import matplotlib.pyplot as plt

import spinlab as sl


class SpecLogImportTester(unittest.TestCase):
    def _write(self, contents, name="log_20250117.csv"):
        directory = tempfile.TemporaryDirectory()
        path = os.path.join(directory.name, name)
        with open(path, "w", encoding="utf-8", newline="") as csv_file:
            csv_file.write(contents)
        self.addCleanup(directory.cleanup)
        return path

    def test_load_speclog(self):
        path = self._write(
            "Date, Time, temperature, status\n"
            "2025-01-17, 00:00:12, +03.248, 0301\n"
            "2025-01-17, 00:00:42, +03.224, \n"
        )

        data = sl.io.speclog.load_speclog(path)

        self.assertEqual(data.dims, ["time", "channel"])
        self.assertEqual(data.values.shape, (2, 2))
        np.testing.assert_array_equal(data.coords["channel"], ["temperature", "status"])
        self.assertEqual(data.coords["time"][0], np.datetime64("2025-01-17T00:00:12"))
        self.assertEqual(data.values[0, 1], 301.0)
        self.assertTrue(np.isnan(data.values[1, 1]))

    def test_load_and_autodetect_speclog(self):
        path = self._write("Date, Time, temperature\n2025-01-17, 00:00:12, 3.248\n")

        data = sl.load(path)

        self.assertEqual(data.dims, ["time", "channel"])
        self.assertEqual(data.values[0, 0], 3.248)

    def test_select_time_with_timestamp_string(self):
        path = self._write(
            "Date, Time, temperature\n"
            "2025-01-17, 00:00:12, 3.248\n"
            "2025-01-17, 00:00:42, 3.224\n"
            "2025-01-17, 00:01:12, 3.188\n"
        )
        data = sl.load(path)

        selected = data["time", "2025-01-17T00:00:40"]

        self.assertEqual(selected.shape, (1, 1))
        self.assertEqual(
            selected.coords["time"][0], np.datetime64("2025-01-17T00:00:42")
        )
        self.assertEqual(selected.values[0, 0], 3.224)

    def test_select_time_range_with_timestamp_strings(self):
        path = self._write(
            "Date, Time, temperature\n"
            "2025-01-17, 00:00:12, 3.248\n"
            "2025-01-17, 00:00:42, 3.224\n"
            "2025-01-17, 00:01:12, 3.188\n"
        )
        data = sl.load(path)

        selected = data[
            "time", ("2025-01-17T00:00:12", "2025-01-17T00:01:12")
        ]

        np.testing.assert_array_equal(selected.values[:, 0], [3.248, 3.224])

    def test_select_channel_with_header_string(self):
        path = self._write(
            "Date, Time, helium_discharge_temperature, status\n"
            "2025-01-17, 00:00:12, 53, 0301\n"
            "2025-01-17, 00:00:42, 54, 0302\n"
        )
        data = sl.load(path)

        selected = data["channel", "helium_discharge_temperature"]

        self.assertEqual(selected.shape, (2, 1))
        np.testing.assert_array_equal(selected.values[:, 0], [53.0, 54.0])
        np.testing.assert_array_equal(
            selected.coords["channel"], ["helium_discharge_temperature"]
        )

    def test_missing_channel_name_raises_key_error(self):
        path = self._write(
            "Date, Time, temperature\n2025-01-17, 00:00:12, 3.248\n"
        )
        data = sl.load(path)

        with self.assertRaisesRegex(KeyError, "missing.*channel"):
            data["channel", "missing"]

    def test_select_multiple_channels_by_name(self):
        path = self._write(
            "Date, Time, temperature, status, pressure\n"
            "2025-01-17, 00:00:12, 3.248, 0301, 80\n"
            "2025-01-17, 00:00:42, 3.224, 0302, 79\n"
        )
        data = sl.load(path)

        selected = data["channel", ["pressure", "temperature"]]

        self.assertEqual(selected.shape, (2, 2))
        np.testing.assert_array_equal(
            selected.coords["channel"], ["pressure", "temperature"]
        )
        np.testing.assert_array_equal(
            selected.values, [[80.0, 3.248], [79.0, 3.224]]
        )

    def test_missing_name_in_multiple_channel_selection_raises_key_error(self):
        path = self._write(
            "Date, Time, temperature\n2025-01-17, 00:00:12, 3.248\n"
        )
        data = sl.load(path)

        with self.assertRaisesRegex(KeyError, "missing.*channel"):
            data["channel", ["temperature", "missing"]]

    def test_load_file_list_merges_and_sorts_by_time(self):
        later = self._write(
            "Date, Time, temperature, status\n"
            "2025-01-18, 00:00:12, 4.0, 0302\n",
            name="log_20250118.csv",
        )
        earlier = self._write(
            "Date, Time, status, temperature\n"
            "2025-01-17, 00:00:42, 0301, 3.2\n"
            "2025-01-17, 00:00:12, 0300, 3.1\n",
            name="log_20250117.csv",
        )

        data = sl.load([later, earlier])

        self.assertEqual(data.dims, ["time", "channel"])
        self.assertEqual(data.shape, (3, 2))
        np.testing.assert_array_equal(
            data.coords["time"],
            np.asarray(
                [
                    "2025-01-17T00:00:12",
                    "2025-01-17T00:00:42",
                    "2025-01-18T00:00:12",
                ],
                dtype="datetime64[us]",
            ),
        )
        np.testing.assert_array_equal(
            data.coords["channel"], ["temperature", "status"]
        )
        np.testing.assert_array_equal(
            data.values,
            [[3.1, 300.0], [3.2, 301.0], [4.0, 302.0]],
        )
        self.assertEqual(len(data.attrs["source_files"]), 2)

    def test_merge_rejects_different_channels(self):
        first = self._write(
            "Date, Time, temperature\n2025-01-17, 00:00:12, 3.1\n",
            name="log_first.csv",
        )
        second = self._write(
            "Date, Time, pressure\n2025-01-18, 00:00:12, 80\n",
            name="log_second.csv",
        )

        with self.assertRaisesRegex(ValueError, "channels.*do not match"):
            sl.load([first, second], data_format="speclog")

    def test_fancy_plot_uses_channel_names(self):
        path = self._write(
            "Date, Time, temperature, status\n"
            "2025-01-17, 00:00:12, 3.248, 0301\n"
            "2025-01-17, 00:00:42, 3.224, 0302\n"
        )
        data = sl.load(path)
        self.addCleanup(plt.close, "all")

        lines = sl.fancy_plot(data)

        axes = plt.gca()
        self.assertEqual(len(lines), 2)
        self.assertEqual(axes.get_xlabel(), "Time")
        self.assertEqual(axes.get_ylabel(), "Value")
        self.assertEqual(axes.get_title(), "SpecLog")
        legend = plt.gcf().legends[0]
        self.assertEqual(
            [text.get_text() for text in legend.get_texts()],
            ["temperature", "status"],
        )
        self.assertIsNone(axes.get_legend())
        self.assertEqual(legend._loc, 8)  # lower center
        self.assertAlmostEqual(
            legend.get_bbox_to_anchor()._bbox.x0, 0.5
        )

    def test_fancy_plot_single_channel_uses_name_as_label(self):
        path = self._write(
            "Date, Time, temperature, status\n"
            "2025-01-17, 00:00:12, 3.248, 0301\n"
            "2025-01-17, 00:00:42, 3.224, 0302\n"
        )
        data = sl.load(path)["channel", "temperature"]
        self.addCleanup(plt.close, "all")

        sl.fancy_plot(data)

        axes = plt.gca()
        self.assertEqual(axes.get_ylabel(), "Value")
        self.assertEqual(
            [text.get_text() for text in plt.gcf().legends[0].get_texts()],
            ["temperature"],
        )

    def test_fancy_plot_formats_channel_labels_for_display(self):
        path = self._write(
            "Date, Time, helium_discharge_temperature\n"
            "2025-01-17, 00:00:12, 53\n"
        )
        data = sl.load(path)
        self.addCleanup(plt.close, "all")

        sl.fancy_plot(data)

        self.assertEqual(
            plt.gcf().legends[0].get_texts()[0].get_text(),
            "helium discharge temperature",
        )
        self.assertEqual(
            data.coords["channel"][0], "helium_discharge_temperature"
        )

    def test_rejects_wrong_row_width(self):
        path = self._write("Date, Time, temperature\n2025-01-17, 00:00:12\n")

        with self.assertRaisesRegex(ValueError, "row 2 has 2 columns; expected 3"):
            sl.io.speclog.load_speclog(path)


if __name__ == "__main__":
    unittest.main()
