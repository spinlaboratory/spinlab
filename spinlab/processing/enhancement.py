import numpy as _np


def calculate_enhancement(data, off_spectrum_index=0, return_complex_values=False):
    """Calculate enhancement of a power series. Needs integrals as input

    Args:
        integrals (SpinData):
        off_spectrum_index (int):
        return_complex_values (bool):

    Returns:
        enhancements (SpinData): Enhancement values

    Examples:
        >>> data = sl.load("path/to/data")
        >>> spectrum = sl.fourier_transform(data)
        >>> integrals = sl.integrate(spectrum)
        >>> enhancements = sl.calculate_enhancement(integrals)
    """

    enhancements = data.copy()

    proc_parameters = {
        "off_spectrum_index": off_spectrum_index,
        "return_complex_values": return_complex_values,
    }

    if "experiment_type" not in data.attrs.keys():
        raise KeyError("Experiment type not defined")

    if data.attrs["experiment_type"] != "integrals":
        raise ValueError("sldata object does not contain integrals.")

    if data.dims[0] == "Power":
        enhancements.attrs["experiment_type"] = "enhancements_P"

        enhancements.values = (
            enhancements.values / enhancements.values[off_spectrum_index]
        )

    elif data.dims[0] == "B0":
        enhancements.attrs["experiment_type"] = "enhancements_B0"
        print("This is a Spin enhancement profile. Not implemented yet.")

    else:
        raise TypeError(
            "Integration axis not recognized. First dimension should be Power or B0."
        )

    proc_attr_name = "calculate_enhancement"
    enhancements.add_proc_attrs(proc_attr_name, proc_parameters)

    if return_complex_values is True:
        return enhancements

    elif return_complex_values is False:
        return enhancements.real
