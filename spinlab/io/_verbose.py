"""Small helpers for importer verbose output."""


def verbose_print(verbose, *args):
    if verbose:
        print(*args)


def verbose_data_summary(verbose, label, data):
    if not verbose:
        return

    if isinstance(data, dict):
        print("{0}: loaded dictionary with keys {1}".format(label, list(data.keys())))
        return

    dims = getattr(data, "dims", None)
    shape = getattr(data, "shape", None)
    attrs = getattr(data, "attrs", {})
    print("{0}: loaded SpinData with shape {1} and dims {2}".format(label, shape, dims))
    if isinstance(attrs, dict):
        summary_attrs = {
            key: attrs[key]
            for key in [
                "experiment_type",
                "spectrometer_format",
                "nmr_frequency",
                "frequency",
            ]
            if key in attrs
        }
        if summary_attrs:
            print("{0}: attrs {1}".format(label, summary_attrs))
