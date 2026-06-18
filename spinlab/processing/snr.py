import numpy as _np

from ..core.data import SpinData
from ..processing.offset import remove_background as _sl_remove_background


def signal_to_noise(
    data: SpinData,
    signal_region: list = slice(0, None),
    noise_region: list = (None, None),
    dim: str = "f2",
    remove_background: list = None,
    complex_noise=False,
    **kwargs,
):
    """Find signal-to-noise ratio

    Simplest implementation: select largest value in a signal_region and divide this value by the estimated std. deviation of another noise_region. If the noise_region list contains (None,None) (the default) then all points except the points +10% and -10% around the maximum are used for the noise_region.

    Args:
        data: Spectrum data
        signal_region (list): list with a single tuple (start,stop) of a region where a signal should be searched, default is [slice(0,None)] which is the whole spectrum
        noise_region (list): list with tuples (start,stop) of regions that should be taken as noise, default is (None,None)
        dim (str): dimension of data that is used for snr calculation, default is 'f2'
        remove_background (list): if this is not None (a list of tuples, or a single tuple) this will be forwarded to sl.remove_background, together with any kwargs
        complex_noise (bool): Flag that indicates whether the noise should be calculated on the real part of the noise or on the complex data (default = False)
        kwargs : parameters for sl.remove_background

    Returns:
        SNR (SpinData): SpinData object that contains SNR values, the axis dim is replaced by an axis named "signal_region"

    Examples:

        Regions can be provided as ``(min, max)`` tuples; slices use indices.

        >>> data = sl.load("path/to/data")
        >>> snr = sl.signal_to_noise(data, signal_region=(-1, 1), noise_region=[(8, 10)])
        >>> snr = sl.signal_to_noise(
        ...     data,
        ...     signal_region=(-1, 1),
        ...     noise_region=[(8, 10)],
        ...     remove_background=[(8, 10)],
        ... )

    """

    # convenience for signal and noise region
    def _convenience_tuple_to_list(possible_region: list):
        if possible_region is None:
            return possible_region
        # we assume its iterable
        try:
            l = len(possible_region)
            if l != 2:
                return possible_region  # it seems to be iterable?
        except TypeError:
            return [possible_region]  # return as is in a list, might be slice
        try:
            # check whether we can interpret it as value
            int(possible_region[0])
            return [
                (possible_region[0], possible_region[1])
            ]  # make a list that contains a tuple
        except TypeError:
            if type(possible_region) == list:
                return possible_region
            return [possible_region]

    signal_region = _convenience_tuple_to_list(signal_region)
    if len(signal_region) > 1:
        snr = []
        for sr in signal_region:
            snr.append(
                _np.squeeze(
                    signal_to_noise(
                        data, sr, noise_region, dim, remove_background, **kwargs
                    )._values
                )
            )

        # return SpinData object with dims: signal_region and all other dimensions copied from data
        dims = ["signal_region" if x == dim else x for x in data.dims]
        coords_new = [
            _np.arange(len(signal_region)) if x == dim else data.coords[x]
            for x in data.dims
        ]
        data_new = _np.array(snr)
        snrData = SpinData(data_new, dims, coords_new)
        return snrData

    noise_region = _convenience_tuple_to_list(noise_region)
    remove_background = _convenience_tuple_to_list(remove_background)

    if not (dim in data.dims):
        raise ValueError("dim {0} not in data.dims ({1})".format(dim, data.dims))

    # remove background
    if remove_background is not None:
        deg = kwargs.pop("deg", 1)
        data = _sl_remove_background(data, dim, deg, remove_background)

    # unfold and calculate snr for each fold_index
    sdata = data
    sdata.unfold(dim)

    # currently only absolute value comparison
    signal = []
    for indx in range(sdata.shape[1]):
        signal.append(
            _np.max(_np.abs(sdata[dim, signal_region[0], "fold_index", indx]))
        )

    # now calculate noise
    noise = []
    for indx in range(sdata.shape[1]):
        idata = sdata[dim, :, "fold_index", indx]
        if (None, None) in noise_region:
            raise ValueError(
                "Noise Region Must be specified. Give noise region as a list of tuples.\nFor example, noise_region = [(0.0, 1.0)] corresponds to noise region between 0 and 1."
            )

        # concatenate noise_regions
        noise_0 = idata[dim, noise_region[0], "fi", 0]
        for k in noise_region[1:]:
            noise_0.concatenate(idata[dim, k, "fi", 0], dim)
        if complex_noise:
            noise.append(_np.std(noise_0[dim, slice(0, None)]))
        else:
            noise.append(_np.std(_np.real(noise_0[dim, slice(0, None)])))

    sdata.fold()

    # return SpinData object
    dims = ["signal_region" if x == dim else x for x in sdata.dims]
    coords_new = [
        _np.arange(1) if x == dim else sdata.coords[x] for x in sdata.dims
    ]  # we know that only one sr is there
    signal = _np.array(signal)
    noise = _np.array(noise)
    snr_values = _np.divide(
        signal,
        noise,
        out=_np.full_like(signal, _np.inf, dtype=float),
        where=noise != 0,
    )
    data_new = snr_values.reshape([x.size for x in coords_new])
    snrData = SpinData(data_new, dims, coords_new)
    return snrData
