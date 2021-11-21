#!/usr/bin/env bash

# TODO add login credentials

# To install OpenMHA v4.12.0
INSTALLATION_DIR=$1
filename='v4.12.0.tar.gz'
fullpath='https://github.com/HoerTech-gGmbH/openMHA/archive/v4.12.0.tar.gz'

wget "$fullpath" -P "$INSTALLATION_DIR"
tar -xvf "$INSTALLATION_DIR"/"$filename" --directory "$INSTALLATION_DIR"
rm "$INSTALLATION_DIR"/"$filename"
mv "$INSTALLATION_DIR"/openMHA-4.12.0 "$INSTALLATION_DIR"/openMHA

echo "Installing openMHA"
(
    cd "$INSTALLATION_DIR"/openMHA || exit
    ./configure
    make
)

text='Read openMHA-4.12.0/INSTALLATION.md and follow instructions for your system.\
OpenMHA is free software: you can redistribute it and/or modify it under the terms \
of the GNU Affero General Public License as published by the Free Software Foundation, \
version 3 of the License.'
echo "$text"

