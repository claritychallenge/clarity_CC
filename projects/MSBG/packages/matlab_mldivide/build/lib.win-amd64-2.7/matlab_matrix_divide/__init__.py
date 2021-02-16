# -*- coding: utf-8 -*-

import os
import glob
from os.path import abspath, dirname, join
import ctypes


def library_path():
    ext = '.so' if os.name == 'posix' else '.pyd'
    dir = join(dirname(abspath(__file__)))
    print(dir)
    matches = glob.glob(join(dir, '_matlab_matrix_divide*%s' % ext))
    return matches[0]


library = ctypes.CDLL(library_path())
