import numpy as _np
import base64 as _base64
import struct as _struct
import xml.etree.ElementTree as _ET

from .. import SpinData

__all__ = ["import_esr5000"]

_rename_dict = {
    "MwFreq": "frequency",
    "QFactor": "q_value",
    "Temperature": "temperature",
    "Phase": "phase",
    "Name": "name",
    "Device": "device",
    "Timestamp": "create_time",
}

_recipe_rename_dict = {
    "Bfrom": "sweep_start",
    "Bto": "sweep_stop",
    "SweepTime": "sweep_time",
    "Modulation": "modulation_amplitude",
    "ModulationFreq": "modulation_frequency",
    "MicrowavePower": "power",
    "Accumulations": "nscans",
}

_float_params = [
    "frequency",
    "q_value",
    "temperature",
    "phase",
    "sweep_start",
    "sweep_stop",
    "sweep_time",
    "modulation_amplitude",
    "modulation_frequency",
    "power",
]

_int_params = [
    "nscans",
]


def import_esr5000(path):
    """Import Bruker ESR5000 XML data and return SpinData object.

    Args:
        path (str): Path to .xml file.

    Returns:
        SpinData: SpinData object containing ESR5000 data.

    """
    tree = _ET.parse(path)
    root = tree.getroot()

    meas = root.find("Data/Measurement")
    if meas is None:
        raise ValueError("No Measurement element found in XML file")

    attrs = _parse_attrs(meas)
    values, dims, coords = _parse_data(meas)

    attrs["experiment_type"] = "epr_spectrum"

    return SpinData(values, dims, coords, attrs)


def _decode_curve(curve_el):
    """Decode a Base64-encoded data curve from ESR5000 XML.

    Args:
        curve_el (Element): XML Curve element with Base64-encoded text.

    Returns:
        ndarray: Decoded array of float64 values.

    """
    raw = curve_el.text.strip()
    chunks = [c + "=" for c in raw.split("=") if c]
    return _np.array([_struct.unpack("d", _base64.b64decode(c))[0] for c in chunks])


def _parse_attrs(meas):
    """Extract and rename parameters from ESR5000 XML Measurement element.

    Args:
        meas (Element): XML Measurement element.

    Returns:
        dict: Dictionary of renamed and typed parameters.

    """
    attrs = {}

    for orig_key, new_key in _rename_dict.items():
        val = meas.get(orig_key)
        if val is not None:
            if new_key in _float_params:
                attrs[new_key] = float(val)
            else:
                attrs[new_key] = val

    recipe = meas.find("Recipe")
    if recipe is not None:
        for param in recipe.find("Parameters"):
            param_name = param.get("Name")
            if param_name in _recipe_rename_dict:
                new_key = _recipe_rename_dict[param_name]
                if new_key in _float_params:
                    attrs[new_key] = float(param.text)
                elif new_key in _int_params:
                    attrs[new_key] = int(float(param.text))
                else:
                    attrs[new_key] = param.text

    return attrs


def _parse_data(meas):
    """Extract data arrays and axes from ESR5000 XML.

    Args:
        meas (Element): XML Measurement element.

    Returns:
        tuple: (values, dims, coords).

    """
    curves = meas.find("DataCurves")
    if curves is None:
        raise ValueError("No DataCurves element found")

    curve_dict = {}
    for curve in curves:
        if curve.text is not None and curve.text.strip():
            curve_dict[curve.get("YType")] = curve

    if "BField" not in curve_dict:
        raise ValueError("No BField curve found in data")

    field = _decode_curve(curve_dict["BField"])

    if "MW_AbsorptionSinus" in curve_dict and "MW_AbsorptionCosinus" in curve_dict:
        sin_data = _decode_curve(curve_dict["MW_AbsorptionSinus"])
        cos_data = _decode_curve(curve_dict["MW_AbsorptionCosinus"])
        values = cos_data + 1j * sin_data
    elif "MW_Absorption" in curve_dict:
        values = _decode_curve(curve_dict["MW_Absorption"])
    else:
        raise ValueError("No absorption data found")

    # Field is already in mT
    coords = [field]
    dims = ["B0"]

    # Interpolate values onto field axis if lengths differ
    if len(values) != len(field):
        x_orig = _np.linspace(field[0], field[-1], len(values))
        values_interp = _np.interp(field, x_orig, values.real)
        if _np.iscomplexobj(values):
            values_interp = values_interp + 1j * _np.interp(
                field, x_orig, values.imag
            )
        values = values_interp

    return values, dims, coords
