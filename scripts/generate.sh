#!/usr/bin/env bash
#
# Calls python code that generates input signals for the hearing aid processor
#

DIRECTORY=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
. "$DIRECTORY"/paths.sh  # Set CLARITY_ROOT, CLARITY_DATA and PYTHON_BIN

GENERATOR_ROOT=$CLARITY_ROOT/projects/SceneGenerator

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

mkdir -p "$CLARITY_DATA"/"$dataset"/scenes

$PYTHON_BIN "$GENERATOR_ROOT"/SceneGenerator/generate_HA_inputs.py "$CLARITY_DATA"/metadata/scenes."$dataset".json  --num_channels "$num_channels" "$CLARITY_DATA" "$CLARITY_DATA"/"$dataset"/scenes

