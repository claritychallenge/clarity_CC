# -*- coding: utf-8 -*-

import numpy as np
import ctypes

from matlab_matrix_divide import library


def mldivide(a_matrix, b_matrix):
    """
    A clone of MATLAB's mldivide implementation (same as C = A \ B).
    Solves the system of linear equations A*x = B

    Args:
        a_matrix(array-like): a ``M``-by-``N`` array
        b_matrix(array-like): a ``M``-by-``P`` array

    Returns:
        :class:`numpy.ndarray(dtype=numpy.complex128)`: an ``N``-by-``P`` array
    """

    a_matrix = np.asarray(a_matrix, dtype=np.complex128, order="F")
    if len(a_matrix.shape) != 2:
        raise ValueError("a_matrix should be an 2D array!")

    b_matrix = np.asarray(b_matrix, dtype=np.complex128, order="F")
    if len(b_matrix.shape) != 2:
        raise ValueError("b_matrix should be a 2D array!")

    if a_matrix.shape[0] != b_matrix.shape[0]:
        raise ValueError("a_matrix should have the same number of rows as b_matrix!")

    c_matrix = np.zeros(shape=(a_matrix.shape[1], b_matrix.shape[1]), dtype=np.complex128, order="F")

    a_ptr = a_matrix.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    b_ptr = b_matrix.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    c_ptr = c_matrix.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

    library.mldivide(a_ptr, a_matrix.shape[0], a_matrix.shape[1], b_ptr, b_matrix.shape[0], b_matrix.shape[1],
                     c_ptr, c_matrix.shape[0], c_matrix.shape[1])

    return np.asarray(c_matrix, order="C")
