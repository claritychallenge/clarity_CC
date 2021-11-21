def freq_interp_sh(f_in, y_in, f):
    """Linear interpolation on logarithmic frequency scale.

    Has samples and hold on edges.

    Args:
        f_in (ndarray): audiogram frequencies (Hz)
        y_in (ndarray): audiogram levels
        f (list): FFT filterbank frequencies

    Returns:
        ndarray: interpolated levels corresponding to filterbank frequencies

    """
    import numpy as np
    from scipy.interpolate import interp1d

    # Checks
    if np.size(f[0]) > 1:
        f = f[0]
    if np.size(f_in[0]) > 1:
        f_in = f_in[0]
    if np.size(y_in[0]) > 1:
        y_in = y_in[0]

    vals = np.pad(
        f_in.astype(np.float), 1, constant_values=((0.5 * f_in[0], 2 * f_in[-1]))
    )
    yvals = np.pad(y_in, 1, constant_values=((y_in[0], y_in[-1])))

    y = interp1d(np.log(vals), yvals, fill_value="extrapolate")(np.log(f))
    y = np.expand_dims(y, 0)

    return y
