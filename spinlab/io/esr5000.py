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

# ESR5000 XML files declare what their two axes actually are via the
# Measurement element's XDatasource/YDatasource attributes. "BField" gets
# the full field-sweep treatment below (channel selection, time-based
# field registration, resampling). Any other (XDatasource, YDatasource)
# pair recognized here is a simple, already sample-aligned X/Y curve pair
# with no further processing -- see _parse_generic_sweep. Unrecognized
# pairs raise rather than guess at a dim name or experiment_type.
_GENERIC_SWEEP_TYPES = {
    # A resonator/cavity tuning dip: ADC response vs. probe frequency.
    ("Frequency", "ADC_24bit"): {"dim": "f", "experiment_type": "cavity_dip_sweep"},
}


def import_esr5000(path, signal=None, raw=False, resolution=None):
    """Import Bruker ESR5000 XML data and return SpinData object.

    Handles two kinds of ESR5000 measurement, dispatched on the XML's own
    Measurement/XDatasource attribute:

    * Field-sweep spectra (XDatasource="BField"): the `signal`, `raw`, and
      `resolution` options below apply. Only tested against 1D CW spectra
      so far (the sample files this module was validated against) -- the
      ESR5000 supports other field-sweep experiment types too, e.g. 2D
      power sweeps, but no test coverage or sample data for those exists
      yet, and this function has not been verified to parse them
      correctly.
    * Other recognized sweeps, currently just a cavity tuning dip
      (XDatasource="Frequency", YDatasource="ADC_24bit"): a plain,
      already sample-aligned X/Y curve pair with no channel choice or
      resampling, so `signal`, `raw`, and `resolution` must be left at
      their defaults -- passing any of them raises. Unrecognized
      (XDatasource, YDatasource) combinations also raise rather than
      guess at how to interpret them.

    Args:
        path (str): Path to .xml file.
        signal (str): Field-sweep only. Which data channel(s) to return.
            One of:

            * None (default): resolves to "absorption" for field-sweep
              files. Must be left as None for any other recognized sweep.
            * "absorption": the real-valued MW_Absorption channel only.
              This is the same channel ESRStudio itself exports as
              "MW_Absorption" in .DSC/.DTA files, so this default matches
              what a vendor export of the same measurement would give you.
            * "complex": a complex-valued signal built from the quadrature
              channels instead, with MW_AbsorptionSinus as the real part
              and MW_AbsorptionCosinus as the imaginary part -- this is
              lossy in the other direction: "absorption" alone cannot be
              un-mixed back into separate sinus/cosinus channels, so choose
              "complex" if you need the full quadrature information (e.g.
              for phase correction). Falls back to the real-valued
              MW_Absorption channel if no quadrature data is present. See
              note below on why sinus, not cosinus, is taken as the real
              part.
            * "sinus": the raw MW_AbsorptionSinus channel only.
            * "cosinus": the raw MW_AbsorptionCosinus channel only.

        raw (bool): Field-sweep only; must be False otherwise. If True,
            return the selected channel(s) exactly as recorded, on their
            own native time axis (dims=["t2"]) instead of interpolating
            onto a field axis. The individual data curves in an ESR5000
            XML file are each sampled on their own timebase, so the
            untouched samples cannot be paired with the (differently
            sampled) BField curve without violating SpinData's requirement
            that coords and values have matching length. The BField curve
            is instead provided untouched, on its own native time axis, as
            attrs["field_raw"] and attrs["field_raw_time"] respectively,
            for the caller to align against the selected channel's own
            time axis (`data.coords["t2"]`) if needed. Cannot be combined
            with `resolution`.
        resolution (int): Field-sweep only; must be None otherwise. Number
            of points to interpolate the selected channel(s) onto.
            Defaults to the native BField curve's own point count and axis
            (the historical behavior of this importer, including any real
            nonlinearity in the recorded sweep). When `resolution` is
            given explicitly, the output instead spans a synthetic axis
            from the nominal sweep_start to sweep_stop field (Bfrom/Bto)
            -- matching the field window vendor-exported files at a given
            point count use, rather than the literal (slightly
            overshooting) BField curve endpoints. If `resolution` exceeds
            the number of native raw samples in the selected channel(s), a
            warning is issued: the extra points are interpolated and do
            not represent additional independent measurements. Cannot be
            combined with `raw`.

            Whenever `raw` is False (whether or not `resolution` is
            given), each raw sample of the selected channel(s) is
            registered to field by interpolating the (coarser) BField
            curve as a function of time onto that channel's own native
            sampling times -- not by assuming samples are spread linearly
            across the field range. This matters because real sweeps can
            have settling/dwell time at the edges (confirmed non-trivial
            in sample data): the naive linear assumption was verified
            against a vendor .DSC/.DTA export of the same measurement to
            produce a measurably stretched/shifted field axis (~0.1 mT
            error in peak/trough position and linewidth), which this
            time-based registration eliminates (verified to match the
            vendor export to numerical precision on two sample files).

    Returns:
        SpinData: SpinData object containing ESR5000 data. attrs
        ["experiment_type"] is "epr_spectrum" for field-sweep files, or
        the recognized sweep's experiment_type otherwise (e.g.
        "cavity_dip_sweep") -- SpinLab's fancy_plot uses this attribute to
        pick a plot design. The processing performed at import (signal,
        raw, resolution, and the native vs. output sample counts) is
        recorded as an "esr5000_import" entry in data.proc_attrs.

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
    parsed = _parse_data(
        meas,
        signal=signal,
        raw=raw,
        resolution=resolution,
        sweep_start=attrs.get("sweep_start"),
        sweep_stop=attrs.get("sweep_stop"),
    )
    attrs.update(parsed["attrs"])

    data = SpinData(parsed["values"], parsed["dims"], parsed["coords"], attrs)
    data.add_proc_attrs(
        "esr5000_import",
        {
            "signal": parsed["signal"],
            "raw": raw,
            "resolution": resolution,
            "native_samples": parsed["native_samples"],
            "output_samples": len(parsed["values"]),
        },
    )
    return data


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


def _resample_to_field(
    values,
    field,
    field_time,
    values_time,
    resolution,
    sweep_start=None,
    sweep_stop=None,
):
    """Interpolate `values` onto a field axis, warning if upsampling.

    The selected channel's samples are registered to field via their
    actual recorded timing, not by assuming they are spread linearly
    across the field range: the (coarser) BField curve is interpolated as
    a function of time onto the selected channel's own native sample
    times, giving the true field value at each raw sample -- capturing any
    real nonlinearity or dwell time in the sweep (both curves are recorded
    against the same clock, just each on their own native timebase, given
    by XOffset/XSlope). Without this, files with sweep settling/dwell time
    at the edges produce a measurably stretched or shifted field axis
    compared to what the field truly was during each sample.

    Args:
        values (ndarray): Decoded curve values, on their own native
            sampling (not yet aligned to `field`).
        field (ndarray): Native BField curve.
        field_time (ndarray): BField curve's own native time axis.
        values_time (ndarray): Selected channel's own native time axis.
        resolution (int): Requested number of output points, or None to
            use the native BField curve's own point count and axis.
        sweep_start (float): Nominal sweep start field (Bfrom), used as
            the target span when `resolution` is given -- vendor-exported
            files at a given point count use this nominal window rather
            than the literal (slightly overshooting) BField curve
            endpoints. Ignored when `resolution` is None, since the
            default output uses the literal BField curve as its target
            axis instead of a synthetic one.
        sweep_stop (float): Nominal sweep stop field (Bto). See
            `sweep_start`.

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

    if resolution is None:
        target_field = field
    else:
        span_start = sweep_start if sweep_start is not None else field[0]
        span_stop = sweep_stop if sweep_stop is not None else field[-1]
        target_field = _np.linspace(span_start, span_stop, resolution)

    field_per_sample = _np.interp(values_time, field_time, field)

    values_interp = _np.interp(target_field, field_per_sample, values.real)
    if _np.iscomplexobj(values):
        values_interp = values_interp + 1j * _np.interp(
            target_field, field_per_sample, values.imag
        )

    return values_interp, target_field


def _parse_data(
    meas,
    signal=None,
    raw=False,
    resolution=None,
    sweep_start=None,
    sweep_stop=None,
):
    """Extract data arrays and axes from ESR5000 XML.

    Dispatches on Measurement/XDatasource: "BField" gets the field-sweep
    treatment (channel selection, time-based field registration,
    resampling); anything else is handed to `_parse_generic_sweep`. See
    `import_esr5000`.

    Args:
        meas (Element): XML Measurement element.
        signal (str): Field-sweep only; see `import_esr5000`.
        raw (bool): Field-sweep only; see `import_esr5000`.
        resolution (int): Field-sweep only; see `import_esr5000`.
        sweep_start (float): Nominal sweep start field (Bfrom). See
            `_resample_to_field`.
        sweep_stop (float): Nominal sweep stop field (Bto). See
            `_resample_to_field`.

    Returns:
        dict: {"values", "dims", "coords", "attrs" (to merge into the
        SpinData attrs, including "experiment_type"), "signal" (the
        concrete channel actually used, or None for non-field-sweep
        sweeps), "native_samples"}.

    """
    curves = meas.find("DataCurves")
    if curves is None:
        raise ValueError("No DataCurves element found")

    curve_dict = {}
    for curve in curves:
        if curve.text is not None and curve.text.strip():
            curve_dict[curve.get("YType")] = curve

    x_datasource = meas.get("XDatasource")

    if x_datasource != "BField":
        return _parse_generic_sweep(
            meas, curve_dict, x_datasource, signal, raw, resolution
        )

    if signal is None:
        signal = "absorption"

    if "BField" not in curve_dict:
        raise ValueError("No BField curve found in data")

    field_el = curve_dict["BField"]
    field = _decode_curve(field_el)
    field_time = _curve_time_axis(field_el, len(field))

    values, time_curve_el = _select_value_curve(curve_dict, signal)
    native_samples = len(values)
    values_time = _curve_time_axis(time_curve_el, native_samples)

    if raw:
        return {
            "values": values,
            "dims": ["t2"],
            "coords": [values_time],
            "attrs": {
                "field_raw": field,
                "field_raw_time": field_time,
                "experiment_type": "epr_spectrum",
            },
            "signal": signal,
            "native_samples": native_samples,
        }

    values, target_field = _resample_to_field(
        values,
        field,
        field_time,
        values_time,
        resolution,
        sweep_start=sweep_start,
        sweep_stop=sweep_stop,
    )
    return {
        "values": values,
        "dims": ["B0"],
        "coords": [target_field],
        "attrs": {"experiment_type": "epr_spectrum"},
        "signal": signal,
        "native_samples": native_samples,
    }


def _parse_generic_sweep(meas, curve_dict, x_datasource, signal, raw, resolution):
    """Parse a non-field-sweep ESR5000 measurement, e.g. a cavity tuning
    dip (a frequency sweep with the ADC response at each frequency).

    These experiments record a plain X/Y curve pair -- declared by the
    Measurement element's XDatasource/YDatasource attributes -- already
    aligned sample-for-sample (both curves share the same native
    XType="Samples", XOffset=0, XSlope=1), unlike field-sweep spectra
    where the absorption/quadrature curves are on a finer, independent
    timebase from BField and must be registered to it (see
    `_resample_to_field`). There is nothing to resample here and no
    alternate channel to select, so `signal`, `raw`, and `resolution` --
    all specific to field-sweep spectra -- are rejected if given
    explicitly, and an unrecognized (XDatasource, YDatasource) pair
    raises rather than guessing at a dim name or experiment_type.

    Args:
        meas (Element): XML Measurement element.
        curve_dict (dict): Mapping of YType to XML Curve elements.
        x_datasource (str): Measurement's XDatasource attribute.
        signal, raw, resolution: See `import_esr5000`; only their
            defaults (None, False, None) are accepted here.

    Returns:
        dict: Same shape as `_parse_data`'s return value.

    """
    if signal is not None:
        raise ValueError(
            "`signal` only applies to BField field-sweep ESR5000 files; "
            "this file's XDatasource is %r" % x_datasource
        )
    if raw:
        raise ValueError(
            "`raw` only applies to BField field-sweep ESR5000 files; "
            "this file's XDatasource is %r" % x_datasource
        )
    if resolution is not None:
        raise ValueError(
            "`resolution` only applies to BField field-sweep ESR5000 files; "
            "this file's XDatasource is %r" % x_datasource
        )

    y_datasource = meas.get("YDatasource")
    sweep_type = _GENERIC_SWEEP_TYPES.get((x_datasource, y_datasource))
    if sweep_type is None:
        raise ValueError(
            "Unrecognized ESR5000 experiment (XDatasource=%r, YDatasource=%r); "
            "only BField field sweeps and %s are currently supported"
            % (
                x_datasource,
                y_datasource,
                ", ".join("%s/%s" % pair for pair in _GENERIC_SWEEP_TYPES),
            )
        )

    if x_datasource not in curve_dict:
        raise ValueError("No %s curve found in data" % x_datasource)
    if y_datasource not in curve_dict:
        raise ValueError("No %s curve found in data" % y_datasource)

    coord = _decode_curve(curve_dict[x_datasource])
    values = _decode_curve(curve_dict[y_datasource])

    if len(coord) != len(values):
        raise ValueError(
            "%s curve (%d points) and %s curve (%d points) have different "
            "lengths" % (x_datasource, len(coord), y_datasource, len(values))
        )

    return {
        "values": values,
        "dims": [sweep_type["dim"]],
        "coords": [coord],
        "attrs": {"experiment_type": sweep_type["experiment_type"]},
        "signal": None,
        "native_samples": len(values),
    }
