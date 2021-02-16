//
// File: matlab_mldivide_emxAPI.cpp
//
// MATLAB Coder version            : 2.8
// C/C++ source code generated on  : 22-Mar-2016 18:59:27
//

// Include Files
#include "rt_nonfinite.h"
#include "matlab_mldivide.h"
#include "matlab_mldivide_emxAPI.h"
#include "matlab_mldivide_emxutil.h"

// Function Definitions

//
// Arguments    : int numDimensions
//                int *size
// Return Type  : emxArray_creal_T *
//
emxArray_creal_T *emxCreateND_creal_T(int numDimensions, int *size)
{
  emxArray_creal_T *emx;
  int numEl;
  int i;
  emxInit_creal_T(&emx, numDimensions);
  numEl = 1;
  for (i = 0; i < numDimensions; i++) {
    numEl *= size[i];
    emx->size[i] = size[i];
  }

  emx->data = (creal_T *)calloc((unsigned int)numEl, sizeof(creal_T));
  emx->numDimensions = numDimensions;
  emx->allocatedSize = numEl;
  return emx;
}

//
// Arguments    : creal_T *data
//                int numDimensions
//                int *size
// Return Type  : emxArray_creal_T *
//
emxArray_creal_T *emxCreateWrapperND_creal_T(creal_T *data, int numDimensions,
  int *size)
{
  emxArray_creal_T *emx;
  int numEl;
  int i;
  emxInit_creal_T(&emx, numDimensions);
  numEl = 1;
  for (i = 0; i < numDimensions; i++) {
    numEl *= size[i];
    emx->size[i] = size[i];
  }

  emx->data = data;
  emx->numDimensions = numDimensions;
  emx->allocatedSize = numEl;
  emx->canFreeData = false;
  return emx;
}

//
// Arguments    : creal_T *data
//                int rows
//                int cols
// Return Type  : emxArray_creal_T *
//
emxArray_creal_T *emxCreateWrapper_creal_T(creal_T *data, int rows, int cols)
{
  emxArray_creal_T *emx;
  int size[2];
  int numEl;
  int i;
  size[0] = rows;
  size[1] = cols;
  emxInit_creal_T(&emx, 2);
  numEl = 1;
  for (i = 0; i < 2; i++) {
    numEl *= size[i];
    emx->size[i] = size[i];
  }

  emx->data = data;
  emx->numDimensions = 2;
  emx->allocatedSize = numEl;
  emx->canFreeData = false;
  return emx;
}

//
// Arguments    : int rows
//                int cols
// Return Type  : emxArray_creal_T *
//
emxArray_creal_T *emxCreate_creal_T(int rows, int cols)
{
  emxArray_creal_T *emx;
  int size[2];
  int numEl;
  int i;
  size[0] = rows;
  size[1] = cols;
  emxInit_creal_T(&emx, 2);
  numEl = 1;
  for (i = 0; i < 2; i++) {
    numEl *= size[i];
    emx->size[i] = size[i];
  }

  emx->data = (creal_T *)calloc((unsigned int)numEl, sizeof(creal_T));
  emx->numDimensions = 2;
  emx->allocatedSize = numEl;
  return emx;
}

//
// Arguments    : emxArray_creal_T *emxArray
// Return Type  : void
//
void emxDestroyArray_creal_T(emxArray_creal_T *emxArray)
{
  emxFree_creal_T(&emxArray);
}

//
// Arguments    : emxArray_creal_T **pEmxArray
//                int numDimensions
// Return Type  : void
//
void emxInitArray_creal_T(emxArray_creal_T **pEmxArray, int numDimensions)
{
  emxInit_creal_T(pEmxArray, numDimensions);
}

//
// File trailer for matlab_mldivide_emxAPI.cpp
//
// [EOF]
//
