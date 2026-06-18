import numpy as _np
from ..core.data import SpinData


def _get_align_dim(data, dim):
    if dim is None:
        if len(data.dims) == 0:
            raise ValueError("Cannot align data without dimensions.")
        return data.dims[0]
    return dim


def _alignment_range(coord, center, width):
    if center is not None and width is not None:
        if width <= 0:
            raise ValueError("width must be positive")
        if coord[0] <= coord[-1]:
            return center - 0.5 * width, center + 0.5 * width
        return center + 0.5 * width, center - 0.5 * width
    if center is None and width is None:
        return coord[0], coord[-1]
    raise ValueError("center and width must be supplied together")


def _prepare_reference(reference, coord, selected_coord, dim):
    if reference is None:
        return None

    if isinstance(reference, SpinData):
        if dim in reference.dims:
            reference_coord = reference.coords[dim]
            reference_values = _np.asarray(reference.values).ravel()
            if reference_coord.size == selected_coord.size:
                reference = reference_values
            elif reference_coord.size == coord.size:
                mask = _np.isin(reference_coord, selected_coord)
                reference = reference_values[mask]
            else:
                reference = reference_values
        else:
            reference = reference.values

    reference = _np.asarray(reference).ravel()
    if reference.size == selected_coord.size:
        return _np.abs(reference)

    if reference.size == coord.size:
        mask = _np.isin(coord, selected_coord)
        return _np.abs(reference[mask])

    raise ValueError(
        "reference length must match the selected alignment range or the full alignment dimension"
    )


def ndalign(data, dim=None, reference=None, center=None, width=None):
    """Align spectra using direct cross correlation.

    Args:
        data (SpinData): Data object.
        dim (str or None): Dimension to align along. If None, the first
            dimension is used.
        reference (array_like or SpinData): Reference spectrum for alignment.
            If None, the last spectrum along the unfolded data is used.
        center (float): Center of alignment range. If None, the entire
            dimension is used.
        width (float): Width of alignment range. Must be supplied together with
            center.

    Returns:
        SpinData: Aligned data

    .. Note::

        Shifts are calculated relative to the supplied reference, then adjusted
        relative to the first spectrum in the unfolded data. This preserves the
        first spectrum's position while aligning the remaining spectra to it.

    Examples:

        >>> data = sl.load("path/to/data")
        >>> data_aligned = sl.ndalign(data)
        >>> data_aligned = sl.ndalign(data, center = 10, width = 20)
    """

    out = data.copy()
    dim = _get_align_dim(out, dim)
    coord = out.coords[dim]
    start, stop = _alignment_range(coord, center, width)
    lower = min(start, stop)
    upper = max(start, stop)
    if not _np.any((coord >= lower) & (coord <= upper)):
        raise ValueError("selected alignment range contains no points")

    proc_parameters = {
        "dim": dim,
        "reference": None if reference is None else type(reference).__name__,
        "reference_shape": (
            None
            if reference is None
            else (
                reference.shape
                if isinstance(reference, SpinData)
                else _np.shape(reference)
            )
        ),
        "center": center,
        "width": width,
    }

    temp_out = out[dim, (start, stop)].copy()
    if temp_out.coords[dim].size == 0:
        raise ValueError("selected alignment range contains no points")

    temp_out.unfold(dim)
    temp_values = temp_out.values.T

    out.unfold(dim)
    all_values = out.values.T

    abs_temp_values = _np.abs(temp_values)
    selected_coord = temp_out.coords[dim]

    if reference is None:
        reference = _np.abs(temp_values[-1])
    else:
        reference = _prepare_reference(reference, coord, selected_coord, dim)

    ref_max_ix = _np.argmax(reference)

    aligned_all_values = _np.zeros_like(all_values)

    for ix in range(len(abs_temp_values)):
        cor = _np.correlate(
            abs_temp_values[ix], reference, mode="same"
        )  # calculate cross-correlation
        max_ix = _np.argmax(cor)  # Maximum of cross correlation
        delta_max_ix = max_ix - ref_max_ix  # Calculate how many points to shift
        if ix == 0:
            first_shift = delta_max_ix
        delta_max_ix -= first_shift
        aligned_all_values[ix] = _np.roll(
            all_values[ix], -1 * delta_max_ix
        )  # shift values

    out.values = aligned_all_values.T  # Add aligned values back to data object

    out.fold()  # Back to original order

    proc_attr_name = "ndalign"
    out.add_proc_attrs(proc_attr_name, proc_parameters)

    return out
