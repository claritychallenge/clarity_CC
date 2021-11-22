#!/usr/bin/env bash

DIRECTORY=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

. "$DIRECTORY"/paths.sh

$PYTHON_BIN "$CLARITY_ROOT"/scripts/check_data.py "$CLARITY_DATA"
