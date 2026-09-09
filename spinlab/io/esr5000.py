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

_SIGNAL_CURVE_KEYS = {
    "sinus": "MW_AbsorptionSinus",
    "cosinus": "MW_AbsorptionCosinus",
    "absorption": "MW_Absorption",
}


def import_esr5000(path, signal="complex"):
    """Import Bruker ESR5000 XML data and return SpinData object.

    Args:
        path (str): Path to .xml file.
        signal (str): Which data channel(s) to return. One of:

            * "complex" (default): a complex-valued signal built from the
              quadrature channels, with MW_AbsorptionSinus as the real part
              and MW_AbsorptionCosinus as the imaginary part. Falls back to
              the real-valued MW_Absorption channel if no quadrature data
              is present. See note below on why sinus, not cosinus, is
              taken as the real part.
            * "sinus": the raw MW_AbsorptionSinus channel only.
            * "cosinus": the raw MW_AbsorptionCosinus channel only.
            * "absorption": the raw MW_Absorption channel only.

    Returns:
        SpinData: SpinData object containing ESR5000 data.

    Note:
        MW_Absorption is not the vector magnitude sqrt(sinus^2 + cosinus^2)
        of the quadrature channels (it takes negative values, which a
        magnitude cannot). Comparing it against sample data instead shows
        it is a near-exact linear function of MW_AbsorptionSinus alone
        (R^2 >= 0.998, and exactly 1.0 for one sample file), i.e. it *is*
        the sinus channel, up to a constant baseline offset. That is why
        "complex" assigns sinus to the real part and cosinus to the
        imaginary part, matching the instrument's own absorption output.

    """
    tree = _ET.parse(path)
    root = tree.getroot()

    meas = root.find("Data/Measurement")
    if meas is None:
        raise ValueError("No Measurement element found in XML file")

    attrs = _parse_attrs(meas)
    values, dims, coords = _parse_data(meas, signal=signal)

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


def _parse_data(meas, signal="complex"):
    """Extract data arrays and axes from ESR5000 XML.

    Args:
        meas (Element): XML Measurement element.
        signal (str): Which channel(s) to return. See `import_esr5000`.

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

    if signal == "complex":
        if "MW_AbsorptionSinus" in curve_dict and "MW_AbsorptionCosinus" in curve_dict:
            sin_data = _decode_curve(curve_dict["MW_AbsorptionSinus"])
            cos_data = _decode_curve(curve_dict["MW_AbsorptionCosinus"])
            values = sin_data + 1j * cos_data
        elif "MW_Absorption" in curve_dict:
            values = _decode_curve(curve_dict["MW_Absorption"])
        else:
            raise ValueError("No absorption data found")
    elif signal in _SIGNAL_CURVE_KEYS:
        curve_key = _SIGNAL_CURVE_KEYS[signal]
        if curve_key not in curve_dict:
            raise ValueError("No %s curve found in data" % curve_key)
        values = _decode_curve(curve_dict[curve_key])
    else:
        raise ValueError(
            "Invalid signal '%s', must be one of 'complex', %s"
            % (signal, ", ".join(repr(k) for k in _SIGNAL_CURVE_KEYS))
        )

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
