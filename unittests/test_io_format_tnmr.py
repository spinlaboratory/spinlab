import os

import pytest
import spinlab as sl


@pytest.mark.xfail(
    raises=UnicodeDecodeError,
    reason="Current TNMR fixture exposes a text-decoding issue in import_tnmr_data.",
)
def test_import_tnmr_1d_fixture():
    data = sl.io.formats.tnmr.import_tnmr(os.path.join(".", "data", "tnmr", "1D.tnt"))

    assert data.attrs["experiment_type"] == "nmr_spectrum"
    assert "t2" in data.dims
