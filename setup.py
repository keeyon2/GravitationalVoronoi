from distutils.core import setup
from Cython.Build import cythonize

setup(
        name = "My kee client"
        ext_modules = cythonize("keeClientC.pyx"),
)
