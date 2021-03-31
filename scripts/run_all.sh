#!/usr/bin/env bash

DIRECTORY=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
. "$DIRECTORY"/paths.sh  # Set CLARITY_ROOT, CLARITY_DATA and PYTHON_BIN

./check_data.sh train || exit -1
./check_data.sh dev || exit -1

echo "Generating HA inputs for all datasets"
for dataset in train dev; do
    ./generate.sh --num_channels 3 "$dataset"
done

echo "Apply HA processing and post-processing to the dev test set"
for dataset in dev; do
    ./enhance.sh --num_channels 3 "$dataset"
done

echo "Run the intelligibility model"
for dataset in dev; do
    ./predict.sh "$dataset"
done


