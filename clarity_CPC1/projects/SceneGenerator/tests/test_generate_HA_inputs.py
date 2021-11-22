import numpy as np
import hypothesis.strategies as st
from hypothesis import given, settings
import hypothesis.extra.numpy as hnp

from functools import partial
import sys

sys.path.append("clarity")

from clarity_core.signal import sum_signals

floats_notnull = partial(st.floats, allow_nan=False, allow_infinity=False)


@settings(max_examples=100)
@given(
    hnp.arrays(
        dtype=np.dtype("float"),
        shape=hnp.array_shapes(min_dims=1, max_dims=1),
        elements=floats_notnull(),
    ),
    hnp.arrays(
        dtype=np.dtype("float"),
        shape=hnp.array_shapes(min_dims=1, max_dims=1),
        elements=floats_notnull(),
    ),
)
def test_sum_signals(x, y):
    """Test output of fftfilt matches output of filter."""

    # Test for mono signals
    z = sum_signals([x, y])
    assert z[0] == x[0] + y[0]

    # Test for stereo signals
    x = np.vstack([x, x]).T
    y = np.vstack([y, y]).T
    z = sum_signals([x, y])
    assert z[0, 0] == x[0, 0] + y[0, 0]
