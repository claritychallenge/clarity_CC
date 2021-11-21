#!/usr/bin/env bash
#
# Script for generating the corrected anechoic reference signals.
#

# Replace the existing scenes json files with the corrected ones.
#   These json files are identical to those originally released except for
#   the HRTF used to construct the anechoic signal, which has now been corrected.

cp data/scenes.dev.json.fixed ../data/clarity_data/metadata/scenes.dev.json
cp data/scenes.train.json.fixed ../data/clarity_data/metadata/scenes.train.json

# First delete the incorrect anechoic reference signals...

rm ../data/clarity_data/dev/scenes/*anechoic*.wav
rm ../data/clarity_data/train/scenes/*anechoic*.wav

# ... and then regenerate the corrected anechoic reference signals.
#   Setting num_channels to 0 will mean that only the anechoic references are recomputed.

./generate.sh --num_channels 0 train
./generate.sh --num_channels 0 dev

# Running predict.sh will now produce correct results.
#
# Results for running 'predict.sh dev' with the baseline enhance.sh can be found in,
#
#    ./scripts/baseline_sii.txt
#
