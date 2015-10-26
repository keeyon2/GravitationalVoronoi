cd cython
python setup.py build_ext --inplace
copy genVoronoi.pyd ..
cd ..