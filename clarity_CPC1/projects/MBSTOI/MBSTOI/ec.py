import numpy as np


def ec(
    xl_hat,
    xr_hat,
    yl_hat,
    yr_hat,
    J,
    N,
    fids,
    cf,
    taus,
    ntaus,
    gammas,
    ngammas,
    d,
    p_ec_max,
    sigma_epsilon,
    sigma_delta,
):
    """Run the equalisation-cancellation (EC) stage of the MBSTOI metric.
    The EC loop evaluates one huge equation in every iteration.
    See referenced notes for details.
    The left and right ear signals are level adjusted by gamma (in dB) and time
    shifted by tau relative to one-another and are thereafter subtracted.
    The processed signals are treated similarly.
    To obtain performance similar to that of humans,the EC stage adds jitter
    We are searching for the level and time adjustments that maximise the
    intermediate correlation coefficients d.
    Could add location of source and interferer to this to reduce search space.
    Args:
        xl_hat(ndarray): clean L short-time DFT coefficients (single-sided) per frequency bin and frame
        xr_hat(ndarray): clean R short-time DFT coefficients (single-sided) per frequency bin and frame
        yl_hat(ndarray): proc. L short-time DFT coefficients (single-sided) per frequency bin and frame
        yr_hat(ndarray): proc. R short-time DFT coefficients (single-sided) per frequency bin and frame
        J (int): number of one-third octave bands
        N (int): number of frames for intermediate intelligibility measure
        fids (ndarray): indices of frequency band edges
        cf (ndarray): centre frequencies
        taus (ndarray): interaural delay (tau) values
        ntaus (int): number tau values
        gammas (ndarray): interaural level difference (gamma) values
        ngammas (int): number gamma values
        d (ndarray): grid for intermediate intelligibility measure
        p_ec_max (ndarray): empty grid for maximum values
        sigma_epsilon (ndarray): jitter for gammas
        sigma_delta (ndarray): jitter for taus
    Returns:
        d (ndarray): updated grid for intermediate intelligibility measure
        p_ec_max (ndarray): grid containing maximum values
    """

    taus = np.expand_dims(taus, axis=0)
    sigma_delta = np.expand_dims(sigma_delta, axis=0)
    sigma_epsilon = np.expand_dims(sigma_epsilon, axis=0)
    gammas = np.expand_dims(gammas, axis=0)
    epsexp = np.exp(2 * np.log(10) ** 2 * sigma_epsilon ** 2)

    for i in range(J):  # per frequency band
        tauexp = np.exp(-1j * cf[i] * taus)
        tauexp2 = np.exp(-1j * 2 * cf[i] * taus)
        deltexp = np.exp(-2 * cf[i] ** 2 * sigma_delta ** 2)
        epsdelexp = np.exp(
            0.5
            * (
                np.ones((ntaus, 1))
                * (
                    np.log(10) ** 2 * sigma_epsilon ** 2
                    - cf[i] ** 2 * np.transpose(sigma_delta) ** 2
                )
                * np.ones((1, ngammas))
            )
        )

        for jj in range(np.shape(d)[1]):  # per frame
            seg_xl = xl_hat[int(fids[i, 0] - 1) : int(fids[i, 1]), jj : (jj + N)]
            seg_xr = xr_hat[int(fids[i, 0] - 1) : int(fids[i, 1]), jj : (jj + N)]
            seg_yl = yl_hat[int(fids[i, 0] - 1) : int(fids[i, 1]), jj : (jj + N)]
            seg_yr = yr_hat[int(fids[i, 0] - 1) : int(fids[i, 1]), jj : (jj + N)]

            # All normalised by subtracting mean
            Lx = np.sum(np.conj(seg_xl) * seg_xl, axis=0)
            Lx = np.expand_dims(Lx, axis=0)
            Lx = Lx - np.mean(Lx)
            Rx = np.sum(np.conj(seg_xr) * seg_xr, axis=0)
            Rx = np.expand_dims(Rx, axis=0)
            Rx = Rx - np.mean(Rx)
            rhox = np.sum(np.conj(seg_xr) * seg_xl, axis=0)
            rhox = np.expand_dims(rhox, axis=0)
            rhox = rhox - np.mean(rhox)
            Ly = np.sum(np.conj(seg_yl) * seg_yl, axis=0)
            Ly = np.expand_dims(Ly, axis=0)
            Ly = Ly - np.mean(Ly)
            Ry = np.sum(np.conj(seg_yr) * seg_yr, axis=0)
            Ry = np.expand_dims(Ry, axis=0)
            Ry = Ry - np.mean(Ry)
            rhoy = np.sum(np.conj(seg_yr) * seg_yl, axis=0)
            rhoy = np.expand_dims(rhoy, axis=0)
            rhoy = rhoy - np.mean(rhoy)

            # Evaluate parts of intermediate correlation - EC stage exhaustive search over ITD/ILD values
            # These correspond to equations 7 and 8 in Andersen et al. 2018
            # Calculate Exy
            firstpart = firstpartfunc(Lx, Ly, Rx, Ry, ntaus, gammas, epsexp)
            secondpart = secondpartfunc(Lx, Ly, rhoy, rhox, tauexp, epsdelexp, gammas)
            thirdpart = thirdpartfunc(Rx, Ry, rhoy, rhox, tauexp, epsdelexp, gammas)
            fourthpart = fourthpartfunc(rhox, rhoy, tauexp2, ngammas, deltexp)
            exy = np.real(firstpart - secondpart - thirdpart + fourthpart)

            # Calculate Exx
            firstpart = firstpartfunc(Lx, Lx, Rx, Rx, ntaus, gammas, epsexp)
            secondpart = secondpartfunc(Lx, Lx, rhox, rhox, tauexp, epsdelexp, gammas)
            thirdpart = thirdpartfunc(Rx, Rx, rhox, rhox, tauexp, epsdelexp, gammas)
            fourthpart = fourthpartfunc(rhox, rhox, tauexp2, ngammas, deltexp)
            exx = np.real(firstpart - secondpart - thirdpart + fourthpart)

            # Calculate Eyy
            firstpart = firstpartfunc(Ly, Ly, Ry, Ry, ntaus, gammas, epsexp)
            secondpart = secondpartfunc(Ly, Ly, rhoy, rhoy, tauexp, epsdelexp, gammas)
            thirdpart = thirdpartfunc(Ry, Ry, rhoy, rhoy, tauexp, epsdelexp, gammas)
            fourthpart = fourthpartfunc(rhoy, rhoy, tauexp2, ngammas, deltexp)
            eyy = np.real(firstpart - secondpart - thirdpart + fourthpart)

            # Ensure that intermediate correlation will be sensible and compute it
            # If all minimum values are less than 1e-40, set d[i,jj] to -1
            if np.min(abs(exx * eyy), axis=0).all() < 1e-40:
                d[i, jj] = -1
                continue
            else:
                p = np.divide(exx, eyy)
                tmp = p.max(axis=0)
                idx1 = p.argmax(axis=0)

                # Return overall maximum and index
                p_ec_max[i, jj] = tmp.max()
                idx2 = tmp.argmax()
                d[i, jj] = np.divide(
                    exy[idx1[idx2], idx2],
                    np.sqrt(exx[idx1[idx2], idx2] * eyy[idx1[idx2], idx2]),
                )

    return d, p_ec_max


def firstpartfunc(L1, L2, R1, R2, ntaus, gammas, epsexp):
    result = (
        np.ones((ntaus, 1))
        * (
            (
                10 ** (2 * gammas) * np.sum(L1 * L2)
                + 10 ** (-2 * gammas) * np.sum(R1 * R2)
            )
            * epsexp
        )
        + np.sum(L1 * R2)
        + np.sum(R1 * L2)
    )
    return result


def secondpartfunc(L1, L2, rho1, rho2, tauexp, epsdelexp, gammas):
    result = (
        2
        * (
            np.transpose(
                np.dot(L1, np.real(np.transpose(rho1) * tauexp))
                + np.dot(L2, np.real(np.transpose(rho2) * tauexp))
            )
            * 10 ** gammas
        )
        * epsdelexp
    )
    return result


def thirdpartfunc(R1, R2, rho1, rho2, tauexp, epsdelexp, gammas):
    result = (
        2
        * np.transpose(
            np.dot(
                R1,
                np.real(np.dot(np.transpose(rho1), tauexp)),
            )
            + np.dot(R2, np.real(np.transpose(rho2) * tauexp))
        )
        * 10 ** -gammas
        * epsdelexp
    )
    return result


def fourthpartfunc(rho1, rho2, tauexp2, ngammas, deltexp):
    result = (
        2
        * np.transpose(
            np.real(np.dot(rho1, np.conj(np.transpose(rho2))))
            + deltexp * np.real(np.dot(rho1, np.transpose(rho2) * tauexp2))
        )
        * np.ones((1, ngammas))
    )

    return result
