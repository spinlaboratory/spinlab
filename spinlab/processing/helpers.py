"""Shared processing utilities and backward-compatible helper exports.

Most user-facing processing functions now live in domain-specific modules such
as :mod:`spinlab.processing.normalization` or :mod:`spinlab.processing.snr`.
This module keeps small reusable helpers and re-exports the historical helper
functions so older imports continue to work.
"""

from .axis import left_shift, reference
from .complex_data import _create_complexEXT, _create_complexINT, create_complex
from .enhancement import calculate_enhancement
from .modulation import pseudo_modulation
from .normalization import normalize
from .smoothing import smooth
from .snr import signal_to_noise
from .._utils import (
    as_1d_array,
    evenly_spaced_coord_spacing,
    ensure_1d_coord,
    get_default_dim,
    monotonic_direction,
    normalize_region_input,
    require_min_coord_size,
    reshape_along_dim,
    validate_coord_matches_dim,
    validate_dim,
    validate_matching_coord_direction,
    validate_positive_int,
)
