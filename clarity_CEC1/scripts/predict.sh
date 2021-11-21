#!/usr/bin/env bash
#
# Calls python code that calculates intelligibility
#

DIRECTORY=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
. "$DIRECTORY"/paths.sh  # Set CLARITY_ROOT, CLARITY_DATA and PYTHON_BIN

usage() { echo "Usage: $0 <dataset> "; exit 0; }
[ $# -eq 0 ] && usage

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--help) usage;;
        *) POSITIONAL+=("$1");;
    esac
    shift
done
set -- "${POSITIONAL[@]}"

dataset=${POSITIONAL[0]}

# Run the HL processing
$PYTHON_BIN "$CLARITY_ROOT"/scripts/run_HL_processing.py  "$CLARITY_DATA"/metadata/scenes."$dataset".json "$CLARITY_DATA"/metadata/listeners.json "$CLARITY_DATA"/metadata/scenes_listeners."$dataset".json "$CLARITY_DATA"/"$dataset"/scenes "$CLARITY_DATA"/"$dataset"/scenes

# Run the intelligibility model
$PYTHON_BIN "$CLARITY_ROOT"/scripts/calculate_SI.py "$CLARITY_DATA"/metadata/scenes."$dataset".json "$CLARITY_DATA"/metadata/listeners.json "$CLARITY_DATA"/metadata/scenes_listeners."$dataset".json "$CLARITY_DATA"/"$dataset"/scenes "$CLARITY_DATA"/"$dataset"/scenes
