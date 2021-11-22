#!/usr/bin/env bash

DIRECTORY=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
. "$DIRECTORY"/paths.sh # Set CLARITY_ROOT, CLARITY_DATA and PYTHON_BIN

./check_data.sh || exit -1

echo "Run the intelligibility model"
for dataset in train; do
    ./predict.sh "$dataset"
done
