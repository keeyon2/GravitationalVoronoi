from setuptools import setup
import numpy
from Cython.Build import cythonize

setup(
  name = 'Gravitational Voronoi',
  ext_modules = cythonize("genVoronoi.pyx"),
  include_dirs=[numpy.get_include()],
)
