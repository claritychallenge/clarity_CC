#!/usr/bin/env bash

full_path=$(realpath $0)
CLARITY_ROOT=$(dirname $(dirname $full_path) ) # up one level from install script

echo $CLARITY_ROOT

DATA_DIR=$CLARITY_ROOT/data
TOOLS_DIR=$CLARITY_ROOT/tools

stage=1

if [ $stage -le 1 ]; then
    echo "Downloading HRIR data "
    
    source get_hrirs.sh "$DATA_DIR"
    (
        cd "$DATA_DIR"/clarity_data  || exit
        ln -s "$DATA_DIR"/hrir hrir
    )
fi

if [ $stage -le 2 ]; then
    echo "Creating Python virtual environment "
    (
        cd "$CLARITY_ROOT" || exit
        python -m venv env
        source env/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
    )
fi

if [ $stage -le 3 ]; then
    echo "Downloading and Installing OpenMHA"
    mkdir -p "$TOOLS_DIR"
    
    source get_openmha.sh "$TOOLS_DIR"
fi