//
// File: main.cpp
//
// MATLAB Coder version            : 2.8
// C/C++ source code generated on  : 22-Mar-2016 18:59:27
//

//***********************************************************************
// This automatically generated example C main file shows how to call
// entry-point functions that MATLAB Coder generated. You must customize
// this file for your application. Do not modify this file directly.
// Instead, make a copy of this file, modify it, and integrate it into
// your development environment.
//
// This file initializes entry-point function arguments to a default
// size and value before calling the entry-point functions. It does
// not store or use any values returned from the entry-point functions.
// If necessary, it does pre-allocate memory for returned values.
// You can use this file as a starting point for a main function that
// you can deploy in your application.
//
// After you copy the file, and before you deploy it, you must make the
// following changes:
// * For variable-size function arguments, change the example sizes to
// the sizes that your application requires.
// * Change the example values of function arguments to the values that
// your application requires.
// * If the entry-point functions return values, store these values or
// otherwise use them as required by your application.
//
//***********************************************************************
// Include Files
#include "rt_nonfinite.h"
#include "matlab_mldivide.h"
#include "main.h"
#include "matlab_mldivide_terminate.h"
#include "matlab_mldivide_emxAPI.h"
#include "matlab_mldivide_initialize.h"

// Function Declarations
static creal_T argInit_creal_T();
static double argInit_real_T();
static emxArray_creal_T *c_argInit_UnboundedxUnbounded_c();
static void main_matlab_mldivide();

// Function Definitions

//
// Arguments    : void
// Return Type  : creal_T
//
static creal_T argInit_creal_T()
{
  creal_T result;

  // Set the value of the complex variable.
  // Change this value to the value that the application requires.
  result.re = argInit_real_T();
  result.im = argInit_real_T();
  return result;
}

//
// Arguments    : void
// Return Type  : double
//
static double argInit_real_T()
{
  return 0.0;
}

//
// Arguments    : void
// Return Type  : emxArray_creal_T *
//
static emxArray_creal_T *c_argInit_UnboundedxUnbounded_c()
{
  emxArray_creal_T *result;
  static int iv0[2] = { 2, 2 };

  int b_j0;
  int b_j1;

  // Set the size of the array.
  // Change this size to the value that the application requires.
  result = emxCreateND_creal_T(2, *(int (*)[2])&iv0[0]);

  // Loop over the array to initialize each element.
  for (b_j0 = 0; b_j0 < result->size[0U]; b_j0++) {
    for (b_j1 = 0; b_j1 < result->size[1U]; b_j1++) {
      // Set the value of the array element.
      // Change this value to the value that the application requires.
      result->data[b_j0 + result->size[0] * b_j1] = argInit_creal_T();
    }
  }

  return result;
}

//
// Arguments    : void
// Return Type  : void
//
static void main_matlab_mldivide()
{
  emxArray_creal_T *C;
  emxArray_creal_T *A;
  emxArray_creal_T *B;
  emxInitArray_creal_T(&C, 2);

  // Initialize function 'matlab_mldivide' input arguments.
  // Initialize function input argument 'A'.
  A = c_argInit_UnboundedxUnbounded_c();

  // Initialize function input argument 'B'.
  B = c_argInit_UnboundedxUnbounded_c();

  // Call the entry-point 'matlab_mldivide'.
  matlab_mldivide(A, B, C);
  emxDestroyArray_creal_T(C);
  emxDestroyArray_creal_T(B);
  emxDestroyArray_creal_T(A);
}

//
// Arguments    : int argc
//                const char * const argv[]
// Return Type  : int
//
int main(int, const char * const [])
{
  // Initialize the application.
  // You do not need to do this more than one time.
  matlab_mldivide_initialize();

  // Invoke the entry-point functions.
  // You can call entry-point functions multiple times.
  main_matlab_mldivide();

  // Terminate the application.
  // You do not need to do this more than one time.
  matlab_mldivide_terminate();
  return 0;
}

//
// File trailer for main.cpp
//
// [EOF]
//
