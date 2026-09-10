import numpy as _np
import base64 as _base64
import struct as _struct
import warnings as _warnings
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


def import_esr5000(path, signal="complex", raw=False, resolution=None):
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

        raw (bool): If True, return the selected channel(s) exactly as
            recorded, on their own native time axis (dims=["t2"]) instead
            of interpolating onto a field axis. The individual data curves
            in an ESR5000 XML file are each sampled on their own timebase,
            so the untouched samples cannot be paired with the (differently
            sampled) BField curve without violating SpinData's requirement
            that coords and values have matching length. The BField curve
            is instead reconstructed onto that same native time axis by
            interpolation (field sweeps are smooth and near-linear in time,
            so this costs essentially no precision) and provided in
            attrs["field_raw"], together with its own native time axis in
            attrs["field_raw_time"], for the caller to use if needed.
            Cannot be combined with `resolution`.
        resolution (int): Number of points to interpolate the selected
            channel(s) onto, spanning the same field range as the native
            BField curve. Defaults to the native BField curve's own point
            count (the historical behavior of this importer). If
            `resolution` exceeds the number of native raw samples in the
            selected channel(s), a warning is issued: the extra points are
            interpolated and do not represent additional independent
            measurements. Cannot be combined with `raw`.

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
    if raw and resolution is not None:
        raise ValueError("`raw` and `resolution` cannot be used together")

    tree = _ET.parse(path)
    root = tree.getroot()

    meas = root.find("Data/Measurement")
    if meas is None:
        raise ValueError("No Measurement element found in XML file")

    attrs = _parse_attrs(meas)
    values, dims, coords, extra_attrs = _parse_data(
        meas, signal=signal, raw=raw, resolution=resolution
    )
    attrs.update(extra_attrs)

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


def _curve_time_axis(curve_el, n):
    """Return a curve's native time axis (s), from its XOffset/XSlope.

    Args:
        curve_el (Element): XML Curve element.
        n (int): Number of samples in the curve.

    Returns:
        ndarray: Time axis of length `n`.

    """
    offset = float(curve_el.get("XOffset"))
    slope = float(curve_el.get("XSlope"))
    return offset + slope * _np.arange(n)


def _select_value_curve(curve_dict, signal):
    """Pick the curve element(s) and decode the values for a given signal.

    Args:
        curve_dict (dict): Mapping of YType to XML Curve elements.
        signal (str): Which channel(s) to return. See `import_esr5000`.

    Returns:
        tuple: (values (ndarray, possibly complex), time_curve_el (Element,
        the curve whose XOffset/XSlope define the native time axis)).

    """
    if signal == "complex":
        if "MW_AbsorptionSinus" in curve_dict and "MW_AbsorptionCosinus" in curve_dict:
            real_el = curve_dict["MW_AbsorptionSinus"]
            values = _decode_curve(real_el) + 1j * _decode_curve(
                curve_dict["MW_AbsorptionCosinus"]
            )
            return values, real_el
        elif "MW_Absorption" in curve_dict:
            abs_el = curve_dict["MW_Absorption"]
            return _decode_curve(abs_el), abs_el
        else:
            raise ValueError("No absorption data found")
    elif signal in _SIGNAL_CURVE_KEYS:
        curve_key = _SIGNAL_CURVE_KEYS[signal]
        if curve_key not in curve_dict:
            raise ValueError("No %s curve found in data" % curve_key)
        curve_el = curve_dict[curve_key]
        return _decode_curve(curve_el), curve_el
    else:
        raise ValueError(
            "Invalid signal '%s', must be one of 'complex', %s"
            % (signal, ", ".join(repr(k) for k in _SIGNAL_CURVE_KEYS))
        )


def _resample_to_field(values, field, resolution):
    """Interpolate `values` onto a field axis, warning if upsampling.

    Args:
        values (ndarray): Decoded curve values, on their own native
            sampling (not yet aligned to `field`).
        field (ndarray): Native BField curve.
        resolution (int): Requested number of output points, or None to
            use the native BField curve's own point count.

    Returns:
        tuple: (values, coords_field).

    """
    native_count = len(values)
    target_len = len(field) if resolution is None else resolution

    if target_len > native_count:
        _warnings.warn(
            "Requested resolution (%d) exceeds the number of native raw "
            "samples (%d) for the selected signal; points beyond the "
            "native resolution are interpolated and do not represent "
            "additional independent measurements." % (target_len, native_count)
        )

    if resolution is None and native_count == len(field):
        return values, field

    target_field = (
        field if resolution is None else _np.linspace(field[0], field[-1], resolution)
    )
    x_orig = _np.linspace(field[0], field[-1], native_count)
    values_interp = _np.interp(target_field, x_orig, values.real)
    if _np.iscomplexobj(values):
        values_interp = values_interp + 1j * _np.interp(
            target_field, x_orig, values.imag
        )

    return values_interp, target_field


def _parse_data(meas, signal="complex", raw=False, resolution=None):
    """Extract data arrays and axes from ESR5000 XML.

    Args:
        meas (Element): XML Measurement element.
        signal (str): Which channel(s) to return. See `import_esr5000`.
        raw (bool): If True, return untouched samples on their native time
            axis. See `import_esr5000`.
        resolution (int): Number of output points to interpolate onto. See
            `import_esr5000`.

    Returns:
        tuple: (values, dims, coords, extra_attrs).

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

    field_el = curve_dict["BField"]
    field = _decode_curve(field_el)

    values, time_curve_el = _select_value_curve(curve_dict, signal)

    if raw:
        time_axis = _curve_time_axis(time_curve_el, len(values))
        extra_attrs = {
            "field_raw": field,
            "field_raw_time": _curve_time_axis(field_el, len(field)),
        }
        return values, ["t2"], [time_axis], extra_attrs

    values, target_field = _resample_to_field(values, field, resolution)
    return values, ["B0"], [target_field], {}
