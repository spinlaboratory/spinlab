"""Import SpecLog CSV files."""

import csv
import os
from datetime import datetime

import numpy as _np

from ..core.data import SpinData


def load_speclog(filename, delimiter=",", encoding="utf-8-sig"):
    """Load a SpecLog CSV file as a two-dimensional :class:`SpinData`.

    SpecLog files contain ``Date`` and ``Time`` columns followed by one or
    more numeric instrument channels.  The returned data has dimensions
    ``time`` and ``channel``.  Its time coordinate uses NumPy
    ``datetime64[us]`` values and its channel coordinate contains the column
    names from the file.

    Args:
        filename (str, path-like, or list): SpecLog CSV file to read, or a
            list of files to merge and sort by time.
        delimiter (str): CSV field delimiter. Defaults to ``,``.
        encoding (str): Text encoding. Defaults to ``utf-8-sig`` so files
            with or without a UTF-8 byte-order mark are accepted.

    Returns:
        SpinData: Numeric log values with shape ``(n_times, n_channels)``.

    Raises:
        ValueError: If the header, a timestamp, a row width, or a numeric
            value is invalid. Empty numeric cells are represented by NaN.
    """
    if isinstance(filename, (list, tuple)):
        if not filename:
            raise ValueError("At least one SpecLog file is required")

        datasets = [
            load_speclog(path, delimiter=delimiter, encoding=encoding)
            for path in filename
        ]
        channels = datasets[0].coords["channel"]
        channel_set = set(channels.tolist())
        aligned_values = []
        for path, dataset in zip(filename, datasets):
            file_channels = dataset.coords["channel"]
            if set(file_channels.tolist()) != channel_set:
                raise ValueError(
                    f"SpecLog channels in {os.fspath(path)!r} do not match "
                    "the first file"
                )
            indices = [
                int(_np.flatnonzero(file_channels == channel)[0])
                for channel in channels
            ]
            aligned_values.append(dataset.values[:, indices])

        values = _np.concatenate(aligned_values, axis=0)
        time_coord = _np.concatenate([dataset.coords["time"] for dataset in datasets])
        order = _np.argsort(time_coord, kind="stable")
        attrs = {
            "source_files": [os.path.abspath(os.fspath(path)) for path in filename],
            "experiment_type": "SpecLog",
        }
        return SpinData(
            values[order],
            dims=["time", "channel"],
            coords=[time_coord[order], channels.copy()],
            attrs=attrs,
        )

    filename = os.fspath(filename)

    with open(filename, "r", newline="", encoding=encoding) as csv_file:
        reader = csv.reader(csv_file, delimiter=delimiter, skipinitialspace=True)
        try:
            header = [field.strip() for field in next(reader)]
        except StopIteration as exc:
            raise ValueError("SpecLog file is empty") from exc

        if len(header) < 3 or [name.lower() for name in header[:2]] != [
            "date",
            "time",
        ]:
            raise ValueError(
                "SpecLog header must start with 'Date, Time' and contain "
                "at least one data channel"
            )

        channels = header[2:]
        if any(not channel for channel in channels):
            raise ValueError("SpecLog channel names must not be empty")

        timestamps = []
        rows = []
        for line_number, row in enumerate(reader, start=2):
            if not row or all(not field.strip() for field in row):
                continue
            if len(row) != len(header):
                raise ValueError(
                    f"SpecLog row {line_number} has {len(row)} columns; "
                    f"expected {len(header)}"
                )

            fields = [field.strip() for field in row]
            try:
                timestamp = datetime.fromisoformat(f"{fields[0]} {fields[1]}")
            except ValueError as exc:
                raise ValueError(
                    f"Invalid SpecLog timestamp on row {line_number}: "
                    f"{fields[0]} {fields[1]}"
                ) from exc

            values = []
            for channel, field in zip(channels, fields[2:]):
                if field == "":
                    values.append(_np.nan)
                    continue
                try:
                    values.append(float(field))
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid numeric value for channel {channel!r} "
                        f"on row {line_number}: {field!r}"
                    ) from exc

            timestamps.append(timestamp)
            rows.append(values)

    values = _np.asarray(rows, dtype=float).reshape((-1, len(channels)))
    time_coord = _np.asarray(timestamps, dtype="datetime64[us]")
    channel_coord = _np.asarray(channels, dtype=str)
    attrs = {
        "source_file": os.path.abspath(filename),
        "experiment_type": "SpecLog",
    }
    return SpinData(
        values,
        dims=["time", "channel"],
        coords=[time_coord, channel_coord],
        attrs=attrs,
    )
