#!/usr/bin/env bash

full_path=$(realpath $0)
CLARITY_ROOT=$(dirname $(dirname $full_path)) # up one level from install script

echo $CLARITY_ROOT

DATA_DIR=$CLARITY_ROOT/data
TOOLS_DIR=$CLARITY_ROOT/tools

stage=1

# Make data dir if not already there and initialise data/clarity_data
# to point to the inbuilt test data if link doesn't already exist
mkdir -p "$DATA_DIR"
(
    cd "$DATA_DIR"
    ln -s ../data_test/clarity_data clarity_data
)

if [ $stage -le 1 ]; then
    echo "Creating Python virtual environment "
    (
        cd "$CLARITY_ROOT" || exit
        python3 -m venv env
        source env/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
    )
fi
