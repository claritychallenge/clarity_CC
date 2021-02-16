#!/usr/bin/env bash

# Script for unpacking clarity data downloads into the clarity root
#
# e.g. unpack.sh clarity_CEC1_data.main.v1_0.tgz <TARGET_DIR>

PACKAGE_NAME=$1
TARGET_DIR=$2

full_path=$(realpath $0)
CLARITY_ROOT=$(dirname $(dirname $full_path) ) # up one level from install script

# Get the top-level directory from the Clarity data
# (Should be 'clarity_CEC1_data' if unpacking main data package)
TOP_DIR=$(tar -tzf "$PACKAGE_NAME" | head -1)

#  Unpack into the top level of the clarity directory
mkdir -p "$TARGET_DIR"
tar -xvzf "$PACKAGE_NAME"  -C "$TARGET_DIR" --keep-old-files

# Add link to the data
(
    cd "$CLARITY_ROOT"/data || exit;
    rm clarity_data;
    ln -s "$TARGET_DIR"/"$TOP_DIR"/clarity_data clarity_data
)

# Add link from data back to downloaded HRIRs
(
    cd "$TARGET_DIR"/"$TOP_DIR"/clarity_data || exit;
    ln -s "$CLARITY_ROOT"/data/hrir hrir
)

# Add a file that was missing from the data package
cp "$CLARITY_ROOT"/install/missing/scenes_listeners.train.json "$CLARITY_ROOT"/data/clarity_data/metadata