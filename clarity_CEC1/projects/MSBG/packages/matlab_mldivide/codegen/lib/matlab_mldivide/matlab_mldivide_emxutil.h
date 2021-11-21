//
// File: matlab_mldivide_emxutil.h
//
// MATLAB Coder version            : 2.8
// C/C++ source code generated on  : 22-Mar-2016 18:59:27
//
#ifndef __MATLAB_MLDIVIDE_EMXUTIL_H__
#define __MATLAB_MLDIVIDE_EMXUTIL_H__

// Include Files
#include <math.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include "rt_nonfinite.h"
#include "rtwtypes.h"
#include "matlab_mldivide_types.h"

// Function Declarations
extern void b_emxInit_creal_T(emxArray_creal_T **pEmxArray, int numDimensions);
extern void emxEnsureCapacity(emxArray__common *emxArray, int oldNumel, int
  elementSize);
extern void emxFree_creal_T(emxArray_creal_T **pEmxArray);
extern void emxFree_int32_T(emxArray_int32_T **pEmxArray);
extern void emxFree_real_T(emxArray_real_T **pEmxArray);
extern void emxInit_creal_T(emxArray_creal_T **pEmxArray, int numDimensions);
extern void emxInit_int32_T(emxArray_int32_T **pEmxArray, int numDimensions);
extern void emxInit_real_T(emxArray_real_T **pEmxArray, int numDimensions);

#endif

//
// File trailer for matlab_mldivide_emxutil.h
//
// [EOF]
//
