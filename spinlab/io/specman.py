import numpy as _np
import os
import spinlab as _sl
import re

scale_dict = {
    "p": 1e-12,
    "n": 1e-9,
    "u": 1e-6,
    "m": 1e-3,
    "1": 1,
    "k": 1e3,
    "M": 1e6,
    "G": 1e9,
    "T": 1e12,
}


def import_specman(
    path,
    autodetect_coords: bool = True,
    autodetect_dims: bool = True,
    make_complex: bool = True,
    complex_dim: str = "x",
):
    """Import SpecMan data and return SpinData object

    SpinLab function to import SpecMan4EPR data (https://specman4epr.com/). The function returns a Spindata object with the spectral data.

    The structure of the Spindata object can be complex and the variables saved by SpecMan depend on the individual spectrometer configuration. Therefore, the import function returns a numpy array with the dimension "x0", "x1", "x2", "x3", "x4". In any case, the dimension "x0" corresponds to the variables stored in the data file. The spectroscopic data is stored in "x1" to "x4", depending on how many dimensions were recorded.
    The import function will require a parser script to properly assign the spectroscopic data and proper coordinates.

    Args:
        path (str):                 Path to either .exp file
        autodetect_coords(bool):    Autodetect coords based on attrs
        autodetect_dims(bool):      Autodetect dims based on attrs
        make_complex (bool):        If True, will create a complex SpinData object if the data is complex
        complex_dim (str):          The dimension to use for complex data (default: 'x')

    Returns:
        data (SpinData):         SpinData object containing SpecMan EPR data
    """

    if path[-1] == os.sep:
        path = path[:-1]
    if path[-1] == "p":
        file_name_d01 = path.replace("exp", "d01")
        file_name_exp = path
    elif path[-1] == "1":
        file_name_exp = path.replace("d01", "exp")
        file_name_d01 = path
    else:
        raise TypeError("Incorrect file type, must be .d01 or .exp")

    attrs = load_specman_exp(file_name_exp)

    if autodetect_coords or autodetect_dims:
        attrs = analyze_attrs(attrs)

    data, dims, coords, attrs = load_specman_d01(file_name_d01, attrs)

    if autodetect_dims:
        new_dims = generate_dims(attrs)
        dims = new_dims
    else:
        new_dims = None

    if autodetect_coords:
        coords = calculate_specman_coords(attrs, coords, new_dims)

    # Add import path
    attrs["import_path"] = path

    # Assign data/spectrum type
    attrs["experiment_type"] = "epr_spectrum"

    specman_data = _sl.SpinData(data, dims, coords, attrs)
    if make_complex:
        if complex_dim in dims and len(specman_data.coords[complex_dim]) == 2:
            specman_data = _sl.create_complex(specman_data, complex_dim)
    return specman_data


def load_specman_exp(path):
    """Import SpecMan parameters

    SpinLab function to read and import the SpecMan exp file. The .exp file is a text file that stores the experimental data, the pulse program, and other spectrometer configuration files.

    Args:
        path (str):     Path to either .d01 or .exp file

    Returns:
        attrs (dict):   Dictionary of parameter fields and values (SpinLab attributes)

    """
    exp_file_opened = open(path, encoding="utf8", errors="ignore")
    file_contents = exp_file_opened.read().splitlines()
    exp_file_opened.close()

    attrs = {}

    c = ""

    for i in range(0, len(file_contents)):
        exp_content = str(file_contents[i])
        if "%%" in exp_content or not exp_content:
            continue

        splt_exp_content = exp_content.split(" = ")
        if "[" in exp_content and "]" in exp_content and "=" not in exp_content:
            c = splt_exp_content[0].replace("[", "").replace("]", "")
        elif exp_content == "":
            c = "param"
        elif len(splt_exp_content) > 1:
            attrs[c + "_" + splt_exp_content[0]] = splt_exp_content[1]
        elif len(splt_exp_content) == 1 and exp_content != "":
            attrs[c + "_" + str(i)] = splt_exp_content
        else:
            pass

    return attrs


def load_specman_d01(path, attrs, verbose=False):
    """Import SpecMan d01 data file

    SpinLab function to import the SpecMan d01 data file. The format of the SpecMan data file is described here:


    Args:
        path (str):         Path to either .d01 or .exp file

    Returns:
        data (ndarray):     SpecMan data as numpy array
        params (dict):      Dictionary with import updated parameters dictionary
    """

    file_opened = open(path, "rb")
    uint_read = _np.fromfile(file_opened, dtype=_np.uint32)
    file_opened.close()

    file_opened = open(path, "rb")
    # "<f4" means float32, little-endian
    float_read = _np.fromfile(file_opened, dtype="<f4")
    file_opened.close()

    # Number of recorded variables stored
    attrs["numberOfVariables"] = uint_read[0]

    # 0 - data stored in double format, 1 -data stored in float format
    attrs["dataFormat"] = uint_read[1]

    # Number of dimensions of stored data. Note: Not clear why this is repeated for every dimension. This seems to be the same number for all dimensions, but is repeated.
    attrs["dims"] = uint_read[2]

    dataShape = uint_read[2 : 2 + uint_read[0] * 6]

    attrs["dataStreamShape"] = dataShape

    attrs["dataStartIndex"] = 2 + attrs["numberOfVariables"] * 6

    if verbose == True:
        print("** Data paramters **")
        print("numberOfVariables : ", attrs["numberOfVariables"])
        print("dataFormat        : ", attrs["dataFormat"])
        print("dims              : ", attrs["dims"])
        print("dataStreamShape   : ", attrs["dataStreamShape"])
        print("dataStartIndex    : ", attrs["dataStartIndex"])

    data = float_read[attrs["dataStartIndex"] :]

    monitor_dict = {}
    for key in attrs:
        if "_monitor" in key and attrs[key] == True:
            monitor_length = attrs[key.replace("_monitor", "_length")]
            monitor_data, data = (
                data[-monitor_length:],
                data[:-monitor_length],
            )  # shift monitor axis
            monitor_dict[key + "_data"] = monitor_data
            uint_read[0] -= 1  # reduce number of axis

    attrs = {**attrs, **monitor_dict}

    if attrs["dims"] == 1:
        data = _np.reshape(data, (uint_read[0], uint_read[3]), order="C")

    elif attrs["dims"] == 2:
        data = _np.reshape(data, (uint_read[0], uint_read[4], uint_read[3]), order="C")
        # data  =  _np.reshape(data[:-101], (2, 101, 101), order="C")
    elif attrs["dims"] == 3:
        data = _np.reshape(
            data, (uint_read[0], uint_read[5], uint_read[4], uint_read[3]), order="C"
        )

    elif attrs["dims"] == 4:
        data = _np.reshape(
            data,
            (uint_read[0], uint_read[4], uint_read[5], uint_read[6], uint_read[3]),
            order="C",
        )

    elif attrs["dims"] >= 4:
        print("Maximum dimensionality for SpecMan data is 4D")
        return None

    # Swap first axis with last
    data = _np.swapaxes(data, 0, -1)

    dims_full = ["x0", "x1", "x2", "x3", "x4"]
    dims = dims_full[0 : dataShape[0] + 1]

    coords = []
    shape = _np.shape(data)
    for index in range(data.ndim):
        coords.append(_np.arange(0.0, shape[index]))

    # SpecMan data can have a maximum of four dimensions

    return data, dims, coords, attrs


def analyze_attrs(attrs):
    """
    Analyze the attrs and add some important attrs to existing dictionary

    Args:
        attrs (dict): Dictionary of specman acqusition parameters

    Returns:
        attrs (dict): The dictionary of specman acqusition parameters and added parameters

    """

    temp = {}
    axis_order = []
    for key, val in attrs.items():
        if "params_" in key:
            new_key = key.split("params_")[1]  # get key value for temp dictionary
            val = val.split(";")[0]  # remove non value related information
            val_list = val.split(" ")  # split value string for further analyze
            unit = None
            if len(val_list) > 1:
                unit = val_list[-1]  # get unit
            val = val_list[0].strip(",")
            val_unit = val_list[1] if len(val_list) == 5 else None
            if "*" in val:
                temp[new_key] = val
            else:
                temp[new_key] = int(val) if "." not in val else float(val)
                temp[new_key] *= _convert_unit(val_unit)

            if unit is not None:
                temp[new_key + "_unit"] = unit

            if "step" in val_list:  # when it indicate the step
                step_index = (
                    val_list.index("step") + 1
                )  # the index of the value of 'step' is equal to the index of string 'index' + 1
                step_unit = (
                    val_list[val_list.index("step") + 2] if len(val_list) == 5 else None
                )
                step = float(val_list[step_index]) * _convert_unit(step_unit)
                temp[new_key + "_step"] = step

            if "to" in val_list:  # when it indicate the stop
                stop_index = (
                    val_list.index("to") + 1
                )  # the index of the value of 'stop' is equal to the index of string 'index' + 1
                stop_unit = (
                    val_list[val_list.index("to") + 2] if len(val_list) == 5 else None
                )
                stop = float(val_list[stop_index]) * _convert_unit(stop_unit)
                temp[new_key + "_stop"] = stop

            if "logto" in val_list:
                logto_index = val_list.index("logto") + 1
                logto_unit = val_list[logto_index + 1] if len(val_list) == 5 else None
                logto = float(val_list[logto_index]) * _convert_unit(logto_unit)
                temp[new_key + "_logto"] = logto

        if "sweep_" in key:
            val_list = val.split(",")
            val = val_list[1]  # get value
            axis = val_list[0]
            if len(axis) > 1 and axis[-1] == "f":  # is monitor
                axis = axis[:-1]
            new_key = "sweep_" + axis
            if new_key not in ["sweep_P", "sweep_I", "sweep_S"]:
                axis_order.append(new_key)
            temp[new_key + "_length"] = int(val)
            temp[new_key + "_monitor"] = (
                True
                if (len(val_list) == 5 and val_list[3] + "M" == val_list[-1])
                else False
            )  # check monitoring axis
            # new_key += '_dim' # last item is the key to the parameters, such as t, p...
            temp[new_key + "_dim"] = val_list[3]

    attrs["axis_order"] = axis_order
    attrs = {**attrs, **temp}
    return attrs


def generate_dims(attrs):
    """Generate dims from specman acquisition parameters

    Args:
        attrs (dict): Dictionary of specman acqusition parameters

    Returns:
        dims (list): a new dims

    """
    kw = attrs["axis_order"]
    dims = [
        attrs[key + "_dim"] if key != "sweep_T" else "t2"
        for key in kw
        if key + "_dim" in attrs
    ]
    dims.append("x")
    return dims


def calculate_specman_coords(attrs, old_coords, dims=None):
    """Generate coords from specman acquisition parameters

    Args:
        attrs (dict): Dictionary of specman acqusition parameters
        dims (list): (Optional) a list of dims

    Returns:
        coords (list): a calculated coords
    """

    kw = attrs["axis_order"]
    coords = []
    lengths = [attrs[key + "_length"] for key in kw if key + "_length" in attrs]
    lengths.append(len(old_coords[-1]))

    if not dims:
        dims = generate_dims(attrs)
        print("Warning: the coords might not be correct")

    for index, dim in enumerate(dims):
        length = lengths[index]
        if dim in attrs and dim + "_step" in attrs:
            start = attrs[dim]
            step = attrs[dim + "_step"]
            stop = start + step * (length - 1)
            coord = _np.linspace(start, stop, length)
        elif dim in attrs and dim + "_stop" in attrs:
            start = attrs[dim]
            stop = attrs[dim + "_stop"]
            coord = _np.linspace(start, stop, length)
        elif dim in attrs and dim + "_logto" in attrs:
            start = attrs[dim]
            logto = attrs[dim + "_logto"]
            coord = _np.logspace(
                _np.log10(start), _np.log10(logto), length, endpoint=True
            )
        elif dim in attrs and dim + "_step" not in attrs and dim + "_stop" not in attrs:
            val_string = attrs["params_" + dim]
            if "*" in val_string:
                i = 0
                while "params_" + dim + f"_{i}" in attrs:
                    val_string += attrs["params_" + dim + f"_{i}"]
                    i += 1
                val_string = val_string.replace("*", "")

            val_string = val_string.split(";")[0]
            val_string = val_string.replace(", ", ",").split(",")
            coord = _np.array(
                [
                    float(val.split()[0])
                    for val in val_string
                    if val.split()[0].replace(".", "").replace("-", "").isdigit()
                ][:length]
            )
            units = []
            try:
                units = [
                    x.split()[1] for x in val_string if not x.split()[1].isdigit()
                ][:length]
            except IndexError:
                pass

            if units:
                for i in range(len(coord)):
                    coord[i] *= _convert_unit(units[i])

        else:
            coord = _np.arange(0.0, length)
        coords.append(_np.array(coord))
    return coords


def _convert_unit(unit_string=None) -> float:
    if not unit_string:
        return 1.0

    if len(unit_string) != 1 and unit_string.lower() != "hz":
        if unit_string[0] in scale_dict:
            return scale_dict[unit_string[0]]

    return 1.0
