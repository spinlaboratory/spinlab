import os

from ..core.util import concat
from ._attrs import _assign_spinlab_attrs
from .auxiliary import cnsi, power
from .formats import bes3t, delta, h5, mat, prospa, rs2d, specman, tnmr, topspin, vna
from .formats import vnmrj, winepr

_LOADERS = {
    "prospa": prospa.import_prospa,
    "topspin": topspin.import_topspin,
    "topspin pdata": topspin.load_pdata,
    "delta": delta.import_delta,
    "vnmrj": vnmrj.import_vnmrj,
    "tnmr": tnmr.import_tnmr,
    "specman": specman.import_specman,
    "xepr": bes3t.import_bes3t,
    "xenon": bes3t.import_bes3t,
    "winepr": winepr.import_winepr,
    "esp": winepr.import_winepr,
    "h5": h5.load_h5,
    "mat": mat.import_mat,
    "power": power.import_power,
    "vna": vna.import_vna,
    "cnsi_powers": cnsi.get_powers,
    "rs2d": rs2d.import_rs2d,
}

_SKIP_SPINLAB_ATTRS = {"h5", "mat", "power", "vna", "cnsi_powers"}


def _format_names():
    return ", ".join(sorted(_LOADERS))


def _normalize_path(path):
    path = os.path.normpath(os.fspath(path))
    if os.path.isdir(path) and not path.endswith(os.sep):
        path += os.sep
    return path


def _normalize_data_format(data_format):
    if data_format is None:
        return None
    return str(data_format).strip().lower()


def load(path, data_format=None, dim=None, coord=None, verbose=False, *args, **kwargs):
    """Import data from a file, directory, or list of paths.

    Args:
        path (str, PathLike, list): Path to data or list of paths to concatenate.
        data_format (str): Format to import. If omitted, the format is detected
            from the path. Allowed values include ``prospa``, ``topspin``,
            ``delta``, ``vnmrj``, ``tnmr``, ``specman``, ``xenon``, ``xepr``,
            ``winepr``, ``esp``, ``h5``, ``mat``, ``power``, ``vna``,
            ``cnsi_powers``, and ``rs2d``.
        dim (str): Name of the concatenation dimension when ``path`` is a list.
        coord (array-like): Coordinates for the concatenation dimension.
        verbose (bool): If True, print debugging output.
        *args: Additional positional arguments passed to the format-specific
            import function.
        **kwargs: Additional keyword arguments passed to the format-specific
            import function.

    Returns:
        SpinData: Loaded data object.

    Examples:
        >>> data = sl.load("path/to/file")
        >>> data = sl.load(
        ...     ["1/data.1d", "2/data.1d", "3/data.1d"],
        ...     dim="t1",
        ...     coord=[0.1, 0.2, 0.3],
        ... )
    """
    if isinstance(path, (list, tuple)):
        if coord is not None and len(coord) == 0:
            coord = None
        if coord is not None and len(coord) != len(path):
            raise ValueError(
                "coord must be a list or array equal in len to the number of paths given"
            )

        if dim is None:
            dim = "unnamed"

        data_list = [
            _load_file(
                filename, data_format=data_format, verbose=verbose, *args, **kwargs
            )
            for filename in path
        ]

        return concat(data_list, dim=dim, coord=coord)

    return _load_file(path, data_format=data_format, verbose=verbose, *args, **kwargs)


def _load_file(path, data_format=None, verbose=False, *args, **kwargs):
    """Import one data file or directory.

    Args:
        path (str, PathLike): Path to data directory or file.
        data_format (str): Format to import. If omitted, the format is detected
            from the path.
        verbose (bool): If True, print additional debug output for importers
            that support it.
        *args: Additional positional arguments passed to the format-specific
            import function.
        **kwargs: Additional keyword arguments passed to the format-specific
            import function.

    Returns:
        SpinData: Loaded data object.
    """
    path = _normalize_path(path)
    data_format = _normalize_data_format(data_format)
    if data_format is None:
        data_format = _detect_load_format(path, verbose=verbose)

    try:
        loader = _LOADERS[data_format]
    except KeyError as exc:
        raise ValueError(
            "Invalid data format: {0}. Allowed values are: {1}".format(
                data_format, _format_names()
            )
        ) from exc

    data = loader(path, *args, verbose=verbose, **kwargs)

    if data_format not in _SKIP_SPINLAB_ATTRS:
        data = _assign_spinlab_attrs(data, data_format)

    return data


def _detect_load_format(test_path, verbose=False):
    """Detect the load format from a path.

    Args:
        test_path (str, PathLike): Path to detect.
        verbose (bool): If True, print detection details.

    Returns:
        str: Detected format name.

    Raises:
        TypeError: If the format cannot be detected.
    """
    test_path = os.path.normpath(os.fspath(test_path))
    test_path = test_path.rstrip("/\\") or test_path

    if verbose:
        print("current directory:", os.getcwd())
        print("data path:", test_path)
        print("absolute path:", os.path.abspath(test_path))

    path_exten = os.path.splitext(test_path)[1].lower()
    if path_exten and verbose:
        print("Extension:", path_exten)

    if path_exten in [".dsc", ".dta", ".ygf"]:
        data_format = "xepr"
    elif path_exten in [".par", ".spc"]:
        data_format = "winepr"
    elif path_exten in [".d01", ".exp"]:
        data_format = "specman"
    elif path_exten == ".jdf":
        data_format = "delta"
    elif os.path.isdir(test_path) and (
        "acqu" in os.listdir(test_path) or "acqus" in os.listdir(test_path)
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
    elif path_exten == ".mat":
        data_format = "mat"
    else:
        raise TypeError(
            "No data format given and autodetect failed to detect format, please specify a format"
        )

    if verbose:
        print("Data Format:", data_format)

    return data_format
