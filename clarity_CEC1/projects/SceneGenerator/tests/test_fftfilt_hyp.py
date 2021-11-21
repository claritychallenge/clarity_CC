from scipy.signal import convolve, lfilter
import numpy as np
import numpy.testing as npt
import hypothesis.strategies as st
from hypothesis import given, settings, Verbosity
import hypothesis.extra.numpy as hnp
from functools import partial


floats_notnull = partial(st.floats, allow_nan=False, allow_infinity=False)


@settings(max_examples=100, verbosity=Verbosity.verbose)
@given(
    hnp.arrays(
        dtype=np.dtype("float"),
        shape=hnp.array_shapes(min_dims=1, max_dims=1, min_side=2000),
        elements=floats_notnull(),
    ),
    hnp.arrays(
        dtype=np.dtype("float"),
        shape=hnp.array_shapes(min_dims=1, max_dims=1, min_side=100,),
        elements=floats_notnull(),
    ),
    st.sampled_from(["direct"]),
)
def test_fftfilt_hyp(x, b, method):
    """Test output of fftfilt matches output of filter."""

    # x = np.random.random(10000000)

    b = np.random.random(20)
    sfs = convolve(b, x, mode="full", method=method)
    sfs = sfs[0 : len(x)]
    sls = lfilter(b, 1, x)
    npt.assert_allclose(sfs, sls)
