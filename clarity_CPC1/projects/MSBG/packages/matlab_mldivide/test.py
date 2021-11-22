# -*- coding: utf-8 -*-

import numpy as np
import numpy.testing

import scipy as sp
import scipy.linalg

import unittest

from matlab_matrix_divide import matrix_divide


class TestMatrixDivision(unittest.TestCase):
    def test_mldivide_square(self):
        a_array = np.asarray([[8, 1, 6], [3, 5, 7], [4, 9, 2]], dtype=np.complex128)
        b_array = np.asarray([[15], [15], [15]], dtype=np.complex128)
        c_array = matrix_divide.mldivide(a_array, b_array)

        np.testing.assert_allclose(c_array, [[1], [1], [1]])

    def test_mldivide_nonsquare(self):
        a_array = np.asarray([[1, 2, 0], [0, 4, 3]], dtype=np.complex128)

        b_array = np.asarray([[8], [18]], dtype=np.complex128)
        c_array = matrix_divide.mldivide(a_array, b_array)

        np.testing.assert_allclose(c_array, [[0], [4], [0.66666666666666]])

if __name__ == "__main__":
    unittest.main()