#!/usr/bin/env bash

# Script for unpacking clarity data downloads into the clarity root
#
# e.g. unpack.sh clarity_CPC1_data.main.v1_1.tgz <TARGET_DIR>

PACKAGE_NAME=$1
TARGET_DIR=$2

full_path=$(realpath $0)
CLARITY_ROOT=$(dirname $(dirname $full_path)) # up one level from install script

TOP_DIR=clarity_CPC1_data

#  Unpack into the top level of the clarity directory
mkdir -p "$TARGET_DIR"
tar -xvzf "$PACKAGE_NAME" -C "$TARGET_DIR" --keep-old-files

# Add link to the data
(
    cd "$CLARITY_ROOT"/data || exit
    rm clarity_data
    ln -s "$TARGET_DIR"/"$TOP_DIR" clarity_data
)
