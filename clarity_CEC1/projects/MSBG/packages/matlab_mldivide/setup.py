# -*- coding: utf-8 -*-
import os
import sys
from distutils.core import setup, Extension

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


matlab_source_dir = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "codegen/lib/matlab_mldivide"))

my_source_dir = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "MatlabMLDivide/TestMatlabMLDivide"))

matlab_sources = filter(lambda x: x.endswith(".cpp") or x.endswith(".c"),
                        os.listdir(matlab_source_dir))
matlab_sources = [os.path.join(matlab_source_dir, source)
                  for source in matlab_sources]

my_sources = filter(lambda x: x.endswith(".cpp") or x.endswith(".c"),
                    os.listdir(my_source_dir))
my_sources = [os.path.join(my_source_dir, source) for source in my_sources]


setup(name='PyMatlabMatrixDivide',
      version='0.1',
      author="Woody W. Woodpecker",
      ext_modules=[Extension("matlab_matrix_divide._matlab_matrix_divide",
                             matlab_sources + my_sources,
                             include_dirs=[matlab_source_dir, my_source_dir],
                             ),
      ],
      packages=['matlab_matrix_divide'])
