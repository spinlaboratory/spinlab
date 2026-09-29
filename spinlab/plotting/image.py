import matplotlib.pyplot as _plt
import numpy as _np


def imshow(data, *args, **kwargs):  # TODO: drop unused args and kwargs
    """Image Plot for sldata object

    Args:
        data (SpinData): SpinData object for image plot
        *args: Additional positional arguments passed to the Matplotlib imshow function.
        **kwargs: Additional keyword arguments passed to the Matplotlib imshow function.

    Returns:
        AxesImage: Matplotlib image object returned by ``imshow``.

    Examples:

       Plotting a sldata object

       >>> sl.plt.figure()
       >>> sl.imshow(data)
       >>> sl.plt.show()

       Plotting a workspace (sldata_collection)

       >>> sl.plt.figure()
       >>> sl.imshow(data)
       >>> sl.plt.show()
    """

    dims = data.dims

    x_coord = data.coords[dims[1]]
    y_coord = data.coords[dims[0]]

    if "origin" in kwargs:
        origin = kwargs["origin"]
        kwargs.pop("origin")
    else:
        origin = "lower"

    x_min = _np.min(x_coord)
    x_max = _np.max(x_coord)

    if origin == "upper":
        y_min = _np.min(y_coord)
        y_max = _np.max(y_coord)
    else:
        y_min = _np.max(y_coord)
        y_max = _np.min(y_coord)

    if "aspect" in kwargs:
        aspect = kwargs["aspect"]
        kwargs.pop("aspect")
    else:
        aspect = "auto"

    if "extent" in kwargs:
        extent = kwargs["extent"]
        kwargs.pop("extent")
    else:
        extent = [x_min, x_max, y_max, y_min]

    image = _plt.imshow(
        data.values, *args, aspect=aspect, extent=extent, origin=origin, **kwargs
    )
    _plt.xlabel(dims[1])
    _plt.ylabel(dims[0])
    return image
