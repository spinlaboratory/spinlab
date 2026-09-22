"""Helpers for mapping raw importer attributes into SpinLab attributes."""

import re
import warnings

from ..config.config import SpinLAB_CONFIG


def _assign_spinlab_attrs(data, data_format):
    """Load and assign experiment attributes to spinlab attributes.

    Args:
        data (SpinData): Data object.
        data_format (str): Format of spectrometer data to import.

    Returns:
        SpinData: Data object with updated ``spinlab_attrs``.
    """
    if data_format is None:
        raise TypeError(
            "No data format given and autodetect failed to detect format, please specify a format"
        )

    spinlab_attrs_data_info = SpinLAB_CONFIG.getlist(
        "SpinLAB_ATTRS_COMMON", "spinlab_attrs_data_info"
    )
    spinlab_attrs_data_info = [x.strip() for x in spinlab_attrs_data_info]
    spinlab_attrs_label = SpinLAB_CONFIG.get(
        "SpinLAB_ATTRS_COMMON", "spinlab_attrs_label", fallback="SpinLAB_ATTRS"
    )
    spinlab_attrs_label += ":" + data_format
    for key, val in SpinLAB_CONFIG[spinlab_attrs_label].items():
        if val != "None":
            try:
                if key not in spinlab_attrs_data_info:
                    params = _convert_spinlab_attrs(data, val)
                else:
                    params = val
                data.spinlab_attrs[key] = params
            except Exception:
                continue
    return data


def _convert_spinlab_attrs(data, exp_key):
    """Load and calculate the value assigned to spinlab attributes.

    Args:
        data (SpinData): Data object.
        exp_key (str): Experiment attribute expression, optionally with unit.

    Returns:
        int or float: SpinLab attribute value.
    """
    if "," in exp_key:
        [params, unit] = exp_key.split(",")
        scaling_factor = _scale_spinlab_attrs(unit)
    else:
        params = exp_key
        scaling_factor = 1

    params_list = params.split("*")
    new_params = 1
    for key in params_list:
        params = data.attrs["".join(key.split())]
        if isinstance(params, str):
            if "." in params and (
                params.find(".") == len(params) - 1
                or params[params.find(".") + 1].isdigit()
            ):
                new_params *= float(re.findall(r"[+-]?\d+\.\d+", params)[0])
            else:
                new_params *= int(re.findall(r"\d+", params)[0])
        else:
            new_params *= params
    return new_params * scaling_factor


def _scale_spinlab_attrs(unit):
    """Scale a SpinLab attribute value to SI units."""
    unit = unit.strip()
    units = [k.strip() for k in SpinLAB_CONFIG.getlist("UNITS", "units", fallback=[])]

    for u in units:
        if u in unit:
            if u == unit:
                return 1
            scaling_letter = unit[0]
            if scaling_letter == "m":
                scaling_letter = "mm"
            scaling_letter = scaling_letter.lower()
            scaling_list = list(SpinLAB_CONFIG["SI_SCALING"].keys())
            if scaling_letter not in scaling_list:
                warnings.warn(
                    "Unit scaling letter {0} is not in scaling list {1}, force scaling factor to 1".format(
                        scaling_letter, scaling_list
                    )
                )
                scaling_factor = 1
            else:
                scaling_factor = SpinLAB_CONFIG.get(
                    "SI_SCALING", scaling_letter, fallback=None
                )
            return float(scaling_factor)
    warnings.warn(
        "no valid unit and prefix found ({0}), will return 1 as scaling factor".format(
            unit
        )
    )
    return 1
