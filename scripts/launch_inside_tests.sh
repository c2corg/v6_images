#!/bin/sh

lib=`python3 -c 'import site; print(site.getsitepackages()[0])'`
python3 $lib/pytest.py -v tests/inside
