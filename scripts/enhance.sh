#!/usr/bin/env bash
#
# Calls python code that processes the hearing aid inputs for a given dataset
#

DIRECTORY=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
. "$DIRECTORY"/paths.sh  # Set CLARITY_ROOT, CLARITY_DATA and PYTHON_BIN

usage() { echo "Usage: $0 [-n num_chans] <dataset> "; exit 0; }
[ $# -eq 0 ] && usage

num_channels=1

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -n|--num_channels) num_channels="$2"; shift ;;
        -h|--help) usage;;
        *) POSITIONAL+=("$1");;
    esac
    shift
done
set -- "${POSITIONAL[@]}"

dataset=${POSITIONAL[0]}

# Run the HA processing
$PYTHON_BIN "$CLARITY_ROOT"/scripts/run_HA_processing.py  --num_channels "$num_channels" "$CLARITY_DATA"/metadata/scenes."$dataset".json "$CLARITY_DATA"/metadata/listeners.json "$CLARITY_DATA"/metadata/scenes_listeners."$dataset".json "$CLARITY_DATA"/"$dataset"/scenes "$CLARITY_DATA"/"$dataset"/scenes

# Postprocess the HA outputs
$PYTHON_BIN "$CLARITY_ROOT"/scripts/run_HA_postprocessing.py "$CLARITY_DATA"/metadata/scenes."$dataset".json "$CLARITY_DATA"/metadata/scenes_listeners."$dataset".json "$CLARITY_DATA"/"$dataset"/scenes "$CLARITY_DATA"/"$dataset"/scenes
