#!/bin/sh

mypy c2corg_images
error=$?
test $error -eq 0 && echo 'Typing OK'
exit $error
