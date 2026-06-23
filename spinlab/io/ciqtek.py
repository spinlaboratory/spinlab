import numpy as _np
import json
import os
import re as _re
from .. import SpinData

__all__ = ["import_ciqtek"]

_rename_dict = {
    "lineEdit_1DFieldSweep_CenterField": "center_field",
    "lineEdit_1DFieldSweep_StartField": "sweep_start",
    "lineEdit_1DFieldSweep_StopField": "sweep_stop",
    "lineEdit_1DFieldSweep_SweepWidth": "x_width",
    "lineEdit_1DFieldSweep_NoOfPoints": "x_points",
    "lineEdit_1DFieldSweep_NoOfSweeps": "nscans",
    "lineEdit_1DFieldSweep_SettlingDelay": "settling_delay",
    "lineEdit_2DTimeFieldSweep_NoOfPoints": "x_points",
    "lineEdit_2DTimeFieldSweep_NoOfPoints01": "y_points",
    "lineEdit_2DTimeFieldSweep_NoOfSweeps": "nscans",
    "lineEdit_2DTimeFieldSweep_Resolution": "conversion_time",
    "lineEdit_2DTimeFieldSweep_StartField": "sweep_start",
    "lineEdit_2DTimeFieldSweep_StopField": "sweep_stop",
    "lineEdit_MB_Power": "power",
    "lineEdit_MB_Attenuation": "attenuation",
    "lineEdit_SC_ConvertTime": "conversion_time",
    "lineEdit_SC_TimeConstant": "time_constant",
    "lineEdit_SC_ModulAmp": "modulation_amplitude",
    "lineEdit_SC_ModulPhase": "modulation_phase",
    "comboBox_SC_ModulFreq": "modulation_frequency",
    "comboBox_SC_ReceiverGain": "receiver_gain",
    "comboBox_SC_ReceiverHarmonic": "receiver_harmonic",
    "comboBox_1DFieldSweep_SweepDirection": "sweep_direction",
    "frequency": "frequency",
    "QValue": "q_value",
    "lineEdit_Temp_CurrTemp": "temperature",
}

_float_params = [
    "center_field",
    "sweep_start",
    "sweep_stop",
    "x_width",
    "power",
    "attenuation",
    "conversion_time",
    "time_constant",
    "modulation_amplitude",
    "modulation_phase",
    "modulation_frequency",
    "receiver_gain",
    "frequency",
    "q_value",
    "temperature",
    "settling_delay",
]

_int_params = [
    "x_points",
    "y_points",
    "nscans",
    "receiver_harmonic",
]


def import_ciqtek(path):
    """Import CIQTEK .epr data and return SpinData object.

    Args:
        path (str): Path to .epr file.

    Returns:
        SpinData: SpinData object containing CIQTEK EPR data.

    """
    if not path.endswith(".epr"):
        raise TypeError("data file must be .epr")

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    attrs = _parse_attrs(raw)
    values, dims, coords = _parse_data(raw, attrs)

    attrs["experiment_type"] = "epr_spectrum"

    return SpinData(values, dims, coords, attrs)


def _parse_attrs(raw):
    """Extract and rename parameters from CIQTEK JSON structure.

    Args:
        raw (dict): Raw JSON data from .epr file.

    Returns:
        dict: Dictionary of renamed and typed parameters.

    """
    attrs = {}

    attrs["device"] = raw.get("devicename", "")
    attrs["experiment"] = raw.get("type", "")
    attrs["create_time"] = raw.get("createTime", "")
    attrs["filename"] = raw.get("filename", "")

    setting = raw.get("setting", {})
    for orig_key, new_key in _rename_dict.items():
        if orig_key in setting:
            val = setting[orig_key]
            if new_key in _float_params:
                attrs[new_key] = float(val)
            elif new_key in _int_params:
                attrs[new_key] = int(float(val))
            else:
                attrs[new_key] = val

    line_data = raw.get("dataStore", {}).get("lineDataList", [])
    if line_data:
        entry = line_data[0]
        if "freq" in entry:
            attrs["frequency"] = float(entry["freq"])

    return attrs


def _extract_field_from_name(name):
    """Extract field value in Gauss from a trace name like 'TimeField_2975'.

    Args:
        name (str): Trace name.

    Returns:
        float or None: Field value in Gauss, or None if not found.

    """
    match = _re.search(r"_([\d.]+)$", name)
    if match:
        return float(match.group(1))
    return None


def _parse_data(raw, attrs):
    """Extract data arrays and axes from CIQTEK JSON structure.

    Args:
        raw (dict): Raw JSON data from .epr file.
        attrs (dict): Parameter dictionary.

    Returns:
        tuple: (values, dims, coords).

    """
    line_data = raw.get("dataStore", {}).get("lineDataList", [])
    if not line_data:
        raise ValueError("No data found in .epr file")

    x_axis_name = raw.get("dataStore", {}).get("xAxisName", "")

    if len(line_data) == 1:
        entry = line_data[0]
        re_data = _np.array(entry.get("ReData", []))
        im_data = _np.array(entry.get("ImData", []))
        x_axis = re_data[:, 0]
        values = re_data[:, 1] + 1j * im_data[:, 1]

        if "Field" in x_axis_name:
            coords = [x_axis / 10.0]
            dims = ["B0"]
        else:
            coords = [x_axis]
            dims = ["t2"]

        return values, dims, coords

    # 2D data: multiple traces in lineDataList
    traces = []
    field_values = []
    for entry in line_data:
        re_data = _np.array(entry.get("ReData", []))
        im_data = _np.array(entry.get("ImData", []))
        traces.append(re_data[:, 1] + 1j * im_data[:, 1])

        field = _extract_field_from_name(entry.get("name", ""))
        if field is not None:
            field_values.append(field)

    x_axis = _np.array(line_data[0].get("ReData", []))[:, 0]
    values = _np.column_stack(traces)

    if "Field" in x_axis_name:
        coords = [x_axis / 10.0]
        dims = ["B0"]
    elif "Time" in x_axis_name:
        coords = [x_axis]
        dims = ["t2"]
    else:
        coords = [x_axis]
        dims = ["x"]

    if field_values and len(field_values) == len(line_data):
        # Convert field from Gauss to mT
        coords.append(_np.array(field_values) / 10.0)
        dims.append("B0")
    else:
        coords.append(_np.arange(len(line_data)))
        dims.append("t1")

    return values, dims, coords
