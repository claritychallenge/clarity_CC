#!/usr/bin/env bash

DIRECTORY=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
. "$DIRECTORY"/paths.sh

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

$PYTHON_BIN "$CLARITY_ROOT"/scripts/check_data.py "$CLARITY_DATA" "$dataset"

