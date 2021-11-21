def remove_silent_frames(xl, xr, yl, yr, dyn_range, framelen, hop):
    """ 
    Remove silent frames of x and y based on x
    A frame is excluded if its energy is lower than max(energy) - dyn_range
    The frame exclusion is based solely on x, the clean speech signal
    Based on mpariente/pystoi/utils.py

    Args:
        xl (ndarray): clean input signal left channel
        xr (ndarray): clean input signal right channel
        yl (ndarray): degraded/processed signal left channel
        yr (ndarray): degraded/processed signal right channel
        dyn_range (ndarray): range, energy range to determine which frame is silent, 40
        framelen (int): N, window size for energy evaluation, 256
        hop (int): K, hop size for energy evaluation, 128

    Returns :
        xl (ndarray): xl without the silent frames
        xr (ndarray): xr without the silent frames
        yl (ndarray): yl without the silent frames in x
        yl (ndarray): yl without the silent frames in x
    """
    import numpy as np

    EPS = np.finfo("float").eps
    dyn_range = int(dyn_range)
    hop = int(hop)

    # Compute Mask
    w = np.hanning(framelen + 2)[1:-1]

    xl_frames = np.array(
        [w * xl[i : i + framelen] for i in range(0, len(xl) - framelen, hop)]
    )
    xr_frames = np.array(
        [w * xr[i : i + framelen] for i in range(0, len(xr) - framelen, hop)]
    )
    yl_frames = np.array(
        [w * yl[i : i + framelen] for i in range(0, len(yl) - framelen, hop)]
    )
    yr_frames = np.array(
        [w * yr[i : i + framelen] for i in range(0, len(yr) - framelen, hop)]
    )

    # Compute energies in dB
    xl_energies = 20 * np.log10(np.linalg.norm(xl_frames, axis=1) + EPS)
    xr_energies = 20 * np.log10(np.linalg.norm(xr_frames, axis=1) + EPS)

    # Find boolean mask of energies lower than dynamic_range dB
    # with respect to maximum clean speech energy frame
    maskxl = (np.max(xl_energies) - dyn_range - xl_energies) < 0
    maskxr = (np.max(xr_energies) - dyn_range - xr_energies) < 0

    mask = (maskxl == True) | (maskxr == True)

    # Remove silent frames by masking
    xl_frames = xl_frames[mask]
    xr_frames = xr_frames[mask]
    yl_frames = yl_frames[mask]
    yr_frames = yr_frames[mask]

    # init zero arrays to hold x, y with silent frames removed
    n_sil = (len(xl_frames) - 1) * hop + framelen
    xl_sil = np.zeros(n_sil)
    xr_sil = np.zeros(n_sil)
    yl_sil = np.zeros(n_sil)
    yr_sil = np.zeros(n_sil)

    for i in range(xl_frames.shape[0]):
        xl_sil[range(i * hop, i * hop + framelen)] += xl_frames[i, :]
        xr_sil[range(i * hop, i * hop + framelen)] += xr_frames[i, :]
        yl_sil[range(i * hop, i * hop + framelen)] += yl_frames[i, :]
        yr_sil[range(i * hop, i * hop + framelen)] += yr_frames[i, :]

    return xl_sil, xr_sil, yl_sil, yr_sil

