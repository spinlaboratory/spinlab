import os

from ..core.data import SpinData
from .formats.h5 import save_h5
from .formats.mat import save_mat

_SAVE_TYPES = {"h5", "mat"}


def _format_names():
    return ", ".join(sorted(_SAVE_TYPES))


def _normalize_save_type(save_type):
    if save_type is None:
        return None
    return str(save_type).strip().lower()


def save(data_object, filename, save_type=None, *args, **kwargs):
    """Save SpinLab data to a supported file format.

    Args:
        data_object (SpinData or dict): Data object or workspace dictionary to save.
        filename (str, PathLike): Output path.
        save_type (str): Save format. If omitted, the format is detected from
            the filename extension. Allowed values are ``h5`` and ``mat``.
        *args: Additional positional arguments passed to the format-specific
            save function.
        **kwargs: Additional keyword arguments passed to the format-specific
            save function.

    Returns:
        None

    Examples:
        >>> sl.save(data, "data.h5", overwrite=True)
        >>> sl.save(data, "data.mat")
    """
    filename = os.fspath(filename)
    save_type = _normalize_save_type(save_type)
    if save_type is None:
        save_type = _detect_save_format(filename)

    if save_type == "h5":
        if isinstance(data_object, SpinData):
            data_object = {"__SpinDATA__": data_object}
        elif not isinstance(data_object, dict):
            raise TypeError(
                "object format not recognized, must be SpinData or a dictionary of SpinData objects"
            )
        return save_h5(data_object, filename, *args, **kwargs)

    if save_type == "mat":
        return save_mat(data_object, filename, *args, **kwargs)

    raise TypeError(
        "File type not recognized. Allowed values are: {0}".format(_format_names())
    )


def _detect_save_format(test_name):
    """Detect the save format from the file extension.

    Args:
        test_name (str, PathLike): File path or name including extension.

    Returns:
        str: Detected format string, such as ``"h5"`` or ``"mat"``.

    Raises:
        TypeError: If the extension is not recognized.
    """
    test_name = os.path.normpath(os.fspath(test_name))
    test_name = test_name.rstrip("/\\") or test_name
    extension = os.path.splitext(test_name)[1].lower()

    if extension == ".h5":
        return "h5"
    if extension == ".mat":
        return "mat"

    raise TypeError(
        "File type not recognized. Allowed values are: {0}".format(_format_names())
    )
