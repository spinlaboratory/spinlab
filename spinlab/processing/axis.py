def left_shift(data, dim="t2", shift_points=0):
    """Remove points from the left

    Args:
        data (SpinData): Data object
        dim (str): Name of dimension to left shift, default is "t2"
        shift_points (int): Number of points to left shift, default is 0.

    Returns:
        data (SpinDdata): Shifted data object

    Examples:
        >>> data = sl.load("path/to/data")
        >>> shifted = sl.left_shift(data, dim="t2", shift_points=8)
    """

    out = data.copy()

    out = out[dim, shift_points:]

    proc_attr_name = "left_shift"
    proc_parameters = {
        "dim": dim,
        "points": shift_points,
    }
    out.add_proc_attrs(proc_attr_name, proc_parameters)

    return out


def reference(data, dim="f2", old_ref=0, new_ref=0):
    """Function for referencing NMR spectra

    Args:
        data (SpinData): Data for referencing
        dim (str): dimension to perform referencing down. By default this dimension is "f2".
        old_ref (float): Value of old reference
        new_ref (float): New reference value

    Returns:
        SpinData: referenced data

    Examples:
        >>> data = sl.load("path/to/data")
        >>> referenced = sl.reference(data, dim="f2", old_ref=7.26, new_ref=0.0)
    """

    out = data.copy()

    out.coords[dim] -= old_ref - new_ref

    proc_attr_name = "reference"
    proc_parameters = {
        "dim": dim,
        "old_ref": old_ref,
        "new_ref": new_ref,
    }
    out.add_proc_attrs(proc_attr_name, proc_parameters)

    return out
