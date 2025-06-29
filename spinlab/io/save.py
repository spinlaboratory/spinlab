import os
from .h5 import save_h5
from .mat import save_mat
from ..core.data import SpinData


def save(data_object, filename, save_type=None, *args, **kwargs):
    """Save data to h5 format

    Args:
        data_object (SpinData) : sldata object to save
        filename (str): name of file, must include extension .h5
        save_type (str): Type of file to save (optional). Allowed values: "h5"

    Returns:
        none

    """

    if save_type == None:
        save_type = autodetect(filename)

    if save_type == "h5":
        if isinstance(data_object, dict):
            return save_h5(data_object, filename, *args, **kwargs)
        elif isinstance(data_object, SpinData):
            ws = {}
            ws["__SpinDATA__"] = data_object
            return save_h5(ws, filename, *args, **kwargs)
        else:
            raise TypeError(
                "object format not recognized, must be sldata or sldata_collection"
            )
    elif save_type == "mat":
        return save_mat(data_object, filename)

    else:
        raise TypeError("File type not recognized, you must specify a save format")


def autodetect(test_name):
    if test_name[-1] == os.sep:
        test_name = test_name[:-1]

    if os.path.splitext(test_name)[1] == ".h5":
        type = "h5"
    elif os.path.splitext(test_name)[1] == ".mat":
        type = "mat"
    else:
        raise TypeError("File type not recognized, you must specify a save format")

    return type
