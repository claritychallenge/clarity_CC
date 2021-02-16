//
// File: matlab_mldivide.cpp
//
// MATLAB Coder version            : 2.8
// C/C++ source code generated on  : 22-Mar-2016 18:59:27
//

// Include Files
#include "rt_nonfinite.h"
#include "matlab_mldivide.h"
#include "matlab_mldivide_emxutil.h"
#include "colon.h"

// Function Declarations
static creal_T b_eml_matlab_zlarfg(creal_T *alpha1);
static double eml_dlapy3(double x1, double x2, double x3);
static void eml_lusolve(const emxArray_creal_T *A, const emxArray_creal_T *B,
  emxArray_creal_T *X);
static creal_T eml_matlab_zlarfg(int n, creal_T *alpha1, emxArray_creal_T *x,
  int ix0);
static void eml_xgeqp3(emxArray_creal_T *A, emxArray_creal_T *tau,
  emxArray_int32_T *jpvt);
static double eml_xnrm2(int n, const emxArray_creal_T *x, int ix0);
static void eml_xscal(int n, const creal_T a, emxArray_creal_T *x, int ix0);
static double rt_hypotd_snf(double u0, double u1);

// Function Definitions

//
// Arguments    : creal_T *alpha1
// Return Type  : creal_T
//
static creal_T b_eml_matlab_zlarfg(creal_T *alpha1)
{
  creal_T tau;
  double beta1;
  int knt;
  double ar;
  double ai;
  int k;
  tau.re = 0.0;
  tau.im = 0.0;
  if (alpha1->im != 0.0) {
    beta1 = eml_dlapy3(alpha1->re, alpha1->im, 0.0);
    if (alpha1->re >= 0.0) {
      beta1 = -beta1;
    }

    if (fabs(beta1) < 1.0020841800044864E-292) {
      knt = 0;
      do {
        knt++;
        beta1 *= 9.9792015476736E+291;
        alpha1->re *= 9.9792015476736E+291;
        alpha1->im *= 9.9792015476736E+291;
      } while (!(fabs(beta1) >= 1.0020841800044864E-292));

      beta1 = eml_dlapy3(alpha1->re, alpha1->im, 0.0);
      if (alpha1->re >= 0.0) {
        beta1 = -beta1;
      }

      ar = beta1 - alpha1->re;
      ai = 0.0 - alpha1->im;
      if (ai == 0.0) {
        tau.re = ar / beta1;
        tau.im = 0.0;
      } else if (ar == 0.0) {
        tau.re = 0.0;
        tau.im = ai / beta1;
      } else {
        tau.re = ar / beta1;
        tau.im = ai / beta1;
      }

      for (k = 1; k <= knt; k++) {
        beta1 *= 1.0020841800044864E-292;
      }

      alpha1->re = beta1;
      alpha1->im = 0.0;
    } else {
      ar = beta1 - alpha1->re;
      ai = 0.0 - alpha1->im;
      if (ai == 0.0) {
        tau.re = ar / beta1;
        tau.im = 0.0;
      } else if (ar == 0.0) {
        tau.re = 0.0;
        tau.im = ai / beta1;
      } else {
        tau.re = ar / beta1;
        tau.im = ai / beta1;
      }

      alpha1->re = beta1;
      alpha1->im = 0.0;
    }
  }

  return tau;
}

//
// Arguments    : double x1
//                double x2
//                double x3
// Return Type  : double
//
static double eml_dlapy3(double x1, double x2, double x3)
{
  double y;
  double a;
  double b;
  double c;
  a = fabs(x1);
  b = fabs(x2);
  c = fabs(x3);
  if ((a >= b) || rtIsNaN(b)) {
    y = a;
  } else {
    y = b;
  }

  if (c > y) {
    y = c;
  }

  if ((y > 0.0) && (!rtIsInf(y))) {
    a /= y;
    b /= y;
    c /= y;
    y *= sqrt((a * a + c * c) + b * b);
  } else {
    y = (a + b) + c;
  }

  return y;
}

//
// Arguments    : const emxArray_creal_T *A
//                const emxArray_creal_T *B
//                emxArray_creal_T *X
// Return Type  : void
//
static void eml_lusolve(const emxArray_creal_T *A, const emxArray_creal_T *B,
  emxArray_creal_T *X)
{
  emxArray_creal_T *b_A;
  int n;
  int i0;
  int jBcol;
  emxArray_int32_T *ipiv;
  int j;
  int mmj;
  int c;
  int iy;
  int ix;
  double smax;
  int k;
  double s;
  boolean_T c_A;
  double temp_re;
  double temp_im;
  int i1;
  double A_re;
  double A_im;
  double b_A_im;
  double brm;
  int jA;
  int nb;
  emxInit_creal_T(&b_A, 2);
  n = A->size[1];
  i0 = b_A->size[0] * b_A->size[1];
  b_A->size[0] = A->size[0];
  b_A->size[1] = A->size[1];
  emxEnsureCapacity((emxArray__common *)b_A, i0, (int)sizeof(creal_T));
  jBcol = A->size[0] * A->size[1];
  for (i0 = 0; i0 < jBcol; i0++) {
    b_A->data[i0] = A->data[i0];
  }

  emxInit_int32_T(&ipiv, 2);
  jBcol = A->size[1];
  eml_signed_integer_colon(jBcol, ipiv);
  if (A->size[1] < 1) {
  } else {
    if (A->size[1] - 1 <= A->size[1]) {
      i0 = A->size[1] - 1;
    } else {
      i0 = A->size[1];
    }

    for (j = 0; j + 1 <= i0; j++) {
      mmj = n - j;
      c = j * (n + 1);
      if (mmj < 1) {
        iy = -1;
      } else {
        iy = 0;
        if (mmj > 1) {
          ix = c;
          smax = fabs(b_A->data[c].re) + fabs(b_A->data[c].im);
          for (k = 1; k + 1 <= mmj; k++) {
            ix++;
            s = fabs(b_A->data[ix].re) + fabs(b_A->data[ix].im);
            if (s > smax) {
              iy = k;
              smax = s;
            }
          }
        }
      }

      c_A = ((b_A->data[c + iy].re != 0.0) || (b_A->data[c + iy].im != 0.0));
      if (c_A) {
        if (iy != 0) {
          ipiv->data[j] = (j + iy) + 1;
          ix = j;
          iy += j;
          for (k = 1; k <= n; k++) {
            temp_re = b_A->data[ix].re;
            temp_im = b_A->data[ix].im;
            b_A->data[ix] = b_A->data[iy];
            b_A->data[iy].re = temp_re;
            b_A->data[iy].im = temp_im;
            ix += n;
            iy += n;
          }
        }

        i1 = c + mmj;
        for (iy = c + 1; iy + 1 <= i1; iy++) {
          A_re = b_A->data[iy].re;
          A_im = b_A->data[iy].im;
          smax = b_A->data[c].re;
          b_A_im = b_A->data[c].im;
          if (b_A_im == 0.0) {
            if (A_im == 0.0) {
              b_A->data[iy].re = A_re / smax;
              b_A->data[iy].im = 0.0;
            } else if (A_re == 0.0) {
              b_A->data[iy].re = 0.0;
              b_A->data[iy].im = A_im / smax;
            } else {
              b_A->data[iy].re = A_re / smax;
              b_A->data[iy].im = A_im / smax;
            }
          } else if (smax == 0.0) {
            if (A_re == 0.0) {
              b_A->data[iy].re = A_im / b_A_im;
              b_A->data[iy].im = 0.0;
            } else if (A_im == 0.0) {
              b_A->data[iy].re = 0.0;
              b_A->data[iy].im = -(A_re / b_A_im);
            } else {
              b_A->data[iy].re = A_im / b_A_im;
              b_A->data[iy].im = -(A_re / b_A_im);
            }
          } else {
            brm = fabs(smax);
            s = fabs(b_A_im);
            if (brm > s) {
              s = b_A_im / smax;
              smax += s * b_A_im;
              b_A->data[iy].re = (A_re + s * A_im) / smax;
              b_A->data[iy].im = (A_im - s * A_re) / smax;
            } else if (s == brm) {
              if (smax > 0.0) {
                s = 0.5;
              } else {
                s = -0.5;
              }

              if (b_A_im > 0.0) {
                smax = 0.5;
              } else {
                smax = -0.5;
              }

              b_A->data[iy].re = (A_re * s + A_im * smax) / brm;
              b_A->data[iy].im = (A_im * s - A_re * smax) / brm;
            } else {
              s = smax / b_A_im;
              smax = b_A_im + s * smax;
              b_A->data[iy].re = (s * A_re + A_im) / smax;
              b_A->data[iy].im = (s * A_im - A_re) / smax;
            }
          }
        }
      }

      jBcol = (n - j) - 1;
      jA = c + n;
      iy = c + n;
      for (nb = 1; nb <= jBcol; nb++) {
        c_A = ((b_A->data[iy].re != 0.0) || (b_A->data[iy].im != 0.0));
        if (c_A) {
          temp_re = -b_A->data[iy].re - b_A->data[iy].im * 0.0;
          temp_im = b_A->data[iy].re * 0.0 + -b_A->data[iy].im;
          ix = c + 1;
          i1 = mmj + jA;
          for (k = 1 + jA; k + 1 <= i1; k++) {
            A_re = b_A->data[ix].re * temp_re - b_A->data[ix].im * temp_im;
            A_im = b_A->data[ix].re * temp_im + b_A->data[ix].im * temp_re;
            b_A->data[k].re += A_re;
            b_A->data[k].im += A_im;
            ix++;
          }
        }

        iy += n;
        jA += n;
      }
    }
  }

  i0 = X->size[0] * X->size[1];
  X->size[0] = B->size[0];
  X->size[1] = B->size[1];
  emxEnsureCapacity((emxArray__common *)X, i0, (int)sizeof(creal_T));
  jBcol = B->size[0] * B->size[1];
  for (i0 = 0; i0 < jBcol; i0++) {
    X->data[i0].re = B->data[i0].re;
    X->data[i0].im = B->data[i0].im;
  }

  nb = B->size[1];
  for (jBcol = 0; jBcol + 1 < n; jBcol++) {
    if (ipiv->data[jBcol] != jBcol + 1) {
      jA = ipiv->data[jBcol] - 1;
      for (iy = 0; iy + 1 <= nb; iy++) {
        temp_re = X->data[jBcol + X->size[0] * iy].re;
        temp_im = X->data[jBcol + X->size[0] * iy].im;
        X->data[jBcol + X->size[0] * iy] = X->data[jA + X->size[0] * iy];
        X->data[jA + X->size[0] * iy].re = temp_re;
        X->data[jA + X->size[0] * iy].im = temp_im;
      }
    }
  }

  emxFree_int32_T(&ipiv);
  if ((B->size[1] == 0) || ((X->size[0] == 0) || (X->size[1] == 0))) {
  } else {
    for (j = 1; j <= nb; j++) {
      jBcol = n * (j - 1);
      for (k = 0; k + 1 <= n; k++) {
        jA = n * k;
        c_A = ((X->data[k + jBcol].re != 0.0) || (X->data[k + jBcol].im != 0.0));
        if (c_A) {
          for (iy = k + 1; iy + 1 <= n; iy++) {
            smax = X->data[k + jBcol].re * b_A->data[iy + jA].re - X->data[k +
              jBcol].im * b_A->data[iy + jA].im;
            b_A_im = X->data[k + jBcol].re * b_A->data[iy + jA].im + X->data[k +
              jBcol].im * b_A->data[iy + jA].re;
            X->data[iy + jBcol].re -= smax;
            X->data[iy + jBcol].im -= b_A_im;
          }
        }
      }
    }
  }

  if ((B->size[1] == 0) || ((X->size[0] == 0) || (X->size[1] == 0))) {
  } else {
    for (j = 1; j <= nb; j++) {
      jBcol = n * (j - 1);
      for (k = n - 1; k + 1 > 0; k--) {
        jA = n * k;
        c_A = ((X->data[k + jBcol].re != 0.0) || (X->data[k + jBcol].im != 0.0));
        if (c_A) {
          temp_re = X->data[k + jBcol].re;
          temp_im = X->data[k + jBcol].im;
          smax = b_A->data[k + jA].re;
          b_A_im = b_A->data[k + jA].im;
          if (b_A_im == 0.0) {
            if (temp_im == 0.0) {
              X->data[k + jBcol].re = temp_re / smax;
              X->data[k + jBcol].im = 0.0;
            } else if (temp_re == 0.0) {
              X->data[k + jBcol].re = 0.0;
              X->data[k + jBcol].im = temp_im / smax;
            } else {
              X->data[k + jBcol].re = temp_re / smax;
              X->data[k + jBcol].im = temp_im / smax;
            }
          } else if (smax == 0.0) {
            if (temp_re == 0.0) {
              X->data[k + jBcol].re = temp_im / b_A_im;
              X->data[k + jBcol].im = 0.0;
            } else if (temp_im == 0.0) {
              X->data[k + jBcol].re = 0.0;
              X->data[k + jBcol].im = -(temp_re / b_A_im);
            } else {
              X->data[k + jBcol].re = temp_im / b_A_im;
              X->data[k + jBcol].im = -(temp_re / b_A_im);
            }
          } else {
            brm = fabs(smax);
            s = fabs(b_A_im);
            if (brm > s) {
              s = b_A_im / smax;
              smax += s * b_A_im;
              X->data[k + jBcol].re = (temp_re + s * temp_im) / smax;
              X->data[k + jBcol].im = (temp_im - s * temp_re) / smax;
            } else if (s == brm) {
              if (smax > 0.0) {
                s = 0.5;
              } else {
                s = -0.5;
              }

              if (b_A_im > 0.0) {
                smax = 0.5;
              } else {
                smax = -0.5;
              }

              X->data[k + jBcol].re = (temp_re * s + temp_im * smax) / brm;
              X->data[k + jBcol].im = (temp_im * s - temp_re * smax) / brm;
            } else {
              s = smax / b_A_im;
              smax = b_A_im + s * smax;
              X->data[k + jBcol].re = (s * temp_re + temp_im) / smax;
              X->data[k + jBcol].im = (s * temp_im - temp_re) / smax;
            }
          }

          for (iy = 0; iy + 1 <= k; iy++) {
            smax = X->data[k + jBcol].re * b_A->data[iy + jA].re - X->data[k +
              jBcol].im * b_A->data[iy + jA].im;
            b_A_im = X->data[k + jBcol].re * b_A->data[iy + jA].im + X->data[k +
              jBcol].im * b_A->data[iy + jA].re;
            X->data[iy + jBcol].re -= smax;
            X->data[iy + jBcol].im -= b_A_im;
          }
        }
      }
    }
  }

  emxFree_creal_T(&b_A);
}

//
// Arguments    : int n
//                creal_T *alpha1
//                emxArray_creal_T *x
//                int ix0
// Return Type  : creal_T
//
static creal_T eml_matlab_zlarfg(int n, creal_T *alpha1, emxArray_creal_T *x,
  int ix0)
{
  creal_T tau;
  double xnorm;
  double beta1;
  int knt;
  int i3;
  int k;
  double ai;
  double br;
  double bi;
  creal_T dc0;
  double brm;
  tau.re = 0.0;
  tau.im = 0.0;
  if (n <= 0) {
  } else {
    xnorm = eml_xnrm2(n - 1, x, ix0);
    if ((xnorm != 0.0) || (alpha1->im != 0.0)) {
      beta1 = eml_dlapy3(alpha1->re, alpha1->im, xnorm);
      if (alpha1->re >= 0.0) {
        beta1 = -beta1;
      }

      if (fabs(beta1) < 1.0020841800044864E-292) {
        knt = 0;
        do {
          knt++;
          i3 = (ix0 + n) - 2;
          for (k = ix0; k <= i3; k++) {
            xnorm = x->data[k - 1].re;
            ai = x->data[k - 1].im;
            x->data[k - 1].re = 9.9792015476736E+291 * xnorm - 0.0 * ai;
            x->data[k - 1].im = 9.9792015476736E+291 * ai + 0.0 * xnorm;
          }

          beta1 *= 9.9792015476736E+291;
          alpha1->re *= 9.9792015476736E+291;
          alpha1->im *= 9.9792015476736E+291;
        } while (!(fabs(beta1) >= 1.0020841800044864E-292));

        xnorm = eml_xnrm2(n - 1, x, ix0);
        beta1 = eml_dlapy3(alpha1->re, alpha1->im, xnorm);
        if (alpha1->re >= 0.0) {
          beta1 = -beta1;
        }

        xnorm = beta1 - alpha1->re;
        ai = 0.0 - alpha1->im;
        if (ai == 0.0) {
          tau.re = xnorm / beta1;
          tau.im = 0.0;
        } else if (xnorm == 0.0) {
          tau.re = 0.0;
          tau.im = ai / beta1;
        } else {
          tau.re = xnorm / beta1;
          tau.im = ai / beta1;
        }

        br = alpha1->re - beta1;
        bi = alpha1->im;
        if (bi == 0.0) {
          dc0.re = 1.0 / br;
          dc0.im = 0.0;
        } else if (br == 0.0) {
          dc0.re = 0.0;
          dc0.im = -(1.0 / bi);
        } else {
          brm = fabs(br);
          xnorm = fabs(bi);
          if (brm > xnorm) {
            ai = bi / br;
            xnorm = br + ai * bi;
            dc0.re = (1.0 + ai * 0.0) / xnorm;
            dc0.im = (0.0 - ai) / xnorm;
          } else if (xnorm == brm) {
            if (br > 0.0) {
              ai = 0.5;
            } else {
              ai = -0.5;
            }

            if (bi > 0.0) {
              xnorm = 0.5;
            } else {
              xnorm = -0.5;
            }

            dc0.re = (ai + 0.0 * xnorm) / brm;
            dc0.im = (0.0 * ai - xnorm) / brm;
          } else {
            ai = br / bi;
            xnorm = bi + ai * br;
            dc0.re = ai / xnorm;
            dc0.im = (ai * 0.0 - 1.0) / xnorm;
          }
        }

        eml_xscal(n - 1, dc0, x, ix0);
        for (k = 1; k <= knt; k++) {
          beta1 *= 1.0020841800044864E-292;
        }

        alpha1->re = beta1;
        alpha1->im = 0.0;
      } else {
        xnorm = beta1 - alpha1->re;
        ai = 0.0 - alpha1->im;
        if (ai == 0.0) {
          tau.re = xnorm / beta1;
          tau.im = 0.0;
        } else if (xnorm == 0.0) {
          tau.re = 0.0;
          tau.im = ai / beta1;
        } else {
          tau.re = xnorm / beta1;
          tau.im = ai / beta1;
        }

        br = alpha1->re - beta1;
        bi = alpha1->im;
        if (bi == 0.0) {
          dc0.re = 1.0 / br;
          dc0.im = 0.0;
        } else if (br == 0.0) {
          dc0.re = 0.0;
          dc0.im = -(1.0 / bi);
        } else {
          brm = fabs(br);
          xnorm = fabs(bi);
          if (brm > xnorm) {
            ai = bi / br;
            xnorm = br + ai * bi;
            dc0.re = (1.0 + ai * 0.0) / xnorm;
            dc0.im = (0.0 - ai) / xnorm;
          } else if (xnorm == brm) {
            if (br > 0.0) {
              ai = 0.5;
            } else {
              ai = -0.5;
            }

            if (bi > 0.0) {
              xnorm = 0.5;
            } else {
              xnorm = -0.5;
            }

            dc0.re = (ai + 0.0 * xnorm) / brm;
            dc0.im = (0.0 * ai - xnorm) / brm;
          } else {
            ai = br / bi;
            xnorm = bi + ai * br;
            dc0.re = ai / xnorm;
            dc0.im = (ai * 0.0 - 1.0) / xnorm;
          }
        }

        eml_xscal(n - 1, dc0, x, ix0);
        alpha1->re = beta1;
        alpha1->im = 0.0;
      }
    }
  }

  return tau;
}

//
// Arguments    : emxArray_creal_T *A
//                emxArray_creal_T *tau
//                emxArray_int32_T *jpvt
// Return Type  : void
//
static void eml_xgeqp3(emxArray_creal_T *A, emxArray_creal_T *tau,
  emxArray_int32_T *jpvt)
{
  int m;
  int n;
  int mn;
  int i2;
  emxArray_creal_T *work;
  int itemp;
  emxArray_real_T *vn1;
  emxArray_real_T *vn2;
  int k;
  int nmi;
  double smax;
  double s;
  int pvt;
  double c_re;
  double c_im;
  int i;
  int i_i;
  int mmi;
  int ix;
  int iy;
  creal_T atmp;
  int i_ip1;
  int lastv;
  boolean_T exitg3;
  boolean_T b_A;
  int lastc;
  boolean_T exitg2;
  int32_T exitg1;
  double A_re;
  double A_im;
  m = A->size[0];
  n = A->size[1];
  if (A->size[0] <= A->size[1]) {
    mn = A->size[0];
  } else {
    mn = A->size[1];
  }

  i2 = tau->size[0];
  tau->size[0] = mn;
  emxEnsureCapacity((emxArray__common *)tau, i2, (int)sizeof(creal_T));
  eml_signed_integer_colon(A->size[1], jpvt);
  if ((A->size[0] == 0) || (A->size[1] == 0)) {
  } else {
    b_emxInit_creal_T(&work, 1);
    itemp = A->size[1];
    i2 = work->size[0];
    work->size[0] = itemp;
    emxEnsureCapacity((emxArray__common *)work, i2, (int)sizeof(creal_T));
    for (i2 = 0; i2 < itemp; i2++) {
      work->data[i2].re = 0.0;
      work->data[i2].im = 0.0;
    }

    emxInit_real_T(&vn1, 1);
    emxInit_real_T(&vn2, 1);
    itemp = A->size[1];
    i2 = vn1->size[0];
    vn1->size[0] = itemp;
    emxEnsureCapacity((emxArray__common *)vn1, i2, (int)sizeof(double));
    i2 = vn2->size[0];
    vn2->size[0] = itemp;
    emxEnsureCapacity((emxArray__common *)vn2, i2, (int)sizeof(double));
    k = 0;
    for (nmi = 0; nmi + 1 <= n; nmi++) {
      smax = 0.0;
      if (m < 1) {
      } else if (m == 1) {
        smax = rt_hypotd_snf(A->data[k].re, A->data[k].im);
      } else {
        s = 2.2250738585072014E-308;
        pvt = k + m;
        for (itemp = k; itemp + 1 <= pvt; itemp++) {
          c_re = fabs(A->data[itemp].re);
          if (c_re > s) {
            c_im = s / c_re;
            smax = 1.0 + smax * c_im * c_im;
            s = c_re;
          } else {
            c_im = c_re / s;
            smax += c_im * c_im;
          }

          c_re = fabs(A->data[itemp].im);
          if (c_re > s) {
            c_im = s / c_re;
            smax = 1.0 + smax * c_im * c_im;
            s = c_re;
          } else {
            c_im = c_re / s;
            smax += c_im * c_im;
          }
        }

        smax = s * sqrt(smax);
      }

      vn1->data[nmi] = smax;
      vn2->data[nmi] = vn1->data[nmi];
      k += m;
    }

    for (i = 0; i + 1 <= mn; i++) {
      i_i = i + i * m;
      nmi = n - i;
      mmi = (m - i) - 1;
      if (nmi < 1) {
        itemp = 0;
      } else {
        itemp = 1;
        if (nmi > 1) {
          ix = i;
          smax = vn1->data[i];
          for (k = 2; k <= nmi; k++) {
            ix++;
            s = vn1->data[ix];
            if (s > smax) {
              itemp = k;
              smax = s;
            }
          }
        }
      }

      pvt = (i + itemp) - 1;
      if (pvt + 1 != i + 1) {
        ix = m * pvt;
        iy = m * i;
        for (k = 1; k <= m; k++) {
          c_re = A->data[ix].re;
          c_im = A->data[ix].im;
          A->data[ix] = A->data[iy];
          A->data[iy].re = c_re;
          A->data[iy].im = c_im;
          ix++;
          iy++;
        }

        itemp = jpvt->data[pvt];
        jpvt->data[pvt] = jpvt->data[i];
        jpvt->data[i] = itemp;
        vn1->data[pvt] = vn1->data[i];
        vn2->data[pvt] = vn2->data[i];
      }

      if (i + 1 < m) {
        atmp = A->data[i_i];
        tau->data[i] = eml_matlab_zlarfg(1 + mmi, &atmp, A, i_i + 2);
      } else {
        atmp = A->data[i_i];
        tau->data[i] = b_eml_matlab_zlarfg(&atmp);
      }

      A->data[i_i] = atmp;
      if (i + 1 < n) {
        atmp = A->data[i_i];
        A->data[i_i].re = 1.0;
        A->data[i_i].im = 0.0;
        i_ip1 = (i + (i + 1) * m) + 1;
        smax = tau->data[i].re;
        s = -tau->data[i].im;
        if ((smax != 0.0) || (s != 0.0)) {
          lastv = mmi + 1;
          itemp = i_i + mmi;
          exitg3 = false;
          while ((!exitg3) && (lastv > 0)) {
            b_A = ((A->data[itemp].re == 0.0) && (A->data[itemp].im == 0.0));
            if (b_A) {
              lastv--;
              itemp--;
            } else {
              exitg3 = true;
            }
          }

          lastc = nmi - 1;
          exitg2 = false;
          while ((!exitg2) && (lastc > 0)) {
            itemp = i_ip1 + (lastc - 1) * m;
            k = itemp;
            do {
              exitg1 = 0;
              if (k <= (itemp + lastv) - 1) {
                b_A = ((A->data[k - 1].re != 0.0) || (A->data[k - 1].im != 0.0));
                if (b_A) {
                  exitg1 = 1;
                } else {
                  k++;
                }
              } else {
                lastc--;
                exitg1 = 2;
              }
            } while (exitg1 == 0);

            if (exitg1 == 1) {
              exitg2 = true;
            }
          }
        } else {
          lastv = 0;
          lastc = 0;
        }

        if (lastv > 0) {
          if (lastc == 0) {
          } else {
            for (iy = 1; iy <= lastc; iy++) {
              work->data[iy - 1].re = 0.0;
              work->data[iy - 1].im = 0.0;
            }

            iy = 0;
            i2 = i_ip1 + m * (lastc - 1);
            itemp = i_ip1;
            while ((m > 0) && (itemp <= i2)) {
              ix = i_i;
              c_re = 0.0;
              c_im = 0.0;
              pvt = (itemp + lastv) - 1;
              for (k = itemp - 1; k + 1 <= pvt; k++) {
                c_re += A->data[k].re * A->data[ix].re + A->data[k].im * A->
                  data[ix].im;
                c_im += A->data[k].re * A->data[ix].im - A->data[k].im * A->
                  data[ix].re;
                ix++;
              }

              work->data[iy].re += c_re - 0.0 * c_im;
              work->data[iy].im += c_im + 0.0 * c_re;
              iy++;
              itemp += m;
            }
          }

          smax = -smax;
          s = -s;
          if ((smax == 0.0) && (s == 0.0)) {
          } else {
            itemp = i_ip1 - 1;
            pvt = 0;
            for (nmi = 1; nmi <= lastc; nmi++) {
              b_A = ((work->data[pvt].re != 0.0) || (work->data[pvt].im != 0.0));
              if (b_A) {
                c_re = work->data[pvt].re * smax + work->data[pvt].im * s;
                c_im = work->data[pvt].re * s - work->data[pvt].im * smax;
                ix = i_i;
                i2 = lastv + itemp;
                for (k = itemp; k + 1 <= i2; k++) {
                  A_re = A->data[ix].re * c_re - A->data[ix].im * c_im;
                  A_im = A->data[ix].re * c_im + A->data[ix].im * c_re;
                  A->data[k].re += A_re;
                  A->data[k].im += A_im;
                  ix++;
                }
              }

              pvt++;
              itemp += m;
            }
          }
        }

        A->data[i_i] = atmp;
      }

      for (nmi = i + 1; nmi + 1 <= n; nmi++) {
        itemp = (i + m * nmi) + 1;
        if (vn1->data[nmi] != 0.0) {
          smax = rt_hypotd_snf(A->data[i + A->size[0] * nmi].re, A->data[i +
                               A->size[0] * nmi].im) / vn1->data[nmi];
          smax = 1.0 - smax * smax;
          if (smax < 0.0) {
            smax = 0.0;
          }

          s = vn1->data[nmi] / vn2->data[nmi];
          s = smax * (s * s);
          if (s <= 1.4901161193847656E-8) {
            if (i + 1 < m) {
              smax = 0.0;
              if (mmi < 1) {
              } else if (mmi == 1) {
                smax = rt_hypotd_snf(A->data[itemp].re, A->data[itemp].im);
              } else {
                s = 2.2250738585072014E-308;
                pvt = itemp + mmi;
                while (itemp + 1 <= pvt) {
                  c_re = fabs(A->data[itemp].re);
                  if (c_re > s) {
                    c_im = s / c_re;
                    smax = 1.0 + smax * c_im * c_im;
                    s = c_re;
                  } else {
                    c_im = c_re / s;
                    smax += c_im * c_im;
                  }

                  c_re = fabs(A->data[itemp].im);
                  if (c_re > s) {
                    c_im = s / c_re;
                    smax = 1.0 + smax * c_im * c_im;
                    s = c_re;
                  } else {
                    c_im = c_re / s;
                    smax += c_im * c_im;
                  }

                  itemp++;
                }

                smax = s * sqrt(smax);
              }

              vn1->data[nmi] = smax;
              vn2->data[nmi] = vn1->data[nmi];
            } else {
              vn1->data[nmi] = 0.0;
              vn2->data[nmi] = 0.0;
            }
          } else {
            vn1->data[nmi] *= sqrt(smax);
          }
        }
      }
    }

    emxFree_real_T(&vn2);
    emxFree_real_T(&vn1);
    emxFree_creal_T(&work);
  }
}

//
// Arguments    : int n
//                const emxArray_creal_T *x
//                int ix0
// Return Type  : double
//
static double eml_xnrm2(int n, const emxArray_creal_T *x, int ix0)
{
  double y;
  double scale;
  int kend;
  int k;
  double absxk;
  double t;
  y = 0.0;
  if (n < 1) {
  } else if (n == 1) {
    y = rt_hypotd_snf(x->data[ix0 - 1].re, x->data[ix0 - 1].im);
  } else {
    scale = 2.2250738585072014E-308;
    kend = (ix0 + n) - 1;
    for (k = ix0; k <= kend; k++) {
      absxk = fabs(x->data[k - 1].re);
      if (absxk > scale) {
        t = scale / absxk;
        y = 1.0 + y * t * t;
        scale = absxk;
      } else {
        t = absxk / scale;
        y += t * t;
      }

      absxk = fabs(x->data[k - 1].im);
      if (absxk > scale) {
        t = scale / absxk;
        y = 1.0 + y * t * t;
        scale = absxk;
      } else {
        t = absxk / scale;
        y += t * t;
      }
    }

    y = scale * sqrt(y);
  }

  return y;
}

//
// Arguments    : int n
//                const creal_T a
//                emxArray_creal_T *x
//                int ix0
// Return Type  : void
//
static void eml_xscal(int n, const creal_T a, emxArray_creal_T *x, int ix0)
{
  double a_re;
  double a_im;
  int i4;
  int k;
  double x_re;
  double x_im;
  a_re = a.re;
  a_im = a.im;
  i4 = (ix0 + n) - 1;
  for (k = ix0; k <= i4; k++) {
    x_re = x->data[k - 1].re;
    x_im = x->data[k - 1].im;
    x->data[k - 1].re = a_re * x_re - a_im * x_im;
    x->data[k - 1].im = a_re * x_im + a_im * x_re;
  }
}

//
// Arguments    : double u0
//                double u1
// Return Type  : double
//
static double rt_hypotd_snf(double u0, double u1)
{
  double y;
  double a;
  double b;
  a = fabs(u0);
  b = fabs(u1);
  if (a < b) {
    a /= b;
    y = b * sqrt(a * a + 1.0);
  } else if (a > b) {
    b /= a;
    y = a * sqrt(b * b + 1.0);
  } else if (rtIsNaN(b)) {
    y = b;
  } else {
    y = a * 1.4142135623730951;
  }

  return y;
}

//
// MATLAB_MLDIVIDE Summary of this function goes here
//    Detailed explanation goes here
// Arguments    : const emxArray_creal_T *A
//                const emxArray_creal_T *B
//                emxArray_creal_T *C
// Return Type  : void
//
void matlab_mldivide(const emxArray_creal_T *A, const emxArray_creal_T *B,
                     emxArray_creal_T *C)
{
  emxArray_creal_T *b_A;
  emxArray_creal_T *tau;
  emxArray_int32_T *jpvt;
  emxArray_creal_T *b_B;
  unsigned int unnamed_idx_0;
  unsigned int unnamed_idx_1;
  int i;
  int minmn;
  int rankR;
  int maxmn;
  double tol;
  int m;
  int nb;
  int mn;
  double tauj_re;
  double tauj_im;
  double wj_re;
  double wj_im;
  double A_re;
  double A_im;
  emxInit_creal_T(&b_A, 2);
  b_emxInit_creal_T(&tau, 1);
  emxInit_int32_T(&jpvt, 2);
  emxInit_creal_T(&b_B, 2);
  if ((A->size[0] == 0) || (A->size[1] == 0) || ((B->size[0] == 0) || (B->size[1]
        == 0))) {
    unnamed_idx_0 = (unsigned int)A->size[1];
    unnamed_idx_1 = (unsigned int)B->size[1];
    i = C->size[0] * C->size[1];
    C->size[0] = (int)unnamed_idx_0;
    emxEnsureCapacity((emxArray__common *)C, i, (int)sizeof(creal_T));
    i = C->size[0] * C->size[1];
    C->size[1] = (int)unnamed_idx_1;
    emxEnsureCapacity((emxArray__common *)C, i, (int)sizeof(creal_T));
    minmn = (int)unnamed_idx_0 * (int)unnamed_idx_1;
    for (i = 0; i < minmn; i++) {
      C->data[i].re = 0.0;
      C->data[i].im = 0.0;
    }
  } else if (A->size[0] == A->size[1]) {
    eml_lusolve(A, B, C);
  } else {
    i = b_A->size[0] * b_A->size[1];
    b_A->size[0] = A->size[0];
    b_A->size[1] = A->size[1];
    emxEnsureCapacity((emxArray__common *)b_A, i, (int)sizeof(creal_T));
    minmn = A->size[0] * A->size[1];
    for (i = 0; i < minmn; i++) {
      b_A->data[i] = A->data[i];
    }

    eml_xgeqp3(b_A, tau, jpvt);
    rankR = 0;
    if (b_A->size[0] < b_A->size[1]) {
      minmn = b_A->size[0];
      maxmn = b_A->size[1];
    } else {
      minmn = b_A->size[1];
      maxmn = b_A->size[0];
    }

    if (minmn > 0) {
      tol = (double)maxmn * (fabs(b_A->data[0].re) + fabs(b_A->data[0].im)) *
        2.2204460492503131E-16;
      while ((rankR < minmn) && (fabs(b_A->data[rankR + b_A->size[0] * rankR].re)
              + fabs(b_A->data[rankR + b_A->size[0] * rankR].im) >= tol)) {
        rankR++;
      }
    }

    i = b_B->size[0] * b_B->size[1];
    b_B->size[0] = B->size[0];
    b_B->size[1] = B->size[1];
    emxEnsureCapacity((emxArray__common *)b_B, i, (int)sizeof(creal_T));
    minmn = B->size[0] * B->size[1];
    for (i = 0; i < minmn; i++) {
      b_B->data[i] = B->data[i];
    }

    m = b_A->size[0];
    nb = B->size[1];
    minmn = b_A->size[0];
    mn = b_A->size[1];
    if (minmn <= mn) {
      mn = minmn;
    }

    minmn = b_A->size[1];
    maxmn = B->size[1];
    i = C->size[0] * C->size[1];
    C->size[0] = minmn;
    emxEnsureCapacity((emxArray__common *)C, i, (int)sizeof(creal_T));
    i = C->size[0] * C->size[1];
    C->size[1] = maxmn;
    emxEnsureCapacity((emxArray__common *)C, i, (int)sizeof(creal_T));
    minmn *= maxmn;
    for (i = 0; i < minmn; i++) {
      C->data[i].re = 0.0;
      C->data[i].im = 0.0;
    }

    for (minmn = 0; minmn + 1 <= mn; minmn++) {
      tauj_re = tau->data[minmn].re;
      tauj_im = -tau->data[minmn].im;
      if ((tauj_re != 0.0) || (tauj_im != 0.0)) {
        for (maxmn = 0; maxmn + 1 <= nb; maxmn++) {
          wj_re = b_B->data[minmn + b_B->size[0] * maxmn].re;
          wj_im = b_B->data[minmn + b_B->size[0] * maxmn].im;
          for (i = minmn + 1; i + 1 <= m; i++) {
            wj_re += b_A->data[i + b_A->size[0] * minmn].re * b_B->data[i +
              b_B->size[0] * maxmn].re + b_A->data[i + b_A->size[0] * minmn].im *
              b_B->data[i + b_B->size[0] * maxmn].im;
            wj_im += b_A->data[i + b_A->size[0] * minmn].re * b_B->data[i +
              b_B->size[0] * maxmn].im - b_A->data[i + b_A->size[0] * minmn].im *
              b_B->data[i + b_B->size[0] * maxmn].re;
          }

          tol = wj_re;
          wj_re = tauj_re * wj_re - tauj_im * wj_im;
          wj_im = tauj_re * wj_im + tauj_im * tol;
          if ((wj_re != 0.0) || (wj_im != 0.0)) {
            b_B->data[minmn + b_B->size[0] * maxmn].re -= wj_re;
            b_B->data[minmn + b_B->size[0] * maxmn].im -= wj_im;
            for (i = minmn + 1; i + 1 <= m; i++) {
              A_re = b_A->data[i + b_A->size[0] * minmn].re * wj_re - b_A->
                data[i + b_A->size[0] * minmn].im * wj_im;
              A_im = b_A->data[i + b_A->size[0] * minmn].re * wj_im + b_A->
                data[i + b_A->size[0] * minmn].im * wj_re;
              b_B->data[i + b_B->size[0] * maxmn].re -= A_re;
              b_B->data[i + b_B->size[0] * maxmn].im -= A_im;
            }
          }
        }
      }
    }

    for (maxmn = 0; maxmn + 1 <= nb; maxmn++) {
      for (i = 0; i + 1 <= rankR; i++) {
        C->data[(jpvt->data[i] + C->size[0] * maxmn) - 1] = b_B->data[i +
          b_B->size[0] * maxmn];
      }

      for (minmn = rankR - 1; minmn + 1 > 0; minmn--) {
        wj_re = C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].re;
        wj_im = C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].im;
        A_re = b_A->data[minmn + b_A->size[0] * minmn].re;
        A_im = b_A->data[minmn + b_A->size[0] * minmn].im;
        if (A_im == 0.0) {
          if (wj_im == 0.0) {
            C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].re = wj_re /
              A_re;
            C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].im = 0.0;
          } else if (wj_re == 0.0) {
            C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].re = 0.0;
            C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].im = wj_im /
              A_re;
          } else {
            C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].re = wj_re /
              A_re;
            C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].im = wj_im /
              A_re;
          }
        } else if (A_re == 0.0) {
          if (wj_re == 0.0) {
            C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].re = wj_im /
              A_im;
            C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].im = 0.0;
          } else if (wj_im == 0.0) {
            C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].re = 0.0;
            C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].im = -(wj_re /
              A_im);
          } else {
            C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].re = wj_im /
              A_im;
            C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].im = -(wj_re /
              A_im);
          }
        } else {
          tauj_im = fabs(A_re);
          tol = fabs(A_im);
          if (tauj_im > tol) {
            tauj_re = A_im / A_re;
            tol = A_re + tauj_re * A_im;
            C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].re = (wj_re +
              tauj_re * wj_im) / tol;
            C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].im = (wj_im -
              tauj_re * wj_re) / tol;
          } else if (tol == tauj_im) {
            if (A_re > 0.0) {
              tauj_re = 0.5;
            } else {
              tauj_re = -0.5;
            }

            if (A_im > 0.0) {
              tol = 0.5;
            } else {
              tol = -0.5;
            }

            C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].re = (wj_re *
              tauj_re + wj_im * tol) / tauj_im;
            C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].im = (wj_im *
              tauj_re - wj_re * tol) / tauj_im;
          } else {
            tauj_re = A_re / A_im;
            tol = A_im + tauj_re * A_re;
            C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].re = (tauj_re *
              wj_re + wj_im) / tol;
            C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].im = (tauj_re *
              wj_im - wj_re) / tol;
          }
        }

        for (i = 0; i + 1 <= minmn; i++) {
          wj_re = C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].re *
            b_A->data[i + b_A->size[0] * minmn].re - C->data[(jpvt->data[minmn]
            + C->size[0] * maxmn) - 1].im * b_A->data[i + b_A->size[0] * minmn].
            im;
          wj_im = C->data[(jpvt->data[minmn] + C->size[0] * maxmn) - 1].re *
            b_A->data[i + b_A->size[0] * minmn].im + C->data[(jpvt->data[minmn]
            + C->size[0] * maxmn) - 1].im * b_A->data[i + b_A->size[0] * minmn].
            re;
          C->data[(jpvt->data[i] + C->size[0] * maxmn) - 1].re -= wj_re;
          C->data[(jpvt->data[i] + C->size[0] * maxmn) - 1].im -= wj_im;
        }
      }
    }
  }

  emxFree_creal_T(&b_B);
  emxFree_int32_T(&jpvt);
  emxFree_creal_T(&tau);
  emxFree_creal_T(&b_A);
}

//
// File trailer for matlab_mldivide.cpp
//
// [EOF]
//
