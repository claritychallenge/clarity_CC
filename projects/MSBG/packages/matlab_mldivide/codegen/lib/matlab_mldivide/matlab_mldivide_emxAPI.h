//
// File: matlab_mldivide_emxAPI.h
//
// MATLAB Coder version            : 2.8
// C/C++ source code generated on  : 22-Mar-2016 18:59:27
//
#ifndef __MATLAB_MLDIVIDE_EMXAPI_H__
#define __MATLAB_MLDIVIDE_EMXAPI_H__

// Include Files
#include <math.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include "rt_nonfinite.h"
#include "rtwtypes.h"
#include "matlab_mldivide_types.h"

// Function Declarations
extern emxArray_creal_T *emxCreateND_creal_T(int numDimensions, int *size);
extern emxArray_creal_T *emxCreateWrapperND_creal_T(creal_T *data, int
  numDimensions, int *size);
extern emxArray_creal_T *emxCreateWrapper_creal_T(creal_T *data, int rows, int
  cols);
extern emxArray_creal_T *emxCreate_creal_T(int rows, int cols);
extern void emxDestroyArray_creal_T(emxArray_creal_T *emxArray);
extern void emxInitArray_creal_T(emxArray_creal_T **pEmxArray, int numDimensions);

#endif

//
// File trailer for matlab_mldivide_emxAPI.h
//
// [EOF]
//
