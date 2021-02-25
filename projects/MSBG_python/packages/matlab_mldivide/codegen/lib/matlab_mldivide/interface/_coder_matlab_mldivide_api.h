/*
 * File: _coder_matlab_mldivide_api.h
 *
 * MATLAB Coder version            : 2.8
 * C/C++ source code generated on  : 22-Mar-2016 18:59:27
 */

#ifndef ___CODER_MATLAB_MLDIVIDE_API_H__
#define ___CODER_MATLAB_MLDIVIDE_API_H__

/* Include Files */
#include "tmwtypes.h"
#include "mex.h"
#include "emlrt.h"
#include <stddef.h>
#include <stdlib.h>
#include "_coder_matlab_mldivide_api.h"

/* Type Definitions */
#ifndef struct_emxArray_creal_T
#define struct_emxArray_creal_T

struct emxArray_creal_T
{
  creal_T *data;
  int32_T *size;
  int32_T allocatedSize;
  int32_T numDimensions;
  boolean_T canFreeData;
};

#endif                                 /*struct_emxArray_creal_T*/

#ifndef typedef_emxArray_creal_T
#define typedef_emxArray_creal_T

typedef struct emxArray_creal_T emxArray_creal_T;

#endif                                 /*typedef_emxArray_creal_T*/

/* Variable Declarations */
extern emlrtCTX emlrtRootTLSGlobal;
extern emlrtContext emlrtContextGlobal;

/* Function Declarations */
extern void matlab_mldivide(emxArray_creal_T *A, emxArray_creal_T *B,
  emxArray_creal_T *C);
extern void matlab_mldivide_api(const mxArray * const prhs[2], const mxArray
  *plhs[1]);
extern void matlab_mldivide_atexit(void);
extern void matlab_mldivide_initialize(void);
extern void matlab_mldivide_terminate(void);
extern void matlab_mldivide_xil_terminate(void);

#endif

/*
 * File trailer for _coder_matlab_mldivide_api.h
 *
 * [EOF]
 */
