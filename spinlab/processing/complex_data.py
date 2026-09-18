import numpy as _np
import warnings as _warnings

from ..core.data import SpinData


def _create_complexEXT(data, real, imag):
    """Combine separate real and imaginary arrays into a complex SpinData object.

    Internal helper called by :func:`create_complex` when explicit real and
    imaginary arrays are passed. The last dimension of ``data`` is removed
    from the output object.

    Args:
        data (SpinData): Template SpinData object whose dims and coords are used
            for the output (last dimension is dropped).
        real (numpy.ndarray): Array of real values.
        imag (numpy.ndarray): Array of imaginary values.

    Returns:
        SpinData: Complex SpinData object with the last dimension removed.
    """
    complexData = _np.vectorize(complex)(real, imag)

    dims = data.dims.copy()
    dims.pop(-1)

    coords = list(data.coords)
    coords.pop(-1)

    attrs = data.attrs

    out = SpinData(complexData, dims, coords, attrs)

    return out


def _create_complexINT(sldata, dim, real=0, imag=1):
    """Combine two slices of a SpinData dimension into a single complex dataset.

    Internal helper called by :func:`create_complex` when a dimension name is
    passed as the ``real`` argument. The specified dimension must have length 2
    (or the ``real`` and ``imag`` index arguments must address valid slices).
    The source dimension is collapsed and removed from the output.

    Args:
        sldata (SpinData): Input SpinData object containing both real and
            imaginary parts along ``dim``.
        dim (str): Name of the dimension containing the real and imaginary parts.
        real (int): Index of the real part along ``dim``. Default is ``0``.
        imag (int): Index of the imaginary part along ``dim``. Default is ``1``.

    Returns:
        SpinData: Complex SpinData object with ``dim`` collapsed.
    """
    try:
        if len(sldata.coords[dim]) != 2:
            _warnings.warn(
                "Dim {} has length > 2 ({}), use real and imag keywords! Not used elements are discarded."
            )
    except KeyError:
        raise KeyError(
            "dim {} not in dims of slDataobject, available dims are: {1}".format(
                dim, sldata.dims
            )
        )
    out = sldata.copy()
    out._values = out._values.astype(complex)
    cut_position = 0
    for k in out.dims:
        if k == dim:
            break
        cut_position = cut_position + 1
    out[dim, 0] = out[dim, real]._values + 1j * out[dim, imag]._values
    axis_int = 0
    for k in sldata.dims:
        if k == dim:
            break
        axis_int = axis_int + 1
    out._values = _np.delete(
        out._values, slice(1, None, None), axis=axis_int
    )  # list(range(out.shape[axis_int]))
    out.coords[dim] = _np.array([0])

    shape = out.shape
    restore_dims = [
        out.dims[x] for x in range(len(shape)) if (shape[x] == 1) and out.dims[x] != dim
    ]
    restore_dims_index = [
        x for x in range(len(shape)) if (shape[x] == 1) and out.dims[x] != dim
    ]
    restore_coords = [out.coords[k][0] for k in restore_dims]  # have length 1
    dims_position = []
    restored_dim_order = []
    i = 0
    for ind, k in enumerate(out.dims):
        if k in restore_dims and ind < cut_position:
            dims_position.append(ind)
        if k in restore_dims and ind > cut_position:
            dims_position.append(ind - 1)

        # save indices for old dimensions
        if ind in restore_dims_index:
            restored_dim_order.append(
                len(shape) - len(restore_dims) - 1 + i
            )  # -1 from the removed complex axis and -1 because counting starts from 0
            i = i + 1
        elif ind < cut_position:
            restored_dim_order.append(ind)
        elif ind > cut_position:
            restored_dim_order.append(ind - 1 - i)

    # remove the single dimensions, including the complex source
    out.squeeze()

    # move single dimensions back to position
    move_dims = 0
    for d, c in zip(restore_dims, restore_coords):
        out.new_dim(d, c)
        move_dims = move_dims + 1
    # move back to old position...
    out._values = _np.moveaxis(
        out._values, [k for k in range(-move_dims, 0, 1)], dims_position
    )
    out.coords.reorder_index(restored_dim_order)

    return out


def create_complex(data, real, imag=None, real_index=0, imag_index=1):
    """Create complex array from input

    This function can be used to concatenate a two dimensions of a SpinData object into a complex array. The unused dims and coords will be removed from the input SpinData object.
    When a String is provided as the second argument the index in that dimension given by real_index is assumed to be the real part of the dataset and the one by imag_index is the imaginary part.
    The dataset is then combined to form one complex dataset, imag is ignored. Note that dimension with size 1 are retained but will be placed at the end of the retuned SpinData object.

    Args:
        data (SpinData): SpinData input object
        real (array, String): Real data if array or when a String is provided the dimension that contains real and imaginary part (the dimension must have length 2)
        imag (array, None): Imaginary data or None, if None is provided a complex dataset is created with the imaginary part set to 0
        real_index (Integer): Index of real part in chosen dimension, default=0, must be 0 or 1 and be different from imag_index
        imag_index (Integer): Index of imaginary part in chosen dimension, default=1, must be 0 or 1 and be different from real_index

    Returns:
        data (SpinData): New SpinData object

    Examples:
        In this example, first a data set is loaded. The data set is of the size 4000 x 2 (ndarray, float32) and the dims are called 't2','x'

        With the first dimension ([...,0]) being the real data and the second ([...,1]) the imaginary data. Using the function create_complex the sldata object is converted into a complex data set.

        .. code-block:: python

            data = sl.load("path/to/data")
            data_complex = sl.create_complex(data, data.values[..., 0], data.values[..., 1])

        Or with the second variant;

        .. code-block:: python

            data = sl.load("path/to/data")
            data_complex = sl.create_complex(data, "x")


    """
    if isinstance(real, str):
        dim = real
        return _create_complexINT(data, dim, real=real_index, imag=imag_index)
    if imag is None:
        imag = _np.zeros(real.shape)
    return _create_complexEXT(data, real, imag)
