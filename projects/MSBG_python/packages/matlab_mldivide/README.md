# matlab_mldivide

---------------
Installation
---------------

Run setup script ``matlab_mldivide/py_matlab_matrix_divide/setup.py install``

This will build and instal the library to your `Python` distribution.

*NB: this requires working C++ compiler for Python*

---------------
Usage
---------------

Just now only `mldivide` function is implemented:

    from matlab_matrix_divide import matrix_divide
    a_matrix = [[8, 1, 6], [3, 5, 7], [4, 9, 2]]
    b_matrix = [[15], [15], [15]]
    
    c_matrix = matrix_divide.mldivide(a_matrix, b_matrix)
    
    print c_matrix
    
