"""Save and load MATLAB ``.mat`` files."""

import ast
import os

import numpy as np
from scipy.io import loadmat, savemat

from ...core.data import SpinData
from .._verbose import verbose_data_summary, verbose_print


def save_mat(data, path, **kwargs):
    """Save a SpinData object as a MATLAB ``.mat`` file.

    Args:
        data (SpinData): Data object to save.
        path (str, PathLike): Output file path.
        **kwargs: Additional keyword arguments passed to ``scipy.io.savemat``.

    Examples:
        >>> sl.save(data, "data.mat")
    """
    if not isinstance(data, SpinData):
        raise TypeError("save_mat expects a SpinData object")

    matlab_dict = {
        "values": data.values,
        "dims": np.asarray(data.dims, dtype=object),
        "coords": np.asarray(data.coords.coords, dtype=object),
        "attrs": repr(data.attrs),
        "spinlab_attrs": repr(data.spinlab_attrs),
        "proc_attrs": repr(data.proc_attrs).replace("None", "'__PYTHON_NONE__'"),
    }

    savemat(os.fspath(path), matlab_dict, **kwargs)


def import_mat(path, verbose=False):
    """Import a MATLAB ``.mat`` file saved by SpinLab.

    Args:
        path (str, PathLike): Path to a ``.mat`` file.

    Returns:
        SpinData: Imported data object.

    Examples:
        >>> data = sl.load("data.mat")
    """
    path = os.fspath(path)
    if os.path.splitext(path.rstrip("/\\"))[1].lower() != ".mat":
        raise TypeError("Incorrect file type, must be .mat")

    mat_data = loadmat(path, squeeze_me=True, chars_as_strings=True)
    verbose_print(verbose, "MAT file:", path)
    verbose_print(
        verbose,
        "MAT keys:",
        [key for key in mat_data.keys() if not key.startswith("__")],
    )
    values = _get_values(mat_data)
    shape = np.shape(values)
    dims = _get_dims(mat_data, shape)
    coords = _get_coords(mat_data, shape)
    attrs = _get_attrs(mat_data, "attrs")
    spinlab_attrs = _get_attrs(mat_data, "spinlab_attrs")
    proc_attrs = _get_proc_attrs(mat_data)

    data = SpinData(
        values=values,
        dims=dims,
        coords=coords,
        attrs=attrs,
        spinlab_attrs=spinlab_attrs,
        proc_attrs=proc_attrs,
    )
    verbose_data_summary(verbose, "MAT", data)
    return data


def _get_values(data):
    if "values" not in data:
        raise KeyError("MAT file does not contain a 'values' entry")
    return data["values"]


def _get_dims(data, shape):
    dims = data.get("dims")
    if dims is None:
        return ["X%i" % (i + 1) for i in range(len(shape))]

    dims = _flatten_loaded_object(dims)
    if len(dims) == 1 and len(shape) != 1:
        dims = ["X%i" % (i + 1) for i in range(len(shape))]
    return [str(dim) for dim in dims]


def _get_coords(data, shape):
    coords = data.get("coords")
    if coords is None:
        return [np.arange(size) for size in shape]

    coords = _flatten_loaded_object(coords)
    coords = [np.asarray(coord).reshape(-1) for coord in coords]
    if len(coords) != len(shape):
        return [np.arange(size) for size in shape]
    return coords


def _get_attrs(data, key):
    value = data.get(key)
    if value is None:
        return {}
    try:
        parsed = ast.literal_eval(str(value))
    except (SyntaxError, ValueError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _get_proc_attrs(data):
    value = data.get("proc_attrs")
    if value is None:
        return []
    try:
        parsed = ast.literal_eval(str(value).replace("__PYTHON_NONE__", "None"))
    except (SyntaxError, ValueError):
        return []
    return parsed if isinstance(parsed, list) else []


def _flatten_loaded_object(value):
    value = np.asarray(value, dtype=object)
    if value.ndim == 0:
        return [value.item()]
    return value.reshape(-1).tolist()
