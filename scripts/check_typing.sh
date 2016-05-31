#!/bin/sh

lib=`python3 -c 'import site; print(site.getsitepackages()[0])'`
python3 $lib/mypy --silent-imports c2corg_images
error=$?
test $error -eq 0 && echo 'Typing OK'
exit $error
