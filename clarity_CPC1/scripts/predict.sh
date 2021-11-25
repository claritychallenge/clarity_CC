#!/usr/bin/env bash
#
# Calls python code that calculates intelligibility
#
# Usage:
#
# predict.sh <DATASET> [<NSIGNALS_TO_PROCESS>]
#
# If NSIGNALS_TO_PROCESS is not specified, all signals in the dataset will be processed.
#

DIRECTORY=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
. "$DIRECTORY"/paths.sh # Set CLARITY_ROOT, CLARITY_DATA and PYTHON_BIN

usage() {
    echo "Usage: $0 <dataset> "
    exit 0
}
[ $# -eq 0 ] && usage

while [[ "$#" -gt 0 ]]; do
    case $1 in
    -h | --help) usage ;;
    *) POSITIONAL+=("$1") ;;
    esac
    shift
done
set -- "${POSITIONAL[@]}"

dataset=${POSITIONAL[0]}
nsignals=${POSITIONAL[1]}

# If nsignals is not set, use all signals
if nsignals==""; then
    nsignals=0
fi

echo $CLARITY_DATA
echo $CLARITY_ROOT

# Run the HL processing
$PYTHON_BIN "$CLARITY_ROOT"/scripts/run_HL_processing.py --nsignals="$nsignals" "$CLARITY_DATA"/metadata/scenes.CPC1_train.json "$CLARITY_DATA"/metadata/listeners.CPC1_train.json "$CLARITY_DATA"/metadata/CPC1."$dataset".json "$CLARITY_DATA"/clarity_data/scenes "$CLARITY_DATA"/clarity_data/HA_outputs/"$dataset" "$CLARITY_DATA"/clarity_data/HA_outputs/"$dataset"

# Run the intelligibility model
$PYTHON_BIN "$CLARITY_ROOT"/scripts/calculate_SI.py --nsignals="$nsignals" "$CLARITY_DATA"/metadata/CPC1."$dataset".json "$CLARITY_DATA"/clarity_data/scenes "$CLARITY_DATA"/clarity_data/HA_outputs/"$dataset" mbstoi."$dataset".csv
