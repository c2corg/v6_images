#!/bin/sh

optipng -force -o7 $1 && advpng -z4 $1 && pngcrush -rem gAMA -rem alla -rem cHRM -rem iCCP -rem sRGB -rem time $1 $1.bak && mv $1.bak $1
