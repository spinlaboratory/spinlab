import os
from . import *
import re
import warnings

from ..core.util import concat
from ..config.config import SpinLAB_CONFIG


def load(path, data_format=None, dim=None, coord=[], verbose=False, *args, **kwargs):
    """Import data from different spectrometer formats

    Args:
        path (str, list): Path to data directory or list of directories
        data_format (str): format of spectrometer data to import (optional). Allowed values: "prospa", "topspin", "delta", "vnmrj", "tnmr", "specman", "xenon", "xepr", "winepr", "esp", "h5", "power", "vna", "cnsi_powers", "rs2d"
        dim (str): If giving directories as list, name of dimension to concatenate data along
        coord (numpy.ndarray): If giving directories as list, coordinates of new dimension
        verbose (bool): If true, print debugging output
        args: Args passed to spectrometer specific import function
        kwargs: Key word args passed to spectrometer specific import function

    Returns:
        data (slData): Data object

    Examples:

        Load a data file

        >>> data = sl.load('Path/To/File')

        Load a list of files and concatenate down a new dimension called 't1' with coordinates

        >>> data = sl.load(['1/data.1d','2/data.1d','3/data.1d'], dim = 't1', coord = np.r_[0.1,0.2,0.3])
    """

    if isinstance(path, list):
        if len(coord) != len(path):
            raise ValueError(
                "coord must be a list or array equal in len to the number of paths given"
            )

        data_list = []
        if dim is None:
            dim = "unnamed"
        for filename in path:
            data = load_file(
                filename, data_format=data_format, verbose=verbose, *args, **kwargs
            )
            data_list.append(data)
        # coord could be empty list
        if len(coord) == 0:
            coord = None  # to not break concat call signature

        data = concat(data_list, dim=dim, coord=coord)

        return data

    else:
        return load_file(
            path, data_format=data_format, verbose=verbose, *args, **kwargs
        )


def load_file(path, data_format=None, verbose=False, *args, **kwargs):
    """Import data from different spectrometer formats

    Args:
        path (str): Path to data directory or file
        data_format (str): Format of spectrometer data to import (optional). Allowed values: "prospa", "topspin", "delta", "vnmrj", "tnmr", "specman", "xenon", "xepr", "winepr", "esp", "h5", "power", "vna", "cnsi_powers"
        verbose (bool): If true, print additional debug outputs
        args: Arguments passed to spectrometer specific import function
        kwargs: Key word arguments passed to spectrometer specific import function

    Returns:
        data (slData): Data object
    """

    path = os.path.normpath(path)
    if os.path.isdir(path) and path[-1] != os.sep:
        path = path + os.sep

    if data_format == None:
        data_format = autodetect(path, verbose=verbose)

    if data_format == "prospa":
        data = prospa.import_prospa(path, *args, **kwargs)

    elif data_format == "topspin":
        data = topspin.import_topspin(path, verbose=verbose, *args, **kwargs)

    elif data_format == "topspin pdata":
        # import_topspin should also handle this format, this is a workaround
        data = topspin.load_pdata(path, verbose=verbose, *args, **kwargs)

    elif data_format == "delta":
        data = delta.import_delta(path, verbose=verbose, *args, **kwargs)

    elif data_format == "vnmrj":
        data = vnmrj.import_vnmrj(path, *args, **kwargs)

    elif data_format == "tnmr":
        data = tnmr.import_tnmr(path, *args, **kwargs)

    elif data_format == "specman":
        data = specman.import_specman(path, *args, **kwargs)

    elif data_format in ["xepr", "xenon"]:
        data = bes3t.import_bes3t(path, *args, **kwargs)

    elif data_format in ["winepr", "esp"]:
        data = winepr.import_winepr(path, *args, **kwargs)

    elif data_format == "h5":
        data = h5.load_h5(path, *args, **kwargs)

    elif data_format == "power":
        data = power.import_power(path, *args, **kwargs)

    elif data_format == "vna":
        data = vna.import_vna(path, *args, **kwargs)

    elif data_format == "cnsi_powers":
        data = cnsi.get_powers(path, *args, **kwargs)

    elif data_format == "rs2d":
        data = rs2d.import_rs2d(path, *args, **kwargs)

    # elif data_format == "mat":
    #     data = mat.import_mat(path, *args, **kwargs)

    else:
        raise ValueError("Invalid data format: %s" % data_format)

    if data_format not in ["h5", "power", "vna", "cnsi_powers", "mat"]:
        data = _assign_spinlab_attrs(data, data_format)

    return data


# TODO rename to detect_file_format
def autodetect(test_path, verbose=False):
    """Automatically detect data format

    Args:
        test_path (str): Test directory
        verbose (bool): If true, print output for debugging

    Returns:
        str: Data format as string

    """

    if verbose == True:
        print("current directory:", os.getcwd())
        print("data path:", test_path)
        abs_path = os.path.abspath(test_path)
        print("absolute path:", abs_path)

    # Remove trailing separator
    if test_path[-1] == os.sep:
        test_path = test_path[:-1]
        if verbose:
            print("removed trailing separator:", os.sep)

    path_exten = os.path.splitext(test_path)[1]
    if path_exten != "" and verbose:
        print("Extension:", path_exten)

    if path_exten == ".DSC" or path_exten == ".DTA" or path_exten == ".YGF":
        data_format = "xepr"
    elif path_exten in [".par", ".spc"]:
        data_format = "winepr"
    elif path_exten in [".d01", ".exp"]:
        data_format = "specman"
    elif path_exten == ".jdf":
        data_format = "delta"
    elif (
        os.path.isdir(test_path)
        #        and ("fid" in os.listdir(test_path) or "ser" in os.listdir(test_path))
        and ("acqu" in os.listdir(test_path) or "acqus" in os.listdir(test_path))
    ):
        data_format = "topspin"
    elif os.path.isdir(test_path) and (
        "proc" in os.listdir(test_path) or "procss" in os.listdir(test_path)
    ):
        data_format = "topspin pdata"
    elif os.path.isdir(test_path) and path_exten == ".fid":
        data_format = "vnmrj"
    elif path_exten in [".1d", ".2d", ".3d", ".4d"]:
        data_format = "prospa"
    elif path_exten == ".tnt":
        data_format = "tnmr"
    elif path_exten in [".s1p", ".s2p"]:
        data_format = "vna"
    elif (
        os.path.isdir(test_path)
        and "acqu.par" in os.listdir(test_path)
        and "data.csv" in os.listdir(test_path)
    ):
        data_format = "prospa"
    elif path_exten == ".h5":
        data_format = "h5"
    elif path_exten in [".xml", ".dat"]:
        data_format = "rs2d"
    elif path_exten in [".mat"]:
        data_format = "mat"
    else:
        raise TypeError(
            "No data format given and autodetect failed to detect format, please specify a format"
        )

    if verbose:
        print("Data Format:", data_format)

    return data_format


def _assign_spinlab_attrs(data, data_format):
    """Load and assign experiment attributes to spinlab attributes

    Args:
        data (slData): Data object
        data_format (str): Format of spectrometer data to import

    Returns:
        data (slData): Data object

    """
    if data_format == None:
        raise TypeError(
            "No data format given and autodetect failed to detect format, please specify a format"
        )

    else:
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
                except:
                    continue
        return data


def _convert_spinlab_attrs(data, exp_key):
    """Load and calculate the value assigned to spinlab attributes

    Args:
        data (slData): Data object
        exp_key (str): A string of experiment attributes possibly with multiplication sign and unit

    Returns:
        new_params (int or float): spinlab attributes values
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
            ):  # when number has decimal
                new_params *= float(
                    re.findall(r"[+-]?\d+\.\d+", params)[0]
                )  # remove unexpected characters

            else:
                new_params *= int(re.findall(r"\d+", params)[0])
        else:
            new_params *= params
    return new_params * scaling_factor


def _scale_spinlab_attrs(unit):
    """Scale all spinlab attributes value to SI unit

    Args:
        unit (str): an unit

    Returns:
        scaling_factor (float): scaling factor
    """
    unit = unit.strip()
    # check for unit and return 1 if no prefix
    units = [k.strip() for k in SpinLAB_CONFIG.getlist("UNITS", "units", fallback=[])]

    for u in units:
        if u in unit:
            if u == unit:
                return 1
            else:
                scaling_letter = unit[0]
                if scaling_letter == "m":
                    scaling_letter = "mm"  # for configuration purpose
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
