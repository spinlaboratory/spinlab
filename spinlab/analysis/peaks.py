import numpy as _np
import scipy.signal as _spsig
from ..core.util import concat, update_axis
from .._utils import (
    evenly_spaced_coord_spacing,
    get_default_dim,
    normalize_region_input,
    validate_coord_matches_dim,
)

__all__ = ["find_peaks", "peak_info"]


def _get_linewidth_frequency(data):
    if "frequency" in data.spinlab_attrs:
        return data.spinlab_attrs["frequency"]
    if "nmr_frequency" in data.attrs:
        return data.attrs["nmr_frequency"]
    raise ValueError(
        "Frequency not found. Peak width conversion requires "
        'spinlab_attrs["frequency"] or attrs["nmr_frequency"].'
    )


def _region_indices(coord, regions):
    if regions is None:
        return [_np.arange(coord.size)]

    index_list = []
    all_indices = _np.arange(coord.size)
    for region in regions:
        if isinstance(region, slice):
            index_list.append(all_indices[region])
        elif isinstance(region, tuple) and len(region) == 1:
            index_list.append(_np.array([int(_np.argmin(_np.abs(coord - region[0])))]))
        else:
            start, stop = region
            low = min(start, stop)
            high = max(start, stop)
            index_list.append(all_indices[(coord >= low) & (coord <= high)])

    return [indices for indices in index_list if indices.size > 0]


def _normalize_peak_values(values, indices):
    if indices.size == 0:
        return values.copy()

    normalized_values = values.copy()
    selected_values = normalized_values[indices]
    factor = _np.max(_np.abs(selected_values))
    if factor != 0:
        normalized_values = normalized_values / factor

    real_array = normalized_values[indices].real
    max_value = _np.max(real_array)
    min_value = _np.min(real_array)
    if _np.abs(max_value) < _np.abs(min_value):
        normalized_values *= -1

    return normalized_values


def find_peaks(
    data,
    dims=None,
    normalize=True,
    regions=None,
    height=0.5,
    threshold=None,
    distance=None,
    prominence=None,
    width=None,
    wlen=None,
    rel_height=0.5,
    plateau_size=None,
    *,
    dim=None,
):
    """Find peaks in spectrum

    Find peaks in spectrum (SpinData object) and return peak index, peak
    coordinate, peak height, peak width (Hz), and peak width height. The
    function uses the SciPy functions ``find_peaks`` and ``peak_widths``.

    Args:
        data (SpinData):                         Data object
        dims (str or None):                     Dimension to find peaks. If
                                                None, the first dimension is
                                                used. ``dim`` is accepted as a
                                                clearer keyword alias.
        regions (None, list):                   List of tuples defining the region to find peaks
        normalize (boolean):                    Normalize data to a maximum value of 1. Default is True
        height (float or numpy.array):          Optionally, height of peaks. If an array is supplied, the first element is minimum and the second is maximum
        threshold (float or numpy.array):       Optionally, threshold of minimum peak height to be counted. If an array is supplied, the first element is minimum and the second is maximum
        distance (float):                       Optionally, minimal horizontal distance in samples between peaks. Smaller peaks are removed first until the condition is fulfilled for all remaining peaks.
        prominence (float or numpy.array):      Optionally, prominence of peaks. If an array is supplied, the first element is minimum and the second is maximum
        width (float or numpy.array):           Optionally, width of peaks. If an array is supplied, the first element is minimum and the second is maximum
        wlen (int):                             Optionally, for calculating the peaks prominences. Only valid if prominence is given
        rel_height (float):                     Optionally, relative height at which peak width is measured. Default is 0.5 for FWHH
        plateau_size (float or numpy.array):    Optionally, size of the flat top of peaks in samples. If an array is supplied, the first element is minimum and the second is maximum
        peak_info (boolean):                    If True print output to terminal

    Returns:
        data (SpinData):         Array of peak index, peak coordinate, peak
                                  height, peak width and relative peak height.
                                  The linewidth is returned in Hz using
                                  ``spinlab_attrs["frequency"]`` or the legacy
                                  ``attrs["nmr_frequency"]``.

    Examples:
        Find peaks in entire data region:

            >>> data = sl.load("path/to/data")
            >>> peak_list = sl.find_peaks(data)

        Find peaks with an amplitude > 0.01 (after normalization):

            >>> peak_list = sl.find_peaks(data, height=0.05)

        Find peaks with an amplitude > 500 (data not normalized):

            >>> peak_list = sl.find_peaks(data, height=500, normalize=False)

    """

    if dim is not None:
        if dims is not None:
            raise ValueError("Use either dims or dim, not both.")
        dims = dim
    dims = get_default_dim(data, dims, "find peaks in")
    regions = normalize_region_input(regions)

    if len(data.dims) == 2:
        data_list = []
        second_dim = [data_dim for data_dim in data.dims if data_dim != dims][0]
        second_coord = data.coords[second_dim]
        for i in range(len(second_coord)):
            sub_data = data[second_dim, i].sum(second_dim)
            data_list.append(
                find_peaks(
                    sub_data,
                    dims=dims,
                    normalize=normalize,
                    regions=regions,
                    height=height,
                    threshold=threshold,
                    distance=distance,
                    prominence=prominence,
                    width=width,
                    wlen=wlen,
                    rel_height=rel_height,
                    plateau_size=plateau_size,
                )
            )

        # data_list, second_coord = _peak_list_checker(
        #     data_list, second_coord, second_dim
        # )

        return concat(data_list, dim=second_dim, coord=second_coord, casting="unsafe")

    elif len(data.dims) == 1:
        out = data.copy()
        out.attrs["experiment_type"] = "peak_list"
        out.attrs["data_type"] = "peak_list"

        coords = validate_coord_matches_dim(out, dims)
        resolution = abs(evenly_spaced_coord_spacing(coords, dims, "find peaks"))
        frequency = _get_linewidth_frequency(out)

        region_indices = _region_indices(coords, regions)
        normalized_indices = (
            _np.concatenate(region_indices)
            if region_indices
            else _np.array([], dtype=int)
        )
        peak_values_for_detection = out.values
        if normalize is True:
            peak_values_for_detection = _normalize_peak_values(
                peak_values_for_detection, normalized_indices
            )

        peak_index_list = []
        peak_width_list = []
        peak_width_height_list = []
        for indices in region_indices:
            segment_values = peak_values_for_detection[indices].real
            segment_peak_index, _ = _spsig.find_peaks(
                segment_values,
                height=height,
                threshold=threshold,
                distance=distance,
                prominence=prominence,
                width=width,
                wlen=wlen,
                rel_height=rel_height,
                plateau_size=plateau_size,
            )
            segment_peak_width_height = _spsig.peak_widths(
                segment_values, peaks=segment_peak_index, rel_height=rel_height
            )
            peak_index_list.append(indices[segment_peak_index])
            peak_width_list.append(
                segment_peak_width_height[0] * resolution * 1e-6 * frequency
            )
            peak_width_height_list.append(segment_peak_width_height[1])

        peak_index = (
            _np.concatenate(peak_index_list)
            if peak_index_list
            else _np.array([], dtype=int)
        )
        peak_width = (
            _np.concatenate(peak_width_list)
            if peak_width_list
            else _np.array([], dtype=float)
        )
        peak_width_height = (
            _np.concatenate(peak_width_height_list)
            if peak_width_height_list
            else _np.array([], dtype=float)
        )
        peak_values = data.values.real[peak_index]
        peak_shift = coords[peak_index]

        out.values = _np.vstack(
            (peak_index, peak_shift, peak_values, peak_width, peak_width_height)
        )

        out = update_axis(
            out, dim=0, new_dims="peak_info", start_stop=(0, len(out.values) - 1)
        )
        out.coords.append(dim="index", coord=_np.arange(0, len(peak_index), 1))

        proc_attr_name = "peak_list"
        proc_parameters = {
            "dims": dims,
            "normalize": normalize,
            "regions": regions,
            "height": height,
            "threshold": threshold,
            "distance": distance,
            "prominence": prominence,
            "width": width,
            "wlen": wlen,
            "rel_height": rel_height,
            "plateau_size": plateau_size,
        }

        out.add_proc_attrs(proc_attr_name, proc_parameters)

        return out

    else:
        raise ValueError("The function only works with 1d or 2d datasets")


def peak_info(data):
    """
    Print peak list in human readable form

    Function to print the peak list in a human readable form. You first have to run find_peaks to create a sldata object that includes a peak list.

    Args:
        data (SpinData):     SpinData object created by find_peaks

    Returns:
        Output (str):       Peak list table
    """

    if data.attrs.get("experiment_type") != "peak_list":
        print("Peak list required as input")
        return

    if len(data.dims) == 3:
        dim = data.dims[-1]
        coord = data.coords[dim]
        for i in range(len(coord)):
            sub_data = data[dim, i].sum(dim)
            print("Dim: %s, Dim Index: %d, Dim Value: %0.01f" % (dim, i, coord[i]))
            print("--------------------------------------------")
            peak_info(sub_data)

    elif len(data.dims) == 2:
        for peak_number in range(len(data.coords["index"])):
            values = data["index", peak_number].sum("index").values
            if any(_np.isnan(values)):
                print("Peak #%d Information Not Available." % (peak_number + 1))
            else:
                print(
                    "Peak #%d: Index: %5d, Shift (ppm): %0.02f, Height : %4.2f, Width (Hz): %4.2f, Width Height: %2.2f"
                    % (
                        peak_number + 1,
                        values[0],
                        values[1],
                        values[2],
                        values[3],
                        values[4],
                    )
                )
        print("--------------------------------------------")
    else:
        raise ValueError("The function only works with peak lists from 1d or 2d datasets")


def _peak_list_checker(peak_list, coord, dim):
    """
    Check peak list before concat. It will remove the inconsistent peak data from list.

    Args:
        peak_list (list): list of peak data
        coord (numpy.array): an array of coord
        dim (str): the dim for concat

    Returns:
        new_peak_list (list): concat-able list of peak data
        new_coord (numpy.array): a new array of coord
    """

    ref = peak_list[-1]
    ref_shape = _np.shape(ref)
    new_peak_list = [peak for peak in peak_list if _np.shape(peak) == ref_shape]
    new_coord = _np.array(
        [
            coord[i]
            for i in range(len(peak_list))
            if _np.shape(peak_list[i]) == ref_shape
        ]
    )

    if new_peak_list != peak_list:
        print("In dim %s, the following datasets are removed." % dim)
        for i in range(len(peak_list)):
            if peak_list[i] not in new_peak_list:
                print(
                    "Index: %i, Value: %0.01f, Number of Peaks Found: %i"
                    % (i, coord[i], len(peak_list[i].coords[1]))
                )

    return new_peak_list, new_coord
