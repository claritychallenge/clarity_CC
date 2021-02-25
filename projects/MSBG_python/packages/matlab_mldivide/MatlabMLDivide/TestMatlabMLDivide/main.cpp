// TestMatlabMLDivide.cpp : Defines the entry point for the console application.
//

//#include "stdafx.h"

#include <iostream>
using namespace std;

//#include <complex.h>

#include "matlab_mldivide.h"

#include "matlab_mldivide_emxAPI.h"

#if defined(_WIN32)
	#define EXPORT_OUT __declspec(dllexport)
#else
	#define EXPORT_OUT
#endif


extern "C"
{
	EXPORT_OUT int test(double* test_complex_array)
	{
		cout << test_complex_array[0] << endl;
		cout << test_complex_array[1] << endl;
		return 0;
	}
}

extern "C"
{
	EXPORT_OUT int mldivide(double* a_data, int a_rows, int a_cols,
		double* b_data, int b_rows, int b_cols, double* c_data, int c_rows, int c_cols)
	{

		emxArray_creal_T* a_array = emxCreate_creal_T(a_rows, a_cols);
		emxArray_creal_T* b_array = emxCreate_creal_T(b_rows, b_cols);
		emxArray_creal_T* c_array = emxCreate_creal_T(c_rows, c_cols);

		int a_size = a_rows * a_cols;
		int b_size = b_rows * b_cols;
		int c_size = c_rows * c_cols;

		for(int i = 0; i < a_size; i++)
		{
			a_array->data[i].re = a_data[2 * i];
			a_array->data[i].im = a_data[2 * i + 1];
		}

		for(int i = 0; i < b_size; i++)
		{
			b_array->data[i].re = b_data[2 * i];
			b_array->data[i].im = b_data[2 * i + 1];
		}

		matlab_mldivide(a_array, b_array, c_array);

		for(int i = 0; i < c_size; i++)
		{
			c_data[2 * i] = c_array->data[i].re;
			c_data[2 * i + 1] = c_array->data[i].im;
		}

		emxDestroyArray_creal_T(a_array);
		emxDestroyArray_creal_T(b_array);
		emxDestroyArray_creal_T(c_array);
		return 0;
	}
}

// Just a dummy init func to make distutils somehow build it.
extern "C"
{
	void init_matlab_matrix_divide()
	{

	}

	void PyInit__matlab_matrix_divide()
	{

	}
}
