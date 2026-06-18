import numpy as _np
from ..core.data import SpinData
from ..core.util import concat
from ._utils import get_default_dim, normalize_region_input

from scipy.integrate import trapezoid as _trapezoid
from scipy.integrate import cumulative_trapezoid as _cumulative_trapezoid


def cumulative_integrate(data, dim=None, regions=None):
    """Cumulative integration

    Args:
        data (SpinData): Data object
        dim (str or None): Dimension to perform cumulative integration. If None,
            the first dimension is used.
        regions (None, list): List of tuples to specify range of integration
            [(min, max), ...]

    Returns:
        data: cumulative sum of data

    Examples:
        Example showing cumulative integration of lorentzian function

        >>> import numpy as np
        >>> import spinlab as sl
        >>> data = sl.load("path/to/data")
        >>> data_int = sl.cumulative_integrate(data)  # integrates along first dim
        >>> sl.plt.figure()
        >>> sl.fancy_plot(data)
        >>> sl.fancy_plot(data_int)
        >>> sl.show()


    """

    out = data.copy()
    dim = get_default_dim(out, dim, "integrate")
    regions = normalize_region_input(regions)

    if regions == None:
        index = out.index(dim)
        out.values = _cumulative_trapezoid(
            out.values, out.coords[dim], axis=index, initial=0
        )

        proc_attr_name = "cumulative_integrate"
        proc_parameters = {
            "dim": dim,
            "regions": regions,
        }
        out.add_proc_attrs(proc_attr_name, proc_parameters)
        return out

    else:
        data_list = []
        for region in regions:
            proc_attr_name = "cumulative_integrate"
            proc_parameters = {
                "dim": dim,
                "regions": regions,
            }
            out.add_proc_attrs(proc_attr_name, proc_parameters)
            data_list.append(cumulative_integrate(out[dim, region], dim))

        return data_list


def integrate(data, dim=None, regions=None):
    """Integrate data along given dimension.

    If no dimension is given, the first dimension is used. If no region is
    given, the integral is calculated over the entire range.

    Args:
        data (SpinData): Data object
        dim (str or None): Dimension to perform integration. If None, the first
            dimension is used.
        regions (None, list): List of tuples defining the region to integrate

    Returns:
        data (SpinData): Integrals of data. If multiple regions are given the first value corresponds to the first region, the second value corresponds to the second region, etc.

    Examples:
        Integrated entire data region:

            >>> data = sl.load("path/to/data")
            >>> integrals = sl.integrate(data)  # integrates along first dim
            >>> integrals = sl.integrate(data, dim='f2')

        Integrate single peak/region:

            >>> data = sl.load("path/to/data")
            >>> integrals = sl.integrate(data, regions=[(4, 5)])

        Integrate two regions:

            >>> data = sl.load("path/to/data")
            >>> integrals = sl.integrate(data, regions=[(1.1, 2.1), (4.5, 4.9)])

    """
    out = data.copy()
    dim = get_default_dim(out, dim, "integrate")
    original_regions = regions
    regions = normalize_region_input(regions)
    proc_regions = (
        tuple(regions)
        if isinstance(original_regions, tuple)
        and len(original_regions) == 2
        and not hasattr(original_regions[0], "__iter__")
        else regions
    )
    out.attrs["experiment_type"] = "integrals"

    index = out.index(dim)
    if regions == None:
        out.values = _trapezoid(out.values, out.coords[dim], axis=index)
        out.coords.pop(dim)

        # if error_regions == None:
        #     out.error = np.zeros(out.shape)
        #     print("add errors")

        # else:
        #     signal = max(out.values)
        #     noise = np.trapz(out.)

    else:
        data_list = []
        for region in regions:
            data_list.append(integrate(out[dim, region], dim))

        x = _np.array(list(range(len(data_list))))
        dim_name = "integrals"
        out = concat(data_list, dim_name, coord=x)

    proc_attr_name = "integrate"
    proc_parameters = {
        "dim": dim,
        "regions": proc_regions,
    }

    out.add_proc_attrs(proc_attr_name, proc_parameters)

    return out
