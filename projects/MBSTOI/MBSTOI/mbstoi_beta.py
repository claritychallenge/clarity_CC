def mbstoi_beta(xl, xr, yl, yr, gridcoarseness=1):
    """A Python implementation of the Modified Binaural Short-Time
    Objective Intelligibility (MBSTOI) measure as described in:
    A. H. Andersen, J. M. de Haan, Z.-H. Tan, and J. Jensen, “Refinement
    and validation of the binaural short time objective intelligibility
    measure for spatially diverse conditions,” Speech Communication,
    vol. 102, pp. 1-13, Sep. 2018. A. H. Andersen, 10/12-2018

    In combination with the MSBG hearing loss model, which simulates
    hearing thresholds by means of signal attenuation, this code
    simulates approximate thresholds in MBSTOI by means of additive noise.
    See documentation in function create_internal_noise.py.

    All title, copyrights and pending patents in and to the original MATLAB
    Software are owned by Oticon A/S and/or Aalborg University. Please see
    details at http://ah-andersen.net/code/

    Args:
        xl (ndarray): clean speech signal from left ear
        xr (ndarray): clean speech signal from right ear.
        yl (ndarray): noisy/processed speech signal from left ear.
        yr (ndarray): noisy/processed speech signal from right ear.
        gridcoarseness (integer): grid coarseness as denominator of ntaus and ngammas (default: 1)

    Returns
        float: MBSTOI index d

    """

    import numpy as np
    import logging
    import math
    from scipy.signal import resample

    import MBSTOI
    from clarity_core.config import CONFIG

    # Basic STOI parameters
    fs_signal = CONFIG.fs
    fs = 10000  # Sample rate of proposed intelligibility measure in Hz
    N_frame = 256  # Window support in samples
    K = 512  # FFT size in samples
    J = 15  # Number of one-third octave bands
    mn = 150  # Centre frequency of first 1/3 octave band in Hz
    N = 30  # Number of frames for intermediate intelligibility measure (length analysis window)
    dyn_range = 40  # Speech dynamic range in dB

    # Values to define EC grid
    tau_min = -0.001  # Minumum interaural delay compensation in seconds. B: -0.01.
    tau_max = 0.001  # Maximum interaural delay compensation in seconds. B: 0.01.
    ntaus = math.ceil(100 / gridcoarseness)  # Number of tau values to try out
    gamma_min = -20  # Minumum interaural level compensation in dB
    gamma_max = 20  # Maximum interaural level compensation in dB
    ngammas = math.ceil(40 / gridcoarseness)  # Number of gamma values to try out

    # Constants for jitter
    # ITD compensation standard deviation in seconds. Equation 6 Andersen et al. 2018 Refinement
    sigma_delta_0 = 65e-6
    # ILD compensation standard deviation.  Equation 5 Andersen et al. 2018
    sigma_epsilon_0 = 1.5
    # Constant for level shift deviation in dB. Equation 5 Andersen et al. 2018
    alpha_0_db = 13
    # Constant for time shift deviation in seconds. Equation 6 Andersen et al. 2018
    tau_0 = 1.6e-3
    # Constant for level shift deviation. Power for calculation of sigma delta gamma in equation 5 Andersen et al. 2018.
    p = 1.6

    # Prepare signals, ensuring that inputs are column vectors
    xl = xl.flatten()
    xr = xr.flatten()
    yl = yl.flatten()
    yr = yr.flatten()

    # Resample signals to 10 kHz
    if fs_signal != fs:

        logging.debug(f"Resampling signals with sr={fs} for MBSTOI calculation.")
        # Assumes fs_signal is 44.1 kHz
        l = len(xl)
        xl = resample(xl, int(l * (fs / fs_signal) + 1))
        xr = resample(xr, int(l * (fs / fs_signal) + 1))
        yl = resample(yl, int(l * (fs / fs_signal) + 1))
        yr = resample(yr, int(l * (fs / fs_signal) + 1))

    # Remove silent frames
    [xl, xr, yl, yr] = MBSTOI.remove_silent_frames(
        xl, xr, yl, yr, dyn_range, N_frame, N_frame / 2
    )

    # Handle case when signals are zeros
    if (
        abs(np.log10(np.linalg.norm(xl) / np.linalg.norm(xl))) > 5.0
        or abs(np.log10(np.linalg.norm(xr) / np.linalg.norm(yr))) > 5.0
    ):
        sii = 0

    # Add internal noise
    nl, nr = create_internal_noise(yl, yr)
    yl += 10 ** (4 / 20) * nl
    yr += 10 ** (4 / 20) * nr

    # STDFT and filtering
    # Get 1/3 octave band matrix
    [H, cf, fids, freq_low, freq_high] = MBSTOI.thirdoct(
        fs, K, J, mn
    )  # (fs, nfft, num_bands, min_freq)
    cf = 2 * math.pi * cf  # This is now the angular frequency in radians per sec

    # Apply short time DFT to signals and transpose
    xl_hat = MBSTOI.stft(xl, N_frame, K).transpose()
    xr_hat = MBSTOI.stft(xr, N_frame, K).transpose()
    yl_hat = MBSTOI.stft(yl, N_frame, K).transpose()
    yr_hat = MBSTOI.stft(yr, N_frame, K).transpose()

    # Take single sided spectrum of signals
    idx = int(K / 2 + 1)
    xl_hat = xl_hat[0:idx, :]
    xr_hat = xr_hat[0:idx, :]
    yl_hat = yl_hat[0:idx, :]
    yr_hat = yr_hat[0:idx, :]

    # Compute intermediate correlation via EC search
    logging.info(f"Starting EC evaluation")
    # Here intermeduiate correlation coefficients are evaluated for a discrete set of
    # gamma and tau values (a "grid") and the highest value is chosen.
    d = np.zeros((J, np.shape(xl_hat)[1] - N + 1))
    p_ec_max = np.zeros((J, np.shape(xl_hat)[1] - N + 1))

    # Interaural compensation time and level values
    taus = np.linspace(tau_min, tau_max, ntaus)
    gammas = np.linspace(gamma_min, gamma_max, ngammas)

    # Jitter incorporated below - Equations 5 and 6 in Andersen et al. 2018
    sigma_epsilon = (
        np.sqrt(2) * sigma_epsilon_0 * (1 + (abs(gammas) / alpha_0_db) ** p) / 20
    )
    gammas = gammas / 20
    sigma_delta = np.sqrt(2) * sigma_delta_0 * (1 + (abs(taus) / tau_0))

    logging.info(f"Processing EC stage")
    d, p_ec_max = MBSTOI.ec(
        xl_hat,
        xr_hat,
        yl_hat,
        yr_hat,
        J,
        N,
        fids,
        cf.flatten(),
        taus,
        ntaus,
        gammas,
        ngammas,
        d,
        p_ec_max,
        sigma_epsilon,
        sigma_delta,
    )

    # Compute the better ear STOI
    logging.info(f"Computing better ear intermediate correlation coefficients")
    # Arrays for the 1/3 octave envelope
    Xl = np.zeros((J, np.shape(xl_hat)[1]))
    Xr = np.zeros((J, np.shape(xl_hat)[1]))
    Yl = np.zeros((J, np.shape(xl_hat)[1]))
    Yr = np.zeros((J, np.shape(xl_hat)[1]))

    # Apply 1/3 octave bands as described in Eq.(1) of the STOI article
    for k in range(np.shape(xl_hat)[1]):
        Xl[:, k] = np.dot(H, abs(xl_hat[:, k]) ** 2)
        Xr[:, k] = np.dot(H, abs(xr_hat[:, k]) ** 2)
        Yl[:, k] = np.dot(H, abs(yl_hat[:, k]) ** 2)
        Yr[:, k] = np.dot(H, abs(yr_hat[:, k]) ** 2)

    # Arrays for better-ear correlations
    dl_interm = np.zeros((J, len(range(N, len(xl_hat[1]) + 1))))
    dr_interm = np.zeros((J, len(range(N, len(xl_hat[1]) + 1))))
    pl = np.zeros((J, len(range(N, len(xl_hat[1]) + 1))))
    pr = np.zeros((J, len(range(N, len(xl_hat[1]) + 1))))

    # Compute temporary better-ear correlations
    for m in range(N, np.shape(xl_hat)[1]):
        Xl_seg = Xl[:, (m - N) : m]
        Xr_seg = Xr[:, (m - N) : m]
        Yl_seg = Yl[:, (m - N) : m]
        Yr_seg = Yr[:, (m - N) : m]

        for n in range(J):
            xln = Xl_seg[n, :] - np.sum(Xl_seg[n, :]) / N
            xrn = Xr_seg[n, :] - np.sum(Xr_seg[n, :]) / N
            yln = Yl_seg[n, :] - np.sum(Yl_seg[n, :]) / N
            yrn = Yr_seg[n, :] - np.sum(Yr_seg[n, :]) / N
            pl[n, m - N] = np.sum(xln * xln) / np.sum(yln * yln)
            pr[n, m - N] = np.sum(xrn * xrn) / np.sum(yrn * yrn)
            dl_interm[n, m - N] = np.sum(xln * yln) / (
                np.linalg.norm(xln) * np.linalg.norm(yln)
            )
            dr_interm[n, m - N] = np.sum(xrn * yrn) / (
                np.linalg.norm(xrn) * np.linalg.norm(yrn)
            )

    # Get the better ear intermediate coefficients
    idx = np.isfinite(dl_interm)
    dl_interm[~idx] = 0
    idx = np.isfinite(dr_interm)
    dr_interm[~idx] = 0
    p_be_max = np.maximum(pl, pr)
    dbe_interm = np.zeros((np.shape(dl_interm)))

    idx = pl > pr
    dbe_interm[idx] = dl_interm[idx]
    dbe_interm[~idx] = dr_interm[~idx]

    # Compute STOI measure
    # Whenever a single ear provides a higher correlation than the corresponding EC
    # processed alternative,the better-ear correlation is used.
    idx = p_be_max > p_ec_max
    d[idx] = dbe_interm[idx]
    sii = np.mean(d)

    logging.info("MBSTOI processing complete")

    return sii


def create_internal_noise(yl, yr):
    """This is a procedure from Andersen et al. 2017 as described in paper cited
    below. This was developed to represent internal noise for an unimpaired listener
    in Non-intrusive STOI and is provided as an experimental option here.
    Use with caution.

    A. H. Andersen, J. M. de Haan, Z.-H. Tan, and J. Jensen, A non-
    intrusive Short-Time Objective Intelligibility measure, IEEE
    International Conference on Acoustics, Speech and Signal Processing
    (ICASSP), March 2017.

    Args:
    yl (ndarray): noisy/processed speech signal from left ear.
    yr (ndarray): noisy/processed speech signal from right ear.

    Returns
        ndarray: nl, noise signal, left ear
        ndarray: nr, noise signal, right ear
    """

    import numpy as np
    from scipy.signal import lfilter

    # Set constants for internal noise: pure tone threshold filter coefficients w. thirdoct weighting
    # fmt: off
    b = [4.63223568447597e-07,3.95804763423376e-07,3.40416398152586e-07,4.90480621069467e-07,6.68540560585734e-07,7.81028680013174e-07,8.75920651313391e-07,1.01748741957954e-06,1.18421268357796e-06,1.35753870159808e-06,1.53965351342009e-06,1.73668963906151e-06,1.95067109891269e-06,2.18258286882111e-06,2.42921440776578e-06,2.69580602048840e-06,2.98044288584707e-06,3.28351867743714e-06,3.60779264056525e-06,3.95376952087341e-06,4.32092128520547e-06,4.71454621721768e-06,5.13294664889275e-06,5.57491810312488e-06,6.04473868918290e-06,6.54486209032411e-06,7.07466618629234e-06,7.63642607466816e-06,8.23039263197709e-06,8.85819498408318e-06,9.52291135828751e-06,1.02251394490452e-05,1.09661530084539e-05,1.17486288330480e-05,1.25736413314098e-05,1.34416349256600e-05,1.43569760550047e-05,1.53203619024355e-05,1.63321322901544e-05,1.73960578819190e-05,1.85136821566292e-05,1.96860629759823e-05,2.09158332301259e-05,2.22029023210556e-05,2.35515355945801e-05,2.49625527183285e-05,2.64388119248411e-05,2.79825228039093e-05,2.95950196915335e-05,3.12791893225816e-05,3.30345767158884e-05,3.48690564659730e-05,3.67773938539164e-05,3.87672612016679e-05,4.08383190645280e-05,4.29940870979890e-05,4.52381644429392e-05,4.75682926501095e-05,4.99904754323671e-05,5.25071474474778e-05,5.51182526506706e-05,5.78303179199120e-05,6.06412363845543e-05,6.35542092867484e-05,6.65769237982221e-05,6.97075223923519e-05,7.29452172828159e-05,7.63002609421171e-05,7.97724423068562e-05,8.33612290335967e-05,8.70729453885824e-05,9.09095701164118e-05,9.48696053619620e-05,9.89618472734489e-05,0.000103189116333718,0.000107547700624995,0.000112043573870822,0.000116683905733352,0.000121465777208754,0.000126391204207258,0.000131467431986651,0.000136697533335933,0.000142081719303346,0.000147622366433250,0.000153324691147885,0.000159194254998620,0.000165227976659995,0.000171428085712266,0.000177803539711709,0.000184357126590935,0.000191087510482159,0.000198000203478090,0.000205098824185154,0.000212384729532196,0.000219862677124480,0.000227536466716943,0.000235404214905072,0.000243475101804598,0.000251749683802402,0.000260232443346237,0.000268924104380759,0.000277827852415613,0.000286946083570595,0.000296284954716766,0.000305846726935474,0.000315631769995254,0.000325645868801282,0.000335889040272034,0.000346363408554798,0.000357076249226131,0.000368027802902966,0.000379221423881524,0.000390655830964727,0.000402336027321133,0.000414266306563451,0.000426446425393675,0.000438876026308649,0.000451561610239731,0.000464504653200045,0.000477705540396710,0.000491164783668493,0.000504884519727757,0.000518866128525178,0.000533112592016642,0.000547625706691059,0.000562406674216167,0.000577455538206665,0.000592775467484733,0.000608366475260337,0.000624229145723395,0.000640363461529544,0.000656775795182693,0.000673464296720971,0.000690426745725994,0.000707665914126946,0.000725184524498427,0.000742979785261316,0.000761054896218770,0.000779408244800082,0.000798039429815064,0.000816951419713172,0.000836142269671092,0.000855607078563403,0.000875356266747647,0.000895381728594042,0.000915678021435756,0.000936248034263464,0.000957097490757732,0.000978218446812753,0.000999608888377018,0.00102126561282083,0.00104318673155324,0.00106537809792895,0.00108783270261424,0.00111054208015476,0.00113351055133600,0.00115673235660786,0.00118020575582907,0.00120392777981002,0.00122789161264948,0.00125209013721148,0.00127653539242743,0.00130120910308814,0.00132609834123171,0.00135121249321649,0.00137654766048417,0.00140208910370767,0.00142783196455332,0.00145377080871331,0.00147990557694528,0.00150622578868854,0.00153272085768705,0.00155938652394322,0.00158622361433310,0.00161321770909050,0.00164036298643406,0.00166764990658087,0.00169507419157054,0.00172262413811552,0.00175029285672437,0.00177806782539621,0.00180594753737917,0.00183391927363745,0.00186196777364870,0.00189008780270213,0.00191827074001897,0.00194650147718131,0.00197477844367474,0.00200307023770511,0.00203137076909630,0.00205968494982095,0.00208799728356797,0.00211626710419934,0.00214449815325440,0.00217268540983739,0.00220081817477120,0.00222886866014102,0.00225681925463488,0.00228467594364424,0.00231241774431644,0.00234001852588666,0.00236748981321033,0.00239480760680207,0.00242195279631305,0.00244890858626707,0.00247567023620154,0.00250221354064148,0.00252855520050762,0.00255464636256791,0.00258047337463633,0.00260604407981344,0.00263132838933498,0.00265628769528043,0.00268092526308689,0.00270520804488653,0.00272913788468673,0.00275274644788028,0.00277596296827884,0.00279870985556400,0.00282109795805551,0.00284305967803870,0.00286454227944494,0.00288557100985247,0.00290613022665734,0.00292619268733173,0.00294578020838621,0.00296477196987528,0.00298325035159109,0.00300127460624396,0.00301867133685430,0.00303540120883443,0.00305163821866788,0.00306729290389745,0.00308227908239600,0.00309659592825259,0.00311031735407959,0.00312328085682532,0.00313565709293447,0.00314724041596896,0.00315815484979807,0.00316840360834303,0.00317787069060462,0.00318639678504576,0.00319386718433644,0.00320077390423438,0.00320896109489148,0.00321634388444806,0.00321853480481436,0.00321665666486592,0.00322655014883679,0.00326035823410413,0.00322655014883679,0.00321665666486592,0.00321853480481436,0.00321634388444806,0.00320896109489148,0.00320077390423438,0.00319386718433644,0.00318639678504576,0.00317787069060462,0.00316840360834303,0.00315815484979807,0.00314724041596896,0.00313565709293447,0.00312328085682532,0.00311031735407959,0.00309659592825259,0.00308227908239600,0.00306729290389745,0.00305163821866788,0.00303540120883443,0.00301867133685430,0.00300127460624396,0.00298325035159109,0.00296477196987528,0.00294578020838621,0.00292619268733173,0.00290613022665734,0.00288557100985247,0.00286454227944494,0.00284305967803870,0.00282109795805551,0.00279870985556400,0.00277596296827884,0.00275274644788028,0.00272913788468673,0.00270520804488653,0.00268092526308689,0.00265628769528043,0.00263132838933498,0.00260604407981344,0.00258047337463633,0.00255464636256791,0.00252855520050762,0.00250221354064148,0.00247567023620154,0.00244890858626707,0.00242195279631305,0.00239480760680207,0.00236748981321033,0.00234001852588666,0.00231241774431644,0.00228467594364424,0.00225681925463488,0.00222886866014102,0.00220081817477120,0.00217268540983739,0.00214449815325440,0.00211626710419934,0.00208799728356797,0.00205968494982095,0.00203137076909630,0.00200307023770511,0.00197477844367474,0.00194650147718131,0.00191827074001897,0.00189008780270213,0.00186196777364870,0.00183391927363745,0.00180594753737917,0.00177806782539621,0.00175029285672437,0.00172262413811552,0.00169507419157054,0.00166764990658087,0.00164036298643406,0.00161321770909050,0.00158622361433310,0.00155938652394322,0.00153272085768705,0.00150622578868854,0.00147990557694528,0.00145377080871331,0.00142783196455332,0.00140208910370767,0.00137654766048417,0.00135121249321649,0.00132609834123171,0.00130120910308814,0.00127653539242743,0.00125209013721148,0.00122789161264948,0.00120392777981002,0.00118020575582907,0.00115673235660786,0.00113351055133600,0.00111054208015476,0.00108783270261424,0.00106537809792895,0.00104318673155324,0.00102126561282083,0.000999608888377018,0.000978218446812753,0.000957097490757732,0.000936248034263464,0.000915678021435756,0.000895381728594042,0.000875356266747647,0.000855607078563403,0.000836142269671092,0.000816951419713172,0.000798039429815064,0.000779408244800082,0.000761054896218770,0.000742979785261316,0.000725184524498427,0.000707665914126946,0.000690426745725994,0.000673464296720971,0.000656775795182693,0.000640363461529544,0.000624229145723395,0.000608366475260337,0.000592775467484733,0.000577455538206665,0.000562406674216167,0.000547625706691059,0.000533112592016642,0.000518866128525178,0.000504884519727757,0.000491164783668493,0.000477705540396710,0.000464504653200045,0.000451561610239731,0.000438876026308649,0.000426446425393675,0.000414266306563451,0.000402336027321133,0.000390655830964727,0.000379221423881524,0.000368027802902966,0.000357076249226131,0.000346363408554798,0.000335889040272034,0.000325645868801282,0.000315631769995254,0.000305846726935474,0.000296284954716766,0.000286946083570595,0.000277827852415613,0.000268924104380759,0.000260232443346237,0.000251749683802402,0.000243475101804598,0.000235404214905072,0.000227536466716943,0.000219862677124480,0.000212384729532196,0.000205098824185154,0.000198000203478090,0.000191087510482159,0.000184357126590935,0.000177803539711709,0.000171428085712266,0.000165227976659995,0.000159194254998620,0.000153324691147885,0.000147622366433250,0.000142081719303346,0.000136697533335933,0.000131467431986651,0.000126391204207258,0.000121465777208754,0.000116683905733352,0.000112043573870822,0.000107547700624995,0.000103189116333718,9.89618472734489e-05,9.48696053619620e-05,9.09095701164118e-05,8.70729453885824e-05,8.33612290335967e-05,7.97724423068562e-05,7.63002609421171e-05,7.29452172828159e-05,6.97075223923519e-05,6.65769237982221e-05,6.35542092867484e-05,6.06412363845543e-05,5.78303179199120e-05,5.51182526506706e-05,5.25071474474778e-05,4.99904754323671e-05,4.75682926501095e-05,4.52381644429392e-05,4.29940870979890e-05,4.08383190645280e-05,3.87672612016679e-05,3.67773938539164e-05,3.48690564659730e-05,3.30345767158884e-05,3.12791893225816e-05,2.95950196915335e-05,2.79825228039093e-05,2.64388119248411e-05,2.49625527183285e-05,2.35515355945801e-05,2.22029023210556e-05,2.09158332301259e-05,1.96860629759823e-05,1.85136821566292e-05,1.73960578819190e-05,1.63321322901544e-05,1.53203619024355e-05,1.43569760550047e-05,1.34416349256600e-05,1.25736413314098e-05,1.17486288330480e-05,1.09661530084539e-05,1.02251394490452e-05,9.52291135828751e-06,8.85819498408318e-06,8.23039263197709e-06,7.63642607466816e-06,7.07466618629234e-06,6.54486209032411e-06,6.04473868918290e-06,5.57491810312488e-06,5.13294664889275e-06,4.71454621721768e-06,4.32092128520547e-06,3.95376952087341e-06,3.60779264056525e-06,3.28351867743714e-06,2.98044288584707e-06,2.69580602048840e-06,2.42921440776578e-06,2.18258286882111e-06,1.95067109891269e-06,1.73668963906151e-06,1.53965351342009e-06,1.35753870159808e-06,1.18421268357796e-06,1.01748741957954e-06,8.75920651313391e-07,7.81028680013174e-07,6.68540560585734e-07,4.90480621069467e-07,3.40416398152586e-07,3.95804763423376e-07,4.63223568447597e-07]
    # fmt: on

    # Filter the noise
    nl = lfilter(b, 1, np.random.randn(len(yl)))
    nr = lfilter(b, 1, np.random.randn(len(yr)))
    # nl = lfilter(b, 1, np.random.normal(size=np.shape(yl)))
    # nr = lfilter(b, 1, np.random.normal(size=np.shape(yr)))

    return nl, nr